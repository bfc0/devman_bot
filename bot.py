import asyncio
from aiogram import Bot


class Messager:
    """A simple wrapper over aiogram bot"""

    def __init__(self, token: str, chat_id: str) -> None:
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send(self, message: str):
        loop = asyncio.get_running_loop()
        async with self.bot as bot:
            loop.create_task(bot.send_message(self.chat_id, message))

    async def disconnect(self):
        await self.bot.session.close()
