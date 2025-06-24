from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "AnalyticsAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
