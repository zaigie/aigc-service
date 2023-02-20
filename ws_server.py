import os
import time
from websocket_server import WebsocketServer

from revChatGPT.V1 import Chatbot

RETRY = 3
CHATGPT_TOKEN = os.environ.get("CHATGPT_TOKEN", None)
PROXY = os.environ.get("PROXY", None)
chatbot = Chatbot(
    config={
        "proxy": PROXY,
        "access_token": CHATGPT_TOKEN,
    }
)


def new_client(client, server):
    print("New client connected and was given id %d" % client["id"])
    # server.send_message_to_all("Hey all, a new client has joined us")


def client_left(client, server):
    print("Client(%d) disconnected" % client["id"])


def message_received(client, server, message):
    # print("Client(%d) said: %s" % (client["id"], message))
    if not message.startswith("<|ask|>$"):
        server.send_message(client, "<|err|>$请使用“<|ask|>$会话ID$上条消息ID$消息内容”为格式发送消息")
        return
    conversation_id = message.split("$")[1]
    if not conversation_id:
        server.send_message(client, "<|err|>$请使用“<|ask|>$会话ID$上条消息ID$消息内容”为格式发送消息")
        return
    if conversation_id == "new":
        conversation_id = None
    parent_id = message.split("$")[2]
    if parent_id == "new":
        parent_id = None
    prompt = message.split("$")[3]
    lines = [line for line in prompt.splitlines() if line.strip()]
    user_input = "\n".join(lines)
    prev_text = ""
    response = {}
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
            server.send_message(client, message)
        server.send_message(
            client, f"<|end|>${response['conversation_id']}${response['parent_id']}"
        )
    except Exception as e:
        count_retry = 0
        while count_retry < RETRY:
            try:
                for data in chatbot.ask(
                    user_input,
                    conversation_id=conversation_id,
                    timeout=40,
                ):
                    message = data["message"][len(prev_text) :]
                    prev_text = data["message"]
                    server.send_message(client, message)
                server.send_message(
                    client,
                    f"<|end|>${response['conversation_id']}${response['parent_id']}",
                )
                return
            except Exception as e:
                count_retry += 1
        server.send_message(client, "<|err|>")


server = WebsocketServer(host="0.0.0.0", port=9001)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
