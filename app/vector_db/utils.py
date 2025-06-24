import os
import re

import magic
import mimetypes

import uuid
import base64
from datetime import datetime

import logging

import asyncio

from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_qdrant import RetrievalMode, QdrantVectorStore as VectorStore

from qdrant_client.models import VectorParams, Distance

from azure.identity import ClientSecretCredential
from azure.storage.blob import (
    BlobClient,
    ContentSettings,
)

from .qdrant_db import (
    client,
    aclient,
)

from ..embedding_model.azure_emb import embeddings_model

from ..chain.rag_payload_rewriter import rag_payload_rewriter

from ..config import Config

logger = logging.getLogger(__name__)


async def retry_rag_payload_rewriter_ainvoke(payload, retries=3, delay=10):
    for attempt in range(retries):
        try:
            return await rag_payload_rewriter.ainvoke(payload)
        except:
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                error_message = (
                    f"ReadTimeout occurred for payload: {payload}. "
                    f"Skipping after {retries} attempts."
                )
                logger.error(error_message)
                return payload["doc_context"]


class KnowledgeBaseManager:
    """
    Manages the processing and storage of documents in
    Azure Blob Storage and a vector store.

    Args:
        ai_agent_app_name: name of the AI Agent application
        config: configuration settings for the document processor
    """

    def __init__(
        self,
        ai_agent_app_name: str,
        config: Config,
        elements_char_size: int = 16000,
        num_questions_per_chunk: int = 10,
        log_interval: float = 1,
    ):
        self.log_interval = log_interval

        # Azure Blob & ADLS details
        self.tenant_id = config.AZ_TENANT_ID
        self.client_id = config.AZ_CLIENT_ID
        self.client_secret = config.AZ_SECRET_ID
        self.dfs_account_url = config.DFS_ACCOUNT_URL
        self.blob_account_url = config.BLOB_ACCOUNT_URL
        self.blob_container_name = config.BLOB_CONTAINER_NAME

        # Vector DB details
        self.client = client
        self.aclient = aclient
        self.ai_agent_app_name = ai_agent_app_name
        self.collection_name = (
            f"{ai_agent_app_name}" f"-CharChunkSize-{config.child_chunk_size}"
        )
        self.max_batch_size = config.max_batch_size
        self.elements_char_size = elements_char_size
        self.embeddings_size = config.embeddings_size
        self.child_chunk_size = config.child_chunk_size
        self.num_questions_per_chunk = num_questions_per_chunk
        self.search_type = config.search_type
        self.search_kwargs = config.search_kwargs
        self.docs_directory = os.path.join(
            ".",
            "app",
            "docs",
            ai_agent_app_name.lower(),
        )

        # This text splitter is used to create the child documents
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.child_chunk_size,
            chunk_overlap=int(self.child_chunk_size * 0.20),
        )

        # Initialize vectorstore and retriever
        self.vectorstore = self.get_vectorstore()
        self.retriever = self.get_retriever()

    def get_file_extension_and_content_type(
        self,
        base64_string: str,
    ) -> tuple[str, str]:
        """
        This function takes a base64 string as input and returns the file extension and content type.

        :param base64_string: A base64 encoded string
        :return: A tuple containing the file extension and content type
        """
        # Decode the base64 string to get binary data
        binary_data = base64.b64decode(base64_string)

        # Use the magic library to detect the MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(binary_data)

        # Get the file extension from the MIME type
        file_extension = mimetypes.guess_extension(mime_type)

        return (file_extension, mime_type)

    def upload_blob(self, file_path, content_type):
        # Create the ClientSecretCredential object
        credential = ClientSecretCredential(
            self.tenant_id,
            self.client_id,
            self.client_secret,
        )

        # Azure Blob client
        blob_name = file_path.split(f"{self.ai_agent_app_name.lower()}/")[-1]
        logger.info(f"Processing file: {blob_name}")
        blob_url = (
            f"{self.blob_account_url}/"
            + f"{self.blob_container_name}/"
            + f"{self.ai_agent_app_name.lower()}/public_docs/"
            + blob_name
        )
        blob_client = BlobClient.from_blob_url(
            blob_url=blob_url,
            credential=credential,
        )
        # Set the PDF properties on blob
        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition="inline",
        )
        if not blob_client.exists():
            # Create and upload the filein Azure Blob
            with open(file_path, "rb") as f:
                blob_client.upload_blob(f, content_settings=content_settings)
        else:
            # Delete, re-create and upload the filein Azure Blob
            blob_client.delete_blob()
            with open(file_path, "rb") as f:
                blob_client.upload_blob(f, content_settings=content_settings)
        blob_client.close()

        return blob_url

    def upload_extra_kb_blob(
        self,
        filename,
        content_type,
        file_path,
    ):
        # Create the ClientSecretCredential object
        credential = ClientSecretCredential(
            self.tenant_id,
            self.client_id,
            self.client_secret,
        )

        # Azure Blob client
        blob_name = "Additional Documents/" + filename
        logger.info(f"Processing file: {blob_name}")
        blob_url = (
            f"{self.blob_account_url}/"
            + f"{self.blob_container_name}/"
            + f"{self.ai_agent_app_name.lower()}/public_docs/"
            + blob_name
        )
        blob_client = BlobClient.from_blob_url(
            blob_url=blob_url,
            credential=credential,
        )
        # Set the PDF properties on blob
        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition="inline",
        )
        if not blob_client.exists():
            # Create and upload the filein Azure Blob
            with open(file_path, "rb") as f:
                blob_client.upload_blob(f, content_settings=content_settings)
        else:
            # Delete, re-create and upload the filein Azure Blob
            blob_client.delete_blob()
            with open(file_path, "rb") as f:
                blob_client.upload_blob(f, content_settings=content_settings)
        blob_client.close()

        return blob_url

    def upload_user_blob(
        self,
        filename,
        doc_id,
        user_id,
        content_type,
        file_path,
    ):
        # Create the ClientSecretCredential object
        credential = ClientSecretCredential(
            self.tenant_id,
            self.client_id,
            self.client_secret,
        )

        # Azure Blob client
        user_directory = f"{self.ai_agent_app_name.lower()}/users_docs/{user_id}"
        blob_name = f"{user_directory}/{doc_id}/{filename}"
        logger.info(f"Processing file: {blob_name}")
        blob_url = (
            f"{self.blob_account_url}/{self.blob_container_name}/" + f"{blob_name}"
        )
        blob_client = BlobClient.from_blob_url(
            blob_url=blob_url,
            credential=credential,
        )
        # Set the File properties on blob
        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition="inline",
        )
        if not blob_client.exists():
            # Create and upload the file in Azure Blob
            with open(file_path, "rb") as f:
                blob_client.upload_blob(f, content_settings=content_settings)
        else:
            # Delete, re-create and upload the file in Azure Blob
            blob_client.delete_blob()
            with open(file_path, "rb") as f:
                blob_client.upload_blob(f, content_settings=content_settings)

        return blob_url

    def upload_user_image_blob(
        self,
        base64_data: str,
        user_id: str,
        session_id: str,
    ) -> str:
        # Generate a UUID using the current datetime as a seed
        current_time = datetime.now().strftime("%Y%m%d%H%M%S%f")
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, current_time))

        # Infer the file extension and content type
        file_extension, content_type = self.get_file_extension_and_content_type(
            base64_data,
        )

        # Create the ClientSecretCredential object
        credential = ClientSecretCredential(
            self.tenant_id,
            self.client_id,
            self.client_secret,
        )

        # Azure Blob client
        filename = f"{doc_id}{file_extension}"
        user_directory = f"{self.ai_agent_app_name.lower()}/users_images/{user_id}"
        blob_name = f"{user_directory}/{session_id}/{filename}"
        logger.info(f"Processing file: {blob_name}")
        blob_url = (
            f"{self.blob_account_url}/{self.blob_container_name}/" + f"{blob_name}"
        )
        blob_client = BlobClient.from_blob_url(
            blob_url=blob_url,
            credential=credential,
        )

        # Set the File properties on blob
        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition="inline",
        )

        # Decode the base64 data
        image_data = base64.b64decode(base64_data)

        if not blob_client.exists():
            # Create and upload the file in Azure Blob
            blob_client.upload_blob(
                image_data,
                content_settings=content_settings,
            )
        else:
            # Delete, re-create and upload the file in Azure Blob
            blob_client.delete_blob()
            blob_client.upload_blob(
                image_data,
                content_settings=content_settings,
            )

        return blob_url

    def upload_user_generated_blob(
        self,
        base64_data: str,
        user_id: str,
        session_id: str,
    ) -> str:
        # Generate a UUID using the current datetime as a seed
        current_time = datetime.now().strftime("%Y%m%d%H%M%S%f")
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, current_time))

        # Infer the file extension and content type
        file_extension, content_type = self.get_file_extension_and_content_type(
            base64_data,
        )

        # Create the ClientSecretCredential object
        credential = ClientSecretCredential(
            self.tenant_id,
            self.client_id,
            self.client_secret,
        )

        # Azure Blob client
        filename = f"{doc_id}{file_extension}"
        user_directory = (
            f"{self.ai_agent_app_name.lower()}/users_generated_docs/{user_id}"
        )
        blob_name = f"{user_directory}/{session_id}/{filename}"
        logger.info(f"Processing file: {blob_name}")
        blob_url = (
            f"{self.blob_account_url}/{self.blob_container_name}/" + f"{blob_name}"
        )
        blob_client = BlobClient.from_blob_url(
            blob_url=blob_url,
            credential=credential,
        )

        # Set the File properties on blob
        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition="inline",
        )

        # Decode the base64 data
        file_data = base64.b64decode(base64_data)

        if not blob_client.exists():
            # Create and upload the file in Azure Blob
            blob_client.upload_blob(
                file_data,
                content_settings=content_settings,
            )
        else:
            # Delete, re-create and upload the file in Azure Blob
            blob_client.delete_blob()
            blob_client.upload_blob(
                file_data,
                content_settings=content_settings,
            )

        return blob_url

    def get_vectorstore(self):
        if not self.client.collection_exists(self.collection_name):
            logger.info("Creating Vector Store")

            # The vectorstore to use to index the child chunks
            self.client.create_collection(
                self.collection_name,
                vectors_config=VectorParams(
                    size=self.embeddings_size, distance=Distance.COSINE
                ),
            )

            self.vectorstore = VectorStore(
                self.client,
                collection_name=self.collection_name,
                embedding=embeddings_model,
                retrieval_mode=RetrievalMode.DENSE,
            )

            logger.info("Loading knowledge base to Vector Store")

            # asyncio.create_task(
            #     self.process_base_knowledge()
            # )

            return VectorStore(
                self.client,
                collection_name=self.collection_name,
                embedding=embeddings_model,
                retrieval_mode=RetrievalMode.DENSE,
            )

        else:
            return VectorStore(
                self.client,
                collection_name=self.collection_name,
                embedding=embeddings_model,
                retrieval_mode=RetrievalMode.DENSE,
            )

    async def process_base_knowledge(self):
        # Get a list of all files in the directory
        pdf_files = [
            os.path.join(root, name)
            for root, _, files in os.walk(self.docs_directory)
            for name in files
            if name.endswith(".pdf")
        ]
        pptx_files = [
            os.path.join(root, name)
            for root, _, files in os.walk(self.docs_directory)
            for name in files
            if name.endswith(".ppt") or name.endswith(".pptx")
        ]
        docxs_files = [
            os.path.join(root, name)
            for root, _, files in os.walk(self.docs_directory)
            for name in files
            if name.endswith(".doc") or name.endswith(".docx")
        ]
        xlsx_files = [
            os.path.join(root, name)
            for root, _, files in os.walk(self.docs_directory)
            for name in files
            if name.endswith(".xlsx") or name.endswith(".xls")
        ]

        vector_db_documents = []

        # Process each PDF file
        total_pdfs = len(pdf_files)
        progress = 0
        for i, file_path in enumerate(pdf_files):
            blob_url = self.upload_blob(
                file_path=file_path, content_type="application/pdf"
            )

            # Load and split the document
            loader = self.process_pdf(file_path=file_path)
            docs = await loader.aload()

            for doc in docs:
                doc.metadata["URL"] = blob_url

            # Add them to the vector db docs list
            vector_db_documents.extend(docs)

            # Calculate the percentage of completion
            progress = (i + 1) / total_pdfs * 100

            # Log the progress
            logger.info(
                f"RAG {self.ai_agent_app_name}: PDF docs... "
                f"{progress:.2f}% complete"
            )

        # Process each Microsoft PPT file
        total_pptxs = len(pptx_files)
        progress = 0
        for i, file_path in enumerate(pptx_files):
            blob_url = self.upload_blob(
                file_path=file_path,
                content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )

            # Load and split the document
            loader = self.process_ppt(file_path=file_path)
            docs = await loader.aload()

            for doc in docs:
                doc.metadata["URL"] = blob_url

            # Add them to the vector db docs list
            vector_db_documents.extend(docs)

            # Calculate the percentage of completion
            progress = (i + 1) / total_pptxs * 100

            # Log the progress
            logger.info(
                f"RAG {self.ai_agent_app_name}: PPT docs... "
                f"{progress:.2f}% complete"
            )

        # Process each Microsoft Word file
        total_docxs = len(docxs_files)
        progress = 0
        for i, file_path in enumerate(docxs_files):
            blob_url = self.upload_blob(
                file_path=file_path, content_type="application/msword"
            )

            # Load and split the document
            loader = self.process_word(file_path=file_path)
            docs = await loader.aload()

            for doc in docs:
                doc.metadata["URL"] = blob_url

            # Add them to the vector db docs list
            vector_db_documents.extend(docs)

            # Calculate the percentage of completion
            progress = (i + 1) / total_docxs * 100

            # Log the progress
            logger.info(
                f"RAG {self.ai_agent_app_name}: Word docs... "
                f"{progress:.2f}% complete"
            )

        # Process each Microsoft Excel file
        total_xlsxs = len(xlsx_files)
        progress = 0
        for i, file_path in enumerate(xlsx_files):
            blob_url = self.upload_blob(
                file_path=file_path, content_type="application/vnd.ms-excel"
            )

            # Load and split the document
            loader = self.process_excel(file_path=file_path)
            docs = await loader.aload()

            for doc in docs:
                doc.metadata["URL"] = blob_url

            # Add them to the vector db docs list
            vector_db_documents.extend(docs)

            # Calculate the percentage of completion
            progress = (i + 1) / total_xlsxs * 100

            # Log the progress at specified intervals
            logger.info(
                f"RAG {self.ai_agent_app_name}: Excel docs... "
                f"{progress:.2f}% complete"
            )

        # Filter empty docs
        vector_db_documents = [v for v in vector_db_documents if v.page_content != ""]

        for doc in vector_db_documents:
            doc.metadata["public_doc"] = "true"

        async for _, _docs in self.process_docs(
            docs=vector_db_documents,
        ):
            if _docs:
                vector_db_documents = _docs

        # Add docs to the vector db
        total_docs = len(vector_db_documents)
        progress = 0
        for i in range(0, total_docs, self.max_batch_size):
            await self.vectorstore.aadd_documents(
                vector_db_documents[i : i + self.max_batch_size],
            )

            # Calculate the percentage of completion
            progress = (i + self.max_batch_size) / total_docs * 100

            # Log the progress
            logger.info(
                f"Adding child docs to {self.collection_name} "
                f"vectorstore... {progress:.2f}% complete"
            )

            # give the API service some time to process the queries backlog
            if (i != 0) & (i % 100 == 0):
                await asyncio.sleep(60)

    def normalize_text(self, input_text):
        s = re.sub(r"\s+", " ", input_text).strip()
        s = re.sub(r". ,", "", s)
        # remove all instances of multiple spaces
        s = s.replace("..", ".")
        s = s.replace(". .", ".")
        s = s.replace("\n", "")
        s = s.strip()

        return s

    async def process_docs(
        self,
        docs,
        user_doc=False,
    ):
        # Total number of documents
        total_docs = len(docs)
        sub_docs = []
        progress = 0

        for i, doc in enumerate(docs):
            # Add citation info in content
            if "page_number" not in doc.metadata.keys():
                doc.metadata["page_number"] = 1
            page_num = doc.metadata["page_number"]
            filename = doc.metadata["filename"]
            filename = "".join(filename.split(".")[:-1])
            filename = filename.replace("_", " ")
            filename = " ".join(filename.split())

            if user_doc:
                file_title = f"On user's shared file titled as: '{filename}', "
            else:
                file_title = f"On the file titled as: '{filename}', "

            doc.metadata["ai_agent_app"] = self.ai_agent_app_name
            doc.metadata["context_type"] = "rag_result"
            doc.metadata.pop("orig_elements")

            if (doc.metadata["category"] == "Table") and (
                "text_as_html" in doc.metadata.keys()
            ):
                doc.metadata["original_page_content"] = doc.metadata["text_as_html"]
                doc.page_content = await retry_rag_payload_rewriter_ainvoke(
                    {
                        "doc_context": (
                            f"{file_title}"
                            f"the following HTML Table was found:\n\n"
                            f"{str(doc.metadata['text_as_html'])}"
                        ),
                        "num_questions_per_chunk": self.num_questions_per_chunk,
                    }
                )
                doc.metadata["original_page_content"] = (
                    f"{file_title}"
                    f"page {page_num}, "
                    f"the following HTML Table was found:\n\n"
                    f"{str(doc.metadata['original_page_content'])}"
                )
                doc.metadata.pop("text_as_html")
                _sub_docs = [doc]
            else:
                doc.page_content = self.normalize_text(doc.page_content)
                doc.metadata["original_page_content"] = doc.page_content
                doc.page_content = await retry_rag_payload_rewriter_ainvoke(
                    {
                        "doc_context": (
                            f"{file_title}"
                            f"the following information was found:\n\n"
                            f"{str(doc.page_content)}"
                        ),
                        "num_questions_per_chunk": self.num_questions_per_chunk,
                    }
                )
                doc.metadata["original_page_content"] = (
                    f"{file_title}"
                    f"page {page_num}, "
                    f"the following information was found:\n\n"
                    f"{str(doc.metadata['original_page_content'])}"
                )
                _sub_docs = self.child_splitter.split_documents([doc])

            sub_docs.extend(_sub_docs)

            # Calculate the percentage of completion
            progress = (i + 1) / total_docs * 100

            # Log the progress
            logger.info(
                f"{self.collection_name}: post-processing {filename} docs... "
                f"{progress:.2f}% complete"
            )
            yield progress, None

            # give the API service some time to process the queries backlog
            if (i != 0) & (i % 5 == 0):
                await asyncio.sleep(30)

        yield progress, sub_docs

    def process_pdf(self, file_path, partition_strategy="hi_res"):
        return UnstructuredPDFLoader(
            file_path=file_path,
            mode="elements",
            include_metadata=True,
            strategy=partition_strategy,
            include_page_breaks=False,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=self.elements_char_size,
            new_after_n_chars=int(self.elements_char_size * 0.75),
            combine_text_under_n_chars=int(self.elements_char_size * 0.15),
            extract_images_in_pdf=False,
            extract_image_block_types=None,  # can be ["Image", "Table"]
            extract_image_block_to_payload=False,
            extract_image_block_output_dir=None,
            languages=["eng", "ara", "spa", "por"],
        )

    def process_ppt(self, file_path, partition_strategy="hi_res"):
        return UnstructuredPowerPointLoader(
            file_path=file_path,
            mode="elements",
            include_metadata=True,
            strategy=partition_strategy,
            include_page_breaks=False,
            include_slide_notes=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=self.elements_char_size,
            new_after_n_chars=int(self.elements_char_size * 0.75),
            combine_text_under_n_chars=int(self.elements_char_size * 0.15),
            detect_language_per_element=False,
            date_from_file_object=False,
            languages=["eng", "ara", "spa", "por"],
        )

    def process_word(self, file_path, partition_strategy="hi_res"):
        return UnstructuredWordDocumentLoader(
            file_path=file_path,
            mode="elements",
            include_metadata=True,
            strategy=partition_strategy,
            include_page_breaks=False,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=self.elements_char_size,
            new_after_n_chars=int(self.elements_char_size * 0.75),
            combine_text_under_n_chars=int(self.elements_char_size * 0.15),
            date_from_file_object=False,
            languages=["eng", "ara", "spa", "por"],
        )

    def process_excel(self, file_path, partition_strategy="hi_res"):
        return UnstructuredExcelLoader(
            file_path=file_path,
            mode="elements",
            include_metadata=True,
            strategy=partition_strategy,
            include_page_breaks=False,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=self.elements_char_size,
            new_after_n_chars=int(self.elements_char_size * 0.75),
            combine_text_under_n_chars=int(self.elements_char_size * 0.15),
            detect_language_per_element=True,
            include_header=False,
            find_subtable=True,
            languages=["eng", "ara", "spa", "por"],
            starting_page_number=1,
        )

    def get_retriever(self):
        logger.info("Loading Vector Store")

        return self.vectorstore.as_retriever(
            search_type=self.search_type,
            search_kwargs=self.search_kwargs,
        )
