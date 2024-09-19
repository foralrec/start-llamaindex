# -*- coding: utf-8 -*-
import os
import json
import oss2

from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex, Settings
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from modelscope_embedding import ModelScopeEmbedding

import logging

logger = logging.getLogger()

host = os.getenv("PG_HOST")
port = os.getenv("PG_PORT")
database = os.getenv("PG_DATABASE")
table_name = os.getenv("TABLE_NAME")
user = os.getenv("PG_USER")
password = os.getenv("PG_PASSWORD")
chunk_size = int(os.getenv("CHUNK_SIZE"), 512)
chunk_overlap = int(os.getenv("CHUNK_OVERLAP"), 64)
dimension = int(os.getenv("DIMENSION"), 768)


def initializer(context):
    model_type = os.getenv("MODEL_TYPE", "modelscope")
    embed_model = ModelScopeEmbedding()  # by default

    if model_type.lower() == "modelscope":
        embed_model = ModelScopeEmbedding()
    elif model_type.lower() == "dashscope":
        embed_model = DashScopeEmbedding(
            model_name=os.getenv("DASHSCOPE_EMBEDDING_MODEL", model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2),
            text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
        )
        global dimension
        dimension = 1536

    Settings.embed_model = embed_model
    Settings.chunk_size = chunk_size
    Settings.chunk_overlap = chunk_overlap
    logger.info("Initialized with modeltype: {}".format(model_type))


def handler(event, context):
    """
    DESCRIPTION: OSS Event Driven handler, load OSS Object of knowledge document, split to data chunk, text embedding and store to pgvector

    STEPS:
        - STEP1: Load and split data
        - STEP2: Text embedding and store to pgvector

    Args:
        - event (dict)
            e.g.
            {
                "events": [{
                    "eventName": "ObjectCreated:PutObject",
                    "eventSource": "acs:oss",
                    "eventTime": "2022-08-13T06:45:43.000Z",
                    "eventVersion": "1.0",
                    "oss": {
                        "bucket": {
                            "arn": "acs:oss:cn-hangzhou:123456789:testbucket",
                            "name": "testbucket",
                            "ownerIdentity": "164901546557****"
                        },
                        "object": {
                            "deltaSize": 122539,
                            "eTag": "688A7BF4F233DC9C88A80BF985AB****",
                            "key": "source/a.png",
                            "size": 122539
                        },
                        "ossSchemaVersion": "1.0",
                        "ruleId": "9adac8e253828f4f7c0466d941fa3db81161****"
                    },
                    "region": "cn-hangzhou",
                    "requestParameters": {
                        "sourceIPAddress": "140.205.XX.XX"
                    },
                    "responseElements": {
                        "requestId": "58F9FF2D3DF792092E12044C"
                    },
                    "userIdentity": {
                        "principalId": "164901546557****"
                    }
                }]
            }

        - context (dict): text or list text to embedding.
          Ref: https://help.aliyun.com/zh/functioncompute/context-1


    Raises:
        Exception that OSS/Dashscope/Postgresql/llamaindex returns
        Exceptions has been logged

    Returns:
        None
    """

    # STEP1: Load and split data
    logger.info("Start to load and split data")
    path = download_object(json.loads(event), context.credentials)
    if not is_valid_path(path):
        return
    documents = SimpleDirectoryReader(os.path.dirname(path)).load_data()
    logger.info("Finished loading and splitting data")

    # STEP2: Text embedding and store to pgvector
    logger.info("Start to text embedding and store to pgvector")
    vector_store = PGVectorStore.from_params(
        database=database,
        host=host,
        password=password,
        port=port,
        user=user,
        table_name=table_name,
        embed_dim=dimension,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, show_progress=True
    )
    logger.info("Finished text embedding and store to pgvector")

    return


def download_object(event: dict, creds: dict) -> str:
    info = event["events"][0]
    bucket_name = info["oss"]["bucket"]["name"]
    object_name = info["oss"]["object"]["key"]
    if object_name.endswith('/'):
        logger.info("object {} is a directory, return".format(object_name))
        return ""

    region = info["region"]
    endpoint = f"https://oss-{region}-internal.aliyuncs.com"

    auth = oss2.StsAuth(
        creds.access_key_id,
        creds.access_key_secret,
        creds.security_token)

    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    path = f"/tmp/{bucket_name}/{object_name}"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        bucket.get_object_to_file(object_name, path)
        logger.info("Successfully download object from '{}/{}' to '{}'".format(bucket_name, object_name, path))
    except Exception as e:
        logger.error("An error occured when download object '{}': '{}'".format(object_name, e))
        raise e

    return path


def is_valid_path(path: str) -> bool:
    return path != ""
