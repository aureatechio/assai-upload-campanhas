import csv
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from upload_supabase_midias import (
    build_object_path,
    ensure_bucket,
    public_url,
    upload_file,
)


CAMPAIGN_SLUG = "operacao-preco-baixo-fev-2026"
CAMPAIGN_BASE_PATH = Path(
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\OPERACAO PRECO BAIXO FEVEREIRO 2026"
)
EXPORT_DIR = Path("exportados")
PROJECT_URL = "https://xhzgscezaaekbaqrkddu.supabase.co"
BUCKET = "assai-midias"

CAMPAIGNS = [
    {
        "region": "NACIONAL",
        "option_sheet": "operacaoPrecoBaixoFev2026Nac",
        "display": "Operacao Preco Baixo Fev 2026 Nacional",
    },
    {
        "region": "MG",
        "option_sheet": "operacaoPrecoBaixoFev2026Mg",
        "display": "Operacao Preco Baixo Fev 2026 Mg",
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


def find_subdir(parent: Path, target: str) -> Optional[Path]:
    target_norm = normalize_name(target)
    for entry in parent.iterdir():
        if entry.is_dir() and normalize_name(entry.name) == target_norm:
            return entry
    return None


def map_region_dirs(parent: Path) -> Dict[str, Path]:
    regions: Dict[str, Path] = {}
    for entry in parent.iterdir():
        if not entry.is_dir():
            continue
        name = normalize_name(entry.name)
        if "NACIONAL" in name or name == "NAC":
            regions["NACIONAL"] = entry
        elif name.endswith("MG") or name == "MG":
            regions["MG"] = entry
    return regions


def scan_files(folder: Path, exts: Tuple[str, ...]) -> List[Path]:
    if not folder.exists():
        return []
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts])


def thumb_by_region(thumb_root: Path) -> Dict[str, Path]:
    mapping: Dict[str, Path] = {}
    region_subdirs = map_region_dirs(thumb_root)
    if region_subdirs:
        for region, folder in region_subdirs.items():
            files = scan_files(folder, (".png", ".jpg", ".jpeg"))
            if files:
                mapping[region] = files[0]
        return mapping
    all_files = scan_files(thumb_root, (".png", ".jpg", ".jpeg"))
    for f in all_files:
        name = normalize_name(f.stem)
        if "MG" in name:
            mapping["MG"] = f
        elif "NAC" in name or "NACIONAL" in name:
            mapping["NACIONAL"] = f
    if not mapping and all_files:
        mapping["NACIONAL"] = all_files[0]
        if len(all_files) > 1:
            mapping["MG"] = all_files[1]
    return mapping


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

    region_dirs = map_region_dirs(CAMPAIGN_BASE_PATH)
    cab_rows: List[dict] = []
    ass_rows: List[dict] = []
    bg_rows: List[dict] = []
    trilha_rows: List[dict] = []
    form_rows: List[dict] = []
    uploaded_cache: Dict[Tuple[str, str, str], str] = {}

    trilha_root = find_subdir(CAMPAIGN_BASE_PATH, "TRILHA") or CAMPAIGN_BASE_PATH
    trilha_files = scan_files(trilha_root, (".mp3", ".wav"))
    trilha_url: Optional[str] = None
    if trilha_files:
        tf = trilha_files[0]
        key = ("trilha", "all", tf.name)
        uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "trilha", "all", tf)
        trilha_url = uploaded_cache[key]
        print(f"  Trilha: {tf.name}")

    thumb_url_by_option: Dict[str, str] = {}
    thumb_root = find_subdir(CAMPAIGN_BASE_PATH, "THUMB") or find_subdir(CAMPAIGN_BASE_PATH, "THUMBS")
    if thumb_root:
        thumb_map = thumb_by_region(thumb_root)
        for campaign in CAMPAIGNS:
            region = campaign["region"]
            thumb_file = thumb_map.get(region)
            if thumb_file:
                key = ("thumb", region, thumb_file.name)
                if key not in uploaded_cache:
                    uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "thumb", region, thumb_file)
                    print(f"  Thumb [{region}]: {thumb_file.name}")
                thumb_url_by_option[campaign["option_sheet"]] = uploaded_cache[key]

    for campaign in CAMPAIGNS:
        region = campaign["region"]
        option = campaign["option_sheet"]
        region_path = region_dirs.get(region)
        if not region_path:
            print(f"  AVISO: regiao {region} nao encontrada")
            continue

        cab_root = find_subdir(region_path, "CAB") or find_subdir(region_path, "CABECA") or region_path
        ass_root = find_subdir(region_path, "ASS") or find_subdir(region_path, "ASSINATURA") or find_subdir(region_path, "ENCERRAMENTO") or region_path
        bg_root = find_subdir(region_path, "BG") or find_subdir(region_path, "BACKGROUND") or region_path

        for media in scan_files(cab_root, (".mp4",)):
            key = ("cabeca", region, media.name)
            if key not in uploaded_cache:
                uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "cabeca", region, media)
                print(f"  Cab [{region}]: {media.name}")
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

        for media in scan_files(ass_root, (".mp4",)):
            key = ("assinatura", region, media.name)
            if key not in uploaded_cache:
                uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "assinatura", region, media)
                print(f"  Ass [{region}]: {media.name}")
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

        bg_files = scan_files(bg_root, (".mp4", ".png", ".jpg", ".jpeg"))
        format_seen: Dict[str, Path] = {}
        for media in bg_files:
            fmt = extract_format_from_filename(media.name)
            if fmt not in format_seen:
                format_seen[fmt] = media
        for fmt in ["16x9", "1x1", "9x16"]:
            media = format_seen.get(fmt)
            if not media:
                continue
            key = ("background", region, media.name)
            if key not in uploaded_cache:
                uploaded_cache[key] = upload_and_url(token, CAMPAIGN_SLUG, "background", region, media)
                print(f"  Bg  [{region}]: {media.name}")
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

    all_options = " , ".join(c["option_sheet"] for c in CAMPAIGNS)
    if trilha_url and trilha_files:
        trilha_rows.append(
            {
                "ligacaoCampanhaFieldName": all_options,
                "locucaoTranscrita": "",
                "nameFile": trilha_files[0].name,
                "OS Formato modelo": "16x9",
                "urlFile": trilha_url,
                "Creation Date": now_label,
            }
        )

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
