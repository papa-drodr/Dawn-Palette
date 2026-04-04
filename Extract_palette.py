"""
Dawn Palette - Color Palette Extractor
Extracts dominant colors from dawn photos using K-means clustering.

Usage:
    python extract_palette.py                    # Process all in data/photos
    python extract_palette.py --image photo.jpg  # Process a single image
    python extract_palette.py --colors 7         # Change number of colors
"""

import argparse
import json
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    print("OpenCV is required: pip install opencv-python")
    exit(1)

try:
    from sklearn.cluster import KMeans
except ImportError:
    print("scikit-learn is required: pip install scikit-learn")
    exit(1)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

DATA_DIR = Path(__file__).parent / "data"
PHOTOS_DIR = DATA_DIR / "photos"
PALETTES_DIR = DATA_DIR / "palettes"

DEFAULT_N_COLORS = 6  # Number of dominant colors to extract


def extract_sky_region(image):
    """
    Estimate and extract the sky region from the image.
    Simple approach: treat the top 60% as sky.

    For more precision, a segmentation model can be applied.
    """
    h, w = image.shape[:2]
    sky_ratio = 0.6  # Top 60%
    sky_region = image[: int(h * sky_ratio), :]
    return sky_region


def extract_palette(image, n_colors=DEFAULT_N_COLORS):
    """
    Extract dominant colors from an image using K-means clustering.

    Args:
        image: BGR image (numpy array)
        n_colors: Number of colors to extract

    Returns:
        list of dict: RGB, HEX, and percentage info for each color
    """
    # Extract sky region
    sky = extract_sky_region(image)

    # Resize for faster processing
    sky_small = cv2.resize(sky, (200, 200))

    # BGR → RGB conversion
    sky_rgb = cv2.cvtColor(sky_small, cv2.COLOR_BGR2RGB)

    # Reshape to 2D array (pixels x 3 channels)
    pixels = sky_rgb.reshape(-1, 3).astype(np.float32)

    # K-means clustering
    kmeans = KMeans(
        n_clusters=n_colors,
        n_init=10,
        max_iter=200,
        random_state=42,
    )
    kmeans.fit(pixels)

    # Calculate percentage for each cluster
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    percentages = counts / counts.sum()

    # Compile color information
    colors = []
    for center, pct in zip(kmeans.cluster_centers_, percentages):
        r, g, b = int(center[0]), int(center[1]), int(center[2])
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        # Compute HSV values (useful for color analysis)
        hsv_pixel = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]

        colors.append(
            {
                "rgb": [r, g, b],
                "hex": hex_color,
                "hsv": [int(hsv_pixel[0]), int(hsv_pixel[1]), int(hsv_pixel[2])],
                "percentage": round(float(pct) * 100, 1),
            }
        )

    # Sort by percentage descending
    colors.sort(key=lambda c: c["percentage"], reverse=True)

    return colors


def create_palette_image(colors, width=600, height=100):
    """
    Generate a palette image from extracted colors.
    Each color's width is proportional to its percentage.
    """
    palette = np.zeros((height, width, 3), dtype=np.uint8)

    x_start = 0
    for color in colors:
        x_end = x_start + int(width * color["percentage"] / 100)
        r, g, b = color["rgb"]
        # OpenCV uses BGR
        palette[:, x_start:x_end] = [b, g, r]
        x_start = x_end

    # Fill remaining pixels from rounding errors
    if x_start < width:
        r, g, b = colors[-1]["rgb"]
        palette[:, x_start:] = [b, g, r]

    return palette


def classify_dawn_mood(colors):
    """
    Classify the mood of a dawn based on its color palette.

    Returns:
        dict: mood, warmth score, and description
    """
    avg_hsv = np.mean([c["hsv"] for c in colors], axis=0)
    avg_hue = avg_hsv[0]
    avg_sat = avg_hsv[1]
    avg_val = avg_hsv[2]

    # Warmth score (0~100)
    # Red/orange/yellow = warm, blue/purple = cool
    warm_hues = sum(
        c["percentage"]
        for c in colors
        if c["hsv"][0] < 30 or c["hsv"][0] > 150  # Red~yellow or purple~red
    )

    # Mood classification
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
    """Process a single image."""
    image_path = Path(image_path)
    print(f"\n Processing: {image_path.name}")

    image = cv2.imread(str(image_path))
    if image is None:
        print(" Cannot read image.")
        return None

    # Extract colors
    colors = extract_palette(image, n_colors)
    mood = classify_dawn_mood(colors)

    # Print results
    print(f" Mood: {mood['description']}")
    print(f" Warmth: {mood['warmth']}%")
    print("  Dominant colors:")
    for c in colors:
        bar = "█" * int(c["percentage"] / 2)
        print(f"      {c['hex']} {bar} {c['percentage']}%")

    if save:
        PALETTES_DIR.mkdir(parents=True, exist_ok=True)
        stem = image_path.stem

        # Save palette image
        palette_img = create_palette_image(colors)
        palette_path = PALETTES_DIR / f"{stem}_palette.png"
        cv2.imwrite(str(palette_path), palette_img)

        # Save JSON
        result = {
            "source_image": image_path.name,
            "colors": colors,
            "mood": mood,
            "n_colors": n_colors,
        }
        json_path = PALETTES_DIR / f"{stem}_palette.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n Palette image: {palette_path}")
        print(f" JSON data: {json_path}")

    return {"colors": colors, "mood": mood}


def process_all(n_colors=DEFAULT_N_COLORS):
    """Process all images in the data/photos folder."""
    if not PHOTOS_DIR.exists():
        print("data/photos folder not found.")
        print("Run collect_dawn.py first to collect photos.")
        return

    images = list(PHOTOS_DIR.glob("*.jpg")) + list(PHOTOS_DIR.glob("*.png"))
    if not images:
        print("No images to process.")
        return

    print(f"\n Dawn Palette - Analyzing {len(images)} dawns")
    print("=" * 50)

    results = []
    for img_path in sorted(images):
        result = process_single(img_path, n_colors)
        if result:
            results.append(result)
        print()

    # Summary
    if results:
        print("\n" + "=" * 50)
        print(f"Analysis complete! {len(results)} photos processed")
        print(f"Palettes saved: {PALETTES_DIR}")

        # Mood statistics
        moods = [r["mood"]["mood"] for r in results]
        unique_moods = set(moods)
        print("\n Dawn moods discovered:")
        for m in unique_moods:
            count = moods.count(m)
            print(f"      {m}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Dawn Palette - Color Palette Extractor"
    )
    parser.add_argument("--image", type=str, help="Path to a single image")
    parser.add_argument(
        "--colors",
        type=int,
        default=DEFAULT_N_COLORS,
        help="Number of colors to extract",
    )
    args = parser.parse_args()

    if args.image:
        process_single(args.image, args.colors)
    else:
        process_all(args.colors)


if __name__ == "__main__":
    main()
