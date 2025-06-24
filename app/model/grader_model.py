
from pydantic import BaseModel, Field


# Data model
class SimpleRAGWebGradeQuery(BaseModel):
    """Score to assess the type of query."""

    query_type: str = Field(
        description=
        "Type of query: 'simple_query', 'rag_query', or 'web_search_query'"
    )


# Data model
class SimpleRAGWebImgGradeQuery(BaseModel):
    """Score to assess the type of query."""

    query_type: str = Field(
        description=(
        "Type of query: 'simple_query', 'rag_query', 'web_search_query', "
        "or 'img_gen_query'"
        )
    )


# Data model
class SimpleRAGWebImgPDFGradeQuery(BaseModel):
    """Score to assess the type of query."""

    query_type: str = Field(
        description=(
        "Type of query: 'simple_query', 'rag_query', 'web_search_query', "
        "'img_gen_query', or 'pdf_gen_query'"
        )
    )


# Data model
class SimpleRAGWebSoWGradeQuery(BaseModel):
    """Score to assess the type of query."""

    query_type: str = Field(
        description=(
        "Type of query: 'simple_query', 'rag_query', 'web_search_query', "
        "or 'sow_doc_query'"
        )
    )
    

# Data model
class SimpleRAGWebSQLGradeQuery(BaseModel):
    """Score to assess the type of query."""

    query_type: str = Field(
        description=(
        "Type of query: 'simple_query', 'rag_query', 'web_search_query', "
        "or 'sql_query'"
        )
    )


# Data model
class SimpleSQLGradeQuery(BaseModel):
    """Score to assess the type of query."""

    query_type: str = Field(
        description=
        "Type of query: 'simple_query' or 'sql_query'"
    )


# Data model
class GradeModeration(BaseModel):
    """Binary score to assess question requires moderation."""

    binary_score: str = Field(
        description=
        "Question needs to be moderated, 'yes' or 'no'"
    )


# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )
