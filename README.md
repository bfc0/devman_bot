# Devman bot
A notification system that sends you a Telegram message when your devman submission has been reviewed.

### Install:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Create .env:
```
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
API_TOKEN=your_devman_token
```
Message BotFather to create your bot token

### Run:
```bash
python main.py
```