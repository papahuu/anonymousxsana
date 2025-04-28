from pyrogram.types import InlineKeyboardButton

import config
from AnonXMusic import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Add Me to Your Group ➕", 
                url=f"https://t.me/{app.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                text="Support Group", 
                url=config.SUPPORT_CHAT
            ),
            InlineKeyboardButton(
                text="Update Channel", 
                url=config.SUPPORT_CHANNEL
            ),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Add Me to Your Group ➕", 
                url=f"https://t.me/{app.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                text="Settings ⚙️", 
                callback_data="settings_back_helper"
            )
        ],
        [
            InlineKeyboardButton(
                text="Owner", 
                user_id=config.OWNER_ID
            ),
            InlineKeyboardButton(
                text="Support Group", 
                url=config.SUPPORT_CHAT
            ),
        ],
    ]
    return buttons
