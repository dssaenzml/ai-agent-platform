from typing import List, Optional

from langchain_core.documents import Document
from pydantic import BaseModel, Field


class ConversationInputChat(BaseModel):
    """Input for the chat endpoint."""

    query: str = Field(
        ...,
        description="The human query to the chat system.",
        extra={"widget": {"type": "chat", "input": "query"}},
    )
    username: str = Field(
        "user@example.com",
        description="The human username to the chat system.",
        extra={"widget": {"type": "chat", "input": "username"}},
    )
    oauth_token: str = Field(
        None,
        description="The Azure OAuth connection token.",
    )
    uploaded_image_blob_URL: Optional[List[str]] = Field(
        [],
        description=(
            "The list of Azure Blob URL for the image(s) provided by human "
            "to the chat system."
        ),
        extra={"widget": {"type": "chat", "input": "uploaded_image_blob_URL"}},
    )
    web_search: bool = Field(
        False,  # Default value for web_search
        description="The human request to do web search with the chat system.",
        extra={"widget": {"type": "chat", "input": "web_search"}},
    )


class ConversationOutputChat(BaseModel):
    """Output for the chat endpoint."""

    context: List[Document]
    answer: str
    sow_blob_url: str
    sow_filename: str


class SoWType(BaseModel):
    """Scope of Work type."""

    sow_type: str = Field(
        description="The scope of work type requested, one of the following: "
        "'Consultancy Services', 'General Services', 'Manpower Supply'"
    )


class ConsultancyServicesSoWDetails(BaseModel):
    """Details required to fill in an SoW template."""

    preamble: str = Field(
        description="This section should include a brief high-level introduction "
        "about the project such as location, objectives and parties "
        "involved in execution."
    )
    general_sow: str = Field(
        description="This section should include an overview of general scope of "
        "services to be performed."
    )
    description_of_services: str = Field(
        description="This section should include a detailed description of the "
        "actual services to be performed."
    )
    codes_standards: str = Field(
        description="This section should include any details around codes and "
        "standards to ensure compliance with the project requirements."
    )
    drawings_specifications: str = Field(
        description="This section should include any detailed drawings and "
        "specifications to ensure compliance with the project requirements."
    )
    review_meetings_reporting: str = Field(
        description="This section describes procedural requirements as regards "
        "review and approval processes and meetings and reporting "
        "requirements."
    )
    training_requirements: str = Field(
        description="This section should include any training that is required "
        "to be provided under the contract."
    )
    interface_requirements: str = Field(
        description="This section should a description of any and all "
        "interfaces that the contractor is required to manage in the "
        "execution of the services. This should include but not be "
        "limited to interfaces and restrictions in terms of availability "
        "of site access and interference with other contractors."
    )
    deliverables: str = Field(
        description="This section should an exhaustive list of deliverables that "
        "the contractor may be required to provide during the course "
        "of execution of the services and upon completion."
    )
    exclusions: str = Field(
        description="This section should include, for the sake of clarity, items "
        "that are excluded from the scope but could be misconstrued as "
        "being part of the scope. Examples include:\n\n"
        "a)	scope executed by others.\n"
        "b)	items free issued by the Employer.\n"
        "c)	charges or expenses to be borne by the Employer."
    )
    optional_scope: str = Field(
        description="This section should optional scope items, which may be "
        "instructed later at Employer's discretion."
    )
    facilities_by_employer: str = Field(
        description="This section should include an exhaustive list and description "
        "of the facilities and support services to be provided by the "
        "Employer such as:\n\n"
        "a)	any specific data or information to be provided at a later "
        "date.\n"
        "b)	office space and related facilities.\n"
        "c)	any other item of general assistance."
    )


class SendEmail(BaseModel):
    """Binary score to assess user requires email to be sent."""

    binary_score: str = Field(description="Email needs to be sent, 'yes' or 'no'")
