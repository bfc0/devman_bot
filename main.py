import os
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import logging
from functools import partial
from polling import poll_forever, send_message


class ParamsMissing(Exception):
    pass


async def main():

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:  %(message)s")
    logging.info("Started bot")

    load_dotenv()
    tg_bot_token = os.environ.get("TG_BOT_TOKEN")
    devman_token = os.environ.get("DEVMAN_TOKEN")
    tg_chat_id = os.environ.get("TG_CHAT_ID")
    url = "https://dvmn.org/api/long_polling/"

    if not all([tg_bot_token, devman_token, tg_chat_id]):
        raise ParamsMissing(
            "Required TG_BOT_TOKEN, DEVMAN_TOKEN, TG_CHAT_ID. did you forget to set .env?"
        )

    try:
        bot = Bot(token=tg_bot_token)  # type:ignore
        send_msg = partial(send_message, bot, tg_chat_id)  # type:ignore
        await poll_forever(url, devman_token, send_msg)  # type:ignore

    except KeyboardInterrupt:
        logging.info("Received CTRL-C")

    except ParamsMissing as e:
        logging.error(e)
        SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
