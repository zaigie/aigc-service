import os
import time
from websocket_server import WebsocketServer

from bot import Chatbot

RETRY = 3
TEMPREATURE = 0.5
API_KEY = os.environ.get("OPENAI_API_KEY")
chatbot = Chatbot(api_key=API_KEY)


def new_client(client, server):
    print("New client connected and was given id %d" % client["id"])
    # server.send_message_to_all("Hey all, a new client has joined us")


def client_left(client, server):
    print("Client(%d) disconnected" % client["id"])


def message_received(client, server, message):
    # print("Client(%d) said: %s" % (client["id"], message))
    if not message.startswith("<|ask|>$"):
        server.send_message(client, "<|err|>$请使用“<|ask|>$会话ID$消息内容”为格式发送消息")
        return
    conversation_id = message.split("$")[1]
    if not conversation_id:
        server.send_message(client, "<|err|>$请使用“<|ask|>$会话ID$消息内容”为格式发送消息")
        return
    prompt = message.split("$")[2]
    lines = [line for line in prompt.splitlines() if line.strip()]
    user_input = "\n".join(lines)
    try:
        for response in chatbot.ask_stream(
            user_input,
            temperature=TEMPREATURE,
            conversation_id=conversation_id,
        ):
            server.send_message(client, response)
        server.send_message(client, "<|end|>")
    except Exception as e:
        count_retry = 0
        while count_retry < RETRY:
            try:
                for response in chatbot.ask_stream(
                    user_input,
                    temperature=TEMPREATURE,
                    conversation_id=conversation_id,
                ):
                    server.send_message(client, response)
                server.send_message(client, "<|end|>")
                return
            except Exception as e:
                count_retry += 1
        server.send_message(client, "<|err|>")


server = WebsocketServer(host="0.0.0.0", port=9001)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
