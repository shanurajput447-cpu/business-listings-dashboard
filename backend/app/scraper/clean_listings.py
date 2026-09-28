"""
Clean, validate, and deduplicate raw listings from data/raw/listings_raw.csv.

Does not collect data, insert into MySQL, or call APIs.

Reproducible command (from the repository root):

    python backend/app/scraper/clean_listings.py
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

CSV_COLUMNS = (
    "business_name",
    "category",
    "city",
    "address",
    "phone",
    "source",
)

MIN_CLEANED_RECORDS = 500
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "listings_raw.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "listings_clean.csv"
DEFAULT_REPORT = PROJECT_ROOT / "data" / "processed" / "data_quality_report.json"

_WHITESPACE_RE = re.compile(r"\s+")
_NON_DIGIT_RE = re.compile(r"\D")


def collapse_whitespace(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value.strip())


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return collapse_whitespace(str(value))


def normalize_title_case(value: str | None) -> str:
    cleaned = normalize_text(value)
    if not cleaned:
        return ""
    return cleaned.title()


def normalize_source(value: str | None) -> str:
    cleaned = normalize_text(value)
    if not cleaned:
        return ""
    return cleaned.replace(" ", "_").lower()


def normalize_phone(value: str | None) -> str:
    cleaned = normalize_text(value)
    if not cleaned:
        return ""

    digits = _NON_DIGIT_RE.sub("", cleaned)
    if len(digits) == 12 and digits.startswith("91"):
        return f"+91 {digits[2:]}"
    if len(digits) == 11 and digits.startswith("0") and len(digits[1:]) == 10:
        remaining = digits[1:]
        if remaining[0] in {"6", "7", "8", "9"}:
            return f"+91 {remaining}"
    if len(digits) == 10 and digits[0] in {"6", "7", "8", "9"}:
        return f"+91 {digits}"

    std_match = re.fullmatch(r"0?(\d{2,4})[-\s]+(\d{6,8})", cleaned)
    if std_match:
        std, local = std_match.group(1), std_match.group(2)
        return f"0{std.lstrip('0')}-{local}" if not std.startswith("0") else f"{std}-{local}"

    if digits:
        if cleaned.startswith("+"):
            return f"+{digits}"
        return digits
    return cleaned


def clean_record(row: dict[str, Any]) -> dict[str, str]:
    return {
        "business_name": normalize_text(row.get("business_name")),
        "category": normalize_title_case(row.get("category")),
        "city": normalize_title_case(row.get("city")),
        "address": normalize_text(row.get("address")),
        "phone": normalize_phone(row.get("phone")),
        "source": normalize_source(row.get("source")),
    }


def is_valid_record(row: dict[str, str]) -> bool:
    return bool(row.get("business_name")) and bool(row.get("source"))


def duplicate_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        normalize_text(row.get("business_name")).casefold(),
        normalize_text(row.get("address")).casefold(),
        normalize_text(row.get("city")).casefold(),
    )


def count_missing_by_field(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {column: 0 for column in CSV_COLUMNS}
    for row in rows:
        for column in CSV_COLUMNS:
            if not normalize_text(row.get(column)):
                counts[column] += 1
    return counts


def deduplicate_records(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    kept: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    removed = 0
    for row in rows:
        key = duplicate_key(row)
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept.append(row)
    return kept, removed


def process_listings(raw_rows: list[dict[str, Any]]) -> tuple[list[dict[str, str]], dict[str, int]]:
    raw_count = len(raw_rows)
    missing_values_by_field = count_missing_by_field(
        [{column: str(row.get(column, "") or "") for column in CSV_COLUMNS} for row in raw_rows]
    )

    cleaned_rows = [clean_record(row) for row in raw_rows]
    valid_rows = [row for row in cleaned_rows if is_valid_record(row)]
    invalid_count = raw_count - len(valid_rows)
    unique_rows, duplicate_count_removed = deduplicate_records(valid_rows)

    report = {
        "raw_record_count": raw_count,
        "valid_record_count": len(valid_rows),
        "invalid_record_count": invalid_count,
        "duplicate_count_removed": duplicate_count_removed,
        "final_cleaned_record_count": len(unique_rows),
        "missing_values_by_field": missing_values_by_field,
    }
    return unique_rows, report


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean and deduplicate raw business listings.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = _resolve(args.input)
    output_path = _resolve(args.output)
    report_path = _resolve(args.report)

    if not input_path.exists():
        print(f"Raw listings file not found: {input_path}", file=sys.stderr)
        return 1

    raw_rows = read_csv(input_path)
    cleaned_rows, report = process_listings(raw_rows)
    write_report(report_path, report)

    if report["final_cleaned_record_count"] < MIN_CLEANED_RECORDS:
        print(
            "Cleaning stopped: final cleaned dataset has "
            f"{report['final_cleaned_record_count']} records, which is below "
            f"the required minimum of {MIN_CLEANED_RECORDS}. Extra records were not invented.",
            file=sys.stderr,
        )
        print(json.dumps(report, indent=2), file=sys.stderr)
        print(f"Quality report written to {report_path}", file=sys.stderr)
        return 1

    write_csv(output_path, cleaned_rows)
    print(f"Raw records: {report['raw_record_count']}")
    print(f"Invalid records: {report['invalid_record_count']}")
    print(f"Duplicates removed: {report['duplicate_count_removed']}")
    print(f"Final cleaned records: {report['final_cleaned_record_count']}")
    print(f"Wrote cleaned CSV to {output_path}")
    print(f"Wrote quality report to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
