#!/usr/bin/env python3
"""Capture one image from every available camera and save to a folder."""

from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import List

import cv2


def discover_camera_indices(max_index: int = 10) -> List[int]:
    """Find working camera indices by probing VideoCapture."""
    found: List[int] = []

    # Prefer Linux video devices if present (Raspberry Pi typical case).
    dev_dir = Path("/dev")
    if dev_dir.exists():
        for path in sorted(dev_dir.glob("video*")):
            suffix = path.name.replace("video", "")
            if suffix.isdigit():
                idx = int(suffix)
                if idx not in found:
                    found.append(idx)

    # Fallback probing.
    for idx in range(max_index):
        if idx not in found:
            found.append(idx)

    working: List[int] = []
    for idx in found:
        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            cap.release()
            continue

        ok, _ = cap.read()
        cap.release()
        if ok:
            working.append(idx)

    return working


def capture_from_camera(index: int, output_dir: Path) -> Path | None:
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        cap.release()
        return None

    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"camera_{index}_{ts}.jpg"
    saved = cv2.imwrite(str(output_path), frame)
    if not saved:
        return None
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Save one image from each detected camera."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="camera_captures",
        help="Folder to save images (default: camera_captures)",
    )
    parser.add_argument(
        "--max-index",
        type=int,
        default=10,
        help="Max camera index to probe in fallback mode (default: 10)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    os.makedirs(output_dir, exist_ok=True)

    indices = discover_camera_indices(max_index=args.max_index)
    if not indices:
        print("No working cameras found.")
        return

    print(f"Detected working cameras: {indices}")

    saved_any = False
    for idx in indices:
        saved_path = capture_from_camera(idx, output_dir)
        if saved_path:
            saved_any = True
            print(f"Saved: {saved_path}")
        else:
            print(f"Failed to capture from camera index {idx}")

    if not saved_any:
        print("No images were saved.")


if __name__ == "__main__":
    main()
