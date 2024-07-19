import asyncio
import logging
import inspect
import aiohttp
import typing as t
from aiohttp import ClientSession

from bot import Messager


DEFAULT_TIMEOUT = 100
ERROR_TIMEOUT = 3


async def handle_response(response: dict[str, t.Any], bot: Messager) -> str | None:

    if response.get("status") == "timeout":
        if ts := response.get("timestamp_to_request"):
            return str(ts)

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

        await bot.send(message)


async def poll_forever(
    url: str, api_token: str, bot: Messager, timeout=DEFAULT_TIMEOUT
) -> None:

    headers = {"Authorization": f"Token {api_token}"}

    async with ClientSession() as session:
        while True:
            try:
                response = await session.get(url, headers=headers, timeout=timeout)
                if response.status != 200:
                    continue
                response = await response.json()
                timestamp = await handle_response(response, bot)

                if timestamp:
                    headers["timestamp"] = timestamp

            except asyncio.TimeoutError:
                continue

            except aiohttp.ClientError as e:
                logging.error(f"error occured: {e}")
                await asyncio.sleep(ERROR_TIMEOUT)

            except asyncio.CancelledError:
                await bot.disconnect()
                return
