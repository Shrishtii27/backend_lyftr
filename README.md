# FastAPI Messaging Webhook Service

A production-style FastAPI backend that ingests WhatsApp-like webhook messages securely, enforces idempotency, and exposes analytics, health checks, logs, and metrics. The service is fully containerized using Docker Compose with SQLite for storage.

---

## Features

- Secure webhook ingestion using HMAC-SHA256 signature validation
- Exactly-once message processing via database-level idempotency
- Paginated and filterable message listing
- Message analytics via /stats endpoint
- Liveness and readiness health probes
- Prometheus-style metrics exposure
- Structured JSON logging (one log per request)
- Dockerized setup with environment-based configuration

---

## Tech Stack

- Python 3
- FastAPI
- SQLite
- Docker & Docker Compose
- Pydantic
- Prometheus-compatible metrics

---

## Project Structure
app/
main.py        # FastAPI app, routes, middleware
models.py     # Database initialization
storage.py    # Database operations
metrics.py    # Metrics helpers
loggins.py    # Structured JSON logging
config.py     # Environment configuration
Dockerfile
docker-compose.yml
Makefile
requirements.txt
README.md

---

## Configuration

The service uses environment variables for configuration:

| Variable | Description |
|--------|------------|
| WEBHOOK_SECRET | Secret key for webhook HMAC verification |
| DATABASE_URL | SQLite database URL |
| LOG_LEVEL | Logging level (INFO / DEBUG) |

---

## Running the Service

Set environment variables:

```bash
export WEBHOOK_SECRET="testsecret"
export DATABASE_URL="sqlite:////data/app.db"
export LOG_LEVEL="INFO"

Health Endpoints
	•	GET /health/live
Returns 200 when the application is running.
	•	GET /health/ready
Returns 200 only if the database is reachable and required configuration is set.

⸻

Webhook Ingestion

POST /webhook

Ingests inbound messages exactly once.
	•	Validates HMAC signature using the raw request body
	•	Rejects invalid signatures with 401
	•	Validates request payload using Pydantic
	•	Enforces idempotency using unique message_id
	•	Returns 200 for both new and duplicate messages

⸻

Messages Listing

GET /messages

Supports:
	•	Pagination using limit and offset
	•	Filtering by sender
	•	Filtering by timestamp
	•	Case-insensitive text search

Results are ordered by timestamp ascending, then message_id.

⸻

Stats Endpoint

GET /stats

Provides message-level analytics:
	•	Total messages
	•	Unique sender count
	•	Top senders by message volume
	•	First and last message timestamps

⸻

Metrics

GET /metrics

Exposes Prometheus-compatible metrics including:
	•	Total HTTP requests
	•	Webhook processing outcomes
	•	Request latency measurements

⸻

Logging
	•	One structured JSON log per request
	•	Includes request_id, path, method, status, and latency
	•	Webhook logs include message-level processing details
	•	Suitable for log aggregation and jq-based inspection

⸻

Design Decisions
	•	Idempotency is enforced at the database level using a primary key
	•	HMAC verification is done before payload validation
	•	SQLite is used for simplicity and portability
	•	Middleware is used for consistent logging and metrics collection
	•	All configuration follows 12-factor principles

⸻

