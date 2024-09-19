"""
Chat completion related APIs.

Reference: https://platform.openai.com/docs/api-reference/completions
"""
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field
from llama_index.core.llms import ChatMessage, MessageRole


class ChatMessageRole(str, Enum):
    System = "system"
    User = "user"
    Assistant = "assistant"


class ChatCompletionMessage(BaseModel):
    role: ChatMessageRole
    content: str
    name: Optional[str] = Field(None, alias="name")

    def to_llamaindex_message(self) -> ChatMessage:
        return ChatMessage(
            role=MessageRole(self.role),
            content=self.content
        )


class ChatCompletionChoice(BaseModel):
    index: int
    delta: ChatCompletionMessage
    finish_reason: str = Field(..., alias="finish_reason")


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatCompletionMessage]
    max_tokens: Optional[int] = Field(None, alias="max_tokens")
    temperature: Optional[float] = Field(None, alias="temperature")
    top_p: Optional[float] = Field(None, alias="top_p")
    n: Optional[int] = Field(None, alias="n")
    stream: Optional[bool] = Field(None, alias="stream")
    stop: Optional[List[str]] = Field(None, alias="stop")
    presence_penalty: Optional[float] = Field(None, alias="presence_penalty")
    frequency_penalty: Optional[float] = Field(None, alias="frequency_penalty")
    logit_bias: Optional[Dict[str, int]] = Field(None, alias="logit_bias")
    user: Optional[str] = Field(None, alias="user")


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: Optional[str] = Field(None, alias="id")
    object: Optional[str] = Field(None, alias="object")
    created: Optional[int] = Field(None, alias="created")
    model: Optional[int] = Field(None, alias="model")
    choices: List[ChatCompletionChoice]
    # usage: Optional[Usage]
