import unittest

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.main import app
from app.models import ListingMaster
from app.services.dashboard import _grouped_count_statement


class FakeResult:
    def __init__(self, rows: list[tuple[str, int]]) -> None:
        self._rows = rows

    def all(self) -> list[tuple[str, int]]:
        return self._rows


class FakeSession:
    def __init__(
        self,
        rows: list[tuple[str, int]] | None = None,
        execute_error: Exception | None = None,
    ) -> None:
        self.rows = rows or []
        self.execute_error = execute_error
        self.executed = False

    def execute(self, _statement: object) -> FakeResult:
        self.executed = True
        if self.execute_error:
            raise self.execute_error
        return FakeResult(self.rows)


class DashboardEndpointTests(unittest.TestCase):
    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def _override_session(self, session: FakeSession) -> TestClient:
        def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        return TestClient(app)

    def test_city_counts_return_grouped_rows(self) -> None:
        session = FakeSession(rows=[("Mumbai", 50), ("Delhi", 45)])
        client = self._override_session(session)
        response = client.get("/api/dashboard/city")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(session.executed)
        self.assertEqual(
            response.json(),
            [{"city": "Mumbai", "count": 50}, {"city": "Delhi", "count": 45}],
        )

    def test_category_counts_return_grouped_rows(self) -> None:
        session = FakeSession(rows=[("Restaurant", 60), ("Cafe", 40)])
        client = self._override_session(session)
        response = client.get("/api/dashboard/category")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"category": "Restaurant", "count": 60}, {"category": "Cafe", "count": 40}],
        )

    def test_source_counts_return_grouped_rows(self) -> None:
        session = FakeSession(rows=[("demo_sample", 150), ("demo_sample_local", 150)])
        client = self._override_session(session)
        response = client.get("/api/dashboard/source")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"source": "demo_sample", "count": 150},
                {"source": "demo_sample_local", "count": 150},
            ],
        )

    def test_null_and_empty_groups_are_returned_as_unknown(self) -> None:
        session = FakeSession(rows=[("Unknown", 3), ("Pune", 1)])
        client = self._override_session(session)
        response = client.get("/api/dashboard/city")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"city": "Unknown", "count": 3}, {"city": "Pune", "count": 1}],
        )

    def test_dashboard_query_uses_group_by_and_count(self) -> None:
        compiled = str(
            _grouped_count_statement(ListingMaster.city, "city").compile(
                compile_kwargs={"literal_binds": True}
            )
        ).lower()
        self.assertIn("group by", compiled)
        self.assertIn("count(", compiled)
        self.assertIn("listing_master", compiled)

    def test_dashboard_endpoint_returns_500_on_database_error(self) -> None:
        session = FakeSession(execute_error=SQLAlchemyError("query failed"))
        client = self._override_session(session)
        response = client.get("/api/dashboard/category")
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
