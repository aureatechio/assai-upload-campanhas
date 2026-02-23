import csv
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
load_dotenv()

from upload_supabase_midias import (
    build_object_path,
    ensure_bucket,
    public_url,
    upload_file,
)


CAMPAIGN_SLUG = "economizassao"
CAMPAIGN_BASE_PATH = Path(
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\ECONOMIZASSAO"
)
EXPORT_DIR = Path("exportados")
PROJECT_URL = "https://xhzgscezaaekbaqrkddu.supabase.co"
BUCKET = "assai-midias"

CAMPAIGNS = [
    {
        "region": "NACIONAL",
        "option_sheet": "economizassaoNac",
        "display": "Economizassao Nacional",
    },
    {
        "region": "MG",
        "option_sheet": "economizassaoMg",
        "display": "Economizassao Mg",
    },
]


def normalize_name(text: str) -> str:
    norm = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in norm if unicodedata.category(ch) != "Mn")
    return stripped.upper()


def extract_format_from_filename(filename: str) -> str:
    lowered = filename.lower()
    if "16x9" in lowered:
        return "16x9"
    if "9x16" in lowered:
        return "9x16"
    if "1x1" in lowered:
        return "1x1"
    return "16x9"


def detect_region_from_filename(filename: str) -> str:
    name = normalize_name(filename)
    if name.endswith("_MG.MP4") or name.endswith("_MG.PNG") or name.endswith("_MG.JPG") or "_MG." in name or "_MG_" in name:
        return "MG"
    return "NACIONAL"


def find_subdir(parent: Path, target: str) -> Optional[Path]:
    target_norm = normalize_name(target)
    for entry in parent.iterdir():
        if entry.is_dir() and normalize_name(entry.name) == target_norm:
            return entry
    return None


def scan_files(folder: Path, exts: Tuple[str, ...]) -> List[Path]:
    if not folder or not folder.exists():
        return []
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts])


def upload_and_url(
    token: str,
    slug: str,
    category: str,
    region: str,
    file_path: Path,
) -> str:
    rel_path = f"{region.lower()}/{file_path.name}"
    object_path = build_object_path(slug, category, rel_path)
    try:
        upload_file(PROJECT_URL, BUCKET, object_path, file_path, token)
    except RuntimeError as exc:
        if "already exists" not in str(exc).lower():
            raise
    return public_url(PROJECT_URL, BUCKET, object_path)


def write_csv(path: Path, headers: List[str], rows: List[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    token = os.environ.get("SUPABASE_SERVICE_ROLE")
    if not token:
        print("SUPABASE_SERVICE_ROLE nao informado.")
        return 2

    EXPORT_DIR.mkdir(exist_ok=True)
    ensure_bucket(PROJECT_URL, BUCKET, token)
    now_label = datetime.now().strftime("%b %d, %Y %I:%M %p")

    cab_root = find_subdir(CAMPAIGN_BASE_PATH, "CAB") or find_subdir(CAMPAIGN_BASE_PATH, "CABECA")
    ass_root = find_subdir(CAMPAIGN_BASE_PATH, "ASS") or find_subdir(CAMPAIGN_BASE_PATH, "ASSINATURA") or find_subdir(CAMPAIGN_BASE_PATH, "ENCERRAMENTO")
    bg_root = find_subdir(CAMPAIGN_BASE_PATH, "BG") or find_subdir(CAMPAIGN_BASE_PATH, "BACKGROUND")
    thumb_root = find_subdir(CAMPAIGN_BASE_PATH, "THUMB")

    cab_rows: List[dict] = []
    ass_rows: List[dict] = []
    bg_rows: List[dict] = []
    trilha_rows: List[dict] = []
    form_rows: List[dict] = []
    uploaded_cache: Dict[Tuple[str, str, str], str] = {}

    # --- Trilha ---
    trilha_root = find_subdir(CAMPAIGN_BASE_PATH, "TRILHA") or find_subdir(CAMPAIGN_BASE_PATH, "TRHILHA")
    trilha_url: Optional[str] = None
    trilha_file: Optional[Path] = None
    if trilha_root:
        trilha_files = scan_files(trilha_root, (".mp3", ".wav"))
        if trilha_files:
            trilha_file = trilha_files[0]
            key = ("trilha", "all", trilha_file.name)
            uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "trilha", "all", trilha_file)
            trilha_url = uploaded_cache[key]
            print(f"  Trilha: {trilha_file.name}")

    # --- Thumb ---
    thumb_url_by_option: Dict[str, str] = {}
    if thumb_root:
        thumb_files = scan_files(thumb_root, (".png", ".jpg", ".jpeg"))
        for tf in thumb_files:
            region = detect_region_from_filename(tf.name)
            key = ("thumb", region, tf.name)
            if key not in uploaded_cache:
                uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "thumb", region, tf)
                print(f"  Thumb [{region}]: {tf.name}")
            for campaign in CAMPAIGNS:
                if campaign["region"] == region:
                    thumb_url_by_option[campaign["option_sheet"]] = uploaded_cache[key]

    # --- Cabeca ---
    cab_files = scan_files(cab_root, (".mp4",))
    for media in cab_files:
        region = detect_region_from_filename(media.name)
        key = ("cabeca", region, media.name)
        if key not in uploaded_cache:
            uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "cabeca", region, media)
            print(f"  Cab [{region}]: {media.name}")
        option = next(c["option_sheet"] for c in CAMPAIGNS if c["region"] == region)
        cab_rows.append(
            {
                "ligacaoCampanhaFieldName": option,
                "locucaoTranscrita": "",
                "nameFile": media.name,
                "OS Formato modelo": extract_format_from_filename(media.name),
                "urlFile": uploaded_cache[key],
                "Creation Date": now_label,
            }
        )

    # --- Assinatura (arquivos compartilhados entre regioes) ---
    ass_files = scan_files(ass_root, (".mp4",))
    for media in ass_files:
        region_from_file = detect_region_from_filename(media.name)
        if region_from_file == "MG":
            regions_to_assign = ["MG"]
        else:
            # Arquivo sem sufixo MG -> compartilhado entre todas as regioes
            regions_to_assign = [c["region"] for c in CAMPAIGNS]
        for region in regions_to_assign:
            key = ("assinatura", region, media.name)
            if key not in uploaded_cache:
                uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "assinatura", region, media)
                print(f"  Ass [{region}]: {media.name}")
            option = next(c["option_sheet"] for c in CAMPAIGNS if c["region"] == region)
            ass_rows.append(
                {
                    "ligacaoCampanhaFieldName": option,
                    "locucaoTranscrita": "",
                    "nameFile": media.name,
                    "OS Formato modelo": extract_format_from_filename(media.name),
                    "urlFile": uploaded_cache[key],
                    "Creation Date": now_label,
                }
            )

    # --- Background ---
    bg_files = scan_files(bg_root, (".mp4", ".png", ".jpg", ".jpeg"))
    for media in bg_files:
        region = detect_region_from_filename(media.name)
        fmt = extract_format_from_filename(media.name)
        key = ("background", region, media.name)
        if key not in uploaded_cache:
            uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "background", region, media)
            print(f"  Bg  [{region}]: {media.name}")
        option = next(c["option_sheet"] for c in CAMPAIGNS if c["region"] == region)
        bg_rows.append(
            {
                "ligacaoCampanhaFieldName": option,
                "locucaoTranscrita": "",
                "nameFile": media.name,
                "OS Formato modelo": fmt,
                "urlFile": uploaded_cache[key],
                "Creation Date": now_label,
            }
        )

    # --- Trilha CSV ---
    all_options = " , ".join(c["option_sheet"] for c in CAMPAIGNS)
    if trilha_url and trilha_file:
        trilha_rows.append(
            {
                "ligacaoCampanhaFieldName": all_options,
                "locucaoTranscrita": "",
                "nameFile": trilha_file.name,
                "OS Formato modelo": "16x9",
                "urlFile": trilha_url,
                "Creation Date": now_label,
            }
        )

    # --- formCampanha ---
    for campaign in CAMPAIGNS:
        form_rows.append(
            {
                "ajusteCampanha": "acelera",
                "ativo": "sim",
                "categoriaLiberacao": "",
                "colorLetras": "#d81510",
                "formCelebridade": "",
                "formSelo": "",
                "imagem": thumb_url_by_option.get(campaign["option_sheet"], ""),
                "option": campaign["display"],
                "optionSheet": campaign["option_sheet"],
                "OS materiais": "Filme de 15s , Filme de 30s , Spot de Radio 15s , Spot de Radio 30s",
                "OS type midia": "Tv , Radio",
            }
        )

    # --- Escrever CSVs ---
    media_headers = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
    ]
    write_csv(EXPORT_DIR / f"export_All-mCabecas-{CAMPAIGN_SLUG}.csv", media_headers, cab_rows)
    write_csv(EXPORT_DIR / f"export_All-mAssinaturas-{CAMPAIGN_SLUG}.csv", media_headers, ass_rows)
    write_csv(EXPORT_DIR / f"export_All-mBackground-{CAMPAIGN_SLUG}.csv", media_headers, bg_rows)
    write_csv(EXPORT_DIR / f"export_All-mTrilhas-{CAMPAIGN_SLUG}.csv", media_headers, trilha_rows)

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
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    write_csv(
        EXPORT_DIR / f"export_All-formCampanhas-{CAMPAIGN_SLUG}-{stamp}.csv",
        form_headers,
        form_rows,
    )

    print(
        f"\n{CAMPAIGN_SLUG}: cabeca={len(cab_rows)} assinatura={len(ass_rows)} "
        f"background={len(bg_rows)} trilha={len(trilha_rows)} form={len(form_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
