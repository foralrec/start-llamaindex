# -*- coding: utf-8 -*-
import uvicorn
from schema import *
from chat import *

from fastapi.responses import StreamingResponse
from fastapi import FastAPI

app = FastAPI()


@app.post("/initialize")
def init():
    initializer()


# Return success to options
@app.options("/v1/chat/completions")
async def root():
    return {"message": "success"}


@app.post("/v1/chat/completions")
def chat_completion(
        req: ChatCompletionRequest,
):
    # TODO temprature 从这里获取
    messages = req.messages
    data = chat(req.messages[-1].content, [message.to_llamaindex_message() for message in messages])
    sse_stream = to_stream(data)

    return StreamingResponse(sse_stream, media_type="text/event-stream")


def to_stream(data: str) -> str:
    """
    DESCRIPTION: convert data to sse stream

    Args:
        - data (string)
          e.g.: "hello world"

    Returns:
        - sse_str (string)
          e.g.: "data: hello\n\ndata: world\n\ndata: [DONE]\n\n"
    """
    sse_str = "\n"
    stream_chunk_size = 2
    i = 0
    while i < len(data):
        end_index = min(i + stream_chunk_size, len(data) - 1)
        chunk = data[i: end_index]
        i = i + stream_chunk_size
        json_data = to_openai_response(chunk).json()
        sse_str += f"data: {json_data}\n\n"
    sse_str += f"data: {'[DONE]'}\n\n"
    return sse_str


def to_openai_response(message: str) -> ChatCompletionResponse:
    """
    DESCRIPTION: convert message to openai-like response
    """

    return ChatCompletionResponse(
        choices=[
            ChatCompletionChoice(
                finish_reason="",
                index=0,
                delta=ChatCompletionMessage(
                    content=message,
                    role=ChatMessageRole.Assistant,
                )
            )
        ]
    )


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
