import os
from fastapi import FastAPI
from pydantic import BaseModel

from bot import Chatbot

app = FastAPI()

TEMPREATURE = 0.5
API_KEY = os.environ.get("OPENAI_API_KEY")
chatbot = Chatbot(api_key=API_KEY)


@app.get("/")
def index():
    return {"message": "Hello World"}


class Ask(BaseModel):
    prompt: str


@app.post("/ask/{conversation_id}")
def chat(conversation_id: str, ask: Ask):
    lines = [line for line in ask.prompt.splitlines() if line.strip()]
    user_input = "\n".join(lines)
    response = chatbot.ask(
        user_input, conversation_id=conversation_id, temperature=TEMPREATURE
    )
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "http_server:app", host="0.0.0.0", port=8000, reload=False, env_file=".env"
    )
