import logging
import importlib
from fastapi import APIRouter

# Import modules with hyphens using importlib
agent_general = importlib.import_module("app.api.endpoints.agent-general")
agent_engineering = importlib.import_module("app.api.endpoints.agent-engineering")
agent_realestate = importlib.import_module("app.api.endpoints.agent-realestate")
agent_finance = importlib.import_module("app.api.endpoints.agent-finance")
agent_hr = importlib.import_module("app.api.endpoints.agent-hr")
agent_operations = importlib.import_module("app.api.endpoints.agent-operations")
agent_analytics = importlib.import_module("app.api.endpoints.agent-analytics")
agent_workflow = importlib.import_module("app.api.endpoints.agent-workflow")
agent_procurement = importlib.import_module("app.api.endpoints.agent-procurement")
agent_automation = importlib.import_module("app.api.endpoints.agent-automation")

# Handlers
from .handlers.health import router as health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('server.log')  # Log to file
    ]
)

logger = logging.getLogger(__name__)

# All routes including by the API will have a /api/v1 prefix
router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)

# Include health endpoint at the API level
router.include_router(health)

# Include all agents
logger.info("Including agent-general")
router.include_router(agent_general.router)

logger.info("Including agent-engineering")
router.include_router(agent_engineering.router)

logger.info("Including agent-realestate")
router.include_router(agent_realestate.router)

logger.info("Including agent-finance")
router.include_router(agent_finance.router)

logger.info("Including agent-hr")
router.include_router(agent_hr.router)

logger.info("Including agent-operations")
router.include_router(agent_operations.router)

logger.info("Including agent-analytics")
router.include_router(agent_analytics.router)

logger.info("Including agent-workflow")
router.include_router(agent_workflow.router)

logger.info("Including agent-procurement")
router.include_router(agent_procurement.router)

logger.info("Including agent-automation")
router.include_router(agent_automation.router)
