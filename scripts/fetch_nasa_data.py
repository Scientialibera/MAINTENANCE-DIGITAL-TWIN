from __future__ import annotations

import argparse
from pathlib import Path
import zipfile

import httpx

CMAPSS_URL = "https://data.nasa.gov/docs/legacy/CMAPSSData.zip"
IMS_URL = "https://data.nasa.gov/docs/legacy/IMS.zip"


def download_and_extract(url: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination.parent / f"{destination.name}.zip"
    print(f"Downloading {url}")
    with httpx.stream("GET", url, timeout=180, follow_redirects=True) as response:
        response.raise_for_status()
        with archive.open("wb") as handle:
            for chunk in response.iter_bytes():
                handle.write(chunk)
    print(f"Extracting {archive}")
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(destination)
    archive.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download public NASA prognostics datasets")
    parser.add_argument("--cmapss", action="store_true", help="Download NASA C-MAPSS benchmark")
    parser.add_argument("--ims", action="store_true", help="Download NASA IMS bearing experiments")
    args = parser.parse_args()
    if not args.cmapss and not args.ims:
        parser.error("Select --cmapss, --ims, or both")
    if args.cmapss:
        download_and_extract(CMAPSS_URL, Path("data/raw/CMAPSSData"))
    if args.ims:
        download_and_extract(IMS_URL, Path("data/raw/IMS"))


if __name__ == "__main__":
    main()
