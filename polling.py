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


def prepare_sender(bot: Bot, tg_chat_id: str) -> t.Callable:

    async def send_message(message: str):
        for _ in range(NUM_TRIES):
            try:
                await bot.send_message(tg_chat_id, message)
                return
            except Exception as e:
                logging.error(f"failed to send message: {e}")
                await asyncio.sleep(ERROR_TIMEOUT)
            finally:
                await bot.session.close()

    return send_message


async def handle_response(response: dict[str, t.Any], send_message: t.Callable):

    if response.get("status") != "found":
        return

    if not isinstance(attempts := response.get("new_attempts"), list):
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
                submission_data = await response.json()
                await handle_response(submission_data, send_message)

                if timestamp := submission_data.get("timestamp_to_request"):
                    headers["timestamp"] = str(timestamp)

            except asyncio.TimeoutError:
                continue

            except aiohttp.ClientError as e:
                logging.error(f"error occured: {e}")
                await asyncio.sleep(ERROR_TIMEOUT)

            except asyncio.CancelledError:
                return
