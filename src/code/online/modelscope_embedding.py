import requests
import os
from typing import Any, List
from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding


class ModelScopeEmbedding(BaseEmbedding):

    def __init__(
            self,
            **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

    def embed(self, input):
        url = os.getenv("MODELSCOPE_EMBEDDING_ENDPOINT")
        data = {
            "input": input
        }
        response = requests.post(url, json=data)
        return response.json()["Data"]

    def _get_query_embedding(self, query: str) -> List[float]:
        text = query.replace("\n", " ")
        inputs = {"source_sentence": [text]}
        return self.embed(input=inputs)['text_embedding'][0]

    def _get_text_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        inputs = {"source_sentence": [text]}
        return self.embed(input=inputs)['text_embedding'][0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        inputs = {"source_sentence": texts}
        return self.embed(input=inputs)['text_embedding']

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)
