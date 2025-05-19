import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from youtubesearchpython.__future__ import VideosSearch

from AnonXMusic import app  # Assuming your bot structure
from config import YOUTUBE_IMG_URL  # Fallback thumbnail

# Helper to trim long titles
def clear(text):
    title = ""
    for word in text.split():
        if len(title) + len(word) < 55:
            title += " " + word
    return title.strip()

# Main thumbnail generator
async def get_thumb(videoid):
    path = f"cache/{videoid}.png"
    if os.path.isfile(path):
        return path

    try:
        # YouTube search
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
        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/temp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # Load and resize image
        base = Image.open(f"cache/temp_{videoid}.png").convert("RGB")
        base = base.resize((1280, 720))

        # Overlay: semi-transparent black panel with blur for text readability
        panel = Image.new("RGBA", (1200, 180), (0, 0, 0, 180))
        panel = panel.filter(ImageFilter.GaussianBlur(4))
        base.paste(panel, (40, 500), panel)

        # Fonts
        font_title = ImageFont.truetype("AnonXMusic/assets/font.ttf", 55)
        font_small = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 28)
        font_channel = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)

        # Drawing text
        draw = ImageDraw.Draw(base)
        draw.text((70, 520), title, font=font_title, fill=(255, 255, 255))
        draw.text((70, 590), f"Channel: {channel}", font=font_channel, fill=(200, 200, 200))
        draw.text((70, 630), f"Duration: {duration}     Views: {views}", font=font_small, fill=(180, 180, 180))

        # Branding text
        draw.text((970, 650), "t.me/BOTMINE_TECH", font=font_small, fill=(255, 255, 255))

        # Cleanup temp and save final
        os.remove(f"cache/temp_{videoid}.png")
        base.save(path)
        return path

    except Exception as e:
        print(f"[Thumbnail] Generation failed: {e}")
        return YOUTUBE_IMG_URL
