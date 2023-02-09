from concurrent import futures
import os
import grpc
import chat_pb2
import chat_pb2_grpc

from bot import Chatbot

TEMPREATURE = 0.5

API_KEY = os.environ.get("OPENAI_API_KEY")
chatbot = Chatbot(api_key=API_KEY)


class Chat(chat_pb2_grpc.ChatServicer):
    def Ask(self, request, context):
        prompt = request.prompt
        conversation_id = request.conversation_id
        lines = [line for line in prompt.splitlines() if line.strip()]
        user_input = "\n".join(lines)
        try:
            for response in chatbot.ask_stream(
                user_input, temperature=TEMPREATURE, conversation_id=conversation_id
            ):
                yield chat_pb2.askresponse(response=response)
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
