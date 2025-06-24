from typing import List

from qdrant_client import models


def get_update(a, b):
    return b


### Vector DB filters
# Public general documents
def generate_public_docs_filter() -> models.Filter:
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.public_doc",
                match=models.MatchValue(value="true"),
            ),
        ]
    )


# Individual documents
def generate_individual_docs_filter(
    doc_ids: List[str],
    user_id: str = None,
) -> models.Filter:
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.doc_id",
                match=models.MatchAny(any=doc_ids),
            ),
            # ONLY FILTERING BY DOC ID
            # models.FieldCondition(
            #     key="metadata.user_id",
            #     match=models.MatchValue(value=user_id),
            #     ),
        ],
        must_not=[
            models.FieldCondition(
                key="metadata.public_doc", match=models.MatchValue(value="true")
            ),
        ],
    )
