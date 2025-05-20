import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from youtubesearchpython.__future__ import VideosSearch

from AnonXMusic import app
from config import YOUTUBE_IMG_URL

def clear(text):
    title = ""
    for word in text.split():
        if len(title) + len(word) < 55:
            title += " " + word
    return title.strip()

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

        # Small preview thumbnail
        preview = base.copy().resize((400, 225))
        preview = ImageOps.expand(preview, border=5, fill='white')  # border
        shadow = Image.new('RGBA', (410, 235), (0, 0, 0, 100))
        base.paste(shadow, (435, 135), shadow)
        base.paste(preview, (440, 140))

        # Draw text on small thumbnail
        preview_text_panel = Image.new("RGBA", (400, 50), (0, 0, 0, 150))
        base.paste(preview_text_panel, (440, 315), preview_text_panel)

        # Fonts
        font_title = ImageFont.truetype("AnonXMusic/assets/font.ttf", 55)
        font_small = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 28)
        font_channel = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)
        font_mini = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 22)

        draw = ImageDraw.Draw(base)

        # Title on small preview
        draw.text((450, 325), title[:50], font=font_mini, fill=(255, 255, 255))

        # Optional: Play button
        try:
            play_icon = Image.open("AnonXMusic/assets/play.png").convert("RGBA").resize((60, 60))
            base.paste(play_icon, (590, 230), play_icon)
        except Exception as e:
            print(f"[Thumbnail] Play button not found: {e}")

        # Info panel at bottom
        panel = Image.new("RGBA", (1200, 180), (0, 0, 0, 180)).filter(ImageFilter.GaussianBlur(4))
        base.paste(panel, (40, 500), panel)

        # Info text
        draw.text((70, 520), "Now Playing", font=font_title, fill=(255, 255, 255))
        draw.text((70, 590), f"Channel: {channel}", font=font_channel, fill=(200, 200, 200))
        draw.text((70, 630), f"Duration: {duration}     Views: {views}", font=font_small, fill=(180, 180, 180))
        draw.text((970, 650), "t.me/BOTMINE_TECH", font=font_small, fill=(255, 255, 255))

        os.remove(f"cache/temp_{videoid}.png")
        base.save(path)
        return path

    except Exception as e:
        print(f"[Thumbnail] Generation failed: {e}")
        return YOUTUBE_IMG_URL
