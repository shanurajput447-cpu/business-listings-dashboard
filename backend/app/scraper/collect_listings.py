"""
Collect or generate raw business listings and write data/raw/listings_raw.csv.

Live scraping of protected directories is not attempted. This script uses a
deterministic demo dataset labeled with demo_sample* sources so it is never
presented as scraped data.

Reproducible command (from the repository root):

    python backend/app/scraper/collect_listings.py

Or from backend/:

    python -m app.scraper.collect_listings
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

CSV_COLUMNS = (
    "business_name",
    "category",
    "city",
    "address",
    "phone",
    "source",
)

DEFAULT_RECORD_COUNT = 600
RANDOM_SEED = 42
LIVE_SCRAPE_DISABLED_REASON = (
    "Live collection is disabled: public business directories typically use "
    "CAPTCHA, login, or anti-bot protection. This script does not bypass those "
    "controls and writes deterministic demo_sample data instead."
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "listings_raw.csv"

CITIES = (
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Kochi",
    "Lucknow",
    "Chandigarh",
)

CITY_LOCALITIES = {
    "Mumbai": ("Andheri West", "Bandra", "Dadar", "Powai", "Thane West"),
    "Delhi": ("Connaught Place", "Karol Bagh", "Saket", "Rohini", "Dwarka"),
    "Bengaluru": ("Koramangala", "Indiranagar", "Whitefield", "Jayanagar", "HSR Layout"),
    "Hyderabad": ("Banjara Hills", "Hitech City", "Secunderabad", "Gachibowli", "Kukatpally"),
    "Chennai": ("T Nagar", "Anna Nagar", "Adyar", "Velachery", "Mylapore"),
    "Pune": ("Kothrud", "Hinjawadi", "Viman Nagar", "Shivajinagar", "Hadapsar"),
    "Kolkata": ("Salt Lake", "Park Street", "Howrah", "Gariahat", "New Town"),
    "Ahmedabad": ("Navrangpura", "Satellite", "Maninagar", "Bodakdev", "CG Road"),
    "Jaipur": ("C Scheme", "Malviya Nagar", "Vaishali Nagar", "Tonk Road", "MI Road"),
    "Kochi": ("MG Road", "Kakkanad", "Edappally", "Fort Kochi", "Panampilly Nagar"),
    "Lucknow": ("Hazratganj", "Gomti Nagar", "Aliganj", "Indira Nagar", "Aminabad"),
    "Chandigarh": ("Sector 17", "Sector 35", "Sector 22", "Industrial Area", "Manimajra"),
}

CITY_STD_CODES = {
    "Mumbai": "022",
    "Delhi": "011",
    "Bengaluru": "080",
    "Hyderabad": "040",
    "Chennai": "044",
    "Pune": "020",
    "Kolkata": "033",
    "Ahmedabad": "079",
    "Jaipur": "0141",
    "Kochi": "0484",
    "Lucknow": "0522",
    "Chandigarh": "0172",
}

CATEGORIES = (
    "Restaurant",
    "Pharmacy",
    "Electronics Store",
    "Clothing Store",
    "Gym",
    "Salon",
    "Clinic",
    "Grocery",
    "Auto Workshop",
    "Education",
    "Real Estate",
    "Hotel",
)

CATEGORY_NAME_PARTS = {
    "Restaurant": ("Spice", "Tandoor", "Curry", "Biryani", "Cafe", "Kitchen"),
    "Pharmacy": ("MedPlus", "Care", "Wellness", "Life", "Apollo-style"),
    "Electronics Store": ("Digital", "Gadget", "Circuit", "Pixel", "Volt"),
    "Clothing Store": ("Silk", "Style", "Wardrobe", "Thread", "Fashion"),
    "Gym": ("Fit", "Power", "Iron", "Pulse", "Strength"),
    "Salon": ("Glow", "Style", "Blossom", "Trim", "Aura"),
    "Clinic": ("Health", "Care", "Healing", "Family", "City"),
    "Grocery": ("Fresh", "Mart", "Basket", "Daily", "Kirana"),
    "Auto Workshop": ("Motor", "Gear", "Wheel", "Service", "Pitstop"),
    "Education": ("Learn", "Academy", "Tutor", "Knowledge", "Bright"),
    "Real Estate": ("Homes", "Estate", "Shelter", "Property", "Nivas"),
    "Hotel": ("Stay", "Inn", "Residency", "Lodge", "Suites"),
}

NAME_SUFFIXES = (
    "Hub",
    "Point",
    "Center",
    "House",
    "Works",
    "Place",
    "Corner",
    "Studio",
    "Depot",
    "Gallery",
)

# Distinct demo labels only — these are not live scrape sources.
DEMO_SOURCES = (
    "demo_sample",
    "demo_sample_directory",
    "demo_sample_local",
    "demo_sample_trade",
)


def build_demo_listings(count: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)
    listings: list[dict[str, str]] = []
    seen_names: set[tuple[str, str, str]] = set()

    # Round-robin city/category/source first so dashboard aggregations stay balanced.
    for index in range(count):
        city = CITIES[index % len(CITIES)]
        category = CATEGORIES[(index // len(CITIES)) % len(CATEGORIES)]
        source = DEMO_SOURCES[index % len(DEMO_SOURCES)]
        locality = rng.choice(CITY_LOCALITIES[city])
        name_stem = rng.choice(CATEGORY_NAME_PARTS[category])
        suffix = rng.choice(NAME_SUFFIXES)
        serial = index + 1
        business_name = f"{name_stem} {suffix} {city[:3].upper()} {serial:03d}"

        key = (business_name, city, category)
        if key in seen_names:
            business_name = f"{business_name} Unit {rng.randint(1, 9)}"
        seen_names.add((business_name, city, category))

        street_no = rng.randint(11, 199)
        address = f"{street_no}, {locality}, {city}"
        phone = _demo_phone(rng, city, index)

        listings.append(
            {
                "business_name": business_name,
                "category": category,
                "city": city,
                "address": address,
                "phone": phone,
                "source": source,
            }
        )

    return listings


def _demo_phone(rng: random.Random, city: str, index: int) -> str:
    if index % 3 == 0:
        std = CITY_STD_CODES[city]
        local = rng.randint(2_000_000, 9_999_999)
        return f"{std}-{local:07d}"
    mobile_body = 7_000_000_000 + rng.randint(0, 2_999_999_999)
    return f"+91 {mobile_body}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate raw business listings CSV (deterministic demo fallback)."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="CSV output path (default: data/raw/listings_raw.csv)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_RECORD_COUNT,
        help=f"Number of records to generate (default: {DEFAULT_RECORD_COUNT}, minimum 550)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help=f"Random seed for reproducible demo data (default: {RANDOM_SEED})",
    )
    parser.add_argument(
        "--try-live",
        action="store_true",
        help="Attempt live collection. Protected sites are not scraped; demo data is used.",
    )
    return parser.parse_args(argv)


def collect_listings(count: int, seed: int, try_live: bool) -> tuple[list[dict[str, str]], str]:
    if try_live:
        print(LIVE_SCRAPE_DISABLED_REASON, file=sys.stderr)
    if count < 550:
        raise ValueError("Record count must be at least 550.")
    return build_demo_listings(count=count, seed=seed), "demo_sample"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows, origin = collect_listings(count=args.count, seed=args.seed, try_live=args.try_live)
    output_path = args.output if args.output.is_absolute() else (PROJECT_ROOT / args.output)
    write_csv(output_path, rows)
    print(f"Wrote {len(rows)} records to {output_path}")
    print(f"Data origin: {origin} (not live-scraped)")
    print(f"Cities: {len(CITIES)}, categories: {len(CATEGORIES)}, sources: {len(DEMO_SOURCES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
