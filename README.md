Initial backend submission
FastAPI Messaging Webhook Service
This repository contains a containerized backend service built with FastAPI that mimics a WhatsApp-style inbound messaging webhook.
 The application securely ingests messages, ensures idempotent storage, and exposes APIs for message retrieval, analytics, health checks, and metrics.
The service is designed to work seamlessly with the provided automated evaluation script.

Technology Stack
Programming Language: Python 3.12


Web Framework: FastAPI


Database: SQLite


Containerization: Docker, Docker Compose


Data Validation: Pydantic


Observability: Structured JSON logs, Prometheus-style metrics



Repository Layout
app/
├── main.py          # FastAPI app, routes, middleware
├── config.py        # Environment configuration
├── models.py        # Database initialization
├── storage.py       # Data access layer
├── metrics.py       # Metrics collection helpers
├── logging_utils.py # Structured logging utilities
Dockerfile
docker-compose.yml
Makefile
README.md


Running the Application
Prerequisites
Docker Desktop


Linux engine / WSL2 enabled (for Windows users)


Start the service
docker compose up --build

Once started, the API will be available at:
http://localhost:8000

Stop and clean up
docker compose down -v


Configuration
The service is fully configured through environment variables (defined in docker-compose.yml).
Required Variables
DATABASE_URL
 SQLite database connection string
 Example:
sqlite:////data/app.db

WEBHOOK_SECRET
 Shared secret used to validate incoming webhook signatures
Optional Variables
LOG_LEVEL
 Controls logging verbosity (default: INFO)

API Endpoints
Health Endpoints
GET /health/live
 Returns 200 OK when the application process is running.
GET /health/ready
 Returns 200 OK only if:
The database is accessible


WEBHOOK_SECRET is configured


Otherwise, returns 503.

Webhook Endpoint
POST /webhook
Receives inbound WhatsApp-like messages and stores them exactly once.
Required Headers
Content-Type: application/json
X-Signature: <hex HMAC-SHA256 signature>

Request Payload
{
  "message_id": "m1",
  "from": "+919876543210",
  "to": "+14155550100",
  "ts": "2025-01-15T10:00:00Z",
  "text": "Hello"
}

Behavior
Missing or invalid signature → 401


Invalid request body → 422


Duplicate message_id → 200 (idempotent)


Valid new message → 200 { "status": "ok" }


Duplicate webhook deliveries do not create duplicate database records.

List Messages
GET /messages
Returns stored messages with pagination and optional filters.
Query Parameters
limit (default: 50, min: 1, max: 100)


offset (default: 0)


from – filter by sender MSISDN


since – ISO-8601 UTC timestamp


q – case-insensitive text search


Response Example
{
  "data": [...],
  "total": 10,
  "limit": 50,
  "offset": 0
}

Messages are always ordered by:
ts ASC, message_id ASC


Analytics
GET /stats
Provides basic message-level statistics.
Response Example
{
  "total_messages": 123,
  "senders_count": 10,
  "messages_per_sender": [
    { "from": "+919876543210", "count": 50 }
  ],
  "first_message_ts": "2025-01-10T09:00:00Z",
  "last_message_ts": "2025-01-15T10:00:00Z"
}

If no messages exist, timestamp fields return null.

Metrics
GET /metrics
Exposes Prometheus-compatible metrics in plain text format.
Guaranteed metrics:
http_requests_total


webhook_requests_total


Always returns HTTP 200.

Logging
One JSON log entry per request


Logs include:


Timestamp


HTTP method and path


Response status


Request latency (milliseconds)


Webhook requests additionally log processing outcome


Logs are suitable for standard log aggregation tools.

Design Notes
Signature Validation
Webhook authenticity is verified using HMAC-SHA256, computed over the raw request body using a shared secret.
Idempotency
Message uniqueness is enforced using a PRIMARY KEY constraint on message_id.
 Duplicate webhook calls return success without inserting additional rows.
Validation
All incoming requests are validated using Pydantic models, ensuring consistent 422 responses for invalid input.
Pagination Strategy
The total field in /messages reflects the number of matching records before pagination is applied.
Observability
The system includes lightweight metrics and structured logging to provide operational visibility without unnecessary complexity.

Development Setup Used
VS Code


Docker Desktop


Occasional use of ChatGPT for explanations and guidance



Additional Notes
SQLite data is persisted using a Docker volume


No external services (Redis, PostgreSQL, etc.) are used


The application is designed to run unchanged under the provided evaluation script

