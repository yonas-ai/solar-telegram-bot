# Solar Energy Telegram Auto-Reply Bot

A bilingual (Amharic + English) Telegram group bot using Python.

## Features

- Welcomes new group members.
- Replies to common solar-related keywords.
- Answers `/start`, `/help`, `/invite`, and `/id`.
- Shares a configured group invite link or creates one using Telegram's API.
- Uses environment variables for secrets; no token is stored in the source code.

## 1. Create a Telegram bot

1. Open https://t.me/BotFather in Telegram.
2. Send `/newbot` and follow the instructions.
3. Copy the token privately. Do not publish it or commit it to GitHub.
4. Add the bot to your solar group.
5. Make it an administrator with permission to invite users. This is needed for the bot to create invitation links.
6. In your group, send `/id` and copy the chat ID from the bot's response.

For keyword replies to ordinary group messages, the bot must receive those messages. Making it an administrator usually enables this. Otherwise, use BotFather's `/setprivacy` command to disable privacy mode, then remove and re-add the bot if Telegram asks you to. Keep privacy enabled if you do not want the bot to read ordinary group messages.

## 2. Environment variables

Required:
- `BOT_TOKEN`: token from BotFather.

Optional:
- `GROUP_CHAT_ID`: numeric ID from the `/id` command. Set this so users can request the link in private chat.
- `GROUP_INVITE_LINK`: an existing group invite link. If set, the bot returns it instead of creating links through the API.

If both optional values are absent, `/invite` works in the group where the command is sent, provided the bot has permission to create invite links. For private chats, configure `GROUP_CHAT_ID` or `GROUP_INVITE_LINK`.

## 3. Run locally in Termux

Install Termux from https://github.com/termux/termux-app, then run:

```bash
pkg update && pkg upgrade
pkg install python nano
pip install -r requirements.txt
```

Put `bot.py` and `requirements.txt` in the same directory. Set the token for the current Termux session:

```bash
export BOT_TOKEN='PASTE_YOUR_TOKEN_HERE'
export GROUP_CHAT_ID='PASTE_NUMERIC_CHAT_ID_HERE'
python bot.py
```

Do not include angle brackets. Keep the token private. Optional link configuration:

```bash
export GROUP_INVITE_LINK='https://t.me/+YOUR_EXISTING_INVITE_CODE'
```

## 4. Deploy to a cloud host

This bot uses long polling, so deploy it as a **Background Worker** or equivalent always-on worker. Do not deploy it as a static site.

1. Create a private GitHub repository, e.g. `solar-telegram-bot`.
2. Upload `bot.py` and `requirements.txt`. Do not upload your token or a `.env` file.
3. On your cloud host, create a Python Background Worker connected to that repository.
4. Build/install command: `pip install -r requirements.txt`
5. Start command: `python bot.py`
6. Add environment variables in the host dashboard:
   - `BOT_TOKEN` = token from BotFather
   - `GROUP_CHAT_ID` = your group ID (optional but recommended)
   - `GROUP_INVITE_LINK` = an existing invite link (optional)
7. Deploy and check the logs for `Solar Energy Telegram bot is starting...`.
8. Open the bot in Telegram and test `/start`, `/help`, and `/invite`.

Render's Background Workers are not available on its free instance plan. For reliable 24/7 operation, select a paid worker or a host with an always-on worker plan. Free web instances can sleep or restart and are not a reliable always-on long-polling host.

## Troubleshooting

- **Bot does not answer normal group keywords:** ensure it is an admin or disable privacy with BotFather's `/setprivacy`, then re-add it if required.
- **Invite link fails:** check that the bot is an administrator with permission to invite users, and that `GROUP_CHAT_ID` is correct.
- **Bot does not start:** confirm `BOT_TOKEN` is set and the package installation succeeded.
- **Token leaked:** use BotFather to revoke/regenerate it immediately, then update the cloud environment variable.

## Customize replies

Edit the `REPLIES` list and `WELCOME_TEXT` in `bot.py`. Keep replies accurate: the example does not invent product prices or technical sizing.
