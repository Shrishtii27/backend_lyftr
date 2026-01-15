import hmac
import hashlib
import json
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Header, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.config import WEBHOOK_SECRET
from app.models import init_db, get_connection
from app.storage import save_message, list_messages, get_stats
from app.metrics import (
    track_http,
    track_webhook,
    record_latency,
    export_prometheus,
)
from app.logging_utils import emit_log


app = FastAPI(title="Messaging API")

# ------------------------------------------------------------------
# Middleware: metrics + structured logging
# ------------------------------------------------------------------

@app.middleware("http")
async def collect_metrics_and_logs(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    elapsed_ms = (time.time() - start_time) * 1000

    record_latency(elapsed_ms)
    track_http(request.url.path, response.status_code)

    emit_log(
        http_method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration_ms=elapsed_ms,
    )
    return response


# ------------------------------------------------------------------
# Startup
# ------------------------------------------------------------------

@app.on_event("startup")
def on_startup():
    init_db()


# ------------------------------------------------------------------
# Health endpoints
# ------------------------------------------------------------------

@app.get("/health/live")
def live_check():
    return {"status": "alive"}


@app.get("/health/ready")
def readiness_check():
    if not WEBHOOK_SECRET:
        return JSONResponse(
            status_code=503,
            content={"status": "missing webhook secret"},
        )

    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "database unavailable"},
        )

    return {"status": "ready"}


# ------------------------------------------------------------------
# Pydantic model
# ------------------------------------------------------------------

class WebhookMessage(BaseModel):
    message_id: str = Field(min_length=1)
    from_: str = Field(alias="from", pattern=r"^\+\d+$")
    to: str = Field(pattern=r"^\+\d+$")
    ts: str = Field(pattern=r"Z$")
    text: Optional[str] = Field(default=None, max_length=4096)

    class Config:
        populate_by_name = True


# ------------------------------------------------------------------
# Signature verification
# ------------------------------------------------------------------

def is_valid_signature(secret: str, body: bytes, provided_sig: str) -> bool:
    digest = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(digest, provided_sig)


# ------------------------------------------------------------------
# Webhook endpoint
# ------------------------------------------------------------------

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_signature: str = Header(None),
):
    raw_payload = await request.body()

    if not x_signature or not WEBHOOK_SECRET:
        track_webhook("invalid_signature")
        raise HTTPException(status_code=401, detail="invalid signature")

    if not is_valid_signature(WEBHOOK_SECRET, raw_payload, x_signature):
        track_webhook("invalid_signature")
        raise HTTPException(status_code=401, detail="invalid signature")

    try:
        parsed = json.loads(raw_payload)
        message = WebhookMessage(**parsed)
    except Exception as exc:
        track_webhook("validation_error")
        raise HTTPException(status_code=422, detail=str(exc))

    created = save_message(
        {
            "message_id": message.message_id,
            "from": message.from_,
            "to": message.to,
            "ts": message.ts,
            "text": message.text,
        }
    )

    track_webhook("created" if created else "duplicate")

    return {"status": "ok"}



# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------

@app.get("/metrics")
def metrics():
    return Response(
        content=export_prometheus(),
        media_type="text/plain",
    )

# ------------------------------------------------------------------
# Messages listing
# ------------------------------------------------------------------

@app.get("/messages")
def get_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_msisdn: Optional[str] = Query(None, alias="from"),
    since: Optional[str] = None,
    q: Optional[str] = None,
):
    rows, total = list_messages(
        limit=limit,
        offset=offset,
        from_msisdn=from_msisdn,
        since=since,
        q=q,
    )

    return {
        "data": rows,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
# ------------------------------------------------------------------
# Stats
# ------------------------------------------------------------------

@app.get("/stats")
def get_stats():
    return get_stats()






