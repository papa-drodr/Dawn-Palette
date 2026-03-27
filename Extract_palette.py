"""
Dawn Palette - 색상 팔레트 추출기
새벽 사진에서 K-means 클러스터링으로 대표 색상을 추출합니다.

사용법:
    python extract_palette.py                    # data/photos 전체 처리
    python extract_palette.py --image photo.jpg  # 단일 이미지 처리
    python extract_palette.py --colors 7         # 추출 색상 수 변경
"""

import argparse
import json
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    print(" OpenCV가 필요합니다: pip install opencv-python")
    exit(1)

try:
    from sklearn.cluster import KMeans
except ImportError:
    print(" scikit-learn이 필요합니다: pip install scikit-learn")
    exit(1)

# ------------------------
#  설정
# ------------------------
DATA_DIR = Path(__file__).parent / "data"
PHOTOS_DIR = DATA_DIR / "photos"
PALETTES_DIR = DATA_DIR / "palettes"

DEFAULT_N_COLORS = 6  # 추출할 대표 색상 수


def extract_sky_region(image):
    """
    이미지에서 하늘 영역을 추정하여 추출합니다.
    간단한 방법: 이미지 상단 60%를 하늘로 간주합니다.

    더 정교한 방법을 원하면 세그멘테이션 모델을 적용할 수 있습니다.
    """
    h, w = image.shape[:2]
    sky_ratio = 0.6
    sky_region = image[: int(h * sky_ratio), :]
    return sky_region


def extract_palette(image, n_colors=DEFAULT_N_COLORS):
    """
    K-means 클러스터링으로 이미지에서 대표 색상을 추출합니다.

    Args:
        image: BGR 이미지 (numpy array)
        n_colors: 추출할 색상 수

    Returns:
        list of dict: 각 색상의 RGB, HEX, 비율 정보
    """
    # 하늘 영역 추출
    sky = extract_sky_region(image)

    # 처리 속도를 위한 리사이즈
    sky_small = cv2.resize(sky, (200, 200))

    # BGR -> RGB
    sky_rgb = cv2.cvtColor(sky_small, cv2.COLOR_BGR2RGB)

    # 2D 배열로 변환 (픽셀 x 3채널)
    pixels = sky_rgb.reshape(-1, 3).astype(np.float32)

    # K-means 클러스터링
    kmeans = KMeans(
        n_clusters=n_colors,
        n_init=10,
        max_iter=200,
        random_state=42,
    )
    kmeans.fit(pixels)

    # 각 클러스터링 비율 계산
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    percentages = counts / counts.sum()

    colors = []
    for center, pct in zip(kmeans.cluster_centers_, percentages):
        r, g, b = int(center[0]), int(center[1]), int(center[2])
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        # HSV 값도 계산
        hsv_pixel = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]

        colors.append(
            {
                "rgb": [r, g, b],
                "hex": hex_color,
                "hsv": [int(hsv_pixel[0]), int(hsv_pixel[1]), int(hsv_pixel[2])],
                "percentage": round(float(pct) * 100, 1),
            }
        )

    # 비율 기준 내림차순 정렬
    colors.sort(key=lambda c: c["percentage"], reverse=True)

    return colors


def create_palette_image(colors, width=600, height=100):
    """
    추출된 색상으로 팔레트 이미지를 생성합니다.
    각 색상의 비율에 따라 너비가 결정됩니다.
    """
    palette = np.zeros((height, width, 3), dtype=np.uint8)

    x_start = 0
    for color in colors:
        x_end = x_start + int(width * color["percentage"] / 100)
        r, g, b = color["rgb"]
        palette[:, x_start:x_end] = [b, g, r]
        x_start = x_end

    if x_start < width:
        r, g, b = colors[-1]["rgb"]
        palette[:, x_start:] = [b, g, r]

    return palette


def classify_dawn_mood(colors):
    """
    색상 팔레트를 기반으로 새벽의 분위기를 분류합니다.

    Returns:
        dict: mood(분위기), warmth(따뜻함 점수), description(설명)
    """
    avg_hsv = np.mean([c["hsv"] for c in colors], axis=0)
    avg_hue = avg_hsv[0]
    avg_sat = avg_hsv[1]
    avg_val = avg_hsv[2]

    # 따뜻함 점수 계산 (0~100)
    # 빨강/주황/노랑 계열이면 따뜻함, 파랑/보라 계열이면 차가움
    warm_hues = sum(
        c["percentage"]
        for c in colors
        if c["hsv"][0] < 30 or c["hsv"][0] > 150  # 빨강~노랑 or 보라~빨강
    )

    # 분위기 분류
    if avg_val < 80:
        mood = "deep_night"
        description = "아직 깊은 밤, 새벽을 기다리는 고요한 어둠"
    elif avg_val < 130 and avg_sat < 80:
        mood = "blue_hour"
        description = "파란 시간, 밤과 낮 사이의 몽환적인 순간"
    elif avg_hue < 15 or avg_hue > 160:
        mood = "burning_dawn"
        description = "타오르는 새벽, 하늘을 물들이는 붉은 빛"
    elif 15 <= avg_hue < 30:
        mood = "golden_dawn"
        description = "황금빛 새벽, 따스한 빛이 번져오는 순간"
    elif 80 <= avg_hue < 130:
        mood = "cool_dawn"
        description = "차가운 새벽, 맑고 푸른 여명"
    elif 130 <= avg_hue < 160:
        mood = "purple_dawn"
        description = "보랏빛 새벽, 신비로운 여명의 시작"
    else:
        mood = "pastel_dawn"
        description = "파스텔 새벽, 부드러운 색들이 어우러진 하늘"

    return {
        "mood": mood,
        "description": description,
        "warmth": round(warm_hues, 1),
        "avg_brightness": round(float(avg_val), 1),
        "avg_saturation": round(float(avg_sat), 1),
    }


def process_single(image_path, n_colors=DEFAULT_N_COLORS, save=True):
    """단일 이미지를 처리합니다."""
    image_path = Path(image_path)
    print(f"\n 처리 중: {image_path.name}")

    image = cv2.imread(str(image_path))
    if image is None:
        print(" 이미지를 읽을 수 없습니다.")
        return None

    # 색상 추출
    colors = extract_palette(image, n_colors)
    mood = classify_dawn_mood(colors)

    # 결과 출력
    print(f"   분위기: {mood['description']}")
    print(f"   따뜻함: {mood['warmth']}%")
    print("   대표 색상:")
    for c in colors:
        bar = "█" * int(c["percentage"] / 2)
        print(f"      {c['hex']} {bar} {c['percentage']}%")

    if save:
        PALETTES_DIR.mkdir(parents=True, exist_ok=True)
        stem = image_path.stem

        # 팔레트 이미지 저장
        palette_img = create_palette_image(colors)
        palette_path = PALETTES_DIR / f"{stem}_palette.png"
        cv2.imwrite(str(palette_path), palette_img)

        # json 저장
        result = {
            "source_image": image_path.name,
            "colors": colors,
            "mood": mood,
            "n_colors": n_colors,
        }
        json_path = PALETTES_DIR / f"{stem}_palette.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n 팔레트 이미지: {palette_img}")
        print(f" JSON 데이터: {json_path}")

    return {"colors": colors, "mood": mood}


def process_all(n_colors=DEFAULT_N_COLORS):
    """data/photos 폴더의 모든 이미지를 처리합니다."""
    if not PHOTOS_DIR.exists():
        print(" data/photos 폴더가 없습니다.")
        print(" 먼저 collect_dawn.py를 실행하여 사진을 수집하세요.")
        return

    images = list(PHOTOS_DIR.glob("*.jpg")) + list(PHOTOS_DIR.glob("*.png"))
    if not images:
        print(" 처리할 이미지가 없습니다.")
        return

    results = []
    for img_path in sorted(images):
        result = process_single(img_path, n_colors)
        if result:
            results.append(result)
        print()

    # 전체 요약
    if results:
        print("\n" + "=" * 50)
        print(f" 분석 완료! 총 {len(results)}장")
        print(f" 팔레트 저장: {PALETTES_DIR}")

        # 분위기 통계
        moods = [r["mood"]["mood"] for r in results]
        unique_moods = set(moods)
        print("\n    발견된 새벽의 종류:")
        for m in unique_moods:
            count = moods.count(m)
            print(f"      {m}: {count}장")


def main():
    parser = argparse.ArgumentParser(description="Dawn Palette - 색상 팔레트 추출기")
    parser.add_argument("--image", type=str, help="단일 이미지 경로")
    parser.add_argument(
        "--colors", type=int, default=DEFAULT_N_COLORS, help="추출할 색상 수"
    )
    args = parser.parse_args()

    if args.image:
        process_single(args.image, args.colors)
    else:
        process_all(args.colors)


if __name__ == "__main__":
    main()
