from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class OpenAIChatCharacter(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class OpenAIChatMessage(BaseModel):
    role: OpenAIChatCharacter
    content: str
