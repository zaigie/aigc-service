import os
import uuid
from websocket_server import WebsocketServer

from bot import Chatbot

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
    lines = [line for line in message.splitlines() if line.strip()]
    user_input = "\n".join(lines)
    for response in chatbot.ask_stream(
        user_input,
        temperature=TEMPREATURE,
        conversation_id=f"ws_{uuid.uuid4().hex[:8]}",
    ):
        server.send_message(client, response)


server = WebsocketServer(host="0.0.0.0", port=9001)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
