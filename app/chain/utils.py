import base64
import io
import logging
from datetime import datetime
from typing import Tuple
from zoneinfo import ZoneInfo

from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobClient
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from pydantic import SecretStr

from ..config import config
from ..tools.agent_general.ms_graph_tool import tool as user_profile_tool

logger = logging.getLogger(__name__)

# get timezone for standard timestamps
tzinfo = ZoneInfo("Asia/Dubai")


# Define the function to format the username
def format_username(func_args: Tuple[str]) -> str:
    username, oauth_token = func_args
    try:
        if oauth_token:
            ms_graph_result = user_profile_tool.invoke(
                {
                    "oauth_token": SecretStr(oauth_token),
                }
            )
            if ms_graph_result["status"] == "success":
                user_profile_details = ms_graph_result["user_profile_details"]
                return user_profile_details["displayName"]

        username_part, domain_part = username.split("@")
        if "." in username_part:
            # Handle the case with firstName.lastName@company.com format
            first_name, last_name = username_part.split(".")[:2]
        elif "noatumlogistics" in domain_part:
            # Handle the case with firstNameL@noatumlogistics.ae format
            first_name, last_name = username_part[:-1], username_part[-1]
        elif "noatum" in domain_part:
            # Handle the case with FlastName@noatum.com /
            # FlastName@noatummaritime.com format
            first_name, last_name = username_part[0], username_part[1:]
        else:
            # Handle the case with firstNameL@company.com format
            first_name, last_name = username_part[:-1], username_part[-1]

        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        return full_name
    except Exception as error_message:
        # Log the error and raise an exception
        logger.error(error_message)
        raise HTTPException(
            status_code=400,
            detail=f"Username ID `{username}` caused an error.\n\n" f"{error_message}",
        )


def get_current_timestamp(chain_input):
    return datetime.now(tzinfo).strftime("%I:%M %p on %dth of %B, %Y")


def get_image_type_data(uploaded_image_blob_URL):
    # Create the ClientSecretCredential object
    credential = ClientSecretCredential(
        config.AZ_TENANT_ID,
        config.AZ_CLIENT_ID,
        config.AZ_SECRET_ID,
    )
    image_data = []
    image_type = []
    for blob_url in uploaded_image_blob_URL:
        try:
            blob_client = BlobClient.from_blob_url(
                blob_url=blob_url,
                credential=credential,
            )
            if blob_client.exists():
                # Download the blob content as bytes
                download_stream = blob_client.download_blob()
                blob_bytes = download_stream.readall()

                # Convert the blob bytes to a base64 encoded string
                base64_image = base64.b64encode(blob_bytes).decode("utf-8")

                # Create an image object using PIL
                image = Image.open(io.BytesIO(blob_bytes))

                image_type.append(image.format.lower())
                image_data.append(base64_image)
            else:
                raise Exception("Azure Blob URL does not exist.")
        except UnidentifiedImageError as e:
            logger.error(f"Provided file is not an image: {e}")
            continue
        except Exception as e:
            logger.error(f"Unable to get image file extension: {e}")
            continue

    return (image_type, image_data)


def itemgetter_with_default(key, default=None):
    def getter(obj):
        return obj.get(key, default)

    return getter
