"""Validate author nationality coverage for the bestseller dataset."""

import csv
from pathlib import Path


DATASET_PATH = Path("pipeline/assets/bestsellers_with_categories.csv")
SEED_PATH = Path("pipeline/assets/author_nationality_seed.csv")


def load_unique_authors(dataset_path: Path) -> set[str]:
    with dataset_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return {row["Author"].strip() for row in reader if row.get("Author", "").strip()}


def load_seed_authors(seed_path: Path) -> dict[str, str]:
    with seed_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return {
            row["author"].strip(): row["nationality"].strip()
            for row in reader
            if row.get("author", "").strip()
        }


def main() -> None:
    if not DATASET_PATH.exists():
        print(f"Missing dataset: {DATASET_PATH}")
        return

    if not SEED_PATH.exists():
        print(f"Missing nationality seed: {SEED_PATH}")
        return

    dataset_authors = load_unique_authors(DATASET_PATH)
    seed_authors = load_seed_authors(SEED_PATH)

    missing_authors = sorted(dataset_authors - seed_authors.keys())
    unknown_nationalities = sorted(
        author for author, nationality in seed_authors.items() if nationality == "Unknown"
    )

    print(f"Dataset authors: {len(dataset_authors)}")
    print(f"Seed authors: {len(seed_authors)}")
    print(f"Missing seed rows: {len(missing_authors)}")
    print(f"Unknown nationalities: {len(unknown_nationalities)}")

    if missing_authors:
        print("\nAuthors missing from the seed:")
        for author in missing_authors:
            print(f"- {author}")

    if unknown_nationalities:
        print("\nAuthors with Unknown nationality:")
        for author in unknown_nationalities:
            print(f"- {author}")


if __name__ == "__main__":
    main()
