import os
import csv
from datetime import datetime
from urllib.parse import quote
from typing import Dict, List, Optional, Tuple

CAMPAIGN_BASE_PATH = "G:\\Drives compartilhados\\__JOBS 2025\\_ASSAI\\_ROBO ASSAI\\MIDIAS\\BLACK IMBAT\u00cdVEL"
EXPORT_DIR = "exportados"
BASE_FIREBASE_URL = "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/"
CAMPAIGN_SLUG = "black-imbativel"
FORMAT_ORDER = ["16x9", "1x1", "9x16"]

TOKEN_BY_BUCKET = {
    "cabeca": "629cda73-b302-4696-9a3b-015ccc586a35",
    "assinatura": "9442f0b8-8dc6-43ed-9431-91e6c0ed5572",
    "backgroundOferta": "531796ff-4d81-4d29-9cf5-c53edb8aaa7f",
    "trilha": "7d2e4acc-15fa-46f0-9d3d-7b026db1f96b",
}

CAB_DIRNAME = "CABECA"
ASS_DIRNAME = "ASSINATURA"

CAMPAIGNS = [
    {
        "period": "HOJE",
        "region": "NACIONAL",
        "option_sheet": "blackImbativelHoje",
        "display": "Black Imbat\u00edvel Hoje Nacional",
        "cabeca_prefix": "cabBlackImbativelHojeNacional",
        "cabeca_path": (CAB_DIRNAME, "NACIONAL", "HOJE"),
        "assinatura_prefix": "assBlackImbativelHojeNacional",
        "assinatura_path": (ASS_DIRNAME, "NACIONAL", "HOJE"),
        "imagem": "",
    },
    {
        "period": "AMANHA",
        "region": "NACIONAL",
        "option_sheet": "blackImbativelAmanha",
        "display": "Black Imbat\u00edvel Amanha Nacional",
        "cabeca_prefix": "cabBlackImbativelAmanhaNacional",
        "cabeca_path": (CAB_DIRNAME, "NACIONAL", "AMANHA"),
        "assinatura_prefix": "assBlackImbativelAmanhaNacional",
        "assinatura_path": (ASS_DIRNAME, "NACIONAL", "AMANHA"),
        "imagem": "",
    },
    {
        "period": "GENERICO",
        "region": "NACIONAL",
        "option_sheet": "blackImbativelGenerico",
        "display": "Black Imbat\u00edvel Generico Nacional",
        "cabeca_prefix": "cabBlackImbativelGenericoNacional",
        "cabeca_path": (CAB_DIRNAME, "NACIONAL", "GENERICO"),
        "assinatura_prefix": "assBlackImbativelGenericoNacional",
        "assinatura_path": (ASS_DIRNAME, "NACIONAL", "GENERICO"),
        "imagem": "",
    },
    {
        "period": "HOJE",
        "region": "MG",
        "option_sheet": "blackImbativelHojeMg",
        "display": "Black Imbat\u00edvel Hoje Mg",
        "cabeca_prefix": "cabBlackImbativelHojeMg",
        "cabeca_path": (CAB_DIRNAME, "MG", "HOJE"),
        "assinatura_prefix": "assBlackImbativelHojeMg",
        "assinatura_path": (ASS_DIRNAME, "MG", "HOJE"),
        "imagem": "",
    },
    {
        "period": "AMANHA",
        "region": "MG",
        "option_sheet": "blackImbativelAmanhaMg",
        "display": "Black Imbat\u00edvel Amanha Mg",
        "cabeca_prefix": "cabBlackImbativelAmanhaMg",
        "cabeca_path": (CAB_DIRNAME, "MG", "AMANHA"),
        "assinatura_prefix": "assBlackImbativelAmanhaMg",
        "assinatura_path": (ASS_DIRNAME, "MG", "AMANHA"),
        "imagem": "",
    },
    {
        "period": "GENERICO",
        "region": "MG",
        "option_sheet": "blackImbativelGenericoMg",
        "display": "Black Imbat\u00edvel Generico Mg",
        "cabeca_prefix": "cabBlackImbativelGenericoMg",
        "cabeca_path": (CAB_DIRNAME, "MG", "GENERICO"),
        "assinatura_prefix": "assBlackImbativelGenericoMg",
        "assinatura_path": (ASS_DIRNAME, "MG", "GENERICO"),
        "imagem": "",
    },
]


def get_firebase_url(bucket_name: str, filename: str) -> str:
    token = TOKEN_BY_BUCKET.get(bucket_name)
    if not token:
        raise ValueError(f"Token n�o configurado para o bucket '{bucket_name}'")

    encoded_name = quote(filename)
    return f"{BASE_FIREBASE_URL}{bucket_name}%2F{encoded_name}?alt=media&token={token}"


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


def build_region_index() -> Dict[str, List[str]]:
    region_map: Dict[str, List[str]] = {}
    for campaign in CAMPAIGNS:
        region_map.setdefault(campaign["region"], []).append(campaign["option_sheet"])
    return region_map


def select_files_by_format(
    folder_path: str, filename_prefix: Optional[str] = None
) -> Dict[str, str]:
    files_by_format: Dict[str, str] = {}

    for media_file in scan_media_files(folder_path):
        if filename_prefix and not media_file.startswith(filename_prefix):
            continue
        file_format = extract_format_from_filename(media_file)
        if file_format not in files_by_format:
            files_by_format[file_format] = media_file

    return files_by_format


def get_bg_variant_dirs() -> List[str]:
    bg_root = os.path.join(CAMPAIGN_BASE_PATH, "BG")
    variant_entries: List[Tuple[str, float]] = []

    if not os.path.isdir(bg_root):
        return variant_entries

    for entry in os.listdir(bg_root):
        entry_path = os.path.join(bg_root, entry)
        if os.path.isdir(entry_path):
            variant_entries.append((entry, os.path.getmtime(entry_path)))

    variant_entries.sort(key=lambda item: item[1], reverse=True)
    return [name for name, _ in variant_entries]


def generate_cabecas_csv(current_date: str) -> int:
    print("Gerando CSV de cabecas...")
    rows = []

    for campaign in CAMPAIGNS:
        folder_parts = campaign.get("cabeca_path")
        if not folder_parts:
            continue

        folder_path = os.path.join(CAMPAIGN_BASE_PATH, *folder_parts)
        files_by_format = select_files_by_format(
            folder_path, campaign.get("cabeca_prefix")
        )

        for file_format in FORMAT_ORDER:
            media_file = files_by_format.get(file_format)
            if not media_file:
                continue
            rows.append(
                {
                    "ligacaoCampanhaFieldName": campaign["option_sheet"],
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": file_format,
                    "urlFile": get_firebase_url("cabeca", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(EXPORT_DIR, f"export_All-mCabecas-{CAMPAIGN_SLUG}.csv")

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "ligacaoCampanhaFieldName",
            "locucaoTranscrita",
            "nameFile",
            "OS Formato modelo",
            "urlFile",
            "Creation Date",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def generate_background_csv(current_date: str) -> int:
    print("Gerando CSV de backgrounds...")
    rows = []
    region_index = build_region_index()
    bg_root = os.path.join(CAMPAIGN_BASE_PATH, "BG")
    variant_dirs = get_bg_variant_dirs()

    for region in sorted(region_index.keys()):
        campaign_options = region_index[region]
        selected_by_format: Dict[str, str] = {}

        search_paths = [
            os.path.join(bg_root, variant, region) for variant in variant_dirs
        ]
        search_paths.append(os.path.join(bg_root, region))

        for folder_path in search_paths:
            files = scan_media_files(folder_path)
            for media_file in files:
                file_format = extract_format_from_filename(media_file)
                if file_format not in selected_by_format:
                    selected_by_format[file_format] = media_file

        for fmt in FORMAT_ORDER:
            media_file = selected_by_format.get(fmt)
            if not media_file:
                continue
            rows.append(
                {
                    "ligacaoCampanhaFieldName": " , ".join(campaign_options),
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": fmt,
                    "urlFile": get_firebase_url("backgroundOferta", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(EXPORT_DIR, f"export_All-mBackground-{CAMPAIGN_SLUG}.csv")

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "ligacaoCampanhaFieldName",
            "locucaoTranscrita",
            "nameFile",
            "OS Formato modelo",
            "urlFile",
            "Creation Date",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def generate_assinaturas_csv(current_date: str) -> int:
    print("Gerando CSV de assinaturas...")
    rows = []

    for campaign in CAMPAIGNS:
        folder_parts = campaign.get("assinatura_path")
        if not folder_parts:
            continue

        folder_path = os.path.join(CAMPAIGN_BASE_PATH, *folder_parts)
        files_by_format = select_files_by_format(
            folder_path, campaign.get("assinatura_prefix")
        )

        for file_format in FORMAT_ORDER:
            media_file = files_by_format.get(file_format)
            if not media_file:
                continue
            rows.append(
                {
                    "ligacaoCampanhaFieldName": campaign["option_sheet"],
                    "locucaoTranscrita": "",
                    "nameFile": media_file,
                    "OS Formato modelo": file_format,
                    "urlFile": get_firebase_url("assinatura", media_file),
                    "Creation Date": current_date,
                }
            )

    output_path = os.path.join(EXPORT_DIR, f"export_All-mAssinaturas-{CAMPAIGN_SLUG}.csv")

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "ligacaoCampanhaFieldName",
            "locucaoTranscrita",
            "nameFile",
            "OS Formato modelo",
            "urlFile",
            "Creation Date",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def generate_trilhas_csv(current_date: str) -> int:
    print("Gerando CSV de trilhas...")
    rows = []
    folder_path = os.path.join(CAMPAIGN_BASE_PATH, "TRILHA")
    files = scan_media_files(folder_path)
    ligacao_value = " , ".join(campaign["option_sheet"] for campaign in CAMPAIGNS)

    if not files:
        print(f"  Aviso: sem arquivos em {folder_path}")

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

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "ligacaoCampanhaFieldName",
            "locucaoTranscrita",
            "nameFile",
            "OS Formato modelo",
            "urlFile",
            "Creation Date",
        ]
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
                "imagem": campaign["imagem"],
                "option": campaign["display"],
                "optionSheet": campaign["option_sheet"],
                "OS materiais": materiais,
                "OS type midia": tipos_midia,
            }
        )

    output_path = os.path.join(
        EXPORT_DIR, f"export_All-formCampanhas-{CAMPAIGN_SLUG}-{timestamp}.csv"
    )

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
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
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  OK - {len(rows)} registros escritos em {output_path}")
    return len(rows)


def main() -> None:
    ensure_export_dir()
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    print("=" * 60)
    print("GERADOR DE CSVs - ACELERA COM PRECO BAIXO")
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
