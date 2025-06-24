from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "OperationsAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
