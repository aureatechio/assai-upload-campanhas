import csv
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

CAMPAIGN_SLUG = "operacao-preco-baixo-fim-de-ano"
CAMPAIGN_BASE_PATH = (
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\OPERACAO PRECO BAIXO FIM DE ANO"
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

MEDIA_EXTS = (".mp4", ".mp3", ".wav")


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


def derive_campaign_name(filename: str) -> Optional[str]:
    name = os.path.splitext(filename)[0]
    lowered = name.lower()
    for prefix in ("cab", "ass"):
        if lowered.startswith(prefix):
            name = name[len(prefix):]
            break

    for fmt in ("16x9", "9x16", "1x1"):
        if name.lower().endswith(fmt):
            name = name[:-len(fmt)]
            break

    name = name.strip("_- ")
    if name.endswith("MG"):
        name = f"{name[:-2]}Mg"
    if not name:
        return None

    return name[0].lower() + name[1:]


def iter_media_files(folder_path: str):
    for root, dirs, files in os.walk(folder_path):
        dirs.sort()
        files.sort()
        for file in files:
            if file.lower().endswith(MEDIA_EXTS):
                yield root, file


def ensure_export_dir() -> None:
    os.makedirs(EXPORT_DIR, exist_ok=True)


def campaign_sort_key(name: str) -> Tuple[int, int, str]:
    lowered = name.lower()
    period_order = {"amanha": 0, "generico": 1}
    region_order = {"nacional": 0, "mg": 1}

    period_idx = 99
    for period, idx in period_order.items():
        if period in lowered:
            period_idx = idx
            break

    region_idx = 99
    for region, idx in region_order.items():
        if region in lowered:
            region_idx = idx
            break

    return (period_idx, region_idx, name)


def collect_campaign_names(cabeca_root: str, assinatura_root: str) -> List[str]:
    names: Dict[str, None] = {}
    for root in (cabeca_root, assinatura_root):
        if not os.path.isdir(root):
            continue
        for _, file in iter_media_files(root):
            campaign_name = derive_campaign_name(file)
            if campaign_name:
                names[campaign_name] = None
    return sorted(names.keys(), key=campaign_sort_key)


def generate_cabecas_json(current_date: str, cabeca_root: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not os.path.isdir(cabeca_root):
        return rows

    for _, file in iter_media_files(cabeca_root):
        campaign_name = derive_campaign_name(file)
        if not campaign_name:
            continue
        rows.append(
            {
                "ligacaoCampanhaFieldName": campaign_name,
                "locucaoTranscrita": "",
                "nameFile": file,
                "OS Formato modelo": extract_format_from_filename(file),
                "urlFile": get_firebase_url("cabeca", file),
                "Creation Date": current_date,
            }
        )

    return rows


def generate_assinaturas_json(current_date: str, assinatura_root: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not os.path.isdir(assinatura_root):
        return rows

    for _, file in iter_media_files(assinatura_root):
        campaign_name = derive_campaign_name(file)
        if not campaign_name:
            continue
        rows.append(
            {
                "ligacaoCampanhaFieldName": campaign_name,
                "locucaoTranscrita": "",
                "nameFile": file,
                "OS Formato modelo": extract_format_from_filename(file),
                "urlFile": get_firebase_url("assinatura", file),
                "Creation Date": current_date,
            }
        )

    return rows


def generate_background_json(
    current_date: str,
    bg_root: str,
    campaign_names: List[str],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not os.path.isdir(bg_root):
        return rows

    campaigns_by_region = {"NACIONAL": [], "MG": []}
    for name in campaign_names:
        lowered = name.lower()
        if "nacional" in lowered:
            campaigns_by_region["NACIONAL"].append(name)
        elif "mg" in lowered:
            campaigns_by_region["MG"].append(name)

    bg_nacional = os.path.join(bg_root, "NACIONAL")
    bg_mg = os.path.join(bg_root, "MG")
    region_dirs = []
    if os.path.isdir(bg_nacional):
        region_dirs.append(("NACIONAL", bg_nacional))
    if os.path.isdir(bg_mg):
        region_dirs.append(("MG", bg_mg))

    if region_dirs:
        for region, folder in region_dirs:
            ligacao = " , ".join(campaigns_by_region.get(region, []))
            for _, file in iter_media_files(folder):
                rows.append(
                    {
                        "ligacaoCampanhaFieldName": ligacao,
                        "locucaoTranscrita": "",
                        "nameFile": file,
                        "OS Formato modelo": extract_format_from_filename(file),
                        "urlFile": get_firebase_url("backgroundOferta", file),
                        "Creation Date": current_date,
                        "formatoMidia": "Video",
                        "Modified Date": current_date,
                    }
                )
        return rows

    ligacao = " , ".join(campaign_names)
    for _, file in iter_media_files(bg_root):
        rows.append(
            {
                "ligacaoCampanhaFieldName": ligacao,
                "locucaoTranscrita": "",
                "nameFile": file,
                "OS Formato modelo": extract_format_from_filename(file),
                "urlFile": get_firebase_url("backgroundOferta", file),
                "Creation Date": current_date,
                "formatoMidia": "Video",
                "Modified Date": current_date,
            }
        )

    return rows


def generate_trilhas_json(
    current_date: str,
    trilha_root: str,
    campaign_names: List[str],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not os.path.isdir(trilha_root):
        return rows

    ligacao = " , ".join(campaign_names)
    for _, file in iter_media_files(trilha_root):
        rows.append(
            {
                "ligacaoCampanhaFieldName": ligacao,
                "locucaoTranscrita": "",
                "nameFile": file,
                "OS Formato modelo": extract_format_from_filename(file),
                "urlFile": get_firebase_url("trilha", file),
                "Creation Date": current_date,
                "Modified Date": current_date,
                "Slug": "",
                "Creator": "(App admin)",
            }
        )

    return rows


def write_json(output_name: str, data: List[Dict[str, str]]) -> str:
    output_path = os.path.join(EXPORT_DIR, output_name)
    with open(output_path, "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=True, indent=2)
    return output_path


def write_csv(output_name: str, fieldnames: List[str], rows: List[Dict[str, str]]) -> str:
    output_path = os.path.join(EXPORT_DIR, output_name)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def campaign_display_from_name(name: str) -> str:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    return spaced[:1].upper() + spaced[1:] if spaced else spaced


def main() -> None:
    ensure_export_dir()
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    cabeca_root = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["cabeca"])
    assinatura_root = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["assinatura"])
    bg_root = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["background"])
    trilha_root = os.path.join(CAMPAIGN_BASE_PATH, DIR_NAMES["trilha"])

    campaign_names = collect_campaign_names(cabeca_root, assinatura_root)

    print("=" * 60)
    print("GERADOR DE JSON - OPERACAO PRECO BAIXO DEZEMBRO")
    print("=" * 60)

    cabecas = generate_cabecas_json(current_date, cabeca_root)
    assinaturas = generate_assinaturas_json(current_date, assinatura_root)
    backgrounds = generate_background_json(current_date, bg_root, campaign_names)
    trilhas = generate_trilhas_json(current_date, trilha_root, campaign_names)

    json_files = [
        (f"{CAMPAIGN_SLUG}_abertura.json", cabecas),
        (f"{CAMPAIGN_SLUG}_assinatura.json", assinaturas),
        (f"{CAMPAIGN_SLUG}_bg.json", backgrounds),
        (f"{CAMPAIGN_SLUG}_trilha.json", trilhas),
    ]

    for name, data in json_files:
        output_path = write_json(name, data)
        print(f"  OK - {len(data)} registros escritos em {output_path}")

    csv_fields_base = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]

    csv_files = [
        (f"export_All-mCabecas-{CAMPAIGN_SLUG}.csv", cabecas, csv_fields_base),
        (f"export_All-mAssinaturas-{CAMPAIGN_SLUG}.csv", assinaturas, csv_fields_base),
        (f"export_All-mBackground-{CAMPAIGN_SLUG}.csv", backgrounds, csv_fields_base),
        (f"export_All-mTrilhas-{CAMPAIGN_SLUG}.csv", trilhas, csv_fields_base),
    ]

    for name, data, fields in csv_files:
        output_path = write_csv(name, fields, data)
        print(f"  OK - {len(data)} registros escritos em {output_path}")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    form_rows = []
    materiais = "Filme de 15s , Filme de 30s , Spot de Radio 15s , Spot de Radio 30s"
    tipos_midia = "Tv , Radio"

    for campaign_name in campaign_names:
        form_rows.append(
            {
                "ajusteCampanha": "acelera",
                "ativo": "sim",
                "categoriaLiberacao": "",
                "colorLetras": "#d81510",
                "formCelebridade": "",
                "formSelo": "",
                "imagem": "",
                "option": campaign_display_from_name(campaign_name),
                "optionSheet": campaign_name,
                "OS materiais": materiais,
                "OS type midia": tipos_midia,
            }
        )

    form_fields = [
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
    form_path = write_csv(
        f"export_All-formCampanhas-{CAMPAIGN_SLUG}-{timestamp}.csv",
        form_fields,
        form_rows,
    )
    print(f"  OK - {len(form_rows)} registros escritos em {form_path}")

    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"  Cabecas: {len(cabecas)} arquivos")
    print(f"  Assinaturas: {len(assinaturas)} arquivos")
    print(f"  Backgrounds: {len(backgrounds)} arquivos")
    print(f"  Trilhas: {len(trilhas)} arquivos")
    print(f"  Campanhas (form): {len(campaign_names)} registros")
    print("=" * 60)


if __name__ == "__main__":
    main()
