import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    # System prompt
    system_prompt = input(
        "Provide System prompt or press 'enter' to continue.\n> "
    ).strip()

    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    conversation = Conversation()
    conversation.add_message(
        Message(role=Role.SYSTEM, content=system_prompt)
    )

    print("\nType your question or 'exit' to quit.")

    client = DialClient(deployment_name="gpt-4o-mini-2024-07-18")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting the chat. Goodbye!")
            break

        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break

        conversation.add_message(
            Message(role=Role.USER, content=user_input)
        )

        if stream:
            response = await client.stream_completion(conversation.messages)
        else:
            response = client.get_completion(conversation.messages)

        conversation.add_message(response)


asyncio.run(start(stream=True))
