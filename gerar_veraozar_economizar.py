import csv
import os
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote

CAMPAIGN_SLUG = "veraozar-economizar"
MIDIAS_ROOT = r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS"
EXPORT_DIR = "exportados"
BASE_FIREBASE_URL = "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/"

TOKEN_BY_BUCKET: Dict[str, str] = {
    "cabeca": "629cda73-b302-4696-9a3b-015ccc586a35",
    "assinatura": "9442f0b8-8dc6-43ed-9431-91e6c0ed5572",
    "backgroundOferta": "531796ff-4d81-4d29-9cf5-c53edb8aaa7f",
    "trilha": "7d2e4acc-15fa-46f0-9d3d-7b026db1f96b",
}

FORMAT_ORDER = ["16x9", "1x1", "9x16"]

CAMPAIGNS = [
    {
        "display": "Veraozar Nacional",
        "option_sheet": "veraozarNacional",
        "cabeca_dir": "VERAOZAR NAC",
        "assinatura_dir": "VERAOZAR NAC",
        "bg_group": ("VERAOZAO",),
    },
    {
        "display": "Veraozar Rj",
        "option_sheet": "veraozarRj",
        "cabeca_dir": "VERAOZAR RJ",
        "assinatura_dir": "VERAOZAR RJ",
        "bg_group": ("VERAOZAO",),
    },
    {
        "display": "Economizar Nacional",
        "option_sheet": "economizarNacional",
        "cabeca_dir": "ECONOMIZAR NAC",
        "assinatura_dir": "ECONOMIZAR NAC",
        "bg_group": ("ECONOMIZAR", "NACIONAL"),
    },
    {
        "display": "Economizar Mg",
        "option_sheet": "economizarMg",
        "cabeca_dir": "ECONOMIZAR MG",
        "assinatura_dir": "ECONOMIZAR MG",
        "bg_group": ("ECONOMIZAR", "MG"),
    },
]


def find_campaign_base_path() -> str:
    if not os.path.isdir(MIDIAS_ROOT):
        return os.path.join(MIDIAS_ROOT, "VERAOZAR   ECONOMIZAR")

    candidates = [
        entry
        for entry in os.listdir(MIDIAS_ROOT)
        if entry.upper().startswith("VERAOZAR")
    ]
    if not candidates:
        return os.path.join(MIDIAS_ROOT, "VERAOZAR   ECONOMIZAR")

    candidates.sort(key=lambda item: item.upper())
    return os.path.join(MIDIAS_ROOT, candidates[0])


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


def find_child_dir(parent: str, prefix: str) -> Optional[str]:
    if not os.path.isdir(parent):
        return None

    prefix_upper = prefix.upper()
    for entry in os.listdir(parent):
        full_path = os.path.join(parent, entry)
        if not os.path.isdir(full_path):
            continue
        if entry.upper().startswith(prefix_upper):
            return full_path
    return None


def find_exact_subdir(parent: str, name: str) -> Optional[str]:
    if not os.path.isdir(parent):
        return None

    name_upper = name.upper()
    for entry in os.listdir(parent):
        full_path = os.path.join(parent, entry)
        if not os.path.isdir(full_path):
            continue
        if entry.upper() == name_upper:
            return full_path
    return None


def group_campaigns_by_bg() -> Dict[Tuple[str, ...], List[Dict[str, str]]]:
    groups: Dict[Tuple[str, ...], List[Dict[str, str]]] = {}
    for campaign in CAMPAIGNS:
        bg_key = tuple(campaign["bg_group"])
        groups.setdefault(bg_key, []).append(campaign)
    return groups


def generate_cabecas_csv(current_date: str, base_path: str) -> int:
    print("Gerando CSV de cabecas...")
    rows = []
    cabeca_root = find_child_dir(base_path, "CABE")

    if not cabeca_root:
        print("  Aviso: pasta de cabeca nao encontrada.")
    else:
        for campaign in CAMPAIGNS:
            folder_path = find_exact_subdir(cabeca_root, campaign["cabeca_dir"])
            if not folder_path:
                continue
            for media_file in scan_media_files(folder_path):
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


def generate_assinaturas_csv(current_date: str, base_path: str) -> int:
    print("Gerando CSV de assinaturas...")
    rows = []
    assinatura_root = find_child_dir(base_path, "ASSINATURA")

    if not assinatura_root:
        print("  Aviso: pasta de assinatura nao encontrada.")
    else:
        for campaign in CAMPAIGNS:
            folder_path = find_exact_subdir(assinatura_root, campaign["assinatura_dir"])
            if not folder_path:
                continue
            for media_file in scan_media_files(folder_path):
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


def generate_background_csv(current_date: str, base_path: str) -> int:
    print("Gerando CSV de backgrounds...")
    rows = []
    bg_root = find_child_dir(base_path, "BG")
    bg_groups = group_campaigns_by_bg()

    if not bg_root:
        print("  Aviso: pasta de BG nao encontrada.")
    else:
        for bg_key, campaigns in bg_groups.items():
            folder_path = os.path.join(bg_root, *bg_key)
            files_by_format: Dict[str, str] = {}
            for media_file in scan_media_files(folder_path):
                file_format = extract_format_from_filename(media_file)
                if file_format not in files_by_format:
                    files_by_format[file_format] = media_file

            ligacao_value = " , ".join(campaign["option_sheet"] for campaign in campaigns)
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


def generate_trilhas_csv(current_date: str, base_path: str) -> int:
    print("Gerando CSV de trilhas...")
    rows = []
    trilha_root = find_child_dir(base_path, "TRILHA")

    if not trilha_root:
        print("  Aviso: pasta de trilha nao encontrada.")
    else:
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
    base_path = find_campaign_base_path()

    print("=" * 60)
    print("GERADOR DE CSVs - VERAOZAR / ECONOMIZAR")
    print("=" * 60)

    total_cabecas = generate_cabecas_csv(current_date, base_path)
    total_backgrounds = generate_background_csv(current_date, base_path)
    total_assinaturas = generate_assinaturas_csv(current_date, base_path)
    total_trilhas = generate_trilhas_csv(current_date, base_path)
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
