import csv
import ssl
from pathlib import Path
from typing import Iterable, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

CSV_FILES = [
    Path("exportados/export_All-mCabecas-dia-imbativel.csv"),
    Path("exportados/export_All-mBackground-dia-imbativel.csv"),
    Path("exportados/export_All-mAssinaturas-dia-imbativel.csv"),
    Path("exportados/export_All-mTrilhas-dia-imbativel.csv"),
]


def load_urls_from_csv(csv_path: Path) -> Iterable[Tuple[int, str]]:
    if not csv_path.exists():
        print(f"[AVISO] Arquivo não encontrado: {csv_path}")
        return []

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if "urlFile" not in reader.fieldnames:
            print(f"[AVISO] Coluna 'urlFile' ausente em {csv_path}")
            return []

        for idx, row in enumerate(reader, start=1):
            url = (row.get("urlFile") or "").strip()
            if url:
                yield idx, url


def fetch_status(url: str, context: ssl.SSLContext) -> int:
    try:
        with urlopen(url, context=context, timeout=10) as response:
            return response.status
    except HTTPError as exc:
        return exc.code
    except URLError:
        return 0


def main() -> None:
    context = ssl.create_default_context()
    overall_errors = 0

    for csv_path in CSV_FILES:
        print(f"\nVerificando URLs em {csv_path}...")
        for row_number, url in load_urls_from_csv(csv_path):
            status = fetch_status(url, context)
            status_label = status or "ERROR"

            if status != 200:
                overall_errors += 1
                print(f"  [FALHA] linha {row_number}: {url} -> {status_label}")
            else:
                print(f"  [OK]    linha {row_number}: {url}")

    if overall_errors:
        print(f"\nConcluído com {overall_errors} falhas.")
    else:
        print("\nTodas as URLs responderam com status 200.")


if __name__ == "__main__":
    main()
