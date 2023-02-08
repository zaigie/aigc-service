import json
import os
from datetime import date

import openai
import tiktoken

ENGINE = os.environ.get("GPT_ENGINE") or "text-chat-davinci-002-20221122"
ENCODING_NAME = os.environ.get("ENCODING_NAME") or "gpt2"
ENCODER = tiktoken.get_encoding(ENCODING_NAME)


def get_max_tokens(prompt: str) -> int:
    return 4000 - len(ENCODER.encode(prompt))


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[: -len(suffix)]
    return input_string


class Chatbot:
    def __init__(self, api_key: str, buffer: int = None, engine: str = None) -> None:
        openai.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.conversations = Conversation()
        self.prompt = Prompt(buffer=buffer)
        self.engine = engine or ENGINE

    def _get_completion(
        self,
        prompt: str,
        temperature: float = 0.5,
        stream: bool = False,
    ):
        return openai.Completion.create(
            engine=self.engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=get_max_tokens(prompt),
            stop=["\n\n\n"],
            stream=stream,
        )

    def _process_completion(
        self,
        user_request: str,
        completion: dict,
        conversation_id: str = None,
        user: str = "User",
    ) -> dict:
        if completion.get("choices") is None:
            raise Exception("ChatGPT API returned no choices")
        if len(completion["choices"]) == 0:
            raise Exception("ChatGPT API returned no choices")
        if completion["choices"][0].get("text") is None:
            raise Exception("ChatGPT API returned no text")
        completion["choices"][0]["text"] = remove_suffix(
            completion["choices"][0]["text"], "<|im_end|>"
        )
        # Add to chat history
        self.prompt.add_to_history(
            user_request,
            completion["choices"][0]["text"],
            user=user,
        )
        if conversation_id is not None:
            self.save_conversation(conversation_id)
        return completion

    def _process_completion_stream(
        self,
        user_request: str,
        completion: dict,
        conversation_id: str = None,
        user: str = "User",
    ) -> str:
        full_response = ""
        for response in completion:
            if response.get("choices") is None:
                raise Exception("ChatGPT API returned no choices")
            if len(response["choices"]) == 0:
                raise Exception("ChatGPT API returned no choices")
            if response["choices"][0].get("finish_details") is not None:
                break
            if response["choices"][0].get("text") is None:
                raise Exception("ChatGPT API returned no text")
            if response["choices"][0]["text"] == "<|im_end|>":
                break
            yield response["choices"][0]["text"]
            full_response += response["choices"][0]["text"]

        # Add to chat history
        self.prompt.add_to_history(user_request, full_response, user)
        if conversation_id is not None:
            self.save_conversation(conversation_id)

    def ask(
        self,
        user_request: str,
        temperature: float = 0.5,
        conversation_id: str = None,
        user: str = "User",
    ) -> dict:
        if conversation_id is not None:
            self.load_conversation(conversation_id)
        completion = self._get_completion(
            self.prompt.construct_prompt(user_request, user=user),
            temperature,
        )
        return self._process_completion(
            user_request, completion, conversation_id=conversation_id, user=user
        )

    def ask_stream(
        self,
        user_request: str,
        temperature: float = 0.5,
        conversation_id: str = None,
        user: str = "User",
    ) -> str:
        if conversation_id is not None:
            self.load_conversation(conversation_id)
        prompt = self.prompt.construct_prompt(user_request, user=user)
        return self._process_completion_stream(
            user_request=user_request,
            completion=self._get_completion(prompt, temperature, stream=True),
            conversation_id=conversation_id,
            user=user,
        )

    def make_conversation(self, conversation_id: str) -> None:
        self.conversations.add_conversation(conversation_id, [])

    def rollback(self, num: int) -> None:
        for _ in range(num):
            self.prompt.chat_history.pop()

    def reset(self) -> None:
        self.prompt.chat_history = []

    def load_conversation(self, conversation_id) -> None:
        if conversation_id not in self.conversations.conversations:
            # Create a new conversation
            self.make_conversation(conversation_id)
        self.prompt.chat_history = self.conversations.get_conversation(conversation_id)

    def save_conversation(self, conversation_id) -> None:
        self.conversations.add_conversation(conversation_id, self.prompt.chat_history)


class AsyncChatbot(Chatbot):
    async def _get_completion(
        self,
        prompt: str,
        temperature: float = 0.5,
        stream: bool = False,
    ):
        return await openai.Completion.acreate(
            engine=self.engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=get_max_tokens(prompt),
            stop=["\n\n\n"],
            stream=stream,
        )

    async def ask(
        self,
        user_request: str,
        temperature: float = 0.5,
        conversation_id: str = None,
        user: str = "User",
    ) -> dict:
        """
        Same as Chatbot.ask but async
        }
        """
        completion = await self._get_completion(
            self.prompt.construct_prompt(user_request, user=user),
            temperature,
        )
        return self._process_completion(
            user_request, completion, user=user, conversation_id=conversation_id
        )

    async def ask_stream(
        self,
        user_request: str,
        temperature: float = 0.5,
        conversation_id: str = None,
        user: str = "User",
    ) -> str:
        """
        Same as Chatbot.ask_stream but async
        """
        prompt = self.prompt.construct_prompt(user_request, user=user)
        return self._process_completion_stream(
            user_request=user_request,
            completion=await self._get_completion(prompt, temperature, stream=True),
            user=user,
            conversation_id=conversation_id,
        )


class Prompt:
    def __init__(self, buffer: int = None) -> None:
        first_prompt = os.environ.get("FIRST_PROMPT") or "你好"
        user_first_prompt = (
            first_prompt if first_prompt == "你好" else first_prompt + "本次请仅回复“好的，收到。”"
        )
        chatgpt_first_ansewer = "你好!今天我能为您效劳吗? " if first_prompt == "你好" else "好的，收到。"
        self.base_prompt = (
            os.environ.get("CUSTOM_BASE_PROMPT")
            or "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally. Do not answer as the user. Current date: "
            + str(date.today())
            + "\n\n"
            + f"User: {user_first_prompt}\n"
            + f"ChatGPT: {chatgpt_first_ansewer} <|im_end|>\n\n\n"
        )
        # Track chat history
        self.chat_history: list = []
        self.buffer = buffer

    def add_to_chat_history(self, chat: str) -> None:
        self.chat_history.append(chat)

    def add_to_history(
        self,
        user_request: str,
        response: str,
        user: str = "User",
    ) -> None:
        self.add_to_chat_history(
            user
            + ": "
            + user_request
            + "\n\n\n"
            + "ChatGPT: "
            + response
            + "<|im_end|>\n",
        )

    def history(self, custom_history: list = None) -> str:
        return "\n".join(custom_history or self.chat_history)

    def construct_prompt(
        self,
        new_prompt: str,
        custom_history: list = None,
        user: str = "User",
    ) -> str:
        prompt = (
            self.base_prompt
            + self.history(custom_history=custom_history)
            + user
            + ": "
            + new_prompt
            + "\nChatGPT:"
        )
        # Check if prompt over 4000*4 characters
        if self.buffer is not None:
            max_tokens = 4000 - self.buffer
        else:
            max_tokens = 3200
        if len(ENCODER.encode(prompt)) > max_tokens:
            # Remove oldest chat
            if len(self.chat_history) == 0:
                return prompt
            self.chat_history.pop(0)
            # Construct prompt again
            prompt = self.construct_prompt(new_prompt, custom_history, user)
        return prompt


class Conversation:
    def __init__(self) -> None:
        self.conversations = {}
        self.base_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "conversations"
        )
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)

    def add_conversation(self, key: str, history: list) -> None:
        keyfile = os.path.join(self.base_dir, key + ".json")
        with open(keyfile, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False)
        self.conversations[key] = history

    def get_conversation(self, key: str) -> list:
        keyfile = os.path.join(self.base_dir, key + ".json")
        with open(keyfile, encoding="utf-8") as f:
            return json.loads(f.read())
        # return self.conversations[key]

    def remove_conversation(self, key: str) -> None:
        keyfile = os.path.join(self.base_dir, key + ".json")
        os.remove(keyfile)
        del self.conversations[key]

    def __str__(self) -> str:
        conversations = {}
        keyfiles = os.listdir(self.base_dir)
        for keyfile in keyfiles:
            key = keyfile.split(".")[0]
            with open(os.path.join(self.base_dir, keyfile), encoding="utf-8") as f:
                conversations[key] = json.loads(f.read())
        self.conversations = conversations
        return json.dumps(self.conversations)
