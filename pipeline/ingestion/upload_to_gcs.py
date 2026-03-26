"""Upload local raw files to a GCS raw-data bucket as a batch ingestion step."""

import os
from pathlib import Path

from google.cloud import storage


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
FILES_TO_UPLOAD = [
    "bestsellers_with_categories.csv",
    "author_nationality_seed.csv",
]


def main() -> None:
    bucket_name = os.getenv("RAW_DATA_LAKE_BUCKET")
    if not bucket_name:
        raise SystemExit("RAW_DATA_LAKE_BUCKET environment variable is required.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for filename in FILES_TO_UPLOAD:
        path = ASSETS_DIR / filename
        blob = bucket.blob(f"raw/{filename}")
        blob.upload_from_filename(path)
        print(f"Uploaded {filename} to gs://{bucket_name}/raw/{filename}")


if __name__ == "__main__":
    main()
