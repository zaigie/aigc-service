# ChatGPT EasyBackend

简单基于 [revChatGPT](https://github.com/acheong08/ChatGPT) 的 ChatGPT 后端，可通过 HTTP、gRPC、Websocket 连接，支持流式回答和上下文对话管理。

## TODO

- [ ] 日志打印和收集
- [ ] SSL/TLS 支持
- [ ] 使用 sqlite3 代替 JSON 文件存储

...

## 准备

1. 创建一个 OpenAI 的 [ChatGPT](https://chat.openai.com/) 账号
2. 获取 AccessToken : [https://chat.openai.com/api/auth/session](https://chat.openai.com/api/auth/session)
3. 复制其中的 "accessToken" 内容

> 目前国内区域的账号无法使用，请在注册申请时全程保证科学上网，具体注册教程网上有很多

## 部署

| 环境变量 | 描述                     | 必须  | 默认值 |
| -------- | ------------------------ | ----- | ------ |
| API_KEY  | 你的 ChatGPT accessToken | True  | -      |
| PROXY    | http(s) 代理             | False | -      |

### Docker 部署

```sh
docker run -d --name chatgpt-easy-backend \
-v $(pwd)/chatgpt/:/app/conversations/ \
-p 8100:8000 -p 9100:9000 -p 9001:9001 \
-e API_KEY=eyxxxxxxxxxxx.xxxxxxx \
jokerwho/chatgpt-easy-backend:latest
```

## 使用

### 包含服务

| 端口 | 服务             | 类型       |
| ---- | ---------------- | ---------- |
| 8000 | HTTP Server      | 非流式回答 |
| 9000 | gRPC Server      | 流式回答   |
| 9001 | Websocket Server | 流式回答   |

### 参数

| 参数            | 说明        |
| --------------- | ----------- |
| prompt          | 对话内容    |
| conversation_id | 对话 ID     |
| parent_id       | 上条消息 ID |

### HTTP

HTTP 服务使用 FastAPI 实现, 你只需要访问 [http://localhost:8000/docs](http://localhost:8000/docs) 到 SwaggerUI 就知道怎么使用。

或者你也可以使用 curl 工具等在终端发送请求：

```sh
curl -X 'POST' \
  'http://localhost:8000/ask/new' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "你好",
  “parent_id": null
}'
```

> 当 conversation_id 为 new 时,表示开启一段新对话

### gRPC

这里有一个 grpc_client 客户端示例： [grpc_client.py](https://github.com/jokerwho/chatgpt-easy-backend/blob/main/grpc_client.py)

运行 `python3 grpc_client.py --url {grpc_url}` ,会自动创建会话并在每个回复的最后一次以 `<|end|>${conversation_id}${parent_id}` 格式返回

如果你想回到之前的某个对话, 请加上 `--conversation_id xxx --parent_id xxx`

### Websocket

1.  连接到 `ws://localhost:9001`
2.  按照约定格式发送消息:

    - 如果要开始新会话: 发送 `<|ask|>$new$new$早上好`,会自动创建会话并在每个回复的最后一次以 `<|end|>${conversation_id}${parent_id}` 格式返回
    - 如要回到之前的某个对话:例如 `conversation_id = 111222333 parent_id = 444` ，则发送 `<|ask|>$111222333$444$早上好`，即可收到回答

3.  接收到 `<|end|>` 消息则表示该条对话回复完毕，可进行下一次提问
