import os
import asyncio
from dotenv import load_dotenv
from bot import Messager
import logging
from polling import poll_forever

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s:  %(message)s')


class ParamsMissing(Exception):
    pass


load_dotenv()
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
DEVMAN_TOKEN = os.environ.get("DEVMAN_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")
URL = "https://dvmn.org/api/long_polling/"


if not all([TG_BOT_TOKEN, DEVMAN_TOKEN, TG_CHAT_ID]):
    raise ParamsMissing(
        "Required TG_BOT_TOKEN, DEVMAN_TOKEN, TG_CHAT_ID. did you forget to set .env?"
    )


async def main():
    logging.info("Started bot")

    try:
        bot = Messager(TG_BOT_TOKEN, TG_CHAT_ID)  # type:ignore
        await poll_forever(URL, DEVMAN_TOKEN, bot)  # type:ignore

    except KeyboardInterrupt:
        logging.info("Received CTRL-C")

    except ParamsMissing as e:
        print("error error")
        logging.error(e)
        SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
