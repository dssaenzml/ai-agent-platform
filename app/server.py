import logging
import os

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from .api.api import router as api_router
from .config import config
from .helpers.security import get_api_key
from .helpers.utils import RequestLoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("server.log"),  # Log to file
    ],
)

# Set logging levels for external libraries to WARNING or ERROR
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("pikepdf").setLevel(logging.WARNING)
logging.getLogger("snowflake.connector").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("unstructured").setLevel(logging.WARNING)
logging.getLogger("unstructured_inference").setLevel(logging.WARNING)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("timm").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("langchain_core").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.API_VERSION,
    description=config.API_DESC,
    root_path=os.getenv("ROOT_PATH", ""),
)

# Add the middleware
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
origins = [
    "http://localhost",
    "https://localhost",
    "http://fleetmateqa.sys.maqta.ae",
    "https://fleetmateqa.sys.maqta.ae",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
    # Additional shutdown logic here


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.get("/", include_in_schema=False)
async def redirect_root_to_docs(request: Request):
    logger.info("Redirecting to docs...")
    return RedirectResponse(request.url_for("docs"))


@app.get("/redoc", include_in_schema=False)
async def redoc(request: Request):
    logger.info("Serving ReDoc documentation...")
    return get_redoc_html(
        openapi_url=request.url_for("openapi"),
        title=app.title,
    )


@app.get("/docs", include_in_schema=False)
async def docs(request: Request):
    logger.info("Serving Swagger UI documentation...")
    return get_swagger_ui_html(
        openapi_url=request.url_for("openapi"),
        title=app.title,
    )


@app.get("/openapi.json", include_in_schema=False)
async def openapi():
    logger.info("Serving OpenAPI schema...")
    return get_openapi(title=app.title, version=app.version, routes=app.routes)


@app.get("/health", tags=["API Health Probe"])
async def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "OK"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


# Include the API router in the main application
app.include_router(
    api_router,
    prefix=config.API_PREFIX_STR,
    dependencies=[Depends(get_api_key)],  # Apply the logging dependency to the router
)
logger.info(f"Included API router with prefix: {config.API_PREFIX_STR}")
