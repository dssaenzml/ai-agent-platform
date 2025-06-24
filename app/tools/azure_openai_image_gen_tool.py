
import logging

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException

from openai import BadRequestError

from .tool_wrapper.azure_openai_image_gen_api_wrapper import (
    AzureDallEAPIWrapper
)

from ..model.file_gen_model import ImageGenerationInput

from ..vector_db.utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)


class AzureOpenAIImageGenerationTool(BaseTool):
    """
    Tool for generating images based on a given query.

    This tool uses the AzureOpenAI API to generate images based on a 
    provided query. The generated image is provided through a URL.

    Attributes:
        name: The name of the tool.
        description: A brief description of the tool's functionality.
        args_schema: The schema for the input arguments.
        return_direct: Tool should return the result directly.
    """
    name: str = "ImageGenerationQuery"
    description: str = (
        "useful for when you need to generate images based on a given "
        "prompt, style, quality and size"
        )
    args_schema: Type[BaseModel] = ImageGenerationInput
    return_direct: bool = True
    api_wrapper: Type[AzureDallEAPIWrapper] = None
    kbm: Type[KnowledgeBaseManager] = None

    def __init__(
        self, 
        api_wrapper: Type[AzureDallEAPIWrapper], 
        kbm: Type[KnowledgeBaseManager], 
        ):
        super().__init__()
        self.api_wrapper = api_wrapper
        self.kbm = kbm

    def generate_image(
        self, 
        query: str, 
        user_id: str, 
        session_id: str, 
        ) -> Optional[str]:
        """
        Generates an image based on the provided query.

        Args:
            query: A detailed description of the image to be generated.
            user_id: The ID of the user requesting the image.
            session_id: The session ID for the current operation.

        Returns:
            A URL pointing to the generated image.
        """
        try:
            generation_message, generated_image_base64 = self.api_wrapper.run(
                query
                )
            
            image_blob_url = self.kbm.upload_user_image_blob(
                base64_data=generated_image_base64, 
                user_id=user_id, 
                session_id=session_id, 
                )

            logger.info("Image generated successfully.")
            return generation_message, image_blob_url
        except BadRequestError as e:
            logger.error(f"Unable to generate image due to: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unable to generate image due to: {e}")
            raise ToolException(e)
    
    def _run(
        self, 
        query: str, 
        user_id: str, 
        session_id: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> Dict[str, Any]:
        """
        Synchronously generates an image.

        Args:
            query: A detailed description of the image to be generated.
            user_id: The ID of the user requesting the image.
            session_id: The session ID for the current operation.

        Returns:
            A dictionary containing the URL pointing to the generated image.
        """
        try:
            generation_message, image_blob_url = self.generate_image(
                query=query, 
                user_id=user_id, 
                session_id=session_id, 
            )
            return {
                "status": "success", 
                "image_generation_message": generation_message, 
                "image_blob_url": image_blob_url, 
                }
        except BadRequestError as e:
            logger.error(f"Unable to generate image due to: {e}")
            return {
                "status": "failure", 
                "message": 
                    "Your request was rejected as a result of our "
                    "safety system. Your prompt may contain text that is "
                    "not allowed by our safety system.", 
                }
        except ToolException as e:
            logger.error(f"Unable to generate image due to: {e}")
            return {
                "status": "failure", 
                "message": "Image generation failed.", 
                }
        except Exception as e:
            logger.error(f"Unable to generate image due to: {e}")
            return {
                "status": "failure", 
                "message": "Image generation failed.", 
                }

    async def _arun(
        self,
        query: str, 
        user_id: str, 
        session_id: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """
        Asynchronously generates an image.

        Args:
            query: A detailed description of the image to be generated.
            user_id: The ID of the user requesting the image.
            session_id: The session ID for the current operation.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the URL pointing to the generated image.
        """
        return self._run(
            query=query, 
            user_id=user_id, 
            session_id=session_id, 
            run_manager=run_manager.get_sync(), 
            )
