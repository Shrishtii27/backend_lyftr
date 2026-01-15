from collections import defaultdict
from typing import Dict, Tuple, List


# Internal metric stores
_http_request_counter: Dict[Tuple[str, str], int] = defaultdict(int)
_webhook_result_counter: Dict[str, int] = defaultdict(int)
_request_latencies: List[float] = []


def track_http(path: str, status_code: int) -> None:
    _http_request_counter[(path, str(status_code))] += 1


def track_webhook(outcome: str) -> None:
    _webhook_result_counter[outcome] += 1


def record_latency(duration_ms: float) -> None:
    _request_latencies.append(duration_ms)


def export_prometheus() -> str:
    output = []

    # Always expose http_requests_total
    if not _http_request_counter:
        output.append(
            'http_requests_total{path="/metrics",status="200"} 0'
        )

    for (path, status), count in _http_request_counter.items():
        output.append(
            f'http_requests_total{{path="{path}",status="{status}"}} {count}'
        )

    # Always expose webhook_requests_total
    if not _webhook_result_counter:
        output.append(
            'webhook_requests_total{result="created"} 0'
        )

    for result, count in _webhook_result_counter.items():
        output.append(
            f'webhook_requests_total{{result="{result}"}} {count}'
        )

    # Minimal latency metric (count only)
    if _request_latencies:
        output.append(
            f'request_latency_ms_count {len(_request_latencies)}'
        )

    return "\n".join(output) + "\n"



