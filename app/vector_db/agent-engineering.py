from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "EngineeringAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
