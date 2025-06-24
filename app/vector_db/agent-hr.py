from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "HRAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
