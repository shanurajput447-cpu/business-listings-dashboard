# Backend

FastAPI application for the Business Listings Dashboard.

## Setup

1. Create and activate a virtual environment.
2. Copy `.env.example` to `.env` and fill in MySQL credentials.
3. Install dependencies from `requirements.txt`.
4. Run the API with Uvicorn (see the root README).

Swagger is available at `/docs` when the server is running.

Database credentials use `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`.

Live routes include `GET /api/health` and `GET /api/health/database`. Bulk insert, dashboard aggregations, and scraping are not implemented yet.
