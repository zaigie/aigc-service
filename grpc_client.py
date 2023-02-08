import grpc
import chat_pb2
import chat_pb2_grpc
import sys


def run():
    with grpc.insecure_channel("localhost:10086") as channel:
        client = chat_pb2_grpc.ChatStub(channel)
        sys.stdout.flush()
        try:
            for i in client.Ask(
                chat_pb2.askrequest(
                    prompt="胰十二指肠手术的术后护理",
                    conversation_id="medical1",
                )
            ):
                print(i.response, end="")
                sys.stdout.flush()
        except Exception as e:
            print("Error: %s" % e)
            print("出了点问题，请查验并重试")


if __name__ == "__main__":
    run()
