"""
Dawn Palette - 새벽 하늘 사진 수집기
Unsplash API를 사용하여 전 세계의 새벽 하늘 사진을 수집합니다.

사용법:
    1. .env 파일에 UNSPLASH_ACCESS_KEY를 설정하세요.
    2. python collect_dawn.py 실행

옵션:
    --query    검색어 (기본값: "dawn sky")
    --count    수집할 사진 수 (기본값: 10, 최대 30)
    --page     페이지 번호 (기본값: 1)
"""

import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# ------------------------
# 설정
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
    """API 키를 .env 파일 또는 환경변수에서 가져옵니다."""
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
        print("❌ API 키가 설정되지 않았습니다!")
        print()
        print("아래 방법 중 하나로 설정해주세요:")
        print()
        print("방법 1) .env 파일 생성:")
        print("  UNSPLASH_ACCESS_KEY=your_key_here")
        print()
        print("방법 2) 환경변수 설정:")
        print("  export UNSPLASH_ACCESS_KEY=your_key_here")
        print("=" * 50)
        return None
    return key


def search_photos(api_key, query="dawn sky", page=1, per_page=10):
    """Unsplash API로 사진을 검색합니다."""
    params = urllib.parse.urlencode(
        {
            "query": query,
            "page": page,
            "per_page": per_page,
            "orientation": "landscape",  # 풍경 사진 위주
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
        print(f"❌ API 요청 실패: {e.code} {e.reason}")
        if e.code == 401:
            print("   → API 키를 확인해주세요.")
        elif e.code == 403:
            print("   → 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
        return None


def download_photo(url, save_path):
    """사진을 다운로드합니다."""
    try:
        urllib.request.urlretrieve(url, save_path)
        return True
    except Exception as e:
        print(f"   ⚠️  다운로드 실패: {e}")
        return False


def collect(api_key, query="dawn sky", count=10, page=1):
    """새벽 사진을 수집하고 메타데이터를 저장합니다."""

    # make dir
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n🌅 '{query}' 검색 중... (page {page})")
    print("-" * 40)

    result = search_photos(api_key, query=query, page=page, per_page=count)

    if not result:
        return []

    photos = result.get("results", [])
    total = result.get("total", 0)
    print(f"📸 총 {total}개 중 {len(photos)}개 가져옴\n")

    collected = []
    for i, photo in enumerate(photos, 1):
        photo_id = photo["id"]
        description = (
            photo.get("description") or photo.get("alt_description") or "untitled"
        )
        photographer = photo["user"]["name"]
        created_at = photo["created_at"]
        color = photo.get("color", "#000000")

        # 다운로드 URL (regular size: 1080px)
        download_url = photo["urls"]["regular"]

        # 파일명: 날짜_id
        date_str = created_at[:10]
        filename = f"{date_str}_{photo_id}.jpg"
        save_path = PHOTOS_DIR / filename

        print(f"  [{i}/{len(photos)}] {description[:40]}...")
        print(f"           📷 {photographer} | 🎨 {color}")

        # 사진 다운로드
        if save_path.exists():
            print("           ⏭️  이미 다운로드됨")
        else:
            success = download_photo(download_url, save_path)
            if success:
                print("           ✅ 저장 완료")

        # metadata save
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

    print(f"✨ 수집 완료! {len(collected)}장 저장됨")
    print(f"   📁 사진: {PHOTOS_DIR}")
    print(f"   📁 메타: {META_DIR}")

    return collected


def main():
    parser = argparse.ArgumentParser(
        description="🌅 Dawn Palette - 새벽 하늘 사진 수집기"
    )
    parser.add_argument("--query", type=str, default="dawn sky", help="검색어")
    parser.add_argument(
        "--count", type=int, default=10, help="수집할 사진 수 (최대 30)"
    )
    parser.add_argument("--page", type=int, default=1, help="페이지 번호")
    parser.add_argument("--all", action="store_true", help="모든 기본 검색어로 수집")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        return

    if args.all:
        # 모든 기본 검색어로 수집
        for query in SEARCH_QUERIES:
            collect(api_key, query=query, count=args.count, page=args.page)
    else:
        collect(api_key, query=args.query, count=args.count, page=args.page)


if __name__ == "__main__":
    main()
