
#!/usr/bin/env python3
"""Render flexible, branded Time To Herbs educational infographics."""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BRAND_PATH = HERE / "brand.json"

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_ITALIC = r"C:\Windows\Fonts\ariali.ttf"
FONT_SERIF = r"C:\Windows\Fonts\georgiab.ttf"

# Permanent Time To Herbs visual identity
BG = (250, 248, 241)
PANEL = (255, 254, 249)
PANEL_ALT = (244, 240, 229)
NAVY = (35, 63, 76)
GOLD = (166, 113, 48)
GOLD_LIGHT = (220, 190, 133)
INK = (39, 53, 58)
MUTED = (100, 105, 99)
GREEN = (83, 112, 79)
PALE_GREEN = (232, 238, 225)
BORDER = (190, 151, 91)
WHITE = (255, 255, 255)


def load_brand():
    if BRAND_PATH.exists():
        try:
            return json.loads(
                BRAND_PATH.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            pass

    return {
        "brand_name": "Time To Herbs",
        "monogram": "TH",
        "watermark": "FOLLOW TIME TO HERBS"
    }


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        try:
            return ImageFont.truetype(
                "DejaVuSans.ttf", size
            )
        except OSError:
            return ImageFont.load_default()


def text_width(draw, text, font):
    return draw.textbbox(
        (0, 0), str(text), font=font
    )[2]


def wrap_text(text, font, max_width, draw):
    words = str(text or "").split()
    lines = []
    line = ""

    for word in words:
        candidate = (line + " " + word).strip()

        if text_width(draw, candidate, font) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)

            if text_width(draw, word, font) > max_width:
                part = ""

                for char in word:
                    if text_width(draw, part + char, font) <= max_width:
                        part += char
                    else:
                        if part:
                            lines.append(part)
                        part = char

                line = part
            else:
                line = word

    if line:
        lines.append(line)

    return lines


def draw_wrapped(
    draw,
    text,
    position,
    font,
    fill,
    max_width,
    line_gap=7,
    max_lines=None
):
    x, y = position

    lines = wrap_text(
        text, font, max_width, draw
    )

    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]

        while last and text_width(
            draw, last + "...", font
        ) > max_width:
            last = last[:-1]

        lines[-1] = last.rstrip() + "..."

    bbox = draw.textbbox(
        (0, 0), "Ag", font=font
    )

    line_height = bbox[3] - bbox[1] + line_gap

    for line in lines:
        draw.text(
            (x, y),
            line,
            font=font,
            fill=fill
        )

        y += line_height

    return y


def card(
    draw,
    box,
    fill=PANEL,
    outline=BORDER,
    radius=18,
    width=2
):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width
    )


def botanical_illustration(
    draw,
    box,
    seed=1,
    label=None
):
    """Draw a decorative botanical sprig."""

    x1, y1, x2, y2 = box

    cx = (x1 + x2) // 2
    base_y = y2 - 18

    span = max(1, y2 - y1)
    stem_top = y1 + int(span * 0.12)

    draw.line(
        [
            (cx - 10, base_y),
            (cx, stem_top + 35),
            (cx + 5, stem_top)
        ],
        fill=GREEN,
        width=max(5, span // 65)
    )

    leaf_colors = [
        GREEN,
        (105, 133, 87),
        (127, 145, 99)
    ]

    directions = [-1, 1, -1, 1, -1, 1]

    for i, direction in enumerate(directions):

        ly = stem_top + int(
            span * (0.15 + i * 0.105)
        )

        lx = cx + direction * int(
            (x2 - x1) * 0.20
        )

        leaf_w = max(
            28, int((x2 - x1) * 0.22)
        )

        leaf_h = max(
            15, int(span * 0.075)
        )

        leaf_box = (
            lx - leaf_w if direction < 0 else lx,
            ly - leaf_h,
            lx if direction < 0 else lx + leaf_w,
            ly + leaf_h
        )

        draw.ellipse(
            leaf_box,
            fill=leaf_colors[
                (i + seed) % len(leaf_colors)
            ]
        )

        draw.line(
            [
                (cx, ly + 3),
                (
                    lx + (leaf_w if direction < 0 else 0),
                    ly
                )
            ],
            fill=(215, 222, 196),
            width=2
        )

    if seed % 3 == 0:

        for dx, dy in [
            (-18, 0),
            (0, -16),
            (18, 0),
            (0, 16)
        ]:

            draw.ellipse(
                (
                    cx + dx - 8,
                    stem_top + dy - 8,
                    cx + dx + 8,
                    stem_top + dy + 8
                ),
                fill=GOLD_LIGHT
            )

        draw.ellipse(
            (
                cx - 7,
                stem_top - 7,
                cx + 7,
                stem_top + 7
            ),
            fill=GOLD
        )

    if label:
        font = get_font(FONT_ITALIC, 19)

        draw.text(
            (cx, y2 - 2),
            label,
            font=font,
            fill=NAVY,
            anchor="ms"
        )


def draw_header(draw, brand, width=1080):

    center = width // 2

    draw.text(
        (center, 42),
        brand.get(
            "brand_name", "TIME TO HERBS"
        ).upper(),
        font=get_font(FONT_BOLD, 28),
        fill=NAVY,
        anchor="mm"
    )

    draw.line(
        (70, 76, width - 70, 76),
        fill=GOLD,
        width=3
    )

    draw.text(
        (center, 99),
        "BOTANICAL KNOWLEDGE • GROW • LEARN • ENJOY",
        font=get_font(FONT_REG, 16),
        fill=MUTED,
        anchor="mm"
    )


def draw_title(draw, title, topic, y, width=1080):

    center = width // 2

    chip_font = get_font(FONT_BOLD, 18)
    chip = topic.upper()[:38]

    chip_w = min(
        800,
        text_width(draw, chip, chip_font) + 42
    )

    draw.rounded_rectangle(
        (
            center - chip_w // 2,
            y,
            center + chip_w // 2,
            y + 38
        ),
        radius=18,
        fill=NAVY
    )

    draw.text(
        (center, y + 19),
        chip,
        font=chip_font,
        fill=(250, 232, 194),
        anchor="mm"
    )

    title_font = get_font(FONT_BOLD, 48)

    lines = wrap_text(
        title, title_font, 900, draw
    )

    while len(lines) > 2 and title_font.size > 34:

        title_font = get_font(
            FONT_BOLD,
            title_font.size - 3
        )

        lines = wrap_text(
            title, title_font, 900, draw
        )

    ty = y + 58

    for line in lines[:2]:

        draw.text(
            (center, ty),
            line,
            font=title_font,
            fill=NAVY,
            anchor="mm"
        )

        ty += title_font.size + 8

    return ty + 12


def draw_footer(draw, brand, y, width=1080):

    draw.line(
        (230, y, width - 230, y),
        fill=GOLD,
        width=2
    )

    draw.text(
        (width // 2, y + 27),
        brand.get(
            "watermark",
            "FOLLOW TIME TO HERBS"
        ).upper(),
        font=get_font(FONT_BOLD, 19),
        fill=NAVY,
        anchor="mm"
    )


# LAYOUT 1: EDITORIAL


def layout_editorial(draw, content, top, seed):

    fact = content.get("short_fact", "")
    points = content.get("key_points", [])[:3]
    how = content.get("how_to_use", "")
    safety = content.get("safety_note", "")

    hero_top = top

    card(
        draw,
        (55, hero_top, 1025, hero_top + 270),
        PANEL,
        radius=22
    )

    draw.text(
        (90, hero_top + 35),
        "PLANT SPOTLIGHT",
        font=get_font(FONT_BOLD, 21),
        fill=GOLD
    )

    draw_wrapped(
        draw,
        fact,
        (90, hero_top + 82),
        get_font(FONT_REG, 27),
        INK,
        535,
        8,
        4
    )

    botanical_illustration(
        draw,
        (
            690,
            hero_top + 28,
            965,
            hero_top + 245
        ),
        seed
    )

    y = hero_top + 295

    card(
        draw,
        (55, y, 525, y + 265),
        PALE_GREEN,
        radius=20
    )

    card(
        draw,
        (555, y, 1025, y + 265),
        PANEL_ALT,
        radius=20
    )

    draw.text(
        (85, y + 28),
        "BOTANICAL NOTES",
        font=get_font(FONT_BOLD, 22),
        fill=NAVY
    )

    py = y + 78

    for point in points[:3]:

        draw.ellipse(
            (85, py + 3, 105, py + 23),
            fill=GOLD
        )

        py = draw_wrapped(
            draw,
            point,
            (120, py),
            get_font(FONT_REG, 20),
            INK,
            365,
            4,
            3
        ) + 12

    draw.text(
        (585, y + 28),
        "EVERYDAY IDEA",
        font=get_font(FONT_BOLD, 22),
        fill=NAVY
    )

    draw_wrapped(
        draw,
        how,
        (585, y + 82),
        get_font(FONT_REG, 23),
        INK,
        390,
        7,
        5
    )

    draw.text(
        (585, y + 190),
        "USE WITH CARE",
        font=get_font(FONT_BOLD, 17),
        fill=GOLD
    )

    draw_wrapped(
        draw,
        safety,
        (585, y + 218),
        get_font(FONT_REG, 17),
        MUTED,
        390,
        3,
        2
    )

    return y + 295


# LAYOUT 2: FACT GRID


def layout_fact_grid(draw, content, top, seed):

    points = content.get("key_points", [])[:3]
    fact = content.get("short_fact", "")
    how = content.get("how_to_use", "")
    safety = content.get("safety_note", "")

    card(
        draw,
        (55, top, 1025, top + 190),
        PANEL,
        radius=20
    )

    draw.text(
        (90, top + 28),
        "A QUICK HERBAL FACT",
        font=get_font(FONT_BOLD, 22),
        fill=GOLD
    )

    draw_wrapped(
        draw,
        fact,
        (90, top + 75),
        get_font(FONT_REG, 28),
        INK,
        850,
        8,
        3
    )

    y = top + 215

    boxes = [
        (55, y, 525, y + 205),
        (555, y, 1025, y + 205),
        (55, y + 225, 525, y + 430)
    ]

    fills = [
        PALE_GREEN,
        PANEL_ALT,
        PANEL
    ]

    for i, (box, point, fill) in enumerate(
        zip(boxes, points, fills),
        start=1
    ):

        card(
            draw,
            box,
            fill,
            radius=18
        )

        x1, y1, x2, y2 = box

        draw.text(
            (x1 + 25, y1 + 25),
            f"FACT 0{i}",
            font=get_font(FONT_BOLD, 19),
            fill=GOLD
        )

        draw_wrapped(
            draw,
            point,
            (x1 + 25, y1 + 68),
            get_font(FONT_REG, 22),
            INK,
            x2 - x1 - 50,
            6,
            4
        )

    # Fourth panel: botanical illustration

    x1, y1, x2, y2 = (
        555,
        y + 225,
        1025,
        y + 430
    )

    card(
        draw,
        (x1, y1, x2, y2),
        PALE_GREEN,
        radius=18
    )

    botanical_illustration(
        draw,
        (
            x1 + 115,
            y1 + 15,
            x2 - 20,
            y2 - 10
        ),
        seed
    )

    y2 = y + 455

    card(
        draw,
        (55, y2, 1025, y2 + 145),
        NAVY,
        outline=NAVY,
        radius=18
    )

    draw.text(
        (85, y2 + 25),
        "TRY THIS",
        font=get_font(FONT_BOLD, 20),
        fill=(242, 211, 145)
    )

    draw_wrapped(
        draw,
        how,
        (85, y2 + 65),
        get_font(FONT_REG, 22),
        WHITE,
        880,
        5,
        2
    )

    draw.text(
        (65, y2 + 170),
        "SAFETY: " + safety[:150],
        font=get_font(FONT_REG, 16),
        fill=MUTED
    )

    return y2 + 205


# LAYOUT 3: BOTANICAL


def layout_botanical(draw, content, top, seed):

    fact = content.get("short_fact", "")
    parts = content.get("plant_parts", [])
    points = content.get("key_points", [])[:3]
    how = content.get("how_to_use", "")
    safety = content.get("safety_note", "")

    card(
        draw,
        (55, top, 1025, top + 330),
        PANEL,
        radius=22
    )

    botanical_illustration(
        draw,
        (
            360,
            top + 20,
            735,
            top + 310
        ),
        seed
    )

    draw.text(
        (100, top + 45),
        "GET TO KNOW",
        font=get_font(FONT_BOLD, 20),
        fill=GOLD
    )

    draw_wrapped(
        draw,
        fact,
        (100, top + 92),
        get_font(FONT_REG, 22),
        INK,
        255,
        6,
        7
    )

    labels = parts[:2] if parts else [
        "Leaves",
        "Stem"
    ]

    label_y = top + 275

    for label in labels:

        draw.rounded_rectangle(
            (
                755,
                label_y,
                990,
                label_y + 36
            ),
            radius=16,
            fill=PALE_GREEN,
            outline=GREEN,
            width=1
        )

        draw.text(
            (872, label_y + 18),
            str(label)[:25],
            font=get_font(FONT_BOLD, 16),
            fill=NAVY,
            anchor="mm"
        )

        label_y += 43

    y = top + 355

    card(
        draw,
        (55, y, 1025, y + 250),
        PANEL_ALT,
        radius=20
    )

    draw.text(
        (85, y + 25),
        "THREE THINGS TO REMEMBER",
        font=get_font(FONT_BOLD, 22),
        fill=NAVY
    )

    py = y + 75

    for index, point in enumerate(points, start=1):

        draw.text(
            (95, py),
            f"{index}.",
            font=get_font(FONT_BOLD, 22),
            fill=GOLD
        )

        py = draw_wrapped(
            draw,
            point,
            (140, py),
            get_font(FONT_REG, 21),
            INK,
            830,
            5,
            2
        ) + 12

    y += 275

    card(
        draw,
        (55, y, 1025, y + 145),
        PALE_GREEN,
        radius=18
    )

    draw.text(
        (85, y + 22),
        "IN THE KITCHEN OR GARDEN",
        font=get_font(FONT_BOLD, 19),
        fill=GREEN
    )

    draw_wrapped(
        draw,
        how,
        (85, y + 62),
        get_font(FONT_REG, 21),
        INK,
        875,
        5,
        2
    )

    draw.text(
        (65, y + 170),
        "USE WITH CARE: " + safety[:145],
        font=get_font(FONT_REG, 16),
        fill=MUTED
    )

    return y + 205


# MAIN RENDER FUNCTION


def render_image(content, output_path, story=False, seed=1):

    brand = load_brand()

    if isinstance(content, str):

        content = {
            "title": content,
            "topic": "Herbal Wisdom",
            "short_fact": content,
            "key_points": [
                "Learn to identify the plant correctly.",
                "Explore how it is grown and stored.",
                "Use botanical ingredients thoughtfully."
            ],
            "how_to_use": (
                "Choose fresh, food-grade herbs "
                "for suitable recipes."
            ),
            "safety_note": (
                "Herbs may not be suitable for everyone."
            )
        }

    title = str(
        content.get("title", "Herbal Wisdom")
    )

    topic = str(
        content.get("topic", "Herbal Education")
    )

    width = 1080
    height = 1920 if story else 1350

    img = Image.new(
        "RGB",
        (width, height),
        BG
    )

    draw = ImageDraw.Draw(img)

    # Editorial border

    draw.rectangle(
        (18, 18, width - 19, height - 19),
        outline=BORDER,
        width=3
    )

    draw_header(draw, brand, width)

    title_bottom = draw_title(
        draw,
        title,
        topic,
        125,
        width
    )

    # Three interchangeable layouts

    layout_number = int(seed) % 3

    top = max(
        270,
        title_bottom + 10
    )

    if layout_number == 0:

        content_bottom = layout_editorial(
            draw,
            content,
            top,
            seed
        )

    elif layout_number == 1:

        content_bottom = layout_fact_grid(
            draw,
            content,
            top,
            seed
        )

    else:

        content_bottom = layout_botanical(
            draw,
            content,
            top,
            seed
        )

    # Additional Story content

    if story:

        extra_top = min(
            height - 170,
            max(content_bottom + 20, 1550)
        )

        draw.line(
            (90, extra_top, width - 90, extra_top),
            fill=GOLD_LIGHT,
            width=2
        )

        draw.text(
            (width // 2, extra_top + 45),
            "GROW YOUR KNOWLEDGE",
            font=get_font(FONT_BOLD, 24),
            fill=NAVY,
            anchor="mm"
        )

        draw.text(
            (width // 2, extra_top + 88),
            "Follow Time To Herbs for more botanical learning.",
            font=get_font(FONT_REG, 20),
            fill=MUTED,
            anchor="mm"
        )

    footer_y = min(
        height - 75,
        max(content_bottom + 28, height - 100)
    )

    draw_footer(
        draw,
        brand,
        footer_y,
        width
    )

    # Save image

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    img.save(
        output_path,
        "JPEG",
        quality=94,
        optimize=True
    )

    return Path(output_path)
