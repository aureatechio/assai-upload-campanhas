import argparse
import csv
import json
import os
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv
load_dotenv()

DEFAULT_BASE_URL = os.getenv("BUBBLE_BASE_URL", "https://assai.geofast.ai/version-test/api/1.1/obj")
AJUSTE_CAMPANHA_ID = os.getenv("AJUSTE_CAMPANHA_ID", "1748539524382x567101974073716860")

TABLE_PATTERNS: Dict[str, str] = {
    "mCabeca": "export_All-mCabecas-*.csv",
    "mAssinatura": "export_All-mAssinaturas-*.csv",
    "mBackgroundOferta": "export_All-mBackground-*.csv",
    "mTrilha": "export_All-mTrilhas-*.csv",
    "formCampanha": "export_All-formCampanhas-*.csv",
}

FIELD_OVERRIDES: Dict[str, Dict[str, str]] = {
    "mTrilha": {"nameFile": "nameFIle"},
    "mBackgroundOferta": {"OS Formato modelo": "OS FormatoModelo"},
}
DROP_FIELDS = {"Creation Date"}
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload de CSVs para o Bubble Data API."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--export-dir", default="exportados")
    parser.add_argument("--token", default=os.environ.get("BUBBLE_API_TOKEN"))
    parser.add_argument("--campaign-slug", help="Filtro por trecho do nome do arquivo.")
    parser.add_argument(
        "--table",
        action="append",
        help="Restringir a uma tabela (pode repetir).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Enviar todos os CSVs encontrados por tabela (padrao: ultimo).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Executa o upload (padrao: dry-run).",
    )
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def collect_csvs(
    export_dir: str,
    campaign_slug: Optional[str],
    tables_filter: Optional[Iterable[str]],
    include_all: bool,
) -> Dict[str, List[Path]]:
    base = Path(export_dir)
    tables = set(tables_filter) if tables_filter else None
    selected: Dict[str, List[Path]] = {}

    for table, pattern in TABLE_PATTERNS.items():
        if tables and table not in tables:
            continue
        candidates = sorted(
            base.glob(pattern),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        if campaign_slug:
            candidates = [item for item in candidates if campaign_slug in item.name]
        if not candidates:
            continue
        selected[table] = candidates if include_all else [candidates[0]]
    return selected


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


def apply_overrides(table: str, row: Dict[str, str]) -> Dict[str, str]:
    overrides = FIELD_OVERRIDES.get(table, {})
    mapped: Dict[str, str] = {}
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


def post_record(base_url: str, table: str, payload: Dict[str, str], token: str) -> None:
    url = f"{base_url}/{quote(table)}"
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    request = Request(url, data=body, method="POST")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=30) as response:
        response.read()


def format_error(error: Exception) -> str:
    if isinstance(error, HTTPError):
        try:
            payload = error.read().decode("utf-8")
        except Exception:
            payload = ""
        return f"HTTP {error.code} {payload}".strip()
    if isinstance(error, URLError):
        return f"URLError {error.reason}"
    return str(error)


def is_unrecognized_field_error(error: Exception, field_name: str) -> bool:
    if not isinstance(error, HTTPError):
        return False
    try:
        payload = error.read().decode("utf-8")
    except Exception:
        return False
    return f"Unrecognized field: {field_name}" in payload


def has_unrecognized_formato_field(error: Exception) -> bool:
    return is_unrecognized_field_error(error, "OS Formato modelo") or is_unrecognized_field_error(
        error, "OS FormatoModelo"
    )


def main() -> int:
    args = parse_args()
    if not args.token:
        print("Token nao informado. Use --token ou BUBBLE_API_TOKEN.")
        return 2

    csvs_by_table = collect_csvs(
        args.export_dir, args.campaign_slug, args.table, args.all
    )
    if not csvs_by_table:
        print("Nenhum CSV encontrado com os filtros informados.")
        return 1

    dry_run = not args.apply
    mode_label = "DRY-RUN" if dry_run else "UPLOAD"
    print(f"Modo: {mode_label}")
    print(f"Base URL: {args.base_url}")

    total_rows = 0
    total_success = 0
    total_failed = 0

    for table, csv_paths in csvs_by_table.items():
        for csv_path in csv_paths:
            rows = load_rows(csv_path, args.max_records)
            print(f"\nTabela: {table}")
            print(f"CSV: {csv_path.name}")
            print(f"Registros: {len(rows)}")
            total_rows += len(rows)

            if dry_run:
                continue

            for row in rows:
                payload = apply_overrides(table, row)
                try:
                    post_record(args.base_url, table, payload, args.token)
                    total_success += 1
                except Exception as exc:
                    # Fallback: alguns ambientes do Bubble nao possuem este campo no schema.
                    if (
                        "OS Formato modelo" in payload or "OS FormatoModelo" in payload
                    ) and has_unrecognized_formato_field(exc):
                        payload.pop("OS Formato modelo", None)
                        payload.pop("OS FormatoModelo", None)
                        try:
                            post_record(args.base_url, table, payload, args.token)
                            total_success += 1
                            if args.verbose:
                                print("Aviso: enviado sem campo de formato.")
                            continue
                        except Exception as retry_exc:
                            total_failed += 1
                            if args.verbose:
                                print(f"Erro: {format_error(retry_exc)}")
                    else:
                        total_failed += 1
                        if args.verbose:
                            print(f"Erro: {format_error(exc)}")
                if args.delay:
                    time.sleep(args.delay)

    print("\nResumo:")
    print(f"  Total linhas: {total_rows}")
    if not dry_run:
        print(f"  Sucesso: {total_success}")
        print(f"  Falhas: {total_failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
