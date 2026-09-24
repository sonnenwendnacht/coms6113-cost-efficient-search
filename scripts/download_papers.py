"""Fetch pinned paper PDFs and verify them against the committed manifest.

No third-party dependencies. Existing files with a different checksum are never
overwritten: investigate a source/version change and update the catalog explicitly.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"id", "title", "authors", "version", "source_url", "pdf_url", "filename", "sha256", "role"}


def read_manifest():
    manifest = json.loads((ROOT / "papers" / "manifest.json").read_text())
    rows = manifest["papers"]
    ids, filenames = set(), set()
    if not rows:
        raise ValueError("Empty paper catalog")
    for row in rows:
        if missing := REQUIRED - row.keys():
            raise ValueError(f"Missing fields: {missing}")
        name = row["filename"]
        if Path(name).name != name or not name.endswith(".pdf") or "\\" in name:
            raise ValueError(f"Unsafe filename: {name}")
        if row["id"] in ids or name in filenames:
            raise ValueError(f"Duplicate paper: {row['id']}")
        if not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
            raise ValueError(f"Invalid checksum: {name}")
        if not all(row[k].startswith("https://") for k in ["source_url", "pdf_url"]):
            raise ValueError(f"Expected HTTPS source: {name}")
        ids.add(row["id"])
        filenames.add(name)
    return rows


def verify(data, row):
    if not data.startswith(b"%PDF-"):
        raise ValueError(f"Not a PDF: {row['filename']}")
    if hashlib.sha256(data).hexdigest() != row["sha256"]:
        raise ValueError(f"Checksum mismatch: {row['filename']}; source may have changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-manifest", action="store_true", help="Validate catalog without network or PDFs")
    parser.add_argument("--verify-local", action="store_true", help="Verify all local PDFs without downloading")
    args = parser.parse_args()
    rows = read_manifest()
    if args.check_manifest:
        print(f"Catalog valid: {len(rows)} papers")
        return
    destination = ROOT / "papers" / "pdf"
    destination.mkdir(exist_ok=True)
    failures = []
    for row in rows:
        path = destination / row["filename"]
        try:
            if path.exists():
                verify(path.read_bytes(), row)
                print(f"Verified {path.name}")
            elif args.verify_local:
                raise FileNotFoundError(f"Missing {path.name}")
            else:
                request = Request(row["pdf_url"], headers={"User-Agent": "COMS6113-paper-fetcher/1.0"})
                with urlopen(request, timeout=90) as response:
                    data = response.read()
                verify(data, row)
                temporary = path.with_suffix(".pdf.part")
                temporary.write_bytes(data)
                temporary.replace(path)
                print(f"Downloaded {path.name}")
        except Exception as error:
            failures.append(str(error))
            print(str(error), file=sys.stderr)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
