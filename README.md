# AIGC Service

简单的 AIGC 微服务，可通过 HTTP、gRPC 连接，支持流式回答。

目前支持 OpenAI ，后续将接入更多 AIGC 接口（文心一言、Bard 等）

## TODO

- [ ] 日志打印和收集
- [ ] 统一消息返回格式

...

## 准备

### OpenAI

1. 创建一个 OpenAI 的 [ChatGPT](https://chat.openai.com/) 账号
2. 获取 OpenAI Key : [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

> 目前国内区域的账号无法使用，请在注册申请时全程保证科学上网，具体注册教程网上有很多

## 部署

> 虽然可以通过代理，但仍然建议在能够直接访问 openai api 的服务器上部署

| 环境变量       | 描述                | 必须  | 默认值 |
| -------------- | ------------------- | ----- | ------ |
| OPENAI_API_KEY | 你的 OPENAI_API_KEY | True  | -      |
| HTTP_PROXY     | http 代理           | False | -      |
| HTTPS_PROXY    | https 代理          | False | -      |
| ALL_PROXY      | socks 代理          | False | -      |

### Docker 一键部署

```sh
docker run -d --name aigc-service \
-p 8000:8000 -p 9000:9000 \
-e OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxx \
jokerwho/aigc-service:latest
```

## 使用

### 包含服务

| 端口 | 服务        | 类型            |
| ---- | ----------- | --------------- |
| 8000 | HTTP Server | 非流式回答      |
| 9000 | gRPC Server | 非流式/流式回答 |

### 参数

#### Completion 模式

> 该模式调用 text-davinci-003 模型

| 参数        | 说明                  | 必须  |
| ----------- | --------------------- | ----- |
| prompt      | 提示内容              | True  |
| max_tokens  | 返回的最长长度        | False |
| temperature | 温度（0-1）           | False |
| top_p       | 多样性（0-1）         | False |
| ...         | openai 支持的其它参数 | False |

#### Chat 模式

> 该模式调用 gpt-3.5-turbo-0301 模型

| 参数        | 说明                  | 必须  |
| ----------- | --------------------- | ----- |
| messages    | 消息列表              | True  |
| max_tokens  | 返回的最长长度        | False |
| temperature | 温度（0-1）           | False |
| top_p       | 多样性（0-1）         | False |
| ...         | openai 支持的其它参数 | False |

### HTTP

HTTP 服务使用 FastAPI 实现, 你只需要访问 [http://localhost:8000/docs](http://localhost:8000/docs) 到 SwaggerUI 就知道怎么使用。

### gRPC

proto 文件存放于: [aigc.proto](https://github.com/jokerwho/aigc-service/blob/main/proto/aigc.proto)
这里有一个 grpc_client 客户端示例： [grpc_client.py](https://github.com/jokerwho/aigc-service/blob/main/tests/grpc_client.py)
