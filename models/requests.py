from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

from ._openai import *


class OpenAICreateCompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 1.0


class OpenAICreateChatRequest(BaseModel):
    messages: List[OpenAIChatMessage]
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 1.0
