import grpc
import chat_pb2
import chat_pb2_grpc
import sys
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


def run(url, conversation_id=None, parent_id=None):
    with grpc.insecure_channel(url) as channel:
        client = chat_pb2_grpc.ChatStub(channel)
        # conversation_id = f"grpc_{uuid.uuid4().hex[:8]}"
        print("连接成功！你可以向他询问任何问题啦！")
        print(
            "=======================================\nNote: 请按两次回车键确定询问\n======================================="
        )
        while True:
            try:
                prompt = get_input("\n你：\n")
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
                        parent_id=parent_id,
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
    parser.add_argument("--conversation_id", type=str, required=False)
    parser.add_argument("--parent_id", type=str, required=False)
    args = parser.parse_args()
    print(f"初始化: 正在连接到位于 {args.url} 的 ChatGPT...")
    try:
        run(args.url, args.conversation_id, args.parent_id)
    except (KeyboardInterrupt, EOFError):
        sys.exit()
