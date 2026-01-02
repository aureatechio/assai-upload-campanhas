import csv
import os
from datetime import datetime
from typing import Dict, List
from urllib.parse import quote

CAMPAIGN_BASE_PATH = (
    "G:\\Drives compartilhados\\__JOBS 2025\\_ASSAI\\_ROBO ASSAI\\MIDIAS\\DIA IMBATIVEL DEZEMBRO"
)
EXPORT_DIR = "exportados"
BASE_FIREBASE_URL = "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/"

TOKEN_BY_BUCKET: Dict[str, str] = {
    "cabeca": "629cda73-b302-4696-9a3b-015ccc586a35",
    "assinatura": "9442f0b8-8dc6-43ed-9431-91e6c0ed5572",
    "backgroundOferta": "531796ff-4d81-4d29-9cf5-c53edb8aaa7f",
    "trilha": "7d2e4acc-15fa-46f0-9d3d-7b026db1f96b",
}

DIR_NAMES = {
    "cabeca": "CABE\u00c7A",
    "assinatura": "ASSINATURA",
    "background": "BG",
    "trilha": "TRILHA",
}

PERIOD_DIR_MAP = {
    "HOJE": "\u00c9 HOJE",
    "AMANHA": "\u00c9 AMANH\u00c3",
    "GENERICO": "GEN\u00c9RICO",
}

CAMPAIGNS = [
    {
        "period": "HOJE",
        "region": "NACIONAL",
        "campaign_field": "diaImbativelDezHoje",
        "display": "Dia Imbat\u00edvel Dezembro Hoje Nacional",
        "option_sheet": "diaImbativelDezHoje",
    },
    {
        "period": "HOJE",
        "region": "MG",
        "campaign_field": "diaImbativelDezHojeMg",
        "display": "Dia Imbat\u00edvel Dezembro Hoje Mg",
        "option_sheet": "diaImbativelDezHojeMg",
    },
    {
        "period": "AMANHA",
        "region": "NACIONAL",
        "campaign_field": "diaImbativelDezAmanha",
        "display": "Dia Imbat\u00edvel Dezembro Amanha Nacional",
        "option_sheet": "diaImbativelDezAmanha",
    },
    {
        "period": "AMANHA",
        "region": "MG",
        "campaign_field": "diaImbativelDezAmanhaMg",
        "display": "Dia Imbat\u00edvel Dezembro Amanha Mg",
        "option_sheet": "diaImbativelDezAmanhaMg",
    },
    {
        "period": "GENERICO",
        "region": "NACIONAL",
        "campaign_field": "diaImbativelDezGenerico",
        "display": "Dia Imbat\u00edvel Dezembro Generico Nacional",
        "option_sheet": "diaImbativelDezGenerico",
    },
    {
        "period": "GENERICO",
        "region": "MG",
        "campaign_field": "diaImbativelDezGenericoMg",
        "display": "Dia Imbat\u00edvel Dezembro Generico Mg",
        "option_sheet": "diaImbativelDezGenericoMg",
    },
]

FORMAT_ORDER = ["16x9", "1x1", "9x16"]


def get_firebase_url(bucket_name: str, filename: str) -> str:
    token = TOKEN_BY_BUCKET.get(bucket_name)
    if not token:
        raise ValueError(f"Token nao configurado para bucket '{bucket_name}'")

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


def scan_media_files(folder_path: str) -> List[str]:
    if not os.path.isdir(folder_path):
        return []

    files: List[str] = []
    for item in sorted(os.listdir(folder_path)):
        lowered = item.lower()
        if lowered.endswith((".mp4", ".mp3", ".wav")):
            files.append(item)

    return files


def ensure_export_dir() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)


def generate_cabecas_csv(current_date: str) -> int:
    print("Gerando CSV de cabecas...")
    rows = []

    for campaign in CAMPAIGNS:
        period_dir = PERIOD_DIR_MAP[campaign["period"]]
        folder_path = os.path.join(
            CAMPAIGN_BASE_PATH,
            DIR_NAMES["cabeca"],
            campaign["region"],
            period_dir,
        )
        files = scan_media_files(folder_path)

        for media_file in files:
            rows.append(
                {
                    "ligacaoCampanhaFieldName": campaign["option_sheet"],
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": extract_format_from_filename(media_file),
                    "urlFile": get_firebase_url("cabeca", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(EXPORT_DIR, "export_All-mCabecas-dia-imbativel.csv")
    fieldnames = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def generate_background_csv(current_date: str) -> int:
    print("Gerando CSV de backgrounds...")
    rows = []

    for region in {"NACIONAL", "MG"}:
        folder_path = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["background"], region)
        files = scan_media_files(folder_path)
        campaigns_for_region = [
            campaign["option_sheet"] for campaign in CAMPAIGNS if campaign["region"] == region
        ]

        formats_seen = set()
        for media_file in files:
            file_format = extract_format_from_filename(media_file)
            if file_format in formats_seen:
                continue
            formats_seen.add(file_format)

            rows.append(
                {
                    "ligacaoCampanhaFieldName": " , ".join(campaigns_for_region),
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": file_format,
                    "urlFile": get_firebase_url("backgroundOferta", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(EXPORT_DIR, "export_All-mBackground-dia-imbativel.csv")
    fieldnames = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def generate_assinaturas_csv(current_date: str) -> int:
    print("Gerando CSV de assinaturas...")
    rows = []

    for campaign in CAMPAIGNS:
        period_dir = PERIOD_DIR_MAP[campaign["period"]]
        folder_path = os.path.join(
            CAMPAIGN_BASE_PATH,
            DIR_NAMES["assinatura"],
            campaign["region"],
            period_dir,
        )
        files = scan_media_files(folder_path)

        for media_file in files:
            rows.append(
                {
                    "ligacaoCampanhaFieldName": campaign["option_sheet"],
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": extract_format_from_filename(media_file),
                    "urlFile": get_firebase_url("assinatura", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(EXPORT_DIR, "export_All-mAssinaturas-dia-imbativel.csv")
    fieldnames = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def generate_trilhas_csv(current_date: str) -> int:
    print("Gerando CSV de trilhas...")
    rows = []
    folder_path = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["trilha"])
    files = scan_media_files(folder_path)
    option_sheets = [campaign["option_sheet"] for campaign in CAMPAIGNS]
    ligacao_value = " , ".join(option_sheets)

    for media_file in files:
        rows.append(
            {
                "ligacaoCampanhaFieldName": ligacao_value,
                "locucaoTranscrita": "",
                "nameFile": media_file,
                "OS Formato modelo": extract_format_from_filename(media_file),
                "urlFile": get_firebase_url("trilha", media_file),
                "Creation Date": current_date,
            }
        )

    output_path = os.path.join(EXPORT_DIR, "export_All-mTrilhas-dia-imbativel.csv")
    fieldnames = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def generate_form_campanhas_csv(current_date: str) -> int:
    print("Gerando CSV de form campanhas...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rows = []

    for campaign in CAMPAIGNS:
        materiais: List[str] = [
            "Filme de 15s",
            "Filme de 30s",
            "Spot de Radio 15s",
            "Spot de Radio 30s",
        ]
        tipos_midia: List[str] = ["Tv", "Radio"]

        rows.append(
            {
                # Ajuste precisa bater com optionset existente
                "ajusteCampanha": "acelera",
                "ativo": "sim",
                "categoriaLiberacao": "",
                "colorLetras": "#d81510",
                "formCelebridade": "",
                "formSelo": "",
                "imagem": "",
                "option": campaign["display"],
                "optionSheet": campaign["option_sheet"],
                "OS materiais": " , ".join(materiais),
                "OS type midia": " , ".join(tipos_midia),
            }
        )

    output_path = os.path.join(EXPORT_DIR, f"export_All-formCampanhas-dia-imbativel-{timestamp}.csv")
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

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def main() -> None:
    ensure_export_dir()
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    print("=" * 60)
    print("GERADOR DE CSVs - DIA IMBATIVEL")
    print("=" * 60)

    total_cabecas = generate_cabecas_csv(current_date)
    total_backgrounds = generate_background_csv(current_date)
    total_assinaturas = generate_assinaturas_csv(current_date)
    total_trilhas = generate_trilhas_csv(current_date)
    total_form = generate_form_campanhas_csv(current_date)

    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"  Cabecas: {total_cabecas} arquivos")
    print(f"  Backgrounds: {total_backgrounds} arquivos")
    print(f"  Assinaturas: {total_assinaturas} arquivos")
    print(f"  Trilhas: {total_trilhas} arquivos")
    print(f"  Campanhas (form): {total_form} registros")
    print("=" * 60)


if __name__ == "__main__":
    main()
