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


CAMPAIGN_SLUG = "dia-imbativel-fev-2026"
CAMPAIGN_BASE_PATH = Path(
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\DIA IMBATIVEL FEVEREIRO 2026"
)
EXPORT_DIR = Path("exportados")
PROJECT_URL = "https://xhzgscezaaekbaqrkddu.supabase.co"
BUCKET = "assai-midias"

CAMPAIGNS = [
    {
        "period": "HOJE",
        "region": "NACIONAL",
        "option_sheet": "diaImbativelFev2026Hoje",
        "display": "Dia Imbativel Fev 2026 Hoje Nacional",
    },
    {
        "period": "HOJE",
        "region": "MG",
        "option_sheet": "diaImbativelFev2026HojeMg",
        "display": "Dia Imbativel Fev 2026 Hoje Mg",
    },
    {
        "period": "AMANHA",
        "region": "NACIONAL",
        "option_sheet": "diaImbativelFev2026Amanha",
        "display": "Dia Imbativel Fev 2026 Amanha Nacional",
    },
    {
        "period": "AMANHA",
        "region": "MG",
        "option_sheet": "diaImbativelFev2026AmanhaMg",
        "display": "Dia Imbativel Fev 2026 Amanha Mg",
    },
    {
        "period": "GENERICA",
        "region": "NACIONAL",
        "option_sheet": "diaImbativelFev2026Gen",
        "display": "Dia Imbativel Fev 2026 Generica Nacional",
    },
    {
        "period": "GENERICA",
        "region": "MG",
        "option_sheet": "diaImbativelFev2026GenMg",
        "display": "Dia Imbativel Fev 2026 Generica Mg",
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


def map_period_dirs(root: Path) -> Dict[str, Path]:
    periods: Dict[str, Path] = {}
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        name = normalize_name(entry.name)
        if "HOJE" in name:
            periods["HOJE"] = entry
        elif "AMANHA" in name:
            periods["AMANHA"] = entry
        elif "GENERICO" in name or "GENERICA" in name:
            periods["GENERICA"] = entry
    return periods


def find_subdir(parent: Path, target: str) -> Optional[Path]:
    target_norm = normalize_name(target)
    for entry in parent.iterdir():
        if entry.is_dir() and normalize_name(entry.name) == target_norm:
            return entry
    return None


def find_subdir_contains(parent: Path, keyword: str) -> Optional[Path]:
    keyword_norm = normalize_name(keyword)
    for entry in parent.iterdir():
        if entry.is_dir() and keyword_norm in normalize_name(entry.name):
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


def thumb_by_period_region(thumb_root: Path) -> Dict[Tuple[str, str], Path]:
    mapping: Dict[Tuple[str, str], Path] = {}
    all_files = scan_files(thumb_root, (".png", ".jpg", ".jpeg"))
    for f in all_files:
        name = normalize_name(f.stem)
        period = None
        if "HOJE" in name:
            period = "HOJE"
        elif "AMANHA" in name:
            period = "AMANHA"
        elif "GENERICO" in name or "GENERICA" in name:
            period = "GENERICA"
        if not period:
            continue
        # (2) = NACIONAL, (3) = MG convention
        if "(2)" in f.name:
            mapping[(period, "NACIONAL")] = f
        elif "(3)" in f.name:
            mapping[(period, "MG")] = f
    return mapping


def upload_and_url(
    token: str,
    slug: str,
    category: str,
    period: str,
    region: str,
    file_path: Path,
) -> str:
    rel_path = f"{period.lower()}/{region.lower()}/{file_path.name}"
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

    period_dirs = map_period_dirs(CAMPAIGN_BASE_PATH)
    cab_rows: List[dict] = []
    ass_rows: List[dict] = []
    bg_rows: List[dict] = []
    form_rows: List[dict] = []
    uploaded_cache: Dict[Tuple[str, str, str, str], str] = {}
    thumb_url_by_option: Dict[str, str] = {}

    # Process thumbnails
    thumb_root = find_subdir(CAMPAIGN_BASE_PATH, "THUMB")
    if thumb_root:
        thumb_map = thumb_by_period_region(thumb_root)
        for campaign in CAMPAIGNS:
            key_tuple = (campaign["period"], campaign["region"])
            thumb_file = thumb_map.get(key_tuple)
            if thumb_file:
                cache_key = ("thumb", campaign["period"], campaign["region"], thumb_file.name)
                if cache_key not in uploaded_cache:
                    uploaded_cache[cache_key] = upload_and_url(
                        token, CAMPAIGN_SLUG, "thumb",
                        campaign["period"], campaign["region"], thumb_file,
                    )
                    print(f"  Thumb [{campaign['period']}/{campaign['region']}]: {thumb_file.name}")
                thumb_url_by_option[campaign["option_sheet"]] = uploaded_cache[cache_key]

    for period, period_path in period_dirs.items():
        cabeca_root = find_subdir(period_path, "CABECA") or period_path
        ass_root = find_subdir(period_path, "ENCERRAMENTO") or period_path
        bg_root = find_subdir_contains(period_path, "BG") or period_path

        cab_regions = map_region_dirs(cabeca_root)
        ass_regions = map_region_dirs(ass_root)
        bg_regions = map_region_dirs(bg_root)

        for campaign in CAMPAIGNS:
            if campaign["period"] != period:
                continue
            region = campaign["region"]
            option = campaign["option_sheet"]

            # Cabeca
            for media in scan_files(cab_regions.get(region, Path()), (".mp4",)):
                key = ("cabeca", period, region, media.name)
                if key not in uploaded_cache:
                    uploaded_cache[key] = upload_and_url(
                        token, CAMPAIGN_SLUG, "cabeca", period, region, media,
                    )
                    print(f"  Cab [{period}/{region}]: {media.name}")
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

            # Assinatura (Encerramento)
            for media in scan_files(ass_regions.get(region, Path()), (".mp4",)):
                key = ("assinatura", period, region, media.name)
                if key not in uploaded_cache:
                    uploaded_cache[key] = upload_and_url(
                        token, CAMPAIGN_SLUG, "assinatura", period, region, media,
                    )
                    print(f"  Ass [{period}/{region}]: {media.name}")
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

            # Background (BG OFERTA)
            bg_files = scan_files(bg_regions.get(region, Path()), (".mp4", ".png", ".jpg", ".jpeg"))
            format_seen: Dict[str, Path] = {}
            for media in bg_files:
                fmt = extract_format_from_filename(media.name)
                if fmt not in format_seen:
                    format_seen[fmt] = media
            for fmt in ["16x9", "1x1", "9x16"]:
                media = format_seen.get(fmt)
                if not media:
                    continue
                key = ("background", period, region, media.name)
                if key not in uploaded_cache:
                    uploaded_cache[key] = upload_and_url(
                        token, CAMPAIGN_SLUG, "background", period, region, media,
                    )
                    print(f"  Bg  [{period}/{region}]: {media.name}")
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

    # Form campanhas
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
        f"background={len(bg_rows)} form={len(form_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
