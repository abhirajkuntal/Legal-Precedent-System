#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import errno
import re
import shutil
import threading
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests


ROOT_URL = "https://static.case.law/"
USER_AGENT = "legal-precedent-system-downloader/1.0"
LINK_RE = re.compile(r'href=["\']([^"\']+)["\']')
GB_DECIMAL = 1000 ** 3


def extract_links(html: str) -> list[str]:
    return LINK_RE.findall(html)


def get_html(url: str, timeout: int = 60) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.text


def iter_jurisdictions() -> list[str]:
    html = get_html(ROOT_URL)
    seen: set[str] = set()
    jurisdictions: list[str] = []

    for link in extract_links(html):
        absolute = urljoin(ROOT_URL, link)
        if not absolute.startswith(ROOT_URL):
            continue
        path = urlparse(absolute).path.strip("/")
        if not path or "/" in path:
            continue
        if path in seen:
            continue
        seen.add(path)
        jurisdictions.append(path)

    if not jurisdictions:
        raise RuntimeError("No jurisdictions discovered from root index.")

    return jurisdictions


def jurisdiction_range(
    jurisdictions: list[str],
    start_slug: str,
    end_slug: str,
) -> list[str]:
    if start_slug not in jurisdictions:
        raise ValueError(f"Start jurisdiction not found: {start_slug}")
    if end_slug not in jurisdictions:
        raise ValueError(f"End jurisdiction not found: {end_slug}")

    start_idx = jurisdictions.index(start_slug)
    end_idx = jurisdictions.index(end_slug)

    if start_idx <= end_idx:
        return jurisdictions[start_idx : end_idx + 1]
    return jurisdictions[end_idx : start_idx + 1]


def iter_zip_urls_for_jurisdiction(slug: str) -> list[str]:
    page_url = urljoin(ROOT_URL, f"{slug}/")
    html = get_html(page_url)
    seen: set[str] = set()
    zip_urls: list[str] = []

    for link in extract_links(html):
        absolute = urljoin(page_url, link)
        if not absolute.endswith(".zip"):
            continue
        path = urlparse(absolute).path.strip("/")
        parts = path.split("/")
        if len(parts) != 2:
            continue
        if parts[0] != slug:
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        zip_urls.append(absolute)

    return zip_urls


def build_download_plan(jurisdictions: Iterable[str]) -> list[tuple[str, str]]:
    plan: list[tuple[str, str]] = []
    for slug in jurisdictions:
        urls = iter_zip_urls_for_jurisdiction(slug)
        plan.extend((slug, url) for url in urls)
        print(f"[plan] {slug}: {len(urls)} zip files")
    return plan


def free_space_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


def trigger_stop(
    stop_event: threading.Event,
    stop_lock: threading.Lock,
    stop_reason: list[str],
    reason: str,
) -> None:
    with stop_lock:
        if not stop_event.is_set():
            stop_reason.append(reason)
            stop_event.set()


def download_one(
    slug: str,
    url: str,
    output_dir: Path,
    retries: int,
    min_free_bytes: int,
    stop_event: threading.Event,
    stop_lock: threading.Lock,
    stop_reason: list[str],
) -> tuple[str, str, str]:
    if stop_event.is_set():
        return slug, url, "stopped"

    filename = Path(urlparse(url).path).name
    target_dir = output_dir / slug
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename

    for attempt in range(1, retries + 1):
        try:
            if min_free_bytes > 0 and free_space_bytes(output_dir) <= min_free_bytes:
                trigger_stop(
                    stop_event,
                    stop_lock,
                    stop_reason,
                    (
                        "Free space reached configured threshold "
                        f"({min_free_bytes / GB_DECIMAL:.3f} GB)."
                    ),
                )
                return slug, str(target), "disk_full_stop"

            existing_size = target.stat().st_size if target.exists() else 0
            headers = {"User-Agent": USER_AGENT}
            mode = "wb"
            if existing_size > 0:
                headers["Range"] = f"bytes={existing_size}-"
                mode = "ab"

            with requests.get(url, headers=headers, timeout=(20, 180), stream=True) as response:
                if response.status_code == 416:
                    return slug, str(target), "skipped"
                if response.status_code == 200 and mode == "ab":
                    mode = "wb"
                response.raise_for_status()

                with target.open(mode) as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue

                        if stop_event.is_set():
                            return slug, str(target), "stopped"

                        if min_free_bytes > 0 and free_space_bytes(output_dir) <= min_free_bytes:
                            trigger_stop(
                                stop_event,
                                stop_lock,
                                stop_reason,
                                (
                                    "Free space reached configured threshold "
                                    f"({min_free_bytes / GB_DECIMAL:.3f} GB)."
                                ),
                            )
                            return slug, str(target), "disk_full_stop"

                        try:
                            f.write(chunk)
                        except OSError as exc:
                            if exc.errno == errno.ENOSPC:
                                trigger_stop(
                                    stop_event,
                                    stop_lock,
                                    stop_reason,
                                    f"Disk full while writing: {target}",
                                )
                                return slug, str(target), "disk_full_stop"
                            raise

            return slug, str(target), "downloaded"
        except Exception as exc:  # noqa: BLE001
            if stop_event.is_set():
                return slug, f"{url} (stopped)", "stopped"
            if attempt >= retries:
                return slug, f"{url} ({exc})", "failed"
            sleep_seconds = min(2 ** attempt, 20)
            time.sleep(sleep_seconds)

    return slug, url, "failed"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download case.law volume ZIPs for jurisdictions in a slug range."
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent),
        help="Destination folder for downloads.",
    )
    parser.add_argument("--start", default="a2d", help="Start jurisdiction slug (inclusive).")
    parser.add_argument("--end", default="yeates", help="End jurisdiction slug (inclusive).")
    parser.add_argument("--workers", type=int, default=6, help="Parallel download workers.")
    parser.add_argument("--retries", type=int, default=4, help="Retries per file.")
    parser.add_argument(
        "--min-free-gb",
        type=float,
        default=0.0,
        help=(
            "Gracefully stop when free disk space is at or below this amount (GB). "
            "0 means stop only when the OS reports disk-full."
        ),
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    min_free_bytes = max(0, int(args.min_free_gb * GB_DECIMAL))

    print("[info] Discovering jurisdiction index...")
    all_jurisdictions = iter_jurisdictions()
    selected = jurisdiction_range(all_jurisdictions, args.start, args.end)
    print(
        f"[info] Jurisdictions selected: {len(selected)} "
        f"({selected[0]} -> {selected[-1]})"
    )

    print("[info] Building download plan from jurisdiction pages...")
    plan = build_download_plan(selected)
    print(f"[info] Total zip files discovered: {len(plan)}")

    downloaded = 0
    skipped = 0
    stopped = 0
    failed: list[str] = []
    stop_event = threading.Event()
    stop_lock = threading.Lock()
    stop_reason: list[str] = []
    cancelled_pending = False

    free_gb_now = free_space_bytes(output_dir) / GB_DECIMAL
    print(
        f"[info] Disk free before download: {free_gb_now:.3f} GB "
        f"(stop threshold: {args.min_free_gb:.3f} GB)"
    )
    print(f"[info] Starting downloads with {args.workers} workers...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(
                download_one,
                slug,
                url,
                output_dir,
                args.retries,
                min_free_bytes,
                stop_event,
                stop_lock,
                stop_reason,
            )
            for slug, url in plan
        ]
        for idx, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            try:
                _slug, info, status = future.result()
            except concurrent.futures.CancelledError:
                status = "cancelled"
                info = "cancelled"

            if status == "downloaded":
                downloaded += 1
            elif status == "skipped":
                skipped += 1
            elif status in {"stopped", "disk_full_stop", "cancelled"}:
                stopped += 1
                if stop_event.is_set() and not cancelled_pending:
                    for pending_future in futures:
                        pending_future.cancel()
                    cancelled_pending = True
            else:
                failed.append(info)

            if idx % 100 == 0 or idx == len(futures):
                print(
                    f"[progress] {idx}/{len(futures)} "
                    f"downloaded={downloaded} skipped={skipped} "
                    f"stopped={stopped} failed={len(failed)}"
                )

    if stop_event.is_set():
        reason_text = stop_reason[0] if stop_reason else "Disk space stop triggered."
        print(f"[stop] {reason_text}")
        print(
            f"[done] downloaded={downloaded} skipped={skipped} stopped={stopped} "
            f"failed={len(failed)} output={output_dir}"
        )
        return 0

    if failed:
        failed_file = output_dir / "failed_case_law_downloads.txt"
        failed_file.write_text("\n".join(failed) + "\n", encoding="utf-8")
        print(f"[warn] Failures recorded in: {failed_file}")

    print(
        f"[done] downloaded={downloaded} skipped={skipped} stopped={stopped} "
        f"failed={len(failed)} output={output_dir}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
