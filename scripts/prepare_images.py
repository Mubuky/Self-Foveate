"""Create responsive WebP derivatives without changing original research figures.

Usage: python scripts/prepare_images.py "static/images/*.png"
Requires Pillow. Only static images supplied on the command line are processed.
"""
import argparse
import glob
from pathlib import Path

from PIL import Image, ImageOps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", help="Image paths or quoted glob patterns.")
    parser.add_argument("--widths", nargs="+", type=int, default=[640, 1280, 2400])
    parser.add_argument("--quality", type=int, default=92)
    args = parser.parse_args()
    if any(width < 1 for width in args.widths) or not 1 <= args.quality <= 100:
        parser.error("Widths must be positive and quality must be between 1 and 100.")
    paths = sorted({Path(match).resolve() for pattern in args.images for match in glob.glob(pattern)})
    if not paths:
        parser.error("No source images matched.")
    for path in paths:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source)
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            output_dir = path.parent / "responsive"
            output_dir.mkdir(exist_ok=True)
            for width in sorted({min(width, image.width) for width in args.widths}):
                height = round(image.height * width / image.width)
                resized = image.resize((width, height), Image.Resampling.LANCZOS)
                output = output_dir / f"{path.stem}-{width}.webp"
                resized.save(output, "WEBP", quality=args.quality, method=6)
                print(f"{output.relative_to(path.parent)}: {width}x{height}, {output.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
