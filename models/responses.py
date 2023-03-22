from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

from ._openai import *


class OpenAICompletionResponse(BaseModel):
    id: str
    answer: str
    usage: int


class OpenAIChatResponse(BaseModel):
    id: str
    message: OpenAIChatMessage
    usage: int
