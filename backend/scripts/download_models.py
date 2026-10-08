# ============================================================
# METROSCAN MODEL WEIGHTS DOWNLOAD UTILITY
# Solves Point 11: How to manage and load 4 GB OCR models
# ============================================================

import os
import sys
import argparse
import urllib.request

WEIGHTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "weights"))

MODEL_REGISTRY = {
    "paddleocr_en": {
        "filename": "paddleocr_en_v4.tar",
        "url": "https://paddleocr.bj.bcebos.com/PP-OCRv4/english/en_PP-OCRv4_rec_infer.tar",
        "description": "PaddleOCR English text recognition model (~20 MB)",
    },
    "trocr_printed": {
        "filename": "trocr-small-printed.bin",
        "url": "",
        "description": "TrOCR Vision-Language printed text model (~350 MB)",
    },
    "yolov8_pdp_detector": {
        "filename": "yolov8m_pdp_packaging.pt",
        "url": "",
        "description": "YOLOv8 packaging panel & text bounding box detector (~50 MB)",
    }
}


def download_file(url: str, dest_path: str):
    """Downloads a file with a live command-line progress bar."""
    if not url:
        print(f"[INFO] No direct public download URL set. Teammate can manually drop file into: {dest_path}")
        return

    print(f"[INFO] Downloading: {url}")
    print(f"[INFO] Destination: {dest_path}")

    def progress_callback(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded / total_size * 100
            sys.stdout.write(f"\rDownloading: {percent:.1f}% ({downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\rDownloading: {downloaded / (1024*1024):.1f} MB")
            sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, reporthook=progress_callback)
    print("\n[SUCCESS] Download completed successfully.")


def main():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    print("=" * 60)
    print("MetroScan 4 GB OCR Model Weights Manager")
    print(f"Weights Directory: {WEIGHTS_DIR}")
    print("=" * 60)

    for key, info in MODEL_REGISTRY.items():
        dest = os.path.join(WEIGHTS_DIR, info["filename"])
        print(f"\nModel: {key}")
        print(f"  Description: {info['description']}")
        print(f"  Target File: {dest}")

        if os.path.exists(dest):
            size_mb = os.path.getsize(dest) / (1024 * 1024)
            print(f"  [STATUS] Already installed ({size_mb:.2f} MB).")
        else:
            print(f"  [STATUS] Not found in weights/ folder.")
            if info["url"]:
                choice = input(f"  Download {key} now? [y/N]: ").strip().lower()
                if choice == "y":
                    download_file(info["url"], dest)
            else:
                print("  [MANUAL HANDOVER]")
                print("  Ask your OCR teammate to copy their trained weights directly to:")
                print(f"  --> {dest}")

    print("\n" + "=" * 60)
    print("All models in weights/ are ignored by Git (*.pt, *.bin, etc.).")
    print("FastAPI will load these once at server startup as singletons.")
    print("=" * 60)


if __name__ == "__main__":
    main()
