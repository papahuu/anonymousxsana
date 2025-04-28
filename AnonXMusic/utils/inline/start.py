import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from AnonXMusic import app

# Buttons for /start and /help commands
def start_panel(support_chat_url: str, support_channel_url: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Add Me to Your Group ➕",
                url=f"https://t.me/{app.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Support",
                url=support_chat_url
            ),
            InlineKeyboardButton(
                text="📢 Updates",
                url=support_channel_url
            ),
        ],
    ]
    return buttons

def private_panel(owner_id: int, support_chat_url: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Add Me to Your Group ➕",
                url=f"https://t.me/{app.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚙️ Settings",
                callback_data="settings_back_helper"
            )
        ],
        [
            InlineKeyboardButton(
                text="👑 Owner",
                user_id=owner_id
            ),
            InlineKeyboardButton(
                text="💬 Support",
                url=support_chat_url
            ),
        ],
    ]
    return buttons

# Settings buttons
def settings_panel():
    buttons = [
        [
            InlineKeyboardButton(
                text="🎶 Toggle Autoplay",
                callback_data="toggle_autoplay"
            ),
            InlineKeyboardButton(
                text="🔊 Adjust Volume",
                callback_data="adjust_volume"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📝 Change Language",
                callback_data="change_language"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏡 Back to Home",
                callback_data="home_helper"
            ),
        ],
    ]
    return buttons

# /start command handler (private)
@app.on_message(filters.command("start") & filters.private)
async def start_command_private(client, message):
    user = message.from_user
    user_mention = user.mention(style="md")

    SUPPORT_CHAT = "https://t.me/BOT_SUPPORT_GROUP7"  # Updated Support Chat
    SUPPORT_CHANNEL = "https://t.me/ll_BOTCHAMBER_ll"  # Updated Update Channel
    OWNER_ID = 8093150680  # Updated Owner ID

    start_text = f"""
**Hey {user_mention}!

I am {app.username}, your friendly Telegram Music Bot!**

➤ Add me to your groups and enjoy nonstop music.
➤ Use Settings to customize your experience.

_Thank you for choosing me!_
"""

    # Send video instead of photo
    await message.reply_video(
        video="https://telegra.ph/file/63e57c9f33c21ef6b7b56.mp4",  # Example welcome video URL
        caption=start_text,
        reply_markup=InlineKeyboardMarkup(
            private_panel(OWNER_ID, SUPPORT_CHAT)
        )
    )

# /start command handler (group)
@app.on_message(filters.command("start") & filters.group)
async def start_command_group(client, message):
    SUPPORT_CHAT = "https://t.me/BOT_SUPPORT_GROUP7"  # Updated Support Chat
    SUPPORT_CHANNEL = "https://t.me/ll_BOTCHAMBER_ll"  # Updated Update Channel

    start_text = "**Hello Group!**\n\nI am alive and ready to play music!"

    await message.reply_text(
        text=start_text,
        reply_markup=InlineKeyboardMarkup(
            start_panel(SUPPORT_CHAT, SUPPORT_CHANNEL)
        )
    )

# /help command handler
@app.on_message(filters.command("help"))
async def help_command(client, message):
    user = message.from_user
    user_mention = user.mention(style="md")

    SUPPORT_CHAT = "https://t.me/BOT_SUPPORT_GROUP7"  # Updated Support Chat

    help_text = f"""
**Hello {user_mention}!

Here is how you can use {app.username}:**

➤ `/play` - Play songs in your voice chat.
➤ `/pause` - Pause the current song.
➤ `/resume` - Resume the paused song.
➤ `/skip` - Skip to the next track.
➤ `/stop` - Stop the music.

➤ `/ping` - Check bot's alive status.
➤ `/stats` - Show bot's usage stats.

➤ **Admin Commands:**
   `/reload` - Reload admin list.
   `/mute` - Mute the voice chat.
   `/unmute` - Unmute the voice chat.

_If you need more help, feel free to join our Support Group!_
"""

    # Send video instead of photo
    await message.reply_video(
        video="https://envs.sh/4l0.mp4",  # Example help video URL
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(
            settings_panel()
        )
    )

# /settings command handler
@app.on_message(filters.command("settings"))
async def settings_command(client, message):
    user = message.from_user
    user_mention = user.mention(style="md")

    settings_text = f"""
**Hey {user_mention}, here are your settings:**

➤ Toggle autoplay to enable or disable automatic play next.
➤ Adjust the bot's volume according to your preferences.
➤ Change the language of the bot.
"""

    await message.reply_text(
        text=settings_text,
        reply_markup=InlineKeyboardMarkup(
            settings_panel()
        )
    )

# /ping command handler
@app.on_message(filters.command("ping"))
async def ping_command(client, message):
    start_time = time.time()

    # Simulate the bot's response (animation)
    await message.reply_text("🏓 Pong! Checking bot's response time...")

    # Calculate the ping time
    ping_time = round((time.time() - start_time) * 1000)  # in milliseconds

    # Send the result
    await message.edit_text(
        f"🏓 **Pong!**\n\nResponse time: `{ping_time}ms`\n\nThe bot is alive and fast!"
)
