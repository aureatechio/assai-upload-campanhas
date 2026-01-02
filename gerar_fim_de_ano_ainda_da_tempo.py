import csv
import os
from datetime import datetime
from typing import Dict, Iterable, List, Optional
from urllib.parse import quote

CAMPAIGN_SLUG = "fim-de-ano-ainda-da-tempo"
CAMPAIGN_BASE_PATH = (
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\FIM DE ANO AINDA DA TEMPO"
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
    "cabeca": "CABECA",
    "assinatura": "ENCERRAMENTO",
    "background": "BG",
    "trilha": "TRILHA",
}

CAMPAIGNS = [
    {
        "region": "NACIONAL",
        "display": "Fim de Ano Ainda Da Tempo Nacional",
        "option_sheet": "fimDeAnoAindaDaTempoNacional",
    },
    {
        "region": "MG",
        "display": "Fim de Ano Ainda Da Tempo Mg",
        "option_sheet": "fimDeAnoAindaDaTempoMg",
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
        if item.lower().endswith((".mp4", ".mp3", ".wav")):
            files.append(item)
    return files


def ensure_export_dir() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)


def group_campaigns_by_region(campaigns: Iterable[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    campaigns_by_region: Dict[str, List[Dict[str, str]]] = {}
    for campaign in campaigns:
        region = campaign["region"]
        campaigns_by_region.setdefault(region, []).append(campaign)
    return campaigns_by_region


def find_region_folder(parent: str, region: str) -> Optional[str]:
    if not os.path.isdir(parent):
        return None
    region_upper = region.upper()
    subdirs = [entry for entry in os.listdir(parent) if os.path.isdir(os.path.join(parent, entry))]
    for entry in subdirs:
        if entry.upper() == region_upper:
            return os.path.join(parent, entry)
    for entry in subdirs:
        if region_upper in entry.upper():
            return os.path.join(parent, entry)
    return None


def generate_cabecas_csv(current_date: str) -> int:
    print("Gerando CSV de cabecas...")
    rows = []
    campaigns_by_region = group_campaigns_by_region(CAMPAIGNS)
    cabeca_root = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["cabeca"])

    for region in campaigns_by_region:
        region_folder = find_region_folder(cabeca_root, region)
        if not region_folder:
            continue
        for media_file in scan_media_files(region_folder):
            for campaign in campaigns_by_region[region]:
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

    output_path = os.path.join(EXPORT_DIR, f"export_All-mCabecas-{CAMPAIGN_SLUG}.csv")
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
    campaigns_by_region = group_campaigns_by_region(CAMPAIGNS)
    assinatura_root = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["assinatura"])

    for region in campaigns_by_region:
        region_folder = find_region_folder(assinatura_root, region)
        if not region_folder:
            continue
        for media_file in scan_media_files(region_folder):
            for campaign in campaigns_by_region[region]:
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

    output_path = os.path.join(EXPORT_DIR, f"export_All-mAssinaturas-{CAMPAIGN_SLUG}.csv")
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
    campaigns_by_region = group_campaigns_by_region(CAMPAIGNS)
    bg_root = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["background"])

    for region, region_campaigns in campaigns_by_region.items():
        folder_path = find_region_folder(bg_root, region)
        if not folder_path:
            continue

        files_by_format: Dict[str, str] = {}
        for media_file in scan_media_files(folder_path):
            fmt = extract_format_from_filename(media_file)
            if fmt not in files_by_format:
                files_by_format[fmt] = media_file

        ligacao_value = " , ".join(c["option_sheet"] for c in region_campaigns)
        for fmt in FORMAT_ORDER:
            media_file = files_by_format.get(fmt)
            if not media_file:
                continue
            rows.append(
                {
                    "ligacaoCampanhaFieldName": ligacao_value,
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": fmt,
                    "urlFile": get_firebase_url("backgroundOferta", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(EXPORT_DIR, f"export_All-mBackground-{CAMPAIGN_SLUG}.csv")
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
    ligacao_value = " , ".join(c["option_sheet"] for c in CAMPAIGNS)

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

    output_path = os.path.join(EXPORT_DIR, f"export_All-mTrilhas-{CAMPAIGN_SLUG}.csv")
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
    materiais = "Filme de 15s , Filme de 30s , Spot de Radio 15s , Spot de Radio 30s"
    tipos_midia = "Tv , Radio"

    for campaign in CAMPAIGNS:
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
                "OS materiais": materiais,
                "OS type midia": tipos_midia,
            }
        )

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
    print("GERADOR DE CSVs - FIM DE ANO AINDA DA TEMPO")
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
