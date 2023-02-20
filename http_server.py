import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from revChatGPT.V1 import Chatbot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
    allow_origins=["*"],
    # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
    allow_credentials=False,
    # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
    allow_methods=["*"],
    # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
    # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
    allow_headers=["*"],
    # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
    # expose_headers=["*"]
    # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
    # max_age=1000
)

CHATGPT_TOKEN = os.environ.get("CHATGPT_TOKEN", None)
PROXY = os.environ.get("PROXY", None)
chatbot = Chatbot(
    config={
        "proxy": PROXY,
        "access_token": CHATGPT_TOKEN,
    }
)


class Ask(BaseModel):
    prompt: str
    parent_id: str = None


@app.post("/ask/{conversation_id}")
def chat(conversation_id: str, ask: Ask):
    lines = [line for line in ask.prompt.splitlines() if line.strip()]
    user_input = "\n".join(lines)
    prev_text = ""
    response = {}
    parent_id = ask.parent_id
    if conversation_id == "new":
        conversation_id = None
        parent_id = None
    try:
        for data in chatbot.ask(
            user_input,
            conversation_id=conversation_id,
            parent_id=parent_id,
            timeout=40,
        ):
            message = data["message"][len(prev_text) :]
            prev_text = data["message"]
            response = data
        return response
    except Exception as e:
        return {"response": "访问人数过多，请重试。", "detail": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "http_server:app", host="0.0.0.0", port=8000, reload=False, env_file=".env"
    )
