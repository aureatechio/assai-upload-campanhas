"""Reusable Bubble Data API upload module.

Extracted from bubble_upload_csvs.py for use by both the CLI script
and the Flask web interface.
"""

import csv
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = os.getenv(
    "BUBBLE_BASE_URL",
    "https://assai.geofast.ai/version-test/api/1.1/obj",
)
AJUSTE_CAMPANHA_ID = os.getenv(
    "AJUSTE_CAMPANHA_ID", "1748539524382x567101974073716860"
)

# ── Category → Bubble table (API object name) ────────────────────────
CATEGORY_TO_TABLE: Dict[str, str] = {
    "abertura": "mCabeca",
    "assinatura": "mAssinatura",
    "bg": "mBackgroundOferta",
    "trilha": "mTrilha",
    "campanhas": "formCampanha",
}

# ── Category → file-name suffix used in export_All-{suffix}-*.csv ────
CATEGORY_TO_FILE_SUFFIX: Dict[str, str] = {
    "abertura": "mCabecas",
    "assinatura": "mAssinaturas",
    "bg": "mBackground",
    "trilha": "mTrilhas",
    "campanhas": "formCampanhas",
}

# ── Field-level transformations ──────────────────────────────────────
FIELD_OVERRIDES: Dict[str, Dict[str, str]] = {
    "mTrilha": {"nameFile": "nameFIle"},
    "mBackgroundOferta": {"OS Formato modelo": "OS FormatoModelo"},
}
DROP_FIELDS = {"Creation Date", "Modified Date", "Slug", "Creator"}
DROP_FIELDS_BY_TABLE: Dict[str, set] = {
    "mBackgroundOferta": {"locucaoTranscrita"},
    "mTrilha": {"locucaoTranscrita", "OS Formato modelo"},
}
BOOLEAN_FIELDS = {"ativo"}
AJUSTE_CAMPANHA_TABLES = {"formCampanha"}
CSV_LIST_FIELDS = {"OS materiais", "OS type midia"}
OPTION_VALUE_MAP: Dict[str, Dict[str, str]] = {
    "OS materiais": {
        "Spot de Radio 15s": "Spot de Rádio 15s",
        "Spot de Radio 30s": "Spot de Rádio 30s",
    },
    "OS type midia": {
        "Radio": "Rádio",
        "TV": "Tv",
    },
}
LIST_FIELDS_BY_TABLE: Dict[str, set] = {
    "mAssinatura": {"ligacaoCampanhaFieldName"},
    "mBackgroundOferta": {"ligacaoCampanhaFieldName"},
    "mTrilha": {"ligacaoCampanhaFieldName"},
}


# ── Helper functions ─────────────────────────────────────────────────

def load_rows(csv_path: Path, max_records: Optional[int] = None) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not any((value or "").strip() for value in row.values()):
                continue
            rows.append(row)
            if max_records and len(rows) >= max_records:
                break
    return rows


def coerce_boolean(value: str) -> Optional[bool]:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"sim", "true", "1", "yes"}:
        return True
    if lowered in {"nao", "não", "false", "0", "no"}:
        return False
    return None


def coerce_list(value: str) -> List[str]:
    if value is None:
        return []
    parts = [part.strip() for part in value.split(",")]
    return [part for part in parts if part]


def map_option_values(field: str, values: List[str]) -> List[str]:
    mapping = OPTION_VALUE_MAP.get(field, {})
    if not mapping:
        return values
    return [mapping.get(item, item) for item in values]


def apply_overrides(table: str, row: Dict[str, str]) -> Dict[str, Any]:
    overrides = FIELD_OVERRIDES.get(table, {})
    mapped: Dict[str, Any] = {}
    drop_for_table = DROP_FIELDS_BY_TABLE.get(table, set())
    for key, value in row.items():
        if key in DROP_FIELDS:
            continue
        if key in drop_for_table:
            continue
        mapped_key = overrides.get(key, key)
        if value == "":
            mapped[mapped_key] = None
        elif mapped_key in CSV_LIST_FIELDS:
            items = coerce_list(value)
            mapped[mapped_key] = map_option_values(mapped_key, items)
        else:
            mapped[mapped_key] = value

    for field in BOOLEAN_FIELDS:
        if field in mapped:
            coerced = coerce_boolean(str(mapped[field]))
            if coerced is not None:
                mapped[field] = coerced

    if table in AJUSTE_CAMPANHA_TABLES and "ajusteCampanha" in mapped:
        mapped["ajusteCampanha"] = AJUSTE_CAMPANHA_ID

    if "categoriaLiberacao" in mapped and not mapped["categoriaLiberacao"]:
        mapped.pop("categoriaLiberacao", None)

    list_fields = LIST_FIELDS_BY_TABLE.get(table, set())
    for field in list_fields:
        if field in mapped:
            mapped[field] = coerce_list(str(mapped[field]))

    return mapped


def post_record(base_url: str, table: str, payload: Dict[str, Any], token: str) -> None:
    url = f"{base_url}/{quote(table)}"
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    request = Request(url, data=body, method="POST")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=30) as response:
        response.read()


def _read_error_body(error: Exception) -> str:
    """Read the HTTP error body once and cache it on the exception object."""
    if not isinstance(error, HTTPError):
        return ""
    cached = getattr(error, "_cached_body", None)
    if cached is not None:
        return cached
    try:
        body = error.read().decode("utf-8")
    except Exception:
        body = ""
    error._cached_body = body
    return body


def format_error(error: Exception) -> str:
    if isinstance(error, HTTPError):
        payload = _read_error_body(error)
        return f"HTTP {error.code} {payload}".strip()
    if isinstance(error, URLError):
        return f"URLError {error.reason}"
    return str(error)


def has_unrecognized_formato_field(error: Exception) -> bool:
    body = _read_error_body(error)
    return "Unrecognized field: OS Formato modelo" in body or \
           "Unrecognized field: OS FormatoModelo" in body


# ── High-level orchestrator ──────────────────────────────────────────

def upload_csv_to_bubble(
    csv_path: str,
    table: str,
    base_url: str,
    token: str,
    delay: float = 0.2,
    progress_callback: Optional[Callable[[int, int, Optional[str]], None]] = None,
) -> Dict[str, Any]:
    """Upload all rows from a CSV to a Bubble table.

    Args:
        csv_path: Path to the CSV file.
        table: Bubble table/object name (e.g. "mCabeca").
        base_url: Bubble Data API base URL.
        token: Bearer token for authentication.
        delay: Seconds to wait between POST requests.
        progress_callback: Optional ``fn(current, total, error_msg)``
            called after each record.

    Returns:
        dict with keys ``total``, ``success``, ``failed``, ``errors``.
    """
    path = Path(csv_path)
    rows = load_rows(path)
    total = len(rows)
    success = 0
    failed = 0
    errors: List[str] = []

    for idx, row in enumerate(rows):
        payload = apply_overrides(table, row)
        error_msg: Optional[str] = None
        try:
            post_record(base_url, table, payload, token)
            success += 1
        except Exception as exc:
            # Retry without formato field if Bubble rejects it
            if (
                "OS Formato modelo" in payload or "OS FormatoModelo" in payload
            ) and has_unrecognized_formato_field(exc):
                payload.pop("OS Formato modelo", None)
                payload.pop("OS FormatoModelo", None)
                try:
                    post_record(base_url, table, payload, token)
                    success += 1
                except Exception as retry_exc:
                    failed += 1
                    error_msg = format_error(retry_exc)
                    errors.append(f"Row {idx + 1}: {error_msg}")
            else:
                failed += 1
                error_msg = format_error(exc)
                errors.append(f"Row {idx + 1}: {error_msg}")

        if progress_callback:
            progress_callback(idx + 1, total, error_msg)

        if delay and idx < total - 1:
            time.sleep(delay)

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "errors": errors[:20],  # cap to avoid huge payloads
    }
