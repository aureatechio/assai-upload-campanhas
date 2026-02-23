import csv
import os
from datetime import datetime
from typing import Dict, List
from urllib.parse import quote

CAMPAIGN_SLUG = "super-sabado"
CAMPAIGN_BASE_PATH = (
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\SUPER SABADO"
)
EXPORT_DIR = "exportados"
BASE_FIREBASE_URL = "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/"

TOKEN_BY_BUCKET: Dict[str, str] = {
    "cabeca": "629cda73-b302-4696-9a3b-015ccc586a35",
    "assinatura": "9442f0b8-8dc6-43ed-9431-91e6c0ed5572",
    "backgroundOferta": "531796ff-4d81-4d29-9cf5-c53edb8aaa7f",
    "trilha": "7d2e4acc-15fa-46f0-9d3d-7b026db1f96b",
}

CAMPAIGN = {
    "display": "Super Sabado Generico Nacional",
    "option_sheet": "superSabadoGenerico",
}

MEDIA_EXTS = (".mp4", ".mp3", ".wav")
BG_EXTS = (".mp4", ".png", ".jpg", ".jpeg")


def get_firebase_url(bucket_name: str, filename: str) -> str:
    token = TOKEN_BY_BUCKET[bucket_name]
    encoded_filename = quote(filename)
    return f"{BASE_FIREBASE_URL}{bucket_name}%2F{encoded_filename}?alt=media&token={token}"


def extract_format_from_filename(filename: str) -> str:
    lowered = filename.lower()
    if "16x9" in lowered:
        return "16x9"
    if "9x16" in lowered:
        return "9x16"
    if "1x1" in lowered:
        return "1x1"
    return "16x9"


def ensure_export_dir() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)


def scan_media_files(folder_path: str, exts: tuple = MEDIA_EXTS) -> List[str]:
    if not os.path.isdir(folder_path):
        return []
    return [
        item
        for item in sorted(os.listdir(folder_path))
        if item.lower().endswith(exts)
    ]


def write_csv(output_path: str, fieldnames: List[str], rows: List[dict]) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def resolve_folder(*candidates: str) -> str:
    for candidate in candidates:
        path = os.path.join(CAMPAIGN_BASE_PATH, candidate)
        if os.path.isdir(path):
            return path
    return os.path.join(CAMPAIGN_BASE_PATH, candidates[0])


def generate_media_csv(kind: str, folder: str, bucket: str, current_date: str, exts: tuple) -> int:
    rows = []
    for media_file in scan_media_files(folder, exts):
        rows.append(
            {
                "ligacaoCampanhaFieldName": CAMPAIGN["option_sheet"],
                "locucaoTranscrita": "",
                "nameFile": media_file,
                "OS Formato modelo": extract_format_from_filename(media_file),
                "urlFile": get_firebase_url(bucket, media_file),
                "Creation Date": current_date,
            }
        )

    output_path = os.path.join(EXPORT_DIR, f"export_All-{kind}-{CAMPAIGN_SLUG}.csv")
    fieldnames = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]
    write_csv(output_path, fieldnames, rows)
    return len(rows)


def generate_form_csv() -> int:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = os.path.join(
        EXPORT_DIR, f"export_All-formCampanhas-{CAMPAIGN_SLUG}-{timestamp}.csv"
    )
    fieldnames = [
        "ajusteCampanha",
        "ativo",
        "categoriaLiberacao",
        "colorLetras",
        "formCelebridade",
        "formSelo",
        "imagem",
        "option",
        "optionSheet",
        "OS materiais",
        "OS type midia",
    ]
    rows = [
        {
            "ajusteCampanha": "acelera",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "",
            "option": CAMPAIGN["display"],
            "optionSheet": CAMPAIGN["option_sheet"],
            "OS materiais": "Filme de 15s , Filme de 30s , Spot de Radio 15s , Spot de Radio 30s",
            "OS type midia": "Tv , Radio",
        }
    ]
    write_csv(output_path, fieldnames, rows)
    return len(rows)


def main() -> None:
    ensure_export_dir()
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    cabeca_count = generate_media_csv(
        kind="mCabecas",
        folder=resolve_folder("CABECA", "CABEÇA"),
        bucket="cabeca",
        current_date=current_date,
        exts=MEDIA_EXTS,
    )
    assinatura_count = generate_media_csv(
        kind="mAssinaturas",
        folder=resolve_folder("ENCERRAMENTO", "ASSINATURA"),
        bucket="assinatura",
        current_date=current_date,
        exts=MEDIA_EXTS,
    )
    bg_count = generate_media_csv(
        kind="mBackground",
        folder=resolve_folder("BG", "BG OFERTAS", "BACKGROUND"),
        bucket="backgroundOferta",
        current_date=current_date,
        exts=BG_EXTS,
    )
    trilha_count = generate_media_csv(
        kind="mTrilhas",
        folder=resolve_folder("TRILHA"),
        bucket="trilha",
        current_date=current_date,
        exts=MEDIA_EXTS,
    )
    form_count = generate_form_csv()

    print(
        f"{CAMPAIGN_SLUG}: cabeca={cabeca_count} assinatura={assinatura_count} "
        f"background={bg_count} trilha={trilha_count} form={form_count}"
    )


if __name__ == "__main__":
    main()
