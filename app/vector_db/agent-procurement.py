from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "ProcurementAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
