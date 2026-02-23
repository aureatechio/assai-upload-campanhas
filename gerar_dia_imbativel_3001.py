import csv
import os
import unicodedata
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote

CAMPAIGN_SLUG = "dia-imbativel-30-01"
CAMPAIGN_BASE_PATH = (
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\DIA IMBATIVEL 30.01"
)
EXPORT_DIR = "exportados"
BASE_FIREBASE_URL = "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/"

TOKEN_BY_BUCKET: Dict[str, str] = {
    "cabeca": "629cda73-b302-4696-9a3b-015ccc586a35",
    "assinatura": "9442f0b8-8dc6-43ed-9431-91e6c0ed5572",
    "backgroundOferta": "531796ff-4d81-4d29-9cf5-c53edb8aaa7f",
    "trilha": "7d2e4acc-15fa-46f0-9d3d-7b026db1f96b",
}

MEDIA_EXTS = (".mp4", ".mp3", ".wav")
BG_MEDIA_EXTS = (".mp4", ".png", ".jpg", ".jpeg")
FORMAT_ORDER = ["16x9", "1x1", "9x16"]

CAMPAIGNS = [
    {
        "period": "HOJE",
        "region": "NACIONAL",
        "option_sheet": "diaImbativel3001Hoje",
        "display": "Dia Imbativel 30.01 Hoje Nacional",
    },
    {
        "period": "HOJE",
        "region": "MG",
        "option_sheet": "diaImbativel3001HojeMg",
        "display": "Dia Imbativel 30.01 Hoje Mg",
    },
    {
        "period": "AMANHA",
        "region": "NACIONAL",
        "option_sheet": "diaImbativel3001Amanha",
        "display": "Dia Imbativel 30.01 Amanha Nacional",
    },
    {
        "period": "AMANHA",
        "region": "MG",
        "option_sheet": "diaImbativel3001AmanhaMg",
        "display": "Dia Imbativel 30.01 Amanha Mg",
    },
    {
        "period": "GENERICO",
        "region": "NACIONAL",
        "option_sheet": "diaImbativel3001Generico",
        "display": "Dia Imbativel 30.01 Generico Nacional",
    },
    {
        "period": "GENERICO",
        "region": "MG",
        "option_sheet": "diaImbativel3001GenericoMg",
        "display": "Dia Imbativel 30.01 Generico Mg",
    },
]


def normalize_name(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return stripped.upper()


def find_subdir_by_normalized(parent: str, target: str) -> Optional[str]:
    if not os.path.isdir(parent):
        return None

    target_norm = normalize_name(target)
    for entry in os.listdir(parent):
        full_path = os.path.join(parent, entry)
        if not os.path.isdir(full_path):
            continue
        if normalize_name(entry) == target_norm:
            return full_path
    return None


def map_period_dirs(parent: str) -> Dict[str, str]:
    periods: Dict[str, str] = {}
    if not os.path.isdir(parent):
        return periods

    for entry in os.listdir(parent):
        full_path = os.path.join(parent, entry)
        if not os.path.isdir(full_path):
            continue
        name_norm = normalize_name(entry)
        if "HOJE" in name_norm:
            periods["HOJE"] = full_path
        elif "AMANHA" in name_norm:
            periods["AMANHA"] = full_path
        elif "GENERICO" in name_norm:
            periods["GENERICO"] = full_path
    return periods


def map_region_dirs(parent: str) -> Dict[str, str]:
    regions: Dict[str, str] = {}
    if not os.path.isdir(parent):
        return regions

    for entry in os.listdir(parent):
        full_path = os.path.join(parent, entry)
        if not os.path.isdir(full_path):
            continue
        name_norm = normalize_name(entry)
        if "NACIONAL" in name_norm or name_norm == "NAC":
            regions["NACIONAL"] = full_path
        elif name_norm.endswith(" MG") or name_norm.endswith("MG"):
            regions["MG"] = full_path
    return regions


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


def scan_media_files(folder_path: str, exts: tuple = MEDIA_EXTS) -> List[str]:
    if not os.path.isdir(folder_path):
        return []

    files: List[str] = []
    for item in sorted(os.listdir(folder_path)):
        if item.lower().endswith(exts):
            files.append(item)
    return files


def ensure_export_dir() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)


def resolve_region_root(period_path: str, inner_folder_name: str) -> str:
    if not os.path.isdir(period_path):
        return ""

    inner_path = find_subdir_by_normalized(period_path, inner_folder_name)
    return inner_path or period_path


def generate_cabecas_csv(current_date: str, cabeca_root: str) -> int:
    print("Gerando CSV de cabecas...")
    rows = []
    period_dirs = map_period_dirs(cabeca_root)

    for campaign in CAMPAIGNS:
        period_path = period_dirs.get(campaign["period"])
        if not period_path:
            continue
        region_root = resolve_region_root(period_path, "CABECA")
        region_dirs = map_region_dirs(region_root)
        region_path = region_dirs.get(campaign["region"])
        if not region_path:
            continue

        for media_file in scan_media_files(region_path):
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


def generate_assinaturas_csv(current_date: str, encerramento_root: str) -> int:
    print("Gerando CSV de assinaturas...")
    rows = []
    period_dirs = map_period_dirs(encerramento_root)

    for campaign in CAMPAIGNS:
        period_path = period_dirs.get(campaign["period"])
        if not period_path:
            continue
        region_root = resolve_region_root(period_path, "ENCERRAMENTO")
        region_dirs = map_region_dirs(region_root)
        region_path = region_dirs.get(campaign["region"])
        if not region_path:
            continue

        for media_file in scan_media_files(region_path):
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


def generate_background_csv(current_date: str, bg_root: str) -> int:
    print("Gerando CSV de backgrounds...")
    rows = []
    region_dirs = map_region_dirs(bg_root)

    if region_dirs:
        for region, folder_path in region_dirs.items():
            ligacao_value = " , ".join(
                campaign["option_sheet"] for campaign in CAMPAIGNS if campaign["region"] == region
            )
            files_by_format: Dict[str, str] = {}
            for media_file in scan_media_files(folder_path, BG_MEDIA_EXTS):
                file_format = extract_format_from_filename(media_file)
                if file_format not in files_by_format:
                    files_by_format[file_format] = media_file

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
    else:
        ligacao_value = " , ".join(campaign["option_sheet"] for campaign in CAMPAIGNS)
        files_by_format: Dict[str, str] = {}
        for media_file in scan_media_files(bg_root, BG_MEDIA_EXTS):
            file_format = extract_format_from_filename(media_file)
            if file_format not in files_by_format:
                files_by_format[file_format] = media_file

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


def generate_trilhas_csv(current_date: str, trilha_root: str) -> int:
    print("Gerando CSV de trilhas...")
    rows = []
    files = scan_media_files(trilha_root)
    ligacao_value = " , ".join(campaign["option_sheet"] for campaign in CAMPAIGNS)

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

    cabeca_root = find_subdir_by_normalized(CAMPAIGN_BASE_PATH, "CABECA")
    encerramento_root = find_subdir_by_normalized(CAMPAIGN_BASE_PATH, "ENCERRAMENTO")
    bg_root = find_subdir_by_normalized(CAMPAIGN_BASE_PATH, "BG")
    trilha_root = find_subdir_by_normalized(CAMPAIGN_BASE_PATH, "TRILHA")

    print("=" * 60)
    print("GERADOR DE CSVs - DIA IMBATIVEL 30.01")
    print("=" * 60)

    total_cabecas = generate_cabecas_csv(current_date, cabeca_root or "")
    total_backgrounds = generate_background_csv(current_date, bg_root or "")
    total_assinaturas = generate_assinaturas_csv(current_date, encerramento_root or "")
    total_trilhas = generate_trilhas_csv(current_date, trilha_root or "")
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
