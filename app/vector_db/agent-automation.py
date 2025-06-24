
from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "AutomationAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
