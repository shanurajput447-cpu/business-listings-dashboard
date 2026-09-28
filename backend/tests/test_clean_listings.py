import unittest

from app.scraper.clean_listings import (
    clean_record,
    deduplicate_records,
    is_valid_record,
    normalize_phone,
    normalize_source,
    normalize_text,
    normalize_title_case,
    process_listings,
)


class NormalizeTests(unittest.TestCase):
    def test_trim_and_collapse_spaces(self) -> None:
        self.assertEqual(normalize_text("  Spice   Works  "), "Spice Works")

    def test_city_and_category_title_case(self) -> None:
        self.assertEqual(normalize_title_case("mumbai"), "Mumbai")
        self.assertEqual(normalize_title_case("electronics  store"), "Electronics Store")

    def test_source_lowercase(self) -> None:
        self.assertEqual(normalize_source("Demo_Sample"), "demo_sample")
        self.assertEqual(normalize_source(" demo sample "), "demo_sample")

    def test_phone_mobile_normalization(self) -> None:
        self.assertEqual(normalize_phone("9876543210"), "+91 9876543210")
        self.assertEqual(normalize_phone("+91-98765 43210"), "+91 9876543210")
        self.assertEqual(normalize_phone("022-3872427"), "022-3872427")


class ValidationTests(unittest.TestCase):
    def test_business_name_and_source_required(self) -> None:
        self.assertFalse(is_valid_record(clean_record({"business_name": " ", "source": "demo_sample"})))
        self.assertFalse(is_valid_record(clean_record({"business_name": "Cafe", "source": ""})))
        self.assertTrue(
            is_valid_record(
                clean_record(
                    {
                        "business_name": "Cafe",
                        "source": "demo_sample",
                        "category": "",
                        "city": "",
                        "address": "",
                        "phone": "",
                    }
                )
            )
        )


class DeduplicationTests(unittest.TestCase):
    def test_dedup_uses_name_address_city(self) -> None:
        rows = [
            {
                "business_name": "Spice Hub",
                "category": "Restaurant",
                "city": "Mumbai",
                "address": "12, Bandra, Mumbai",
                "phone": "+91 9000000001",
                "source": "demo_sample",
            },
            {
                "business_name": " spice  hub ",
                "category": "Restaurant",
                "city": "MUMBAI",
                "address": "12,  Bandra, Mumbai",
                "phone": "+91 9000000002",
                "source": "demo_sample_local",
            },
            {
                "business_name": "Spice Hub",
                "category": "Restaurant",
                "city": "Delhi",
                "address": "12, Bandra, Mumbai",
                "phone": "+91 9000000003",
                "source": "demo_sample",
            },
        ]
        cleaned = [clean_record(row) for row in rows]
        unique, removed = deduplicate_records(cleaned)
        self.assertEqual(removed, 1)
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0]["phone"], "+91 9000000001")

    def test_process_listings_counts(self) -> None:
        raw = [
            {
                "business_name": "  Alpha  ",
                "category": "gym",
                "city": "pune",
                "address": "1, Kothrud, Pune",
                "phone": "9876543210",
                "source": "DEMO_SAMPLE",
            },
            {
                "business_name": "",
                "category": "Gym",
                "city": "Pune",
                "address": "1, Kothrud, Pune",
                "phone": "9876543210",
                "source": "demo_sample",
            },
            {
                "business_name": "Alpha",
                "category": "Gym",
                "city": "Pune",
                "address": "1, Kothrud, Pune",
                "phone": "022-1234567",
                "source": "demo_sample_local",
            },
        ]
        cleaned, report = process_listings(raw)
        self.assertEqual(report["raw_record_count"], 3)
        self.assertEqual(report["invalid_record_count"], 1)
        self.assertEqual(report["valid_record_count"], 2)
        self.assertEqual(report["duplicate_count_removed"], 1)
        self.assertEqual(report["final_cleaned_record_count"], 1)
        self.assertEqual(report["missing_values_by_field"]["business_name"], 1)
        self.assertEqual(cleaned[0]["city"], "Pune")
        self.assertEqual(cleaned[0]["category"], "Gym")
        self.assertEqual(cleaned[0]["source"], "demo_sample")
        self.assertEqual(cleaned[0]["phone"], "+91 9876543210")


if __name__ == "__main__":
    unittest.main()
