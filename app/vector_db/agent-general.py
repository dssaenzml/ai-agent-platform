from ..config import config
from .utils import KnowledgeBaseManager

BOT_NAME = "GeneralAgent"

kbm = KnowledgeBaseManager(BOT_NAME, config)

BOT_NAME = "GeneralAgent-Avatar"

avatar_kbm = KnowledgeBaseManager(BOT_NAME, config)
