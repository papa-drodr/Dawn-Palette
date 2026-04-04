"""
Dawn Palette - Dawn Sky Photo Collector
Collects dawn sky photos from around the world using the Unsplash API.

Usage:
    1. Set UNSPLASH_ACCESS_KEY in the .env file.
    2. Run: python collect_dawn.py

Options:
    --query    Search query (default: "dawn sky")
    --count    Number of photos to collect (default: 10, max: 30)
    --page     Page number (default: 1)
"""

import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# ------------------------
# Configuration
# ------------------------

DATA_DIR = Path(__file__).parent / "data"
PHOTOS_DIR = DATA_DIR / "photos"
META_DIR = DATA_DIR / "metadata"

SEARCH_QUERIES = [
    "dawn sky",
    "sunrise sky colors",
    "early morning sky",
    "twilight dawn",
    "새벽 하늘",
]


def load_api_key():
    """Load API key from .env file or environment variable."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("UNSPLASH_ACCESS_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip('"')

    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        print("=" * 50)
        print("API key is not set!")
        print()
        print("Set it using one of the following methods:")
        print()
        print("Method 1) Create a .env file:")
        print("  UNSPLASH_ACCESS_KEY=your_key_here")
        print()
        print("Method 2) Set an environment variable:")
        print("  export UNSPLASH_ACCESS_KEY=your_key_here")
        print("=" * 50)
        return None
    return key


def search_photos(api_key, query="dawn sky", page=1, per_page=10):
    """Search photos using the Unsplash API."""
    params = urllib.parse.urlencode(
        {
            "query": query,
            "page": page,
            "per_page": per_page,
            "orientation": "landscape",
            "order_by": "relevant",
        }
    )

    url = f"https://api.unsplash.com/search/photos?{params}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Client-ID {api_key}")
    req.add_header("Accept-Version", "v1")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        print(f"API request failed: {e.code} {e.reason}")
        if e.code == 401:
            print("→ Please check your API key.")
        elif e.code == 403:
            print("→ Rate limit exceeded. Please try again later.")
        return None


def download_photo(url, save_path):
    """Download a photo."""
    try:
        urllib.request.urlretrieve(url, save_path)
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def collect(api_key, query="dawn sky", count=10, page=1):
    """Collect dawn photos and save metadata."""

    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n Searching '{query}'... (page {page})")
    print("-" * 40)

    result = search_photos(api_key, query=query, page=page, per_page=count)

    if not result:
        return []

    photos = result.get("results", [])
    total = result.get("total", 0)
    print(f"📸 Fetched {len(photos)} of {total} total\n")

    collected = []
    for i, photo in enumerate(photos, 1):
        photo_id = photo["id"]
        description = (
            photo.get("description") or photo.get("alt_description") or "untitled"
        )
        photographer = photo["user"]["name"]
        created_at = photo["created_at"]
        color = photo.get("color", "#000000")

        # Download URL (regular size: 1080px)
        download_url = photo["urls"]["regular"]

        # Filename: date_id
        date_str = created_at[:10]
        filename = f"{date_str}_{photo_id}.jpg"
        save_path = PHOTOS_DIR / filename

        print(f"[{i}/{len(photos)}] {description[:40]}...")
        print(f"{photographer} | {color}")

        # Download photo
        if save_path.exists():
            print("Already downloaded")
        else:
            success = download_photo(download_url, save_path)
            if success:
                print("Saved")

        # Save metadata
        metadata = {
            "id": photo_id,
            "description": description,
            "photographer": photographer,
            "photographer_url": photo["user"]["links"]["html"],
            "created_at": created_at,
            "dominant_color": color,
            "width": photo["width"],
            "height": photo["height"],
            "download_url": download_url,
            "unsplash_url": photo["links"]["html"],
            "collected_at": datetime.now().isoformat(),
            "query": query,
        }

        meta_path = META_DIR / f"{date_str}_{photo_id}.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        collected.append(metadata)
        print()

    print(f"Collection complete! {len(collected)} photos saved")
    print(f"Photos: {PHOTOS_DIR}")
    print(f"Metadata: {META_DIR}")

    return collected


def main():
    parser = argparse.ArgumentParser(
        description="Dawn Palette - Dawn Sky Photo Collector"
    )
    parser.add_argument("--query", type=str, default="dawn sky", help="Search query")
    parser.add_argument(
        "--count", type=int, default=10, help="Number of photos to collect (max 30)"
    )
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument(
        "--all", action="store_true", help="Collect with all default queries"
    )
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        return

    if args.all:
        for query in SEARCH_QUERIES:
            collect(api_key, query=query, count=args.count, page=args.page)
    else:
        collect(api_key, query=args.query, count=args.count, page=args.page)


if __name__ == "__main__":
    main()
