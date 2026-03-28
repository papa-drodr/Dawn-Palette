"""
Dawn Palette - GitHub Pages 갤러리 생성기
수집한 새벽 사진과 팔레트 데이터를 docs/ 폴더에 배포 가능한 형태로 생성합니다.

사용법:
    python generate_gallery.py

생성 결과:
    docs/
    ├── index.html
    ├── style.css      (이미 존재하면 건드리지 않음)
    └── photos/        (사진 복사)
"""

import json
import shutil
from pathlib import Path

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────

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
    """팔레트 JSON 파일들을 읽어옵니다."""
    if not PALETTES_DIR.exists():
        print("❌ data/palettes 폴더가 없습니다.")
        print("   먼저 extract_palette.py를 실행하세요.")
        return []

    json_files = sorted(PALETTES_DIR.glob("*_palette.json"))
    if not json_files:
        print("❌ 팔레트 데이터가 없습니다.")
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
    """사진을 docs/photos/로 복사합니다."""
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
    """index.html을 생성합니다."""

    # 분위기별 통계
    mood_counts = {}
    for entry in entries:
        mood_key = entry["mood"].get("mood", "unknown")
        mood_counts[mood_key] = mood_counts.get(mood_key, 0) + 1

    # 통계 바
    stats_html = ""
    for mood_key, count in sorted(mood_counts.items(), key=lambda x: -x[1]):
        emoji = MOOD_EMOJI.get(mood_key, "✨")
        label = MOOD_LABEL.get(mood_key, mood_key)
        stats_html += f"""
            <div class="stat-item" data-mood="{mood_key}" onclick="filterMood('{mood_key}')">
                <span class="stat-emoji">{emoji}</span>
                <span class="stat-label">{label}</span>
                <span class="stat-count">{count}</span>
            </div>"""

    # 카드
    cards_html = ""
    for i, entry in enumerate(entries):
        colors = entry["colors"]
        mood = entry["mood"]
        mood_key = mood.get("mood", "unknown")
        emoji = MOOD_EMOJI.get(mood_key, "✨")

        swatches = ""
        for c in colors:
            hex_color = c["hex"]
            pct = c["percentage"]
            swatches += f"""
                <div class="swatch" style="background:{hex_color}; flex-grow:{pct};"
                     title="{hex_color} ({pct}%)">
                    <span class="swatch-label">{hex_color}</span>
                </div>"""

        if entry["photo_exists"]:
            photo_html = f'<img src="photos/{entry["photo_name"]}" alt="dawn" class="card-photo" loading="lazy">'
        else:
            photo_html = '<div class="card-photo no-photo">사진 없음</div>'

        cards_html += f"""
        <article class="card" data-mood="{mood_key}" style="animation-delay: {i * 0.08}s">
            <div class="card-image-wrap">
                {photo_html}
                <div class="card-mood-badge">{emoji}</div>
            </div>
            <div class="card-palette">
                {swatches}
            </div>
            <div class="card-info">
                <p class="card-mood-text">{mood.get('description', '')}</p>
                <div class="card-meta">
                    <span class="meta-item">따뜻함 {mood.get('warmth', 0)}%</span>
                    <span class="meta-item">밝기 {mood.get('avg_brightness', 0)}</span>
                </div>
            </div>
        </article>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dawn Palette</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1 class="title">Dawn Palette</h1>
        <p class="subtitle">collected colors of dawn</p>
        <div class="divider"></div>
        <p class="collection-count">{len(entries)} dawns collected</p>
    </header>

    <section class="stats">
        {stats_html}
    </section>

    <main class="gallery">
        {cards_html}
    </main>

    <footer>
        <p class="footer-text">for the dawn I dearly miss</p>
    </footer>

    <script>
        let activeFilter = null;

        function filterMood(mood) {{
            const cards = document.querySelectorAll('.card');
            const stats = document.querySelectorAll('.stat-item');

            if (activeFilter === mood) {{
                activeFilter = null;
                cards.forEach(c => c.classList.remove('hidden'));
                stats.forEach(s => s.classList.remove('active'));
                return;
            }}

            activeFilter = mood;
            cards.forEach(c => {{
                if (c.dataset.mood === mood) {{
                    c.classList.remove('hidden');
                }} else {{
                    c.classList.add('hidden');
                }}
            }});
            stats.forEach(s => {{
                s.classList.toggle('active', s.dataset.mood === mood);
            }});
        }}
    </script>
</body>
</html>"""

    return html


def main():
    print("\n Dawn Palette Gallery 생성 중...")
    print("=" * 50)

    entries = load_palette_data()
    if not entries:
        return

    print(f" {len(entries)}개의 새벽 데이터 로드 완료")

    # docs 폴더 생성
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 사진 복사
    copied = copy_photos(entries)
    print(f" 사진 {copied}장 새로 복사 (docs/photos/)")

    # HTML 생성
    html = generate_html(entries)
    html_path = DOCS_DIR / "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(" index.html 생성 완료")

    # style.css 확인
    css_path = DOCS_DIR / "style.css"
    if css_path.exists():
        print(" style.css 이미 존재 (덮어쓰지 않음)")
    else:
        print("  style.css가 없습니다. docs/ 폴더에 추가해주세요.")

    print("\n 갤러리 생성 완료!")
    print(f"    {DOCS_DIR.resolve()}")


if __name__ == "__main__":
    main()
