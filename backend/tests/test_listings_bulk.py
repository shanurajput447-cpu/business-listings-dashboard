import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.main import app


class FakeSession:
    def __init__(self, commit_error: Exception | None = None) -> None:
        self.added: list[object] = []
        self.committed = False
        self.rolled_back = False
        self._commit_error = commit_error

    def add_all(self, items: list[object]) -> None:
        self.added.extend(items)

    def commit(self) -> None:
        if self._commit_error:
            raise self._commit_error
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def _sample_listing() -> dict[str, str]:
    return {
        "business_name": "Spice Works MUM 001",
        "category": "Restaurant",
        "city": "Mumbai",
        "address": "73, Andheri West, Mumbai",
        "phone": "022-3872427",
        "source": "demo_sample",
    }


class BulkListingsEndpointTests(unittest.TestCase):
    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_bulk_insert_rejects_empty_payload(self) -> None:
        client = TestClient(app)
        response = client.post("/api/listings/bulk", json={"listings": []})
        self.assertEqual(response.status_code, 422)

    def test_bulk_insert_commits_records_and_returns_count(self) -> None:
        session = FakeSession()

        def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        payload = {"listings": [_sample_listing(), {**_sample_listing(), "city": "Pune"}]}
        response = client.post("/api/listings/bulk", json=payload)

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["inserted_count"], 2)
        self.assertEqual(len(session.added), 2)
        self.assertTrue(session.committed)
        self.assertFalse(session.rolled_back)

    def test_bulk_insert_rolls_back_on_database_error(self) -> None:
        session = FakeSession(commit_error=SQLAlchemyError("commit failed"))

        def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        response = client.post("/api/listings/bulk", json={"listings": [_sample_listing()]})

        self.assertEqual(response.status_code, 500)
        self.assertTrue(session.rolled_back)
        self.assertFalse(session.committed)

    def test_bulk_insert_does_not_use_unoverridden_session_factory(self) -> None:
        """The route must depend on get_db so tests can avoid a real MySQL write."""
        session = MagicMock()
        session.add_all = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()

        def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        response = client.post("/api/listings/bulk", json={"listings": [_sample_listing()]})
        self.assertEqual(response.status_code, 201)
        session.add_all.assert_called_once()
        session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
