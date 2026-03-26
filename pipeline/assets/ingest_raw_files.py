"""@bruin
name: ingest_raw_files
type: python
image: python:3.12
depends:
  - raw_bestsellers
  - raw_author_nationality
@bruin"""

import os
from pathlib import Path


def main() -> None:
    bucket = os.getenv("RAW_DATA_LAKE_BUCKET", "")
    base = Path(__file__).resolve().parent
    files = [
        base / "bestsellers_with_categories.csv",
        base / "author_nationality_seed.csv",
    ]

    print("Batch ingestion step prepared.")
    print(f"Configured bucket: {bucket or 'RAW_DATA_LAKE_BUCKET not set'}")
    for path in files:
        print(f"Ready to upload: {path.name}")


if __name__ == "__main__":
    main()
