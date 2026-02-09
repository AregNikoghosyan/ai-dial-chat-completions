import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = (
            f"{DIAL_ENDPOINT}/openai/deployments/"
            f"{deployment_name}/chat/completions"
        )

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            "Api-Key": self._api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [m.to_dict() for m in messages]
        }

        response = requests.post(
            self._endpoint,
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        data = response.json()

        if not data.get("choices"):
            raise Exception("No choices in response found")

        content = data["choices"][0]["message"]["content"]
        print(f"AI: {content}")

        return Message(
            role=Role.AI,
            content=content
        )

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "Api-Key": self._api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "stream": True,
            "messages": [m.to_dict() for m in messages],
        }

        contents: list[str] = []

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._endpoint,
                headers=headers,
                json=payload,
            ) as response:

                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"HTTP {response.status}: {text}")

                print("AI: ", end="")

                async for raw in response.content:
                    line = raw.decode("utf-8").strip()

                    if not line or line == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        payload = json.loads(line[6:])
                        delta = payload["choices"][0]["delta"]

                        if "content" in delta:
                            chunk = delta["content"]
                            print(chunk, end="")
                            contents.append(chunk)

        print()

        return Message(
            role=Role.AI,
            content="".join(contents)
        )
