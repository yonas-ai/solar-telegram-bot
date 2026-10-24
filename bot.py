import logging
import os
import re
from typing import Optional

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GROUP_CHAT_ID_RAW = os.getenv("GROUP_CHAT_ID", "").strip()
GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK", "").strip()

GROUP_CHAT_ID: Optional[int] = int(GROUP_CHAT_ID_RAW) if GROUP_CHAT_ID_RAW else None

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "☀️ እንኳን ወደ ሶላር ኢነርጂ ቡድናችን በደህና መጡ!\n\n"
    "Welcome to our Solar Energy Group!\n"
    "Ask us about solar panels, hybrid inverters, lithium batteries, "
    "solar water pumps, system sizing, and installation.\n\n"
    "የሶላር ፓነል፣ ሃይብሪድ ኢንቨርተር፣ ሊቲየም ባትሪ፣ "
    "የውሃ ፓምፕ እና የመጫኛ አገልግሎት ለመጠየቅ ይጻፉ።\n\n"
    "Type /help to see what I can answer. Type /invite for the group link."
)

HELP_TEXT = (
    "☀️ Solar Energy Assistant | የሶላር ኢነርጂ ረዳት\n\n"
    "You can ask about:\n"
    "• Solar panels / ሶላር ፓነል\n"
    "• Inverters / ኢንቨርተር\n"
    "• Batteries / ባትሪ\n"
    "• Prices / ዋጋ\n"
    "• Solar water pumps / የሶላር የውሃ ፓምፕ\n"
    "• Installation / ተከላ\n"
    "• Group invitation / የቡድን መግቢያ ሊንክ\n\n"
    "Commands: /start, /help, /invite, /id\n"
    "ትእዛዞች፦ /start, /help, /invite, /id"
)

REPLIES = [
    {
        "keywords": [
            "price", "prices", "cost", "how much", "quotation", "quote",
            "ዋጋ", "ስንት ነው", "ዋጋው", "የስንት"
        ],
        "reply": (
            "💰 For an accurate price, please tell us the system size (kW), "
            "battery backup needed, and location. Our team can then prepare a quote.\n\n"
            "💰 ትክክለኛ ዋጋ ለማወቅ የሲስተሙን አቅም (kW)፣ "
            "የባትሪ የመጠባበቂያ ጊዜ እና የሚገኙበትን ቦታ ይግለጹ። "
            "ከዚያ የዋጋ ግምት ልናዘጋጅልዎ እንችላለን።"
        ),
    },
    {
        "keywords": [
            "solar panel", "solar panels", "panel", "panels", "photovoltaic",
            "ፓነል", "ሶላር ፓነል", "የፀሐይ ፓነል"
        ],
        "reply": (
            "☀️ Solar panels convert sunlight into electricity. The right size depends "
            "on your daily energy use, roof/land space, and sunlight conditions.\n\n"
            "☀️ ሶላር ፓነሎች የፀሐይ ብርሃንን ወደ ኤሌክትሪክ ይቀይራሉ። "
            "ትክክለኛው አቅም በዕለታዊ የኃይል ፍጆታዎ፣ በቦታዎ እና "
            "በፀሐይ ብርሃን ሁኔታ ላይ ይመሰረታል።"
        ),
    },
    {
        "keywords": [
            "inverter", "hybrid inverter", "inverters", "ሃይብሪድ",
            "ኢንቨርተር", "ኢንቨርተሮች"
        ],
        "reply": (
            "⚡ A hybrid inverter manages power from solar panels, batteries, and—"
            "where connected—the utility grid. Tell us your appliances and their wattage "
            "so we can help estimate the required capacity.\n\n"
            "⚡ ሃይብሪድ ኢንቨርተር ከሶላር ፓነል፣ ከባትሪ እና ከኤሌክትሪክ መስመር "
            "የሚመጣውን ኃይል ያስተዳድራል። የሚጠቀሙባቸውን መሳሪያዎችና "
            "የእያንዳንዳቸውን ዋት ይንገሩን።"
        ),
    },
    {
        "keywords": [
            "battery", "batteries", "lithium", "storage", "ባትሪ",
            "ሊቲየም", "የኃይል ማከማቻ"
        ],
        "reply": (
            "🔋 Battery capacity is usually described in kWh. The size you need depends "
            "on which appliances must run and for how many hours. Please share your "
            "essential loads and desired backup time.\n\n"
            "🔋 የባትሪ አቅም በአብዛኛው በkWh ይገለጻል። የሚያስፈልግዎ አቅም "
            "በሚጠቀሙባቸው መሳሪያዎችና በሚፈልጉት የመጠባበቂያ ሰዓት ላይ "
            "ይመሰረታል።"
        ),
    },
    {
        "keywords": [
            "water pump", "solar pump", "pumping", "የውሃ ፓምፕ",
            "የሶላር ፓምፕ", "ውሃ ማንሳት"
        ],
        "reply": (
            "💧 For solar water-pump sizing, share the borehole/water depth, total "
            "pumping head, required litres per day, and water source. These details "
            "help estimate pump power and solar-array size.\n\n"
            "💧 የሶላር የውሃ ፓምፕ ለመምረጥ የጉድጓዱን ጥልቀት፣ አጠቃላይ የማንሳት "
            "ቁመት፣ በቀን የሚያስፈልገውን የውሃ መጠን እና የውሃ ምንጩን ይግለጹ።"
        ),
    },
    {
        "keywords": [
            "install", "installation", "installer", "maintenance", "repair",
            "ተከላ", "ጥገና", "መጫን", "አገልግሎት"
        ],
        "reply": (
            "🛠️ We can help you plan solar installation and maintenance. Please send "
            "your location, the type of building/site, and the equipment you need.\n\n"
            "🛠️ የሶላር ተከላና ጥገና ለማቀድ የሚገኙበትን ቦታ፣ የህንፃውን/የቦታውን "
            "አይነት እና የሚያስፈልግዎን መሳሪያ ይጻፉ።"
        ),
    },
    {
        "keywords": [
            "solar", "solar energy", "renewable energy", "ሶላር",
            "የፀሐይ ኃይል", "የፀሐይ ሀይል", "ኃይል"
        ],
        "reply": (
            "☀️ We provide information about solar systems for homes, offices, shops, "
            "businesses, and water pumping. What would you like to power?\n\n"
            "☀️ ለቤት፣ ለቢሮ፣ ለሱቅ፣ ለንግድ ቦታ እና ለውሃ ፓምፕ የሶላር ሲስተሞች "
            "መረጃ እንሰጣለን። በሶላር ምን ማስኬድ ይፈልጋሉ?"
        ),
    },
]

INVITE_KEYWORDS = [
    "invite link", "group link", "join the group", "join group",
    "invitation", "telegram link", "የቡድን ሊንክ", "የቡድን መግቢያ",
    "ሊንኩን ላክ", "ቡድኑን ልቀላቀል", "መግቢያ ሊንክ"
]


async def get_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Return a configured invite link or create one using a configured/current group."""
    if GROUP_INVITE_LINK:
        return GROUP_INVITE_LINK

    current_chat = update.effective_chat
    target_chat_id = None

    if current_chat and current_chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        target_chat_id = current_chat.id
    elif GROUP_CHAT_ID is not None:
        target_chat_id = GROUP_CHAT_ID

    if target_chat_id is None:
        return None

    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=target_chat_id,
            name="Solar Energy Group Invite",
        )
        return invite.invite_link
    except Exception:
        logger.exception("Could not create invite link. Check bot admin permissions and GROUP_CHAT_ID.")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "☀️ Welcome! እንኳን ደህና መጡ!\n\n"
            "I'm your bilingual Solar Energy Assistant.\n"
            "እኔ የሶላር ኢነርጂ ረዳት ቦት ነኝ።\n\n"
            "Use /help for topics or /invite for the group link.\n"
            "ርዕሶችን ለማየት /help ወይም የቡድን ሊንክ ለማግኘት /invite ይጠቀሙ።"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(HELP_TEXT)


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    link = await get_invite_link(update, context)
    if link:
        await update.message.reply_text(
            f"🔗 Join our Solar Energy Telegram group:\n{link}\n\n"
            f"🔗 የሶላር ኢነርጂ ቡድናችንን ለመቀላቀል፦\n{link}"
        )
    else:
        await update.message.reply_text(
            "I couldn't create the invitation link. Please ask a group admin to set "
            "GROUP_CHAT_ID or GROUP_INVITE_LINK and make the bot an administrator "
            "with permission to invite users.\n\n"
            "የመግቢያ ሊንኩን ማዘጋጀት አልቻልኩም። አስተዳዳሪው GROUP_CHAT_ID "
            "ወይም GROUP_INVITE_LINK እንዲያዘጋጅና ቦቱን የሰዎች መጋበዝ ፈቃድ "
            "ያለው አስተዳዳሪ እንዲያደርገው ይጠይቁ።"
        )


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print current chat ID to help configure GROUP_CHAT_ID."""
    if update.message and update.effective_chat:
        await update.message.reply_text(f"Chat ID: `{update.effective_chat.id}`", parse_mode="Markdown")


async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.new_chat_members:
        return

    # Do not greet the bot itself if it is added to a group.
    new_people = [
        member for member in message.new_chat_members
        if not member.is_bot or member.id != context.bot.id
    ]
    if new_people:
        names = ", ".join(person.first_name for person in new_people[:5])
        text = f"👋 Welcome, {names}!\n\n{WELCOME_TEXT}"
        await message.reply_text(text)


async def reply_to_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.text:
        return
    if message.from_user and message.from_user.is_bot:
        return

    text = message.text.strip()
    if not text or text.startswith("/"):
        return

    normalized = re.sub(r"\s+", " ", text.casefold())

    # Share the group link only when the user clearly asks for it.
    if any(word.casefold() in normalized for word in INVITE_KEYWORDS):
        link = await get_invite_link(update, context)
        if link:
            await message.reply_text(
                f"🔗 Group invitation / የቡድን መግቢያ፦\n{link}"
            )
        else:
            await message.reply_text(
                "Please use /invite or ask a group admin for the link.\n"
                "እባክዎ /invite ይጠቀሙ ወይም የቡድኑን አስተዳዳሪ ያነጋግሩ።"
            )
        return

    for item in REPLIES:
        if any(keyword.casefold() in normalized for keyword in item["keywords"]):
            await message.reply_text(item["reply"])
            return


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("An exception occurred while handling an update", exc_info=context.error)


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Add it as an environment variable.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("invite", invite_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_keywords)
    )
    app.add_error_handler(error_handler)

    logger.info("Solar Energy Telegram bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
