import os
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import logging
import typing as t
from logging.handlers import SysLogHandler
from functools import partial
from polling import poll_forever, send_message

logger = logging.getLogger("tg logger")


class TgLogsHandler(logging.Handler):
    def __init__(self, send_msg: t.Callable):
        super().__init__()
        self.send_msg = send_msg

    def emit(self, record):
        text = self.format(record)
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(self.send_msg(text), loop)


class ParamsMissing(Exception):
    pass


async def main():
    logger.addHandler(SysLogHandler(address="/dev/log"))
    logger.setLevel(logging.INFO)

    load_dotenv()
    tg_bot_token = os.environ.get("TG_BOT_TOKEN")
    devman_token = os.environ.get("DEVMAN_TOKEN")
    tg_chat_id = os.environ.get("TG_CHAT_ID")
    url = "https://dvmn.org/api/long_polling/"

    if not all([tg_bot_token, devman_token, tg_chat_id]):
        raise ParamsMissing(
            "Required TG_BOT_TOKEN, DEVMAN_TOKEN, TG_CHAT_ID. did you forget to set .env?"
        )

    bot = Bot(token=tg_bot_token)  # type:ignore
    send_msg = partial(send_message, bot, tg_chat_id)  # type:ignore

    logger.addHandler(TgLogsHandler(send_msg))
    logger.info("Started dvmn bot")

    try:
        await poll_forever(url, devman_token, send_msg)  # type:ignore

    except KeyboardInterrupt:
        logger.info("Shutting down")

    except ParamsMissing as e:
        logger.error(e)
        SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
