#!/usr/bin/env python3
"""
Find new/changed blobs and sync them to s3.

Requires BLOB_SERVICE_URL, BLOB_SERVICE_USER, BLOB_SERVICE_PASS in the
environment. BLOB_SERVICE_USER/BLOB_SERVICE_PASS are BasicAuth credentials
for the Blob Service.

  BLOB_SERVICE_URL is a template containing the literal placeholder
  "{blobcsid}", e.g.:
    https://cspace.museumca.org/cspace-services/blobs/{blobcsid}/derivatives/Original/content
"""

from __future__ import annotations

import csv
import gzip
import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import requests

# the Solr export can contain fields (e.g. long free-text descriptions)
# past csv's default 128 KiB per-field cap
csv.field_size_limit(sys.maxsize)

# --- config: edit here ---
SOLR_PIPELINES_DIR = Path("~/solr-pipelines").expanduser()
SOLR_CSV_GZ = Path("4solr.omca.media-public.csv.gz")
LOCAL_CACHE = Path("/var/www/html/images").expanduser()
S3_BUCKET = "s3://omca-media/thumbnails"
UPDATE_LOG = Path("s3_update.log")

ALREADY_CONVERTED_CSV = Path("s3_already_converted.csv")
CURRENT_BLOBS_CSV = Path("s3_current_blobs.csv")
NEW_BLOBS_CSV = Path("s3_new_blobs.csv")
STATS_CSV = Path("s3_resize_stats.csv")
FAILURES_CSV = Path("s3_resize_failures.csv")

CURL_TIMEOUT = 30

log = logging.getLogger("s3_update")


@dataclass(frozen=True)
class Result:
    blobcsid: str
    ok: bool
    resized_bytes: int | None = None
    error: str | None = None


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        log.error("%s must be set", name)
        sys.exit(1)
    return value


def load_current_blobs(csv_path: Path) -> set[str]:
    """Read the Solr export, column "blobcsid".

    The export is standard RFC4180 CSV (comma-delimited, double-quote
    encapsulated; a field may legitimately contain an embedded
    comma/newline/quote), hence csv.DictReader's default dialect rather
    than a tab delimiter. Column is picked by header name "blobcsid", not
    position, so the file can be reordered upstream without silently
    corrupting this. A trailing solr row-count footer line (e.g.
    "26913 rows") can end up in this column too -- skip it, same as the
    old `grep -v ' rows'`.
    """
    blobs: set[str] = set()
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            blobcsid = (row.get("blobcsid") or "").strip()
            if blobcsid and " rows" not in blobcsid:
                blobs.add(blobcsid)
    return blobs


def load_cached_blobs(cache_dir: Path) -> set[str]:
    return {p.stem for p in cache_dir.glob("*.jpg")}


def write_list(path: Path, values: set[str]) -> None:
    with open(path, "w") as f:
        for v in sorted(values):
            f.write(v + "\n")


def fetch_blob(blobcsid: str, url_template: str, auth: tuple[str, str]) -> bytes:
    url = url_template.replace("{blobcsid}", blobcsid)
    resp = requests.get(url, auth=auth, timeout=CURL_TIMEOUT)
    if resp.status_code == 404:
        raise LookupError("blob not found (404)")
    if resp.status_code != 200:
        raise LookupError(f"fetch failed (http {resp.status_code})")
    if not resp.content:
        raise LookupError("fetch returned empty body")
    return resp.content


def convert_to_jpeg(data: bytes, output_path: Path) -> int:
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        tmp.flush()
        subprocess.run(
            ["convert", tmp.name, "-quality", "80", "-scale", "600x>", str(output_path)],
            check=True, capture_output=True, text=True,
        )
    return output_path.stat().st_size


def process_blob(blobcsid: str, url_template: str, auth: tuple[str, str]) -> Result:
    output_path = LOCAL_CACHE / f"{blobcsid}.jpg"
    try:
        data = fetch_blob(blobcsid, url_template, auth)
    except (requests.RequestException, LookupError) as e:
        return Result(blobcsid, ok=False, error=str(e))

    try:
        size = convert_to_jpeg(data, output_path)
    except subprocess.CalledProcessError as e:
        output_path.unlink(missing_ok=True)
        stderr = e.stderr.strip().replace("\n", " ") if e.stderr else ""
        return Result(blobcsid, ok=False, error=f"convert failed: {stderr}")

    return Result(blobcsid, ok=True, resized_bytes=size)


def write_stats(results: list[Result]) -> None:
    with open(STATS_CSV, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for i, r in enumerate((r for r in results if r.ok), start=1):
            writer.writerow([i, r.blobcsid, r.resized_bytes])

    with open(FAILURES_CSV, "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for i, r in enumerate((r for r in results if not r.ok), start=1):
            writer.writerow([i, r.blobcsid, r.error])


def sync_to_s3() -> None:
    subprocess.run(["aws", "s3", "sync", str(LOCAL_CACHE), S3_BUCKET], check=True)


def count_lines(path: Path) -> int:
    with open(path) as f:
        return sum(1 for _ in f)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(UPDATE_LOG), logging.StreamHandler()],
    )

    url_template = require_env("BLOB_SERVICE_URL")
    auth = (require_env("BLOB_SERVICE_USER"), require_env("BLOB_SERVICE_PASS"))

    log.info("s3 image update started")

    if not SOLR_PIPELINES_DIR.is_dir():
        log.error("%s does not exist", SOLR_PIPELINES_DIR)
        return 1
    os.chdir(SOLR_PIPELINES_DIR)

    # make a list of the images in the local 'cache'
    cached_blobs = load_cached_blobs(LOCAL_CACHE)
    write_list(ALREADY_CONVERTED_CSV, cached_blobs)

    # make a list of the current public blobs
    # (the list of public media is created as part of the solr refresh)
    solr_csv = SOLR_CSV_GZ.with_suffix("")
    try:
        with gzip.open(SOLR_CSV_GZ, "rb") as src, open(solr_csv, "wb") as dst:
            dst.write(src.read())
    except OSError as e:
        log.error("failed to unpack %s: %s", SOLR_CSV_GZ, e)
        return 1
    current_blobs = load_current_blobs(solr_csv)
    write_list(CURRENT_BLOBS_CSV, current_blobs)

    # make a list of the public blobs that are not already in the local 'cache'
    new_blobs = sorted(current_blobs - cached_blobs)
    write_list(NEW_BLOBS_CSV, set(new_blobs))
    log.info("%d current blob(s), %d already cached, %d new", len(current_blobs), len(cached_blobs), len(new_blobs))

    # fetch each new blob from the Blob Service and make a servable
    # (smaller) jpeg for it in the local cache. Failures are reported
    # (logged + recorded) and skipped, not fatal.
    results = [process_blob(b, url_template, auth) for b in new_blobs]
    write_stats(results)

    failures = [r for r in results if not r.ok]
    if failures:
        log.warning("%d of %d new blob(s) failed to fetch/convert, see %s", len(failures), len(new_blobs), FAILURES_CSV)

    # sync the new servable images to s3
    # (nb: aws credentials need to be set up in the shell for this)
    try:
        sync_to_s3()
    except subprocess.CalledProcessError as e:
        log.error("aws s3 sync failed (exit %d)", e.returncode)
        return 1

    # make counts
    for path in (ALREADY_CONVERTED_CSV, CURRENT_BLOBS_CSV, NEW_BLOBS_CSV, STATS_CSV, FAILURES_CSV):
        log.info("%d %s", count_lines(path), path)

    # tidy up
    solr_csv.unlink(missing_ok=True)
    log.info("s3 image update ended")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logging.getLogger("s3_update").exception("unhandled error")
        sys.exit(1)
