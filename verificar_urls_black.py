import argparse
import csv
import ssl
from pathlib import Path
from typing import Iterable, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def build_csv_list(slug: str) -> List[Path]:
    prefix = f"export_All-m{{}}-{slug}.csv"
    return [
        Path("exportados") / prefix.format("Cabecas"),
        Path("exportados") / prefix.format("Background"),
        Path("exportados") / prefix.format("Assinaturas"),
        Path("exportados") / prefix.format("Trilhas"),
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

        for idx, row in enumerate(reader, start=2):
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valida URLs presentes nos CSVs exportados."
    )
    parser.add_argument(
        "--slug",
        default="black",
        help="Slug usado no nome dos arquivos exportados (ex: black, black-imbativel).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_files = build_csv_list(args.slug)
    context = ssl.create_default_context()
    overall_errors = 0

    for csv_path in csv_files:
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
