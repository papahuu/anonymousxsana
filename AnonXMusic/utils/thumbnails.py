import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
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
        print(f"Search failed: {e}")
        return YOUTUBE_IMG_URL

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/temp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        base = Image.open(f"cache/temp_{videoid}.png").convert("RGBA")
        base = base.resize((1280, 720))

        # Cinematic background
        blur_bg = base.filter(ImageFilter.GaussianBlur(radius=12))
        overlay = Image.new("RGBA", (1280, 720), (30, 20, 50, 180))
        bg = Image.alpha_composite(blur_bg, overlay)

        draw = ImageDraw.Draw(bg)
        font_title = ImageFont.truetype("AnonXMusic/assets/font.ttf", 52)
        font_small = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)
        font_glow = ImageFont.truetype("AnonXMusic/assets/font.ttf", 54)

        # Vertical light beam (cinematic feel)
        light_beam = Image.new("RGBA", (1280, 720))
        beam_draw = ImageDraw.Draw(light_beam)
        beam_draw.rectangle([(580, 0), (700, 720)], fill=(255, 255, 255, 30))
        bg = Image.alpha_composite(bg, light_beam)

        # Central title glow
        glow = Image.new("RGBA", (1280, 720))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.text((60, 510), title, font=font_glow, fill=(255, 255, 255, 100))
        bg = Image.alpha_composite(bg, glow)

        # Main Title
        draw.text((60, 510), title, font=font_title, fill="white")

        # Glass Info Panel
        panel = Image.new("RGBA", (1160, 140), (255, 255, 255, 30))
        panel = panel.filter(ImageFilter.GaussianBlur(2))
        bg.paste(panel, (60, 600), panel)

        # Metadata Text
        draw.text((90, 615), f"Channel: {channel}", fill="white", font=font_small)
        draw.text((90, 655), f"Views: {views}    Duration: {duration}", fill="white", font=font_small)

        # Progress bar
        draw.rectangle([(60, 685), (1220, 700)], fill="#FFFFFF40")
        draw.rectangle([(60, 685), (520, 700)], fill="#1DB954")  # Spotify green style

        # Watermark
        draw.text((1050, 675), f"Powered by {app.name}", fill="#DDDDDD", font=font_small)

        # Clean and Save
        os.remove(f"cache/temp_{videoid}.png")
        bg.save(path)
        return path

    except Exception as e:
        print(f"Thumbnail generation error: {e}")
        return YOUTUBE_IMG_URL
