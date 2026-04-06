import os
from functools import lru_cache

from langchain_deepseek import ChatDeepSeek


@lru_cache(maxsize=1)
def get_deepseek():
    return ChatDeepSeek(
        model="deepseek-chat",
        temperature=0.0,
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
    )