"""
Dawn Palette - GitHub Pages Gallery Generator
Generates a deployable web gallery from collected dawn photos and palette data.

Usage:
    python generate_gallery.py
"""

import json
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PHOTOS_DIR = DATA_DIR / "photos"
PALETTES_DIR = DATA_DIR / "palettes"
DOCS_DIR = Path(__file__).parent / "docs"
DOCS_PHOTOS_DIR = DOCS_DIR / "photos"

MOOD_EMOJI = {
    "deep_night": "🌑",
    "blue_hour": "💙",
    "burning_dawn": "🔥",
    "golden_dawn": "🌟",
    "cool_dawn": "🧊",
    "purple_dawn": "💜",
    "pastel_dawn": "🎨",
}

MOOD_LABEL = {
    "deep_night": "deep night",
    "blue_hour": "blue hour",
    "burning_dawn": "burning dawn",
    "golden_dawn": "golden dawn",
    "cool_dawn": "cool dawn",
    "purple_dawn": "purple dawn",
    "pastel_dawn": "pastel dawn",
}


def load_palette_data():
    """Load palette JSON files."""
    if not PALETTES_DIR.exists():
        print("data/palettes folder not found. Run extract_palette.py first.")
        return []

    json_files = sorted(PALETTES_DIR.glob("*_palette.json"))
    if not json_files:
        print("No palette data found.")
        return []

    entries = []
    for json_path in json_files:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        photo_name = data.get("source_image", "")
        photo_path = PHOTOS_DIR / photo_name
        entries.append(
            {
                "photo_name": photo_name,
                "photo_exists": photo_path.exists(),
                "colors": data.get("colors", []),
                "mood": data.get("mood", {}),
            }
        )
    return entries


def copy_photos(entries):
    """Copy photos to docs/photos/ for deployment."""
    DOCS_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    for entry in entries:
        if not entry["photo_exists"]:
            continue
        src = PHOTOS_DIR / entry["photo_name"]
        dst = DOCS_PHOTOS_DIR / entry["photo_name"]
        if not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
    return copied


def generate_html(entries):
    """Generate index.html."""

    # Mood statistics
    mood_counts = {}
    for entry in entries:
        mood_key = entry["mood"].get("mood", "unknown")
        mood_counts[mood_key] = mood_counts.get(mood_key, 0) + 1

    stats_parts = []
    for mood_key, count in sorted(mood_counts.items(), key=lambda x: -x[1]):
        emoji = MOOD_EMOJI.get(mood_key, "✨")
        label = MOOD_LABEL.get(mood_key, mood_key)
        stats_parts.append(
            f'            <div class="stat-item" data-mood="{mood_key}" onclick="filterMood(\'{mood_key}\')">\n'
            f'                <span class="stat-emoji">{emoji}</span>\n'
            f'                <span class="stat-label">{label}</span>\n'
            f'                <span class="stat-count">{count}</span>\n'
            f"            </div>"
        )
    stats_html = "\n".join(stats_parts)

    # Cards
    card_parts = []
    for i, entry in enumerate(entries):
        colors = entry["colors"]
        mood = entry["mood"]
        mood_key = mood.get("mood", "unknown")
        emoji = MOOD_EMOJI.get(mood_key, "✨")

        swatch_parts = []
        for c in colors:
            hex_color = c["hex"]
            pct = c["percentage"]
            swatch_parts.append(
                f'                <div class="swatch" style="background:{hex_color}; flex-grow:{pct};" '
                f'title="{hex_color} ({pct}%)">\n'
                f'                    <span class="swatch-label">{hex_color}</span>\n'
                f"                </div>"
            )
        swatches_html = "\n".join(swatch_parts)

        if entry["photo_exists"]:
            photo_html = f'<img src="photos/{entry["photo_name"]}" alt="dawn" class="card-photo" loading="lazy">'
        else:
            photo_html = '<div class="card-photo no-photo">No photo</div>'

        card_parts.append(
            f'        <article class="card" data-mood="{mood_key}" style="animation-delay: {i * 0.08}s">\n'
            f'            <div class="card-image-wrap">\n'
            f"                {photo_html}\n"
            f'                <div class="card-mood-badge">{emoji}</div>\n'
            f"            </div>\n"
            f'            <div class="card-palette">\n'
            f"{swatches_html}\n"
            f"            </div>\n"
            f'            <div class="card-info">\n'
            f'                <p class="card-mood-text">{mood.get("description", "")}</p>\n'
            f'                <div class="card-meta">\n'
            f'                    <span class="meta-item">따뜻함 {mood.get("warmth", 0)}%</span>\n'
            f'                    <span class="meta-item">밝기 {mood.get("avg_brightness", 0)}</span>\n'
            f"                </div>\n"
            f"            </div>\n"
            f"        </article>"
        )
    cards_html = "\n".join(card_parts)

    # Assemble HTML
    lines = [
        "<!DOCTYPE html>",
        '<html lang="ko">',
        "<head>",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "    <title>Dawn Palette</title>",
        '    <link rel="stylesheet" href="style.css">',
        "</head>",
        "<body>",
        "    <header>",
        '        <h1 class="title">Dawn Palette</h1>',
        '        <p class="subtitle">collected colors of dawn</p>',
        '        <div class="divider"></div>',
        f'        <p class="collection-count">{len(entries)} dawns collected</p>',
        "    </header>",
        "",
        '    <section class="upload-section" id="upload-section">',
        '        <div class="upload-area" id="upload-area">',
        '            <div class="upload-icon">🌅</div>',
        '            <p class="upload-text">새벽 사진을 여기에 드래그하거나</p>',
        '            <label class="upload-button" for="file-input">파일 선택</label>',
        '            <input type="file" id="file-input" accept="image/*" hidden>',
        '            <p class="upload-hint">JPG, PNG 지원</p>',
        "        </div>",
        '        <div class="upload-result" id="upload-result" style="display:none;">',
        '            <div class="upload-result-image">',
        '                <img id="upload-preview" alt="uploaded dawn">',
        "            </div>",
        '            <div class="upload-result-palette" id="upload-palette"></div>',
        '            <div class="upload-result-info" id="upload-info"></div>',
        '            <button class="upload-reset" onclick="resetUpload()">다른 사진 분석하기</button>',
        "        </div>",
        "    </section>",
        "",
        '    <section class="stats">',
        stats_html,
        "    </section>",
        "",
        '    <main class="gallery">',
        cards_html,
        "    </main>",
        "",
        "    <footer>",
        '        <p class="footer-text">for the dawn I dearly miss</p>',
        "    </footer>",
        "",
        '    <canvas id="palette-canvas" style="display:none;"></canvas>',
        '    <script src="script.js"></script>',
        "</body>",
        "</html>",
    ]

    return "\n".join(lines)


def main():
    print("\nDawn Palette Gallery - Generating...")
    print("=" * 50)

    entries = load_palette_data()
    if not entries:
        return

    print(f"Loaded {len(entries)} dawn entries")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    copied = copy_photos(entries)
    print(f"Copied {copied} new photos (docs/photos/)")

    html = generate_html(entries)
    html_path = DOCS_DIR / "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html generated")

    css_path = DOCS_DIR / "style.css"
    if css_path.exists():
        print("style.css already exists (not overwritten)")
    else:
        print("style.css not found. Please add it to docs/")

    js_path = DOCS_DIR / "script.js"
    if js_path.exists():
        print("script.js already exists (not overwritten)")
    else:
        print("script.js not found. Please add it to docs/")

    print(f"\nGallery generated!")
    print(f"{DOCS_DIR.resolve()}")


if __name__ == "__main__":
    main()
