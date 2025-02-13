import asyncio
import logging
import inspect
from aiogram import Bot
import aiohttp
import typing as t
from aiohttp import ClientSession


DEFAULT_TIMEOUT = 100
ERROR_TIMEOUT = 3
NUM_TRIES = 3

logger = logging.getLogger("tg logger")


async def send_message(bot: Bot, tg_chat_id: str, message: str):
    for _ in range(NUM_TRIES):
        try:
            await bot.send_message(tg_chat_id, message)
            return
        except Exception as e:
            logger.error(f"failed to send message: {e}")
            await asyncio.sleep(ERROR_TIMEOUT)
        finally:
            await bot.session.close()


async def handle_payload(payload: dict[str, t.Any], send_message: t.Callable):

    if payload.get("status") != "found":
        return

    if not isinstance(attempts := payload.get("new_attempts"), list):
        return

    for attempt in attempts:
        if attempt.get("is_negative"):
            message = inspect.cleandoc(
                f""" You have failed your recent submission
            {attempt.get('lesson_title')} at
            {attempt.get('lesson_url')}"""
            )
        else:
            message = inspect.cleandoc(
                f"""Your recent submission on
            {attempt.get('lesson_title')} has been accepted at
            {attempt.get('lesson_url')}"""
            )

        await send_message(message)


async def poll_forever(
    url: str, api_token: str, send_message: t.Callable, timeout=DEFAULT_TIMEOUT
) -> None:

    headers = {"Authorization": f"Token {api_token}"}

    async with ClientSession() as session:
        while True:
            try:
                response = await session.get(url, headers=headers, timeout=timeout)
                if response.status != 200:
                    continue
                payload = await response.json()
                await handle_payload(payload, send_message)

                if timestamp := payload.get("timestamp_to_request"):
                    headers["timestamp"] = str(timestamp)

            except asyncio.TimeoutError:
                continue

            except aiohttp.ClientError as e:
                logger.error(f"error occured: {e}")
                await asyncio.sleep(ERROR_TIMEOUT)

            except asyncio.CancelledError:
                return
