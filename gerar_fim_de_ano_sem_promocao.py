import argparse
import csv
import os
from datetime import datetime
from typing import Dict, Iterable, List, Optional
from urllib.parse import quote

CAMPAIGN_SLUG = "fim-de-ano-sem-promocao"
CAMPAIGN_BASE_PATH = (
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\FIM DE ANO"
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
    "cabeca": "CABEÇA",
    "assinatura": "ASSINATURA",
    "background": "BG",
    "trilha": "TRILHA",
}

CAMPAIGN_SETS = {
    # 2 campanhas (Nacional + MG)
    "2camp": [
        {
            "region": "NACIONAL",
            "display": "Fim de Ano Sem Promocao Nacional",
            "option_sheet": "fimDeAnoSemPromocaoNacional",
        },
        {
            "region": "MG",
            "display": "Fim de Ano Sem Promocao Mg",
            "option_sheet": "fimDeAnoSemPromocaoMg",
        },
    ],
    # 6 campanhas (Hoje/Amanha/Generico para Nacional + MG)
    "6camp": [
        {
            "region": "NACIONAL",
            "period": "HOJE",
            "display": "Fim de Ano Sem Promocao Hoje Nacional",
            "option_sheet": "fimDeAnoSemPromocaoHojeNacional",
        },
        {
            "region": "NACIONAL",
            "period": "AMANHA",
            "display": "Fim de Ano Sem Promocao Amanha Nacional",
            "option_sheet": "fimDeAnoSemPromocaoAmanhaNacional",
        },
        {
            "region": "NACIONAL",
            "period": "GENERICO",
            "display": "Fim de Ano Sem Promocao Generico Nacional",
            "option_sheet": "fimDeAnoSemPromocaoGenericoNacional",
        },
        {
            "region": "MG",
            "period": "HOJE",
            "display": "Fim de Ano Sem Promocao Hoje Mg",
            "option_sheet": "fimDeAnoSemPromocaoHojeMg",
        },
        {
            "region": "MG",
            "period": "AMANHA",
            "display": "Fim de Ano Sem Promocao Amanha Mg",
            "option_sheet": "fimDeAnoSemPromocaoAmanhaMg",
        },
        {
            "region": "MG",
            "period": "GENERICO",
            "display": "Fim de Ano Sem Promocao Generico Mg",
            "option_sheet": "fimDeAnoSemPromocaoGenericoMg",
        },
    ],
}

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


def infer_region_from_filename(filename: str) -> Optional[str]:
    upper = filename.upper()
    if "NACIONAL" in upper:
        return "NACIONAL"
    if "MG" in upper:
        return "MG"
    return None


def group_campaigns_by_region(campaigns: Iterable[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    campaigns_by_region: Dict[str, List[Dict[str, str]]] = {}
    for campaign in campaigns:
        region = campaign["region"]
        campaigns_by_region.setdefault(region, []).append(campaign)
    return campaigns_by_region


def generate_cabecas_csv(current_date: str, campaigns: List[Dict[str, str]], variant: str) -> int:
    print("Gerando CSV de cabecas (sem promocao)...")
    rows = []
    campaigns_by_region = group_campaigns_by_region(campaigns)
    folder_path = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["cabeca"])
    files = scan_media_files(folder_path)

    for media_file in files:
        lowered = media_file.lower()
        if "sempromocao" not in lowered:
            continue

        region = infer_region_from_filename(media_file)
        region_campaigns = campaigns_by_region.get(region, [])
        for campaign in region_campaigns:
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

    output_path = os.path.join(
        EXPORT_DIR, f"export_All-mCabecas-{CAMPAIGN_SLUG}-{variant}.csv"
    )
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


def generate_background_csv(current_date: str, campaigns: List[Dict[str, str]], variant: str) -> int:
    print("Gerando CSV de backgrounds (sem promocao)...")
    rows = []
    campaigns_by_region = group_campaigns_by_region(campaigns)

    for region in ("NACIONAL", "MG"):
        folder_path = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["background"], region)
        files = [
            media_file
            for media_file in scan_media_files(folder_path)
            if "fimdeano" in media_file.lower()
        ]
        region_campaigns = campaigns_by_region.get(region, [])
        if not region_campaigns:
            continue
        ligacao_value = " , ".join([c["option_sheet"] for c in region_campaigns])

        formats_seen = set()
        for media_file in files:
            file_format = extract_format_from_filename(media_file)
            if file_format in formats_seen:
                continue
            formats_seen.add(file_format)

            rows.append(
                {
                    "ligacaoCampanhaFieldName": ligacao_value,
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": file_format,
                    "urlFile": get_firebase_url("backgroundOferta", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(
        EXPORT_DIR, f"export_All-mBackground-{CAMPAIGN_SLUG}-{variant}.csv"
    )
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


def generate_assinaturas_csv(current_date: str, campaigns: List[Dict[str, str]], variant: str) -> int:
    print("Gerando CSV de assinaturas (sem promocao)...")
    rows = []
    campaigns_by_region = group_campaigns_by_region(campaigns)
    folder_path = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["assinatura"])
    files = scan_media_files(folder_path)

    for media_file in files:
        lowered = media_file.lower()
        if "sempromocao" not in lowered:
            continue

        region = infer_region_from_filename(media_file)
        region_campaigns = campaigns_by_region.get(region, [])
        for campaign in region_campaigns:
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

    output_path = os.path.join(
        EXPORT_DIR, f"export_All-mAssinaturas-{CAMPAIGN_SLUG}-{variant}.csv"
    )
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


def generate_trilhas_csv(current_date: str, campaigns: List[Dict[str, str]], variant: str) -> int:
    print("Gerando CSV de trilhas...")
    rows = []
    folder_path = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["trilha"])
    files = scan_media_files(folder_path)
    ligacao_value = " , ".join([campaign["option_sheet"] for campaign in campaigns])

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

    output_path = os.path.join(
        EXPORT_DIR, f"export_All-mTrilhas-{CAMPAIGN_SLUG}-{variant}.csv"
    )
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


def generate_form_campanhas_csv(current_date: str, campaigns: List[Dict[str, str]], variant: str) -> int:
    print("Gerando CSV de form campanhas...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rows = []

    for campaign in campaigns:
        materiais: List[str] = [
            "Filme de 15s",
            "Filme de 30s",
            "Spot de Radio 15s",
            "Spot de Radio 30s",
        ]
        tipos_midia: List[str] = ["Tv", "Radio"]

        rows.append(
            {
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
                "OS type mídia": " , ".join(tipos_midia),
            }
        )

    output_path = os.path.join(
        EXPORT_DIR, f"export_All-formCampanhas-{CAMPAIGN_SLUG}-{variant}-{timestamp}.csv"
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
        "OS type mídia",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gerador de CSVs - Fim de Ano (sem promocao)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--set",
        dest="campaign_set",
        choices=sorted(CAMPAIGN_SETS.keys()),
        default="2camp",
        help="Escolha a variacao (2camp = Nacional+MG, 6camp = Hoje/Amanha/Generico para Nacional+MG)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    campaign_set_key = args.campaign_set
    campaigns = CAMPAIGN_SETS[campaign_set_key]

    ensure_export_dir()
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    print("=" * 60)
    print("GERADOR DE CSVs - FIM DE ANO (SEM PROMOCAO)")
    print("=" * 60)

    total_cabecas = generate_cabecas_csv(current_date, campaigns, campaign_set_key)
    total_backgrounds = generate_background_csv(current_date, campaigns, campaign_set_key)
    total_assinaturas = generate_assinaturas_csv(current_date, campaigns, campaign_set_key)
    total_trilhas = generate_trilhas_csv(current_date, campaigns, campaign_set_key)
    total_form = generate_form_campanhas_csv(current_date, campaigns, campaign_set_key)

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
