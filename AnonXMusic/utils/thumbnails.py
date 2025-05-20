import os
import re
import base64
import aiofiles
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from youtubesearchpython.__future__ import VideosSearch

# Fallback thumbnail URL
YOUTUBE_IMG_URL = "https://i.imgur.com/6NfmK9b.jpg"

# Embedded Telegram logo as base64 (24x24 PNG)
TELEGRAM_LOGO_BASE64 = '''
iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAABW0lEQVR4nO2UwU3DMBCEGxNGmAEVgBWYARWQBVYARWAEVkAFWAFViAaEtFiFdiV82LSzy7S82a3Eev7r0v17A2AeNbbqjxAK7AjQ30S9ICnhcFkEkR6H+I6w8rdYkzKkJXAj/9n8qg/9MRJQ1kI4O6l+CGuW/dYozWCGM4QQAxYgkl5b0yefjZkkGct9lA3VaApsHJu4hzU6APjh1gDli5wNjMBtxlAj8EcV6CM/GPRvcvg6vALTPoxgJwnzLkOhIzO2BBcRkC0jYTwD+XyHiO3jvBl8zYF+98IB3dG4AMwMchRQYX4/1TzzmhhgOpICZ9uK9CAAAAABJRU5ErkJggg==
'''

def load_telegram_logo():
    logo_data = base64.b64decode(TELEGRAM_LOGO_BASE64)
    return Image.open(BytesIO(logo_data)).convert("RGBA").resize((24, 24))

def clear(text):
    title = ""
    for word in text.split():
        if len(title) + len(word) < 55:
            title += " " + word
    return title.strip()

def draw_play_icon(size=60, color=(255, 255, 255, 200)):
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    points = [(size * 0.3, size * 0.2), (size * 0.7, size * 0.5), (size * 0.3, size * 0.8)]
    draw.polygon(points, fill=color)
    return icon

async def get_thumb(videoid):
    path = f"cache/{videoid}.png"
    if os.path.isfile(path):
        return path

    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        result = (await results.next())["result"][0]
        title = clear(re.sub(r"\W+", " ", result.get("title", "Unknown Title").title()))
        duration = result.get("duration", "Unknown")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")
    except Exception as e:
        print(f"[Thumbnail] YouTube search failed: {e}")
        return YOUTUBE_IMG_URL

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/temp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        base = Image.open(f"cache/temp_{videoid}.png").convert("RGB")
        base = base.resize((1280, 720))

        preview = base.copy().resize((400, 225))
        preview = ImageOps.expand(preview, border=5, fill='white')
        shadow = Image.new('RGBA', (410, 235), (0, 0, 0, 100))
        base.paste(shadow, (435, 135), shadow)
        base.paste(preview, (440, 140))

        play_icon = draw_play_icon()
        base.paste(play_icon, (590, 230), play_icon)

        panel = Image.new("RGBA", (1200, 180), (0, 0, 0, 180)).filter(ImageFilter.GaussianBlur(4))
        base.paste(panel, (40, 500), panel)

        try:
            font_title = ImageFont.truetype("arial.ttf", 55)
            font_small = ImageFont.truetype("arial.ttf", 28)
            font_channel = ImageFont.truetype("arial.ttf", 30)
            font_watermark = ImageFont.truetype("arial.ttf", 24)
        except:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_channel = ImageFont.load_default()
            font_watermark = ImageFont.load_default()

        draw = ImageDraw.Draw(base)

        preview_title = title if len(title) <= 40 else title[:37] + "..."
        draw.text((450, 380), preview_title, font=font_small, fill=(0, 0, 0))

        draw.text((70, 520), title, font=font_title, fill=(255, 255, 255))
        draw.text((70, 590), f"Channel: {channel}", font=font_channel, fill=(200, 200, 200))
        draw.text((70, 630), f"Duration: {duration}     Views: {views}", font=font_small, fill=(180, 180, 180))

        # Watermark with Telegram icon
        watermark_text = "t.me/BOTMINE_TECH"
        wm_w, wm_h = draw.textsize(watermark_text, font=font_watermark)
        wm_x = 1280 - wm_w - 60
        wm_y = 720 - wm_h - 25

        draw.rectangle([(wm_x - 10, wm_y - 5), (wm_x + wm_w + 30, wm_y + wm_h + 5)], fill=(0, 0, 0, 150))

        tg_icon = load_telegram_logo()
        base.paste(tg_icon, (wm_x, wm_y), tg_icon)
        draw.text((wm_x + 30, wm_y), watermark_text, font=font_watermark, fill=(255, 255, 255))

        os.remove(f"cache/temp_{videoid}.png")
        base.save(path)
        return path

    except Exception as e:
        print(f"[Thumbnail] Generation failed: {e}")
        return YOUTUBE_IMG_URL


# Run sample
if __name__ == "__main__":
    import asyncio
    video_id = "dQw4w9WgXcQ"  # Example video ID
    result_path = asyncio.run(get_thumb(video_id))
    print(f"Thumbnail saved at: {result_path}")
