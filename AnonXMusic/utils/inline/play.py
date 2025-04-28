from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

# Initialize your Pyrogram Client
app = Client("your_bot", 
api_id="14050586", 
api_hash="42a60d9c657b106370c79bb0a8ac560c",
bot_token="7967697232:AAHSVO7F8xk3wOGOcPYiqxMnHl1oKWKzZrs")

# ---------- Buttons ----------
def stylish_stream_panel():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏸️ Pause", callback_data="pause_stream"),
                InlineKeyboardButton("▶️ Resume", callback_data="resume_stream")
            ],
            [
                InlineKeyboardButton("⏭️ Next Song", callback_data="skip_stream"),
                InlineKeyboardButton("🔁 Replay Song", callback_data="replay_stream")
            ],
            [
                InlineKeyboardButton("⛔ Stop Stream", callback_data="stop_stream"),
                InlineKeyboardButton("❌ Close Menu", callback_data="close_panel")
            ]
        ]
    )

# ---------- Progress Bar ----------
def progress_bar(current_time: int, total_time: int) -> str:
    percentage = current_time / total_time
    progress_markers = 20
    filled_markers = int(progress_markers * percentage)
    empty_markers = progress_markers - filled_markers

    bar = "▰" * filled_markers + "▱" * empty_markers
    return f"🎵 {bar} {format_time(current_time)} / {format_time(total_time)}"

def format_time(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"

# ---------- Stream Progress Updater ----------
async def stream_progress_updater(message, duration):
    current = 0
    while current <= duration:
        try:
            bar_text = progress_bar(current, duration)
            await message.edit_text(
                f"🎶 Streaming Now...\n\n{bar_text}",
                reply_markup=stylish_stream_panel()
            )
            await asyncio.sleep(5)
            current += 5
        except Exception as e:
            print(f"Error during stream progress update: {e}")
            break  # Exit if an error occurs (e.g., message is deleted)

# ---------- Command to Start Streaming ----------
@app.on_message(filters.command("stream") & filters.private)
async def start_streaming(client, message):
    m = await message.reply_text(
        "🎶 Streaming Started!\n\n🎵 ▰▱▱▱▱▱▱▱▱▱ 0:00 / 3:08",
        reply_markup=stylish_stream_panel()
    )
    await stream_progress_updater(m, duration=188)  # 3 min 8 sec => 188 seconds

# ---------- Button Handler ----------
@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    data = callback_query.data

    if data == "pause_stream":
        await callback_query.answer("⏸️ Paused!", show_alert=True)

    elif data == "resume_stream":
        await callback_query.answer("▶️ Resumed!", show_alert=True)

    elif data == "skip_stream":
        await callback_query.answer("⏭️ Skipped to Next Song!", show_alert=True)

    elif data == "replay_stream":
        await callback_query.answer("🔁 Replaying!", show_alert=True)

    elif data == "stop_stream":
        await callback_query.answer("⛔ Stopped Streaming!", show_alert=True)

    elif data == "close_panel":
        await callback_query.message.delete()
        await callback_query.answer()

# ---------- Run the Bot ----------
app.run()
