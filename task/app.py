import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    deployment_name = "gpt-4o-mini-2024-07-18"
    dial_client = DialClient(deployment_name)

    custom_client = CustomDialClient(deployment_name)

    conversation = Conversation()

    system_prompt = input("System prompt (press Enter for default): ").strip()
    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    conversation.add_message(
        Message(role=Role.SYSTEM, content=system_prompt)
    )

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Bye 👋")
            break

        conversation.add_message(
            Message(role=Role.USER, content=user_input)
        )

        if stream:
            response = await dial_client.stream_completion(conversation.messages)
        else:
            response = dial_client.get_completion(conversation.messages)

        conversation.add_message(response)

        print("\n--- Custom client response ---")
        if stream:
            await custom_client.stream_completion(conversation.messages)
        else:
            custom_client.get_completion(conversation.messages)


asyncio.run(start(True))
