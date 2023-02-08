# ChatGPT EasyBackend

## How to use?

| ENV            | Description            | Required | Default                        |
| -------------- | ---------------------- | -------- | ------------------------------ |
| OPENAI_API_KEY | Your OpenAI Key        | True     | -                              |
| GPT_ENGINE     | GPT Model Name         | False    | text-chat-davinci-002-20221122 |
| ENCODING_NAME  | tiktoken encoding name | False    | gpt2                           |
| FIRST_PROMPT   | Your First Prompt      | False    | Hello                          |

In general, we would use GPT_ENGINE as text-chat-davinci-002-20221122 and ENCODING_NAME as gpt2 as the default (this pairing is free).
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

## Include Services

| Port | Service             | Type      |
| ---- | ------------------- | --------- |
| 8000 | FastAPI HTTP Server | No Stream |
| 9000 | gRPC Server         | Stream    |
| 9001 | Websocket Server    | Stream    |
