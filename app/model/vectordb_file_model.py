from pydantic import Field

from langserve import CustomUserType


class KBFileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    file: str = Field(
        ...,
        description="The base64 encoded file string of the to-be-processed.",
        extra={"widget": {"type": "base64file"}},
    )
    filename: str = Field(
        ...,
        description="The file name of the to-be-processed file.",
    )
    extract_type: str = Field(
        "high_resolution",
        description="The extraction type for the to-be-processed file.",
    )


class KBFileProcessingOutput(CustomUserType):
    message: dict = Field(
        {},
        description="The processed file's output message.",
    )


class KBFilePurgingRequest(CustomUserType):
    """Request including the document filename."""

    filename: str = Field(
        ...,
        description="The file name of the to-be-purged file.",
    )


class KBFilePurgingOutput(CustomUserType):
    message: dict = Field(
        {},
        description="The purged file's output message.",
    )


class UserFileProcessingRequest(CustomUserType):
    """Request including a base64 encoded file."""

    file: str = Field(
        ...,
        description="The base64 encoded file string of the to-be-processed.",
        extra={"widget": {"type": "base64file"}},
    )
    filename: str = Field(
        ...,
        description="The file name of the to-be-processed file.",
    )
    doc_id: str = Field(
        "test",
        description="The unique identifier of the to-be-processed file.",
    )
    user_id: str = Field(
        "user@example.com",
        description="The user ID of owner of the to-be-processed file.",
    )
    extract_type: str = Field(
        "fast",
        description="The extraction type for the to-be-processed file.",
    )


class UserFileProcessingOutput(CustomUserType):
    message: dict = Field(
        {},
        description="The processed file's output message.",
    )


class UserFilePurgingRequest(CustomUserType):
    """Request including the document id."""

    doc_id: str = Field(
        None,
        description="The unique identifier of the processed file.",
    )
    user_id: str = Field(
        ...,
        description="The user ID of owner of the processed file(s).",
    )


class UserFilePurgingOutput(CustomUserType):
    message: dict = Field(
        {},
        description="The purged file's output message.",
    )
