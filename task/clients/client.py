from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)

        self.client = Dial(
            api_key=self._api_key,
            base_url=DIAL_ENDPOINT
        )

        self.async_client = AsyncDial(
            api_key=self._api_key,
            base_url=DIAL_ENDPOINT
        )

    def get_completion(self, messages: list[Message]) -> Message:
        response = self.client.chat.completions.create(
    deployment_name=self._deployment_name,
    messages=[m.to_dict() for m in messages],

        )

        if not response.choices:
            raise Exception("No choices in response found")

        content = response.choices[0].message.content
        print(content)

        return Message(
            role=Role.AI,
            content=content
        )

    async def stream_completion(self, messages: list[Message]) -> Message:
        
        chunks = await self.async_client.chat.completions.create(
    deployment_name=self._deployment_name,
    messages=[m.to_dict() for m in messages],
    stream=True,
)


        contents: list[str] = []

        async for chunk in chunks:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if delta and delta.content:
                print(delta.content, end="")
                contents.append(delta.content)

        print()

        return Message(
            role=Role.AI,
            content="".join(contents)
        )
