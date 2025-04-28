from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Client("music_bot")

# Callback query handler
@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    if data == "support":
        await callback_query.answer("Redirecting to Support Chat...")
        await callback_query.message.reply_text("You can reach out to us here: https://t.me/BOT_SUPPORT_GROUP7")
    elif data == "updates":
        await callback_query.answer("Redirecting to Updates Channel...")
        await callback_query.message.reply_text("Stay updated with new features here: https://t.me/ll_BOTCHAMBER_ll")

# /start command handler
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

    try:
        # Send photo with inline buttons
        await message.reply_photo(
            photo="https://envs.sh/4lw.jpg",  # Example welcome image URL
            caption=start_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Support Chat", url=SUPPORT_CHAT)],
                    [InlineKeyboardButton("Updates Channel", url=SUPPORT_CHANNEL)]
                ]
            )
        )
        print("Start message sent successfully")
    except Exception as e:
        print(f"Error sending photo: {e}")
        await message.reply("There was an issue processing your start command. Please try again later.")

app.run()
