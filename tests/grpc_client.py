import grpc
import sys

sys.path.append("..")
from proto import aigc_pb2
from proto import aigc_pb2_grpc


def run_completion_stub(stub):
    request = aigc_pb2.OpenAICreateCompletionRequest(
        prompt="请告诉我一个急救知识", max_tokens=50, temperature=1, top_p=0.9
    )
    response = stub.Completion(request)
    print("Completion Response:\n", response)


def run_chat_stub(stub):
    messages = [
        aigc_pb2.RequestMessage(role="system", content="你是一个测试员"),
        aigc_pb2.RequestMessage(role="user", content="如果正常，请回复啊啊啊成功了"),
    ]
    request = aigc_pb2.OpenAICreateChatRequest(
        messages=messages, max_tokens=50, temperature=0.8, top_p=0.9
    )
    response = stub.Chat(request)
    print("Chat Response:\n", response)


def run_stream_completion_stub(stub):
    request = aigc_pb2.OpenAICreateCompletionRequest(
        prompt="请告诉我一个急救知识", max_tokens=50, temperature=0.8, top_p=0.9
    )
    responses = stub.StreamCompletion(request)
    for response in responses:
        print("Stream Completion Response:\n", response)


def run_stream_chat_stub(stub):
    messages = [
        aigc_pb2.RequestMessage(role="system", content="你是一个测试员"),
        aigc_pb2.RequestMessage(role="user", content="如果正常，请回复啊啊啊成功了"),
    ]
    request = aigc_pb2.OpenAICreateChatRequest(
        messages=messages, max_tokens=50, temperature=0.8, top_p=0.9
    )
    responses = stub.StreamChat(request)
    for response in responses:
        print("Stream Chat Response:\n", response)


def run():
    with grpc.insecure_channel("localhost:9000") as channel:
        stub = aigc_pb2_grpc.OpenAIStub(channel)
        # # Call Completion API
        # run_completion_stub(stub)

        # # Call Chat API
        # run_chat_stub(stub)

        # # Call StreamCompletion API
        # run_stream_completion_stub(stub)

        # Call StreamChat API
        run_stream_chat_stub(stub)


if __name__ == "__main__":
    run()
