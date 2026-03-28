# 🌅 Dawn Palette

> Collecting the colors of dawn skies from around the world, recording what each dawn looked like.

A project born from missing the dawn.

## Preview

🔗 **[View Dawn Palette Gallery](https://papa-drodr.github.io/Dawn-Palette/)**

Extracts dominant colors from dawn photos, automatically classifies the mood, and displays them in a web gallery.

- 🔥 **burning dawn** — A blazing dawn, the sky painted in red
- 💙 **blue hour** — The blue hour, a dreamlike moment between night and day
- 🌟 **golden dawn** — A golden dawn, warm light spreading across the sky
- 💜 **purple dawn** — A violet dawn, the start of a mystical twilight
- 🧊 **cool dawn** — A cool dawn, clear and blue daybreak
- 🌑 **deep night** — Still deep night, a quiet darkness waiting for dawn
- 🎨 **pastel dawn** — A pastel dawn, soft colors blending across the sky

## Project Structure

```
dawn_palette/
├── collect_dawn.py        # Collect dawn photos via Unsplash API
├── extract_palette.py     # Extract color palettes with OpenCV + K-means
├── generate_gallery.py    # Generate web gallery (writes index.html)
├── requirements.txt
├── .env                   # API key (not included in git)
├── .env.example
├── data/
│   ├── photos/            # Collected dawn photos
│   ├── metadata/          # Photo metadata (JSON)
│   └── palettes/          # Extracted palette images + JSON
└── docs/                  # GitHub Pages deployment folder
    ├── index.html         # Gallery page (auto-generated)
    ├── style.css          # Stylesheet
    └── photos/            # Copies of photos for the web
```

---

## Getting Started

### 1. Install

```bash
pip install -r requirements.txt
```

---

### 2. Get an Unsplash API Key

1. Sign up at [unsplash.com/join](https://unsplash.com/join)
2. Go to [unsplash.com/developers](https://unsplash.com/developers) → **Your apps** → **New Application**
3. Accept the terms, enter app name (`Dawn Palette`) and description
4. Copy the **Access Key** from your app page

---

### 3. Set Up the API Key

```bash
cp .env.example .env
```

Open `.env` and paste your key.

```
UNSPLASH_ACCESS_KEY=your_access_key_here
```

---

## Usage

### Step 1. Collect Dawn Photos

```bash
# Collect 10 photos with default query
python collect_dawn.py

# Collect with a specific query
python collect_dawn.py --query "sunrise ocean" --count 20

# Collect next page
python collect_dawn.py --query "dawn sky" --page 2

# Collect with all default queries at once
python collect_dawn.py --all
```

Default queries: `dawn sky`, `sunrise sky colors`, `early morning sky`, `twilight dawn`, `새벽 하늘`

### Step 2. Extract Color Palettes

```bash
# Analyze all collected photos
python extract_palette.py

# Analyze a single image
python extract_palette.py --image data/photos/photo.jpg

# Change the number of colors to extract (default: 6)
python extract_palette.py --colors 8
```

### Step 3. Generate Web Gallery

```bash
python generate_gallery.py
```

This generates `index.html` in the `docs/` folder and copies photos to `docs/photos/`.

Open `docs/index.html` in a browser to preview locally.

---

## Tech Stack

- **Python 3.10+**
- **OpenCV** — Image processing, sky region extraction
- **scikit-learn** — K-means clustering for dominant color extraction
- **Unsplash API** — Dawn photo collection
- **GitHub Pages** — Gallery hosting

---

## Notes

- The Unsplash free plan (Demo) is limited to 50 requests per hour.
- All collected photos are copyrighted by their respective photographers and are subject to the [Unsplash License](https://unsplash.com/license).

---

## .gitignore

```
.env
data/
__pycache__/
```

The `data/` folder is excluded from git due to its size. Photos needed for the web gallery are copied to `docs/photos/`, so only `docs/` needs to be pushed.

## License

MIT License
