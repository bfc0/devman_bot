import os
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import logging
from polling import poll_forever, prepare_sender


class ParamsMissing(Exception):
    pass


async def main():

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:  %(message)s")
    logging.info("Started bot")

    load_dotenv()
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
    DEVMAN_TOKEN = os.environ.get("DEVMAN_TOKEN")
    TG_CHAT_ID = os.environ.get("TG_CHAT_ID")
    URL = "https://dvmn.org/api/long_polling/"

    if not all([TG_BOT_TOKEN, DEVMAN_TOKEN, TG_CHAT_ID]):
        raise ParamsMissing(
            "Required TG_BOT_TOKEN, DEVMAN_TOKEN, TG_CHAT_ID. did you forget to set .env?"
        )

    try:
        bot = Bot(token=TG_BOT_TOKEN)  # type:ignore
        send_message = prepare_sender(bot, TG_CHAT_ID)  # type:ignore
        await poll_forever(URL, DEVMAN_TOKEN, send_message)  # type:ignore

    except KeyboardInterrupt:
        logging.info("Received CTRL-C")

    except ParamsMissing as e:
        logging.error(e)
        SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
