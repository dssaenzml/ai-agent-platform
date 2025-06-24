import os

from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader, APIKeyQuery

API_KEYS = []

if os.getenv("API_KEY_1"):
    API_KEYS.append(str(os.getenv("API_KEY_1")))
if os.getenv("API_KEY_2"):
    API_KEYS.append(str(os.getenv("API_KEY_2")))

API_KEYS = set(API_KEYS)

api_key_query = APIKeyQuery(name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
) -> str:
    """Retrieve and validate an API key from the query parameters or HTTP header.

    Args:
        api_key_query: The API key passed as a query parameter.
        api_key_header: The API key passed in the HTTP header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If the API key is invalid or missing.
    """
    if api_key_query in API_KEYS:
        return api_key_query
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
