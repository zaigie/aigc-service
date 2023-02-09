import grpc
import chat_pb2
import chat_pb2_grpc
import sys
import uuid
import readline


def get_input(prompt):
    print(prompt, end="")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    user_input = "\n".join(lines)
    return user_input


def run(url):
    with grpc.insecure_channel(url) as channel:
        client = chat_pb2_grpc.ChatStub(channel)
        conversation_id = f"grpc_{uuid.uuid4().hex[:8]}"
        print("连接成功！你可以向他询问任何问题啦！")
        print(
            "=======================================\nNote: 因为支持多行输入，若确定了问题，请按两次回车键哦。\n======================================="
        )
        while True:
            try:
                prompt = get_input("\n你：\n")
            except UnicodeDecodeError:
                print(
                    "=======================================\n你刚刚的输入包含特殊字符，无法识别。\n======================================="
                )
                continue
            except KeyboardInterrupt:
                print("\n退出中...")
                sys.exit()
            print("\nChatGPT: ")
            sys.stdout.flush()
            try:
                sys.stdout.flush()
                for i in client.Ask(
                    chat_pb2.askrequest(
                        prompt=prompt,
                        conversation_id=conversation_id,
                    )
                ):
                    print(i.response, end="")
                    sys.stdout.flush()
                print()
            except Exception as e:
                # print("Error: %s" % e)
                # print("访问人数多，请重试")
                try:
                    sys.stdout.flush()
                    for i in client.Ask(
                        chat_pb2.askrequest(
                            prompt=prompt,
                            conversation_id=conversation_id,
                        )
                    ):
                        print(i.response, end="")
                        sys.stdout.flush()
                    print()
                except:
                    print("访问人数过多，请重试")
                    continue


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="gRPC URL e.g. localhost:9000",
    )
    args = parser.parse_args()
    url = args.url
    print(f"初始化: 正在连接到位于 {url} 的 ChatGPT...")
    try:
        run(url)
    except (KeyboardInterrupt, EOFError):
        sys.exit()
