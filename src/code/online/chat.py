import os

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.vector_stores.postgres import PGVectorStore
from modelscope_embedding import ModelScopeEmbedding
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)

# database config
host = os.getenv("PG_HOST")
port = os.getenv("PG_PORT", "5432")
database = os.getenv("PG_DATABASE")
table_name = os.getenv("TABLE_NAME")
user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")

# model config
model_type = os.getenv("MODEL_TYPE")
ollama_url = os.getenv("OLLAMA_LLM_ENDPOINT")

dashscope_embedding_model = os.getenv("DASHSCOPE_EMBEDDING_MODEL", DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2)
dashscope_llm_model = os.getenv("DASHSCOPE_LLM_MODEL", DashScopeGenerationModels.QWEN_MAX)


def initializer():
    """
    Description: Init llamaindex settings with model config and init chat engine with vectordb config.
    """
    embed_model = ModelScopeEmbedding()  # by default
    llm_model = Ollama(model="llama3:8b", base_url=ollama_url)
    dimension = 768

    if model_type.lower() == "dashscope":
        embed_model = DashScopeEmbedding(
            model_name=dashscope_embedding_model,
            text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
        )
        llm_model = DashScope(model_name=dashscope_llm_model)
        dimension = 1536

    Settings.embed_model = embed_model
    Settings.llm = llm_model

    vector_store = PGVectorStore.from_params(
        database=database,
        host=host,
        password=password,
        port=port,
        user=user,
        table_name=table_name,
        embed_dim=dimension,
    )

    # load index
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    global chat_engine
    chat_engine = index.as_chat_engine(storage_context=storage_context,
                                       chat_mode="condense_plus_context",
                                       context_prompt=(
                                           "你是一个聊天机器人，需要和提问者进行正常互动"
                                           "这里是和提问相关的上下文\n"
                                           "{context_str}"
                                           "\n说明：根据以上信息与 chat history，对用户问题提供详细解答。你需要用简体中文回答问题。"
                                       ),
                                       )
    print("Initialized with modeltype: {}, database: {} and table_name: {}".format(model_type, database, table_name))


def chat(message: str, chat_history: list[ChatMessage]) -> str:
    print("Received messages: {}\n", message)

    """
    Description: Query the vector database && search for llm based on user query messages and chat history

    Args:
        - message (str)
          e.g.: "CAP 是什么"
        - chat_history (list[ChatMessage])

    Returns:
        - str
          e.g.: "CAP（Cloud Application Platform）是云原生应用开发平台，全称为 Cloud Application Platform，简称 CAP。CAP立足于 Serverless && AI，通过丰富的模板、流程式编排、组装式研发让应用开发更简单。Serverless 形态的云资源既保障了业务弹性可扩展，又降低企业上云成本"
    """
    response = chat_engine.chat(message, chat_history=chat_history)

    print("Got response: {}\n", response.response)
    return response.response
