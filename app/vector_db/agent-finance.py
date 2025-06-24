
from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "FinanceAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
