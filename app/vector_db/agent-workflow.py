from .utils import KnowledgeBaseManager

from ..config import config

BOT_NAME = "WorkflowAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)
