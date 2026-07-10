#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report count and total size of downloaded case.law ZIP files."
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent),
        help="Directory where ZIP files are being downloaded.",
    )
    parser.add_argument(
        "--glob",
        default="*.zip",
        help="Glob pattern to match downloaded files (default: *.zip).",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    if not output_dir.exists():
        raise SystemExit(f"Directory does not exist: {output_dir}")

    file_count = 0
    total_bytes = 0

    for file_path in output_dir.rglob(args.glob):
        if file_path.is_file():
            file_count += 1
            total_bytes += file_path.stat().st_size

    total_gb_decimal = total_bytes / (1000 ** 3)
    total_gib_binary = total_bytes / (1024 ** 3)

    print(f"directory: {output_dir}")
    print(f"downloaded_files: {file_count}")
    print(f"total_size_bytes: {total_bytes}")
    print(f"total_size_gb: {total_gb_decimal:.3f}")
    print(f"total_size_gib: {total_gib_binary:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
