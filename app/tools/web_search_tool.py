from langchain_community.tools.bing_search import BingSearchResults
from langchain_community.utilities import BingSearchAPIWrapper

from ..config import config

web_search = BingSearchAPIWrapper(
    bing_subscription_key=config.BING_SUBSCRIPTION_KEY,
    bing_search_url=config.BING_SEARCH_URL,
    k=config.web_search_num_results,
    search_kwargs={
        "count": config.web_search_num_results,  # Number of results to return
        "offset": 0,  # Offset for pagination
        # 'freshness': 'Month'  # Freshness of the results
        "textDecorations": True,  # Enable text decorations
        "textFormat": "HTML",  # Format of the text in the search results
    },
)

web_search_tool = BingSearchResults(api_wrapper=web_search)
