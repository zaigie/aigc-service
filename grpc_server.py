from concurrent import futures
import os
import grpc
import chat_pb2
import chat_pb2_grpc

from revChatGPT.V1 import Chatbot

CHATGPT_TOKEN = os.environ.get("CHATGPT_TOKEN", None)
PROXY = os.environ.get("PROXY", None)
chatbot = Chatbot(
    config={
        "proxy": PROXY,
        "access_token": CHATGPT_TOKEN,
    }
)


class Chat(chat_pb2_grpc.ChatServicer):
    def Ask(self, request, context):
        prompt = request.prompt
        conversation_id = request.conversation_id
        parent_id = request.parent_id
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
                yield chat_pb2.askresponse(response=message)
            yield chat_pb2.askresponse(
                response=f"<|end|>${response['conversation_id']}${response['parent_id']}"
            )
            # print(context.is_active())
        except Exception as e:
            yield chat_pb2.askresponse(response="<|err|>")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port("[::]:9000")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
