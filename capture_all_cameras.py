#!/usr/bin/env python3
"""Capture one image from every camera detected by Picamera2."""

from __future__ import annotations

import argparse
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from picamera2 import Picamera2


def discover_cameras() -> List[Dict]:
    """Return camera metadata provided by libcamera/Picamera2."""
    return Picamera2.global_camera_info() or []


def capture_from_camera(camera_num: int, output_dir: Path, warmup_seconds: float) -> Path | None:
    picam2 = None
    try:
        picam2 = Picamera2(camera_num)
        config = picam2.create_still_configuration()
        picam2.configure(config)
        picam2.start()

        # Let auto-exposure/auto-white-balance settle.
        if warmup_seconds > 0:
            time.sleep(warmup_seconds)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"camera_{camera_num}_{ts}.jpg"
        picam2.capture_file(str(output_path))
        return output_path
    except Exception:
        return None
    finally:
        if picam2 is not None:
            try:
                picam2.stop()
            except Exception:
                pass
            try:
                picam2.close()
            except Exception:
                pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Save one image from each camera detected by Picamera2."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="camera_captures",
        help="Folder to save images (default: camera_captures)",
    )
    parser.add_argument(
        "--warmup",
        type=float,
        default=0.7,
        help="Seconds to wait after camera start before capture (default: 0.7)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    os.makedirs(output_dir, exist_ok=True)

    cameras = discover_cameras()
    if not cameras:
        print("No cameras detected by Picamera2.")
        return

    print(f"Detected cameras: {len(cameras)}")

    saved_any = False
    for i, info in enumerate(cameras):
        camera_num = int(info.get("Num", i))
        model = info.get("Model", "Unknown")
        location = info.get("Location", "Unknown")
        print(f"- Camera {camera_num}: model={model}, location={location}")

        saved_path = capture_from_camera(camera_num, output_dir, args.warmup)
        if saved_path:
            saved_any = True
            print(f"  Saved: {saved_path}")
        else:
            print(f"  Failed to capture from camera {camera_num}")

    if not saved_any:
        print("No images were saved.")


if __name__ == "__main__":
    main()
