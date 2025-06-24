
from qdrant_client import QdrantClient, AsyncQdrantClient

from ..config import config

VEC_DB_URL = config.VEC_DB_URL
VEC_DB_API_KEY = config.VEC_DB_API_KEY

client = QdrantClient(
    # prefer_grpc=True,
    url=VEC_DB_URL,
    api_key=VEC_DB_API_KEY
    )

aclient = AsyncQdrantClient(
    # prefer_grpc=True,
    url=VEC_DB_URL,
    api_key=VEC_DB_API_KEY
    )
