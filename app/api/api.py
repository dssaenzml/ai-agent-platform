import logging
from fastapi import APIRouter

from .endpoints.agent_general import router as agent_general
from .endpoints.agent_engineering import router as agent_engineering
from .endpoints.agent_realestate import router as agent_realestate
from .endpoints.agent_finance import router as agent_finance
from .endpoints.agent_hr import router as agent_hr
from .endpoints.agent_operations import router as agent_operations
from .endpoints.agent_analytics import router as agent_analytics
from .endpoints.agent_workflow import router as agent_workflow
from .endpoints.agent_procurement import router as agent_procurement
from .endpoints.agent_automation import router as agent_automation

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
router.include_router(agent_general)

logger.info("Including agent-engineering")
router.include_router(agent_engineering)

logger.info("Including agent-realestate")
router.include_router(agent_realestate)

logger.info("Including agent-finance")
router.include_router(agent_finance)

logger.info("Including agent-hr")
router.include_router(agent_hr)

logger.info("Including agent-operations")
router.include_router(agent_operations)

logger.info("Including agent-analytics")
router.include_router(agent_analytics)

logger.info("Including agent-workflow")
router.include_router(agent_workflow)

logger.info("Including agent-procurement")
router.include_router(agent_procurement)

logger.info("Including agent-automation")
router.include_router(agent_automation)
