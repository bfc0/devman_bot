import os
import asyncio
from dotenv import load_dotenv
import typing as t
from bot import Messager
from polling import long_polling


class ParamsMissing(Exception):
    pass


def bootstrap() -> t.Coroutine:
    load_dotenv()
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    API_TOKEN = os.environ.get("DEVMAN_TOKEN")
    CHAT_ID = os.environ.get("CHAT_ID")
    URL = "https://dvmn.org/api/long_polling/"

    if not all([BOT_TOKEN, API_TOKEN, CHAT_ID]):
        raise ParamsMissing(
            "Required BOT_TOKEN, DEVMAN_TOKEN, CHAT_ID. did you forget to set .env?"
        )

    bot = Messager(BOT_TOKEN, CHAT_ID)  # type:ignore

    return long_polling(URL, API_TOKEN, bot)  # type:ignore


async def main():

    print("Started")

    try:

        poll_forever = bootstrap()
        await poll_forever

    except KeyboardInterrupt:
        print("Bye-bye")
    except ParamsMissing as e:
        print(e)
        SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
