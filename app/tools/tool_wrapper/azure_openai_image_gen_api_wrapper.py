
import logging
from typing import Any, Dict, Mapping, Optional, Tuple, Union

from langchain_core.utils import (
    from_env,
    get_pydantic_field_names,
    secret_from_env,
)
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self

from langchain_community.utils.openai import is_openai_v1

from openai import BadRequestError

logger = logging.getLogger(__name__)


class AzureDallEAPIWrapper(BaseModel):
    """Wrapper for Azure OpenAI's DALL-E Image Generator.

    https://platform.openai.com/docs/guides/images/generations?context=node

    Usage instructions:

    1. `pip install openai`
    2. save your OPENAI_API_KEY in an environment variable
    """

    client: Any = None  #: :meta private:
    async_client: Any = Field(default=None, exclude=True)  #: :meta private:
    model_name: str = Field(default="dall-e-3", alias="model")
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    az_openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env(
            "AZURE_OPENAI_API_KEY",
            default=None,
        ),
    )
    """Automatically inferred from env var `AZURE_OPENAI_API_KEY` if not provided."""
    az_openai_endpoint: Optional[str] = Field(
        alias="base_url", 
        default_factory=from_env("AZURE_OPENAI_API_BASE", default=None)
    )
    """Base URL path for API requests, leave blank if not using a proxy or service 
        emulator."""
    az_openai_api_version: Optional[str] = Field(
        alias="api_version",
        default_factory=from_env(
            "AZURE_OPENAI_API_VERSION",
            default=None,
        ),
    )
    az_openai_deployment_name: Optional[str] = Field(
        alias="api_deployment_name",
        default_factory=from_env(
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            default=None,
        ),
    )
    openai_organization: Optional[str] = Field(
        alias="organization",
        default_factory=from_env(
            ["OPENAI_ORG_ID", "OPENAI_ORGANIZATION"], default=None
        ),
    )
    """Automatically inferred from env var `OPENAI_ORG_ID` if not provided."""
    # to support explicit proxy for OpenAI
    openai_proxy: str = Field(default_factory=from_env("OPENAI_PROXY", default=""))
    request_timeout: Union[float, Tuple[float, float], Any, None] = Field(
        default=None, alias="timeout"
    )
    n: int = 1
    """Number of images to generate"""
    size: str = Field(
        "1024x1024", 
        description=(
            "The pixel size of the image, one of '1024x1024', '1792x1024', "
            "or '1024x1792'."
            )
    )
    """Size of image to generate"""
    separator: str = "\n"
    """Separator to use when multiple URLs are returned."""
    quality: Optional[str] = Field(
        "standard", 
        description=(
            "The quality of the image, either 'hd' or 'standard'."
            )
    )
    """Quality of the image that will be generated"""
    style: Optional[str] = Field(
        "vivid", 
        description=(
            "The style of the image, either 'natural' or 'vivid'."
            )
    )
    """Style of the image that will be generated"""
    response_format: Optional[str] = Field(
        "b64_json", 
        description=(
            "The format in which the generated images are returned, "
            "one of 'url', or 'b64_json'."
            )
    )
    """Response format of the generated image"""
    max_retries: int = 2
    """Maximum number of retries to make when generating."""
    default_headers: Union[Mapping[str, str], None] = None
    default_query: Union[Mapping[str, object], None] = None
    # Configure a custom httpx client. See the
    # [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
    http_client: Union[Any, None] = None
    """Optional httpx.Client."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: Dict[str, Any]) -> Any:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name in extra:
                raise ValueError(f"Found {field_name} supplied twice.")
            if field_name not in all_required_field_names:
                logger.warning(
                    f"""WARNING! {field_name} is not default parameter.
                    {field_name} was transferred to model_kwargs.
                    Please confirm that {field_name} is what you intended."""
                )
                extra[field_name] = values.pop(field_name)

        invalid_model_kwargs = all_required_field_names.intersection(extra.keys())
        if invalid_model_kwargs:
            raise ValueError(
                f"Parameters {invalid_model_kwargs} should be specified explicitly. "
                f"Instead they were passed in as part of `model_kwargs` parameter."
            )

        values["model_kwargs"] = extra
        return values

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that api key and python package exists in environment."""
        try:
            import openai

        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )

        if is_openai_v1():
            client_params: dict = {
                "api_version": self.az_openai_api_version,
                "azure_endpoint": self.az_openai_endpoint,
                "azure_deployment": self.az_openai_deployment_name,
                "api_key": (
                    self.az_openai_api_key.get_secret_value() if self.az_openai_api_key else None
                ),
                "organization": self.openai_organization,
                "timeout": self.request_timeout,
                "max_retries": self.max_retries,
                "default_headers": self.default_headers,
                "default_query": self.default_query,
                "http_client": self.http_client,
            }

            if not self.client:
                self.client = openai.AzureOpenAI(**client_params).images
            if not self.async_client:
                self.async_client = openai.AsyncAzureOpenAI(**client_params).images  # type: ignore[arg-type, arg-type, arg-type, arg-type, arg-type, arg-type, arg-type, arg-type]
        elif not self.client:
            self.client = openai.Image  # type: ignore[attr-defined]
        else:
            pass
        return self


    def run(self, query: str) -> str:
        """Run query through OpenAI and parse result."""
        
        try:
            if is_openai_v1():
                response = self.client.generate(
                    prompt=query,
                    model=self.model_name,
                    n=self.n,
                    size=self.size,
                    quality=self.quality,
                    style=self.style,
                    response_format=self.response_format,
                )
                image_revised_prompt = self.separator.join([
                    item.revised_prompt 
                    for item in response.data
                    ])
                if self.response_format == "url":
                    image_content = self.separator.join([
                        item.url 
                        for item in response.data
                        ])
                elif self.response_format == "b64_json":
                    image_content = self.separator.join([
                        item.b64_json 
                        for item in response.data
                        ])
            else:
                response = self.client.generate(
                    prompt=query,
                    model=self.model_name,
                    n=self.n,
                    size=self.size,
                    quality=self.quality,
                    style=self.style,
                    response_format=self.response_format,
                )
                image_revised_prompt = self.separator.join([
                    item.revised_prompt 
                    for item in response.data
                    ])
                if self.response_format == "url":
                    image_content = self.separator.join([
                        item["url"] 
                        for item in response["data"]
                        ])
                elif self.response_format == "b64_json":
                    image_content = self.separator.join([
                        item["b64_json"] 
                        for item in response["data"]
                        ])
        
            return image_revised_prompt, image_content
        except BadRequestError as e:
            raise e
        except Exception as e:
            raise e
