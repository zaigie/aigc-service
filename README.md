# ChatGPT EasyBackend

## TODO

- [ ] Log printing and collection
- [ ] SSL/TLS Support
- [ ] Use sqlite3 replace json file storage

...

## Prepare

You need You need an OpenAI account and generate API keys: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)

## Deploy

| ENV            | Description            | Required | Default                        |
| -------------- | ---------------------- | -------- | ------------------------------ |
| OPENAI_API_KEY | Your OpenAI Key        | True     | -                              |
| GPT_ENGINE     | GPT Model Name         | False    | text-chat-davinci-002-20221122 |
| ENCODING_NAME  | tiktoken encoding name | False    | gpt2                           |
| FIRST_PROMPT   | Your First Prompt      | False    | Hello                          |

In general, we would use `GPT_ENGINE=text-chat-davinci-002-20221122` and `ENCODING_NAME=gpt2` as the default **(this pairing is free)**.

However, due to the popularity of ChatGPT, these collocations are often disabled to indicate a "model does not exist" error, so the following collocations can be used:

```sh
ENCODING_NAME=p50k_base
GPT_ENGINE=text-davinci-003
```

However, please note that this collocation may lead to some costs!

### Docker

```sh
docker run -d --name chatgpt-easy-backend \
-v $(pwd)/chatgpt/:/app/conversations/ \
-p 8100:8000 -p 9100:9000 -p 9001:9001 \
-e OPENAI_API_KEY=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 \
jokerwho/chatgpt-easy-backend:latest
```

## Use

### Include Services

| Port | Service          | Type      |
| ---- | ---------------- | --------- |
| 8000 | HTTP Server      | No Stream |
| 9000 | gRPC Server      | Stream    |
| 9001 | Websocket Server | Stream    |

### HTTP

HTTP server is using a FastAPI, you can visit [http://localhost:8000/docs](http://localhost:8000/docs) to SwaggerUI.

or use the curl tool to request the interface

```sh
curl -X 'POST' \
  'http://localhost:8000/ask/{conversation_id}' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "Hello"
}'
```

### gRPC

Here is a sample program [grpc_client.py](https://github.com/jokerwho/chatgpt-easy-backend/blob/main/grpc_client.py)

### Websocket

Connect to `ws://localhost:9001` then send message.
