import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFilter, ImageFont
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
        # Download thumbnail image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/temp_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        base = Image.open(f"cache/temp_{videoid}.png").convert("RGBA")
        base = base.resize((1280, 720))

        # Cinematic blurred background + color overlay (purple-pink tint)
        blur_bg = base.filter(ImageFilter.GaussianBlur(radius=15))
        overlay = Image.new("RGBA", (1280, 720), (70, 20, 60, 180))
        bg = Image.alpha_composite(blur_bg, overlay)

        draw = ImageDraw.Draw(bg)
        font_title = ImageFont.truetype("AnonXMusic/assets/font.ttf", 70)
        font_small = ImageFont.truetype("AnonXMusic/assets/font2.ttf", 30)

        # Vertical light beam with gradient alpha (stronger at center)
        light_beam = Image.new("RGBA", (1280, 720))
        beam_draw = ImageDraw.Draw(light_beam)
        for x in range(580, 700):
            alpha = int(30 * (1 - abs((x - 640) / 60)))  # tapering effect
            beam_draw.line([(x, 0), (x, 720)], fill=(255, 255, 255, alpha))
        bg = Image.alpha_composite(bg, light_beam)

        # Glow effect on title: draw multiple offset blurred shadows
        glow = Image.new("RGBA", (1280, 720))
        glow_draw = ImageDraw.Draw(glow)
        glow_text_pos = (60, 520)

        # Draw glow layers behind text (offsets for glow)
        for offset in range(1, 6):
            glow_draw.text((glow_text_pos[0] - offset, glow_text_pos[1] - offset), title, font=font_title, fill=(255, 255, 255, 50))
            glow_draw.text((glow_text_pos[0] + offset, glow_text_pos[1] - offset), title, font=font_title, fill=(255, 255, 255, 50))
            glow_draw.text((glow_text_pos[0] - offset, glow_text_pos[1] + offset), title, font=font_title, fill=(255, 255, 255, 50))
            glow_draw.text((glow_text_pos[0] + offset, glow_text_pos[1] + offset), title, font=font_title, fill=(255, 255, 255, 50))
        glow_draw.text(glow_text_pos, title, font=font_title, fill=(255, 255, 255, 200))
        bg = Image.alpha_composite(bg, glow)

        # Main title (sharp white text)
        draw.text(glow_text_pos, title, font=font_title, fill="white")

        # Glass Info Panel with Gaussian blur background
        panel = Image.new("RGBA", (1160, 140), (255, 255, 255, 40))
        panel = panel.filter(ImageFilter.GaussianBlur(4))
        bg.paste(panel, (60, 580), panel)

        # Metadata text
        draw.text((90, 600), f"Channel: {channel}", fill="white", font=font_small)
        draw.text((90, 640), f"Views: {views}    Duration: {duration}", fill="white", font=font_small)

        # Rounded progress bar background
        bar_x1, bar_y1 = 60, 685
        bar_x2, bar_y2 = 1220, 700
        radius = 10

        def rounded_rect(draw_obj, box, radius, fill):
            x1, y1, x2, y2 = box
            draw_obj.rounded_rectangle(box, radius=radius, fill=fill)

        rounded_rect(draw, (bar_x1, bar_y1, bar_x2, bar_y2), radius, fill="#FFFFFF40")

        # Progress portion - let's say 40% filled for demo
        progress_end = bar_x1 + int((bar_x2 - bar_x1) * 0.4)
        rounded_rect(draw, (bar_x1, bar_y1, progress_end, bar_y2), radius, fill="#FF00AA")  # Pinkish glow color

        # Watermark bottom right
        wm_text = f"Powered by {app.name}"
        w, h = draw.textsize(wm_text, font=font_small)
        draw.text((1280 - w - 50, 670), wm_text, fill="#DDDDDD", font=font_small)

        # Clean temp file & save final image
        os.remove(f"cache/temp_{videoid}.png")
        bg.save(path)

        return path

    except Exception as e:
        print(f"Thumbnail generation error: {e}")
        return YOUTUBE_IMG_URL
