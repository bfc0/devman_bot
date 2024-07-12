import asyncio
import inspect
import aiohttp
import typing as t
from aiohttp import ClientSession

from bot import Messager


DEFAULT_TIMEOUT = 100


async def handle_response(
    response: dict[str, t.Any], bot: Messager, headers: dict[str, str]
) -> None:

    if response.get("status") == "timeout":
        if (ts := response.get("timestamp_to_request")) is not None:
            headers["timestamp"] = str(ts)
            return

    if response.get("status") != "found":
        return

    if not isinstance(attempts := response.get("new_attempts"), list):
        return

    for attempt in attempts:
        if attempt.get("is_negative") is True:
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


async def long_polling(
    url: str, api_token: str, bot: Messager, timeout=DEFAULT_TIMEOUT
) -> None:

    headers = {"Authorization": f"Token {api_token}"}

    async with ClientSession() as session:
        while True:
            try:
                response = await session.get(url, headers=headers, timeout=timeout)
                if response.status != 200:
                    continue
                as_dict = await response.json()
                await handle_response(as_dict, bot, headers)

            except asyncio.TimeoutError:
                continue

            except aiohttp.ClientError as e:
                print(f"error occurred: {e}")
                await asyncio.sleep(3)

            except asyncio.CancelledError:
                await bot.disconnect()
                return
