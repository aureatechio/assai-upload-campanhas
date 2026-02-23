import csv
import os
from datetime import datetime
from typing import Dict, List
from urllib.parse import quote

BASE_PATH = r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\Sabado"
EXPORT_DIR = "exportados"
BASE_FIREBASE_URL = "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/"

TOKEN_BY_BUCKET: Dict[str, str] = {
    "cabeca": "629cda73-b302-4696-9a3b-015ccc586a35",
    "assinatura": "9442f0b8-8dc6-43ed-9431-91e6c0ed5572",
    "backgroundOferta": "531796ff-4d81-4d29-9cf5-c53edb8aaa7f",
    "trilha": "7d2e4acc-15fa-46f0-9d3d-7b026db1f96b",
}

MEDIA_EXTS = (".mp4", ".mp3", ".wav")
BG_EXTS = (".mp4", ".png", ".jpg", ".jpeg")

CAMPAIGNS = [
    {
        "folder": "GENÉRICO SEM HORÁRIO",
        "slug": "sabado-generico-sem-horario",
        "option_sheet": "sabadoGenericoSemHorario",
        "display": "Sabado Generico Sem Horario",
    },
    {
        "folder": "GENÉRICO COM HORÁRIO",
        "slug": "sabado-generico-com-horario",
        "option_sheet": "sabadoGenericoComHorario",
        "display": "Sabado Generico Com Horario",
    },
]


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


def scan_files(root: str, exts: tuple, recursive: bool = False) -> List[str]:
    if not os.path.isdir(root):
        return []
    if recursive:
        found: List[str] = []
        for base, _, files in os.walk(root):
            for item in sorted(files):
                if item.lower().endswith(exts):
                    found.append(os.path.join(base, item))
        return found
    return [
        os.path.join(root, item)
        for item in sorted(os.listdir(root))
        if item.lower().endswith(exts)
    ]


def write_csv(path: str, headers: List[str], rows: List[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def media_rows(option_sheet: str, file_paths: List[str], bucket: str, date_str: str) -> List[dict]:
    rows: List[dict] = []
    for path in file_paths:
        name = os.path.basename(path)
        rows.append(
            {
                "ligacaoCampanhaFieldName": option_sheet,
                "locucaoTranscrita": "",
                "nameFile": name,
                "OS Formato modelo": extract_format_from_filename(name),
                "urlFile": get_firebase_url(bucket, name),
                "Creation Date": date_str,
            }
        )
    return rows


def generate_for_campaign(campaign: Dict[str, str], date_str: str) -> None:
    folder = os.path.join(BASE_PATH, campaign["folder"])
    slug = campaign["slug"]
    option_sheet = campaign["option_sheet"]

    cabeca_files = scan_files(os.path.join(folder, "CABEÇA"), MEDIA_EXTS)
    ass_files = scan_files(os.path.join(folder, "ENCERRAMENTO"), MEDIA_EXTS)
    bg_files = scan_files(os.path.join(folder, "BG OFERTAS"), BG_EXTS, recursive=True)

    headers = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]

    write_csv(
        os.path.join(EXPORT_DIR, f"export_All-mCabecas-{slug}.csv"),
        headers,
        media_rows(option_sheet, cabeca_files, "cabeca", date_str),
    )
    write_csv(
        os.path.join(EXPORT_DIR, f"export_All-mAssinaturas-{slug}.csv"),
        headers,
        media_rows(option_sheet, ass_files, "assinatura", date_str),
    )
    write_csv(
        os.path.join(EXPORT_DIR, f"export_All-mBackground-{slug}.csv"),
        headers,
        media_rows(option_sheet, bg_files, "backgroundOferta", date_str),
    )
    write_csv(
        os.path.join(EXPORT_DIR, f"export_All-mTrilhas-{slug}.csv"),
        headers,
        [],
    )

    form_headers = [
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
    form_rows = [
        {
            "ajusteCampanha": "acelera",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "",
            "option": campaign["display"],
            "optionSheet": option_sheet,
            "OS materiais": "Filme de 15s , Filme de 30s , Spot de Radio 15s , Spot de Radio 30s",
            "OS type midia": "Tv , Radio",
        }
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    write_csv(
        os.path.join(EXPORT_DIR, f"export_All-formCampanhas-{slug}-{timestamp}.csv"),
        form_headers,
        form_rows,
    )

    print(
        f"{slug}: cabeca={len(cabeca_files)} assinatura={len(ass_files)} "
        f"background={len(bg_files)} trilha=0 form=1"
    )


def main() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")
    for campaign in CAMPAIGNS:
        generate_for_campaign(campaign, current_date)


if __name__ == "__main__":
    main()
