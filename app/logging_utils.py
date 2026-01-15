import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


def emit_log(
    http_method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    context: Optional[Dict[str, Any]] = None,
):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "severity": "INFO",
        "req_id": str(uuid.uuid4()),
        "method": http_method,
        "path": endpoint,
        "status": status_code,
        "latency_ms": round(duration_ms, 2),
    }

    if context:
        log_entry |= context  # merge extra fields

    print(json.dumps(log_entry))

