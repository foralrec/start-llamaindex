
> 注：当前项目为 Serverless Devs 应用，由于应用中会存在需要初始化才可运行的变量（例如应用部署地区、函数名等等），所以**不推荐**直接 Clone 本仓库到本地进行部署或直接复制 s.yaml 使用，**强烈推荐**通过 `s init ${模版名称}` 的方法或应用中心进行初始化，详情可参考[部署 & 体验](#部署--体验) 。

# start-llamaindex 帮助文档

<description>

基于 LlamaIndex 构建 RAG 应用

</description>

<codeUrl>



</codeUrl>
<preview>



</preview>


## 前期准备

使用该项目，您需要有开通以下服务并拥有对应权限：

<service>



| 服务/业务 |  权限  | 相关文档 |
| --- |  --- | --- |
| 函数计算 |  AliyunFCFullAccess | [帮助文档](https://help.aliyun.com/product/2508973.html) [计费文档](https://help.aliyun.com/document_detail/2512928.html) |
| 云数据库RDS |  AliyunRDSFullAccess | [帮助文档](undefined) [计费文档](undefined) |
| 对象存储 |  AliyunFCServerlessDevsRolePolicy | [帮助文档](https://help.aliyun.com/zh/oss) [计费文档](https://help.aliyun.com/zh/oss/product-overview/billing) |
| 日志服务 |  AliyunFCServerlessDevsRolePolicy | [帮助文档](https://help.aliyun.com/zh/sls) [计费文档](https://help.aliyun.com/zh/sls/product-overview/billing) |
| 专有网络 |  AliyunFCServerlessDevsRolePolicy | [帮助文档](https://help.aliyun.com/zh/vpc) [计费文档](https://help.aliyun.com/zh/vpc/product-overview/billing) |

</service>

<remark>



</remark>

<disclaimers>



</disclaimers>

## 部署 & 体验

<appcenter>
   
:fire: 通过 [Dipper 应用中心](https://devs.console.aliyun.com/applications/createtemplate=start-llamaindex) ，[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://devs.console.aliyun.com/applications/createtemplate=start-llamaindex) 该应用。
   
</appcenter>
<deploy>

</deploy>

## 案例介绍

<appdetail id="flushContent">

## 项目架构图
![架构图](https://img.alicdn.com/imgextra/i2/O1CN01UOBro81tp9aEbfhpn_!!6000000005950-0-tps-2936-1704.jpg)

本案例基于 [LlamaIndex](https://www.llamaindex.ai/) 与阿里云云产品一键拉起 RAG 应用，项目分为**离线知识库向量化**与**在线问答**两个部分：
- **离线知识库向量化**：离线的知识库分割、向量化、入库过程。
  - **OfflineEmbedding**: 基于 LlamaIndex 的离线数据处理过程：配置了 OSS 事件触发器，接收 OSS 事件触发请求，当 OSS Bucket 中有 Object 上传时，自动触发离线知识库 embedding 。OfflineEmbedding 负责 **Loading** 存储于 OSS 的知识库文档，对文档进行切分，并 **Indexing** 至向量数据库。
  - **Embedding**: 文本向量化模型，对切分后的文档进行向量化处理。
  - **Vectordb**：安装了 Vector 插件的 Postgresql RDS 实例。

- **在线问答**：在线的机器人聊天页面
  - **WebUI**: 托管的开源 UI 项目 [ChatGPT-Next-Web](https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web)，用于聊天的页面展示。
  - **OnlineProcessor**: 基于 LlamaIndex 的在线数据处理流程：搜索向量数据库、查询 LLM 并返回问题答案
  - **Embedding**: 文本向量化模型，对用户问题进行向量化处理。注意：在线问答的 Embedding 模型需要与离线知识库向量化使用同一个 Embedding 模型。
  - **LLM**: 大语言模型，根据检索出的知识库内容，对聊天的问题进行推理和生成。


## 项目接入点
**在线问答访问入口**：`${resources.WebUI.output.customDomain.domainName}`

**离线 OSS 上传知识库入口**：
- 进入 [OSS 控制台](https://oss.console.aliyun.com/overview)，找到您配置的 OSS bucket，进入您配置文件前缀对应的目录下上传知识库文档即可。

然后，聊天页面可以根据您的知识库进行在线作答了

> 如何在控制台上找到上传知识库的 OSS 地址？

进入名为 **OfflineEmbedding** 的 service，进入调度规则，即可以看到对应的 bucket 和文件前缀，您需要进入前缀对应的目录上传知识库文件。
例如：bucket 为 `cap-hz`，前缀为 `CAP/0917/rag/llamaindex`，则进入 `cap-hz` bucket  中的  `CAP/0917/rag/llamaindex` 目录中上传文件即可。
如果 Bucket 下原本没有目录，需要手动创建目录
![](https://img.alicdn.com/imgextra/i2/O1CN01cBl22E24Vsgn8kIVP_!!6000000007397-0-tps-2304-1006.jpg)

> 如何在控制台找到聊天页面地址？
找到 **WebUI** 这个 service，找到访问入口，在浏览器中打开即可。


## 项目介绍
RAG（Retrieval-Augmented Generation）应用是一种结合了信息检索（Retrieval）和文本生成（Generation）的人工智能技术。使其能够在生成响应之前引用训练数据来源之外的权威知识库。大型语言模型（LLM）用海量数据进行训练，使用数十亿个参数为回答问题、翻译语言和完成句子等任务生成原始输出。在 LLM 本就强大的功能基础上，RAG 将其扩展为能访问特定领域或组织的内部知识库，所有这些都无需重新训练模型。这是一种经济高效地改进 LLM 输出的方法，让它在各种情境下都能保持相关性、准确性和实用性。

本案例基于 [LlamaIndex](https://www.llamaindex.ai/) 与阿里云云产品一键拉起 RAG 应用，达到的效果是：您通过上传文本文件（.txt/.pdf 格式）到阿里云 OSS，自动触发函数计算对文件进行切分，存储到向量数据库中。当与机器人进行对话时，会自动从知识库中检索相关的信息，机器人根据上下文并在回答中引用这些信息。

</appdetail>

## 使用流程

<usedetail id="flushContent">

步骤一：上传知识库到 OSS
您可以下载 [CAP 简介](https://cap-template.oss-cn-hangzhou.aliyuncs.com/rag/cap_intro.txt
)的知识库文档，上传到您的 OSS Bucket 的指定目录下

步骤二：打开在线聊天入口，与机器人进行对话问答

步骤三：您可以持续上传您的知识库文档进行测试，如果当前模板不满足您的业务需求，您可以根据二次开发指南对模板进行二次开发。


## 二次开发指南
### 更换模型
您可以更换 Embedding 模型与 LLM 模型，您可以选择其他的模型在 CAP 上进行托管，您也可以使用模型 API Provider 提供的 API。
当前模板默认使用的 Embedding 模型是托管的 ModelScope 的 `iic/nlp_corom_sentence-embedding_chinese-base` ，
使用的 LLM 模型是托管的 Ollama `llama3:8b` 

#### 更换 Embedding 模型：
您需要根据 [LlamaIndex Embedding 文档](https://docs.llamaindex.ai/en/stable/module_guides/models/embeddings/) 更改 `OfflineEmbedding` 服务与 `OnlineProcessor` 的服务代码。
值得注意的是，不同 Embedding 模型的相似度计算方式不同，向量维度也可能不同，更换 Embedding 模型后需要新建数据库 Table，您需要在 `OfflineEmbedding` 服务与 `OnlineProcessor` 的服务的服务变量中更新 `TableName` 与 `Dimension` 字段。

#### 更换 LLM 模型：
您需要根据 [LlamaIndex LLM 文档](https://docs.llamaindex.ai/en/stable/module_guides/models/llms/) 更改  `OnlineProcessor` 的服务代码。

> 注意：更换模型后可以删除模板中的 LLM 与 Embedding 服务，或将实例数置为 0，否则会持续产生费用。

### 更改提示词
您可以在聊天过程中输入提示词。
模板在问答过程中，使用了默认的提示词，在 `OnlineProcessor` 的 `chat.py` 中，您可以对提示词进行自定义更改。


###  更换向量数据库
您需要根据 [LlamaIndex Vector Stores 文档](https://docs.llamaindex.ai/en/stable/module_guides/storing/vector_stores/) 更改  `OnlineProcessor` 与 `OfflineEmbedding` 的服务代码。

> 注意：更换数据库后可以删除模板中的 VectorDB 服务。

### 自定义开发
模板部署完成后为您的应用，您可以对目标应用进行定制化的二次开发，使其更适配您的业务。
模板中 `OnlineProcessor` 与 `OfflineEmbedding` 服务使用的依赖打包在公开的层中，依赖的版本在对应的 `requirements.txt` 内，您可以继续使用 CAP 公开层，也可以自行安装依赖。

## 常见问题
1. 聊天机器人回答的很慢怎么办？

可以尝试调大实例规格，使用 Ada 规格的实例；可以尝试将实例数量调大；可以尝试更换模型。

2. 聊天机器人总是答非所问怎么办？

更换模型，或者更改提示词

</usedetail>

## 注意事项

<matters id="flushContent">
</matters>


<devgroup>


## 开发者社区

您如果有关于错误的反馈或者未来的期待，您可以在 [Serverless Devs repo Issues](https://github.com/serverless-devs/serverless-devs/issues) 中进行反馈和交流。如果您想要加入我们的讨论组或者了解 FC 组件的最新动态，您可以通过以下渠道进行：

<p align="center">  

| <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407298906_20211028074819117230.png" width="130px" > | <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407044136_20211028074404326599.png" width="130px" > | <img src="https://images.devsapp.cn/fc-faq/33947367.png" width="130px" > |
| --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| <center>微信公众号：`serverless`</center>                                                                                         | <center>微信小助手：`xiaojiangwh`</center>                                                                                        | <center>钉钉交流群：`33947367`</center>                                                                                           |
</p>
</devgroup>
