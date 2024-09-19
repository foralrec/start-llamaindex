## 基本介绍
任务基于 LlamaIndex 进行离线数据处理。配置了 OSS 事件触发器，接收 OSS 事件触发请求，当 OSS Bucket 中有 Object 上传时，自动触发任务执行。任务执行过程中，将 OSS 文件 load 到本地，使用 LlamaIndex 框架对知识库进行切分、向量化，并写入向量数据库。

## 开发指南
### 更换模型
示例代码中默认使用的是托管的 ModelScope Embedding 模型，也适配了  [Dashscope API](https://dashscope.console.aliyun.com/model) ，您可以通过配置或代码替换 Embedding 模型：

**示例 1：更改使用 DashScope 的 Embedding 模型。**
```python
# 为函数设置环境变量
MODEL_TYPE: "Dashscope"
DASHSCOPE_API_KEY: "sk-c123456789"
DIMENSION: "1536"
TABLE_NAME: "llamaindex-dashscope"

# DASHSCOPE_API_KEY 获取方式见 DashScope API Key 管理：https://dashscope.console.aliyun.com/apiKey
```

**示例 2：更改为其他模型。** 可参考 [LlamaIndex Embedding 文档](https://docs.llamaindex.ai/en/stable/module_guides/models/embeddings/#list-of-supported-embeddings)

 需要注意的是，不同 Embedding 模型的相似度计算方式不同，向量维度可能不同，因此更换 Embedding 模型后需要新建数据库 Table。

### 更换数据库
参考 [LlamaIndex Vector Stores 文档](https://docs.llamaindex.ai/en/stable/module_guides/storing/vector_stores/#example-notebooks) 更新代码。

### 可配置的环境变量
在本项目中，您可以通过设置以下环境变量来配置数据库连接和数据处理的相关参数。

- PG_HOST
  - 描述：数据库实例连接地址。
  - 示例：`pgm-bp1sj22kx6p40vab.pg.rds.aliyuncs.com`
- PG_PORT
  - 描述：PostgreSQL 数据库服务器的端口号。
  - 默认值：5432
  - 示例：`5432` （PostgreSQL 的默认端口）
- PG_DATABASE
  - 描述：PostgreSQL 数据库的名称。
  - 示例：`llamaindex_rag_database`
- TABLE_NAME
  - 描述：数据库表名称。
  - 示例：`llamaindex_default`
- PG_USER
  - 描述：连接数据库的用户名。
  - 示例：`cap"`
- PG_PASSWORD
  - 描述：连接数据库的密码。
  - 示例：`cap`
- CHUNK_SIZE
  - 描述：在处理数据时每个数据块的大小
  - 类型：整数
  - 默认值：512
  - 示例：512
- CHUNK_OVERLAP
  - 描述：指定数据块之间的重叠记录数。重叠可以用于确保数据的连续性和一致性。
  - 类型：整数
  - 默认值：64
  - 示例：64
- DIMENSION
  - 描述：数据向量化的维度
  - 类型：整数
  - 默认值：768
  - 示例：768（根据 Embedding 模型的维度设置）


## 依赖库
依赖库在 `requirements.txt` 中，您可以根据需要安装依赖库。