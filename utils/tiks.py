import tiktoken


def get_openai_chat_tokens(messages, model="gpt-3.5-turbo-0301"):
    if model not in [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-32k",
        "gpt-4-32k-0314",
    ]:
        error = NotImplementedError("Unsupported engine {self.engine}")
        raise error

    tiktoken.model.MODEL_PREFIX_TO_ENCODING["gpt-4-"] = "cl100k_base"
    tiktoken.model.MODEL_TO_ENCODING["gpt-4"] = "cl100k_base"

    encoding = tiktoken.encoding_for_model(model)

    num_tokens = 0
    for message in messages:
        # every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += 1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def get_openai_completion_tokens(prompt, model="text-davinci-003"):
    if model not in [
        "text-davinci-002",
        "text-davinci-003",
    ]:
        error = NotImplementedError("Unsupported engine {self.engine}")
        raise error

    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(prompt))
