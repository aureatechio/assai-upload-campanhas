import argparse
import csv
import json
import mimetypes
import os
import re
import unicodedata
from base64 import b64encode
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv
load_dotenv()


DEFAULT_PROJECT_URL = "https://xhzgscezaaekbaqrkddu.supabase.co"
DEFAULT_BUCKET = "assai-midias"
DEFAULT_CAMPAIGN_PATH = (
    r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\DIA IMBATIVEL 30.01"
)
MAX_SIMPLE_UPLOAD = 50 * 1024 * 1024
TUS_CHUNK_SIZE = 6 * 1024 * 1024

MEDIA_EXTS = (".mp4", ".mp3", ".wav")
BG_EXTS = (".mp4", ".png", ".jpg", ".jpeg")
THUMB_EXTS = (".png", ".jpg", ".jpeg")

CATEGORY_FOLDERS = {
    "cabeca": {"CABECA", "CABECA", "CABECAS", "CABECA"},
    "assinatura": {"ASSINATURA", "ASSINATURAS", "ENCERRAMENTO"},
    "background": {"BG", "BACKGROUND", "BG OFERTAS"},
    "trilha": {"TRILHA"},
    "thumb": {"THUMB", "THUMBS"},
}

INVALID_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._ -]+")

CSV_PATTERNS = {
    "cabeca": "export_All-mCabecas-{slug}.csv",
    "assinatura": "export_All-mAssinaturas-{slug}.csv",
    "background": "export_All-mBackground-{slug}.csv",
    "trilha": "export_All-mTrilhas-{slug}.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload de midias para o Supabase Storage e atualiza CSVs."
    )
    parser.add_argument("--project-url", default=DEFAULT_PROJECT_URL)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--campaign-path", default=DEFAULT_CAMPAIGN_PATH)
    parser.add_argument("--export-dir", default="exportados")
    parser.add_argument("--campaign-slug")
    parser.add_argument(
        "--category",
        action="append",
        choices=["cabeca", "assinatura", "background", "trilha", "thumb"],
        help="Restringir categorias a enviar (pode repetir).",
    )
    parser.add_argument("--apply", action="store_true", help="Executar uploads e atualizar CSVs.")
    parser.add_argument("--no-csv", action="store_true", help="Nao atualizar CSVs.")
    parser.add_argument("--dry-run", action="store_true", help="Nao faz upload nem altera CSV.")
    return parser.parse_args()


def normalize_segment(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    stripped = stripped.replace(" ", "_")
    stripped = re.sub(r"[^A-Za-z0-9._-]+", "", stripped)
    stripped = re.sub(r"_+", "_", stripped).strip("_")
    return stripped or "segment"


def sanitize_filename(filename: str) -> str:
    stem, ext = os.path.splitext(filename)
    clean_stem = INVALID_FILENAME_PATTERN.sub("", stem).strip()
    clean_stem = re.sub(r"\\s+", " ", clean_stem)
    if not clean_stem:
        clean_stem = "arquivo"
    return f"{clean_stem}{ext}"


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream"


def request_json(method: str, url: str, token: str, payload: Optional[dict] = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("apikey", token)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ensure_bucket(project_url: str, bucket: str, token: str) -> None:
    url = f"{project_url}/storage/v1/bucket"
    data = request_json("GET", url, token)
    existing = {item.get("id") for item in data} if isinstance(data, list) else set()
    if bucket in existing:
        return
    payload = {"id": bucket, "name": bucket, "public": True}
    request_json("POST", url, token, payload)


def find_category_dir(campaign_path: Path, names: Iterable[str]) -> Optional[Path]:
    target = {normalize_segment(name).upper() for name in names}
    for entry in campaign_path.iterdir():
        if not entry.is_dir():
            continue
        if normalize_segment(entry.name).upper() in target:
            return entry
    return None


def detect_period(segments: Iterable[str]) -> Optional[str]:
    for seg in segments:
        upper = normalize_segment(seg).upper()
        if "HOJE" in upper:
            return "HOJE"
        if "AMANHA" in upper:
            return "AMANHA"
        if "GENERICO" in upper:
            return "GENERICO"
    return None


def detect_region(segments: Iterable[str]) -> Optional[str]:
    for seg in segments:
        upper = normalize_segment(seg).upper()
        if "NACIONAL" in upper or upper == "NAC":
            return "NACIONAL"
        if upper.endswith("MG") or upper == "MG":
            return "MG"
    return None


def scan_files(
    root: Path, category: str, exts: Tuple[str, ...]
) -> List[Tuple[Path, str, Optional[str], Optional[str]]]:
    files: List[Tuple[Path, str, Optional[str], Optional[str]]] = []
    if not root or not root.exists():
        return files
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if not path.name.lower().endswith(exts):
            continue
        if category == "thumb":
            sanitized = sanitize_filename(path.name)
            if sanitized != path.name:
                new_path = path.with_name(sanitized)
                if not new_path.exists():
                    path.rename(new_path)
                    path = new_path
        rel = path.relative_to(root)
        segments = rel.parts[:-1]
        period = detect_period(segments) if category in {"cabeca", "assinatura"} else None
        region = detect_region(segments) if category in {"cabeca", "assinatura"} else None
        files.append((path, str(rel), period, region))
    return files


def build_object_path(slug: str, category: str, rel_path: str) -> str:
    rel_parts = Path(rel_path).parts
    file_name = rel_parts[-1]
    stem, ext = os.path.splitext(file_name)
    safe_file = f"{normalize_segment(stem)}{ext.lower()}"
    if len(rel_parts) <= 1:
        return f"campanhas/{slug}/{category}/{safe_file}"
    sanitized_dirs = [normalize_segment(part) for part in rel_parts[:-1]]
    sanitized_rel = "/".join(sanitized_dirs)
    return f"campanhas/{slug}/{category}/{sanitized_rel}/{safe_file}"


def upload_file(
    project_url: str, bucket: str, object_path: str, file_path: Path, token: str
) -> None:
    if file_path.stat().st_size > MAX_SIMPLE_UPLOAD:
        tus_upload(project_url, bucket, object_path, file_path, token)
        return
    url_path = quote(object_path, safe="/")
    url = f"{project_url}/storage/v1/object/{bucket}/{url_path}"
    data = file_path.read_bytes()
    req = Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("apikey", token)
    req.add_header("Content-Type", guess_mime(file_path))
    req.add_header("x-upsert", "true")
    try:
        with urlopen(req, timeout=60) as resp:
            resp.read()
    except HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        raise RuntimeError(f"HTTP {exc.code} {body}".strip()) from exc


def storage_host(project_url: str) -> str:
    parsed = urlparse(project_url)
    host = parsed.netloc
    if host.endswith(".supabase.co"):
        project_id = host.split(".")[0]
        return f"{parsed.scheme}://{project_id}.storage.supabase.co"
    return project_url


def tus_upload(
    project_url: str, bucket: str, object_path: str, file_path: Path, token: str
) -> None:
    storage_base = storage_host(project_url)
    endpoint = f"{storage_base}/storage/v1/upload/resumable"
    size = file_path.stat().st_size
    content_type = guess_mime(file_path)

    metadata = {
        "bucketName": bucket,
        "objectName": object_path,
        "contentType": content_type,
        "cacheControl": "3600",
    }
    metadata_header = ",".join(
        f"{key} {b64encode(str(value).encode('utf-8')).decode('utf-8')}"
        for key, value in metadata.items()
    )

    create_req = Request(endpoint, method="POST")
    create_req.add_header("Authorization", f"Bearer {token}")
    create_req.add_header("apikey", token)
    create_req.add_header("Tus-Resumable", "1.0.0")
    create_req.add_header("Upload-Length", str(size))
    create_req.add_header("Upload-Metadata", metadata_header)
    create_req.add_header("x-upsert", "true")

    try:
        with urlopen(create_req, timeout=30) as resp:
            location = resp.headers.get("Location")
    except HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        raise RuntimeError(f"tus create HTTP {exc.code} {body}".strip()) from exc

    if not location:
        raise RuntimeError("Upload resumable sem Location.")
    if location.startswith("/"):
        location = f"{storage_base}{location}"

    offset = 0
    with file_path.open("rb") as handle:
        while offset < size:
            chunk = handle.read(TUS_CHUNK_SIZE)
            if not chunk:
                break
            patch_req = Request(location, data=chunk, method="PATCH")
            patch_req.add_header("Authorization", f"Bearer {token}")
            patch_req.add_header("apikey", token)
            patch_req.add_header("Tus-Resumable", "1.0.0")
            patch_req.add_header("Upload-Offset", str(offset))
            patch_req.add_header("Content-Type", "application/offset+octet-stream")
            try:
                with urlopen(patch_req, timeout=60) as resp:
                    new_offset = resp.headers.get("Upload-Offset")
            except HTTPError as exc:
                body = exc.read().decode("utf-8") if exc.fp else ""
                raise RuntimeError(
                    f"tus patch HTTP {exc.code} {body}".strip()
                ) from exc
            if new_offset is not None:
                offset = int(new_offset)
            else:
                offset += len(chunk)


def public_url(project_url: str, bucket: str, object_path: str) -> str:
    url_path = quote(object_path, safe="/")
    return f"{project_url}/storage/v1/object/public/{bucket}/{url_path}"


def infer_period_region_from_option(option: str) -> Tuple[Optional[str], Optional[str]]:
    if not option:
        return None, None
    lowered = option.lower()
    period = None
    if "hoje" in lowered:
        period = "HOJE"
    elif "amanha" in lowered:
        period = "AMANHA"
    elif "generico" in lowered:
        period = "GENERICO"
    region = "MG" if lowered.endswith("mg") or "mg" in lowered else "NACIONAL"
    return period, region


def update_csv(
    csv_path: Path,
    category: str,
    url_map: Dict[Tuple[Optional[str], Optional[str], str], str],
    project_url: str,
    bucket: str,
) -> int:
    updated = 0
    rows: List[dict] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        for row in reader:
            filename = row.get("nameFile", "")
            if not filename:
                rows.append(row)
                continue
            if category in {"cabeca", "assinatura"}:
                period, region = infer_period_region_from_option(
                    row.get("ligacaoCampanhaFieldName", "")
                )
                key = (period, region, filename)
            else:
                key = (None, None, filename)

            new_url = url_map.get(key)
            if not new_url and category in {"cabeca", "assinatura"}:
                fallback_key = (None, None, filename)
                new_url = url_map.get(fallback_key)

            if new_url:
                row["urlFile"] = new_url
                updated += 1
            rows.append(row)

    if updated:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    return updated


def derive_slug(export_dir: Path) -> Optional[str]:
    pattern = re.compile(r"export_All-formCampanhas-(.+)-\d{4}-\d{2}-\d{2}_")
    candidates = sorted(export_dir.glob("export_All-formCampanhas-*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    for csv_path in candidates:
        match = pattern.search(csv_path.name)
        if match:
            return match.group(1)
    return None


def main() -> int:
    args = parse_args()
    token = os.environ.get("SUPABASE_SERVICE_ROLE")
    if not token:
        print("SUPABASE_SERVICE_ROLE nao informado.")
        return 2

    export_dir = Path(args.export_dir)
    campaign_path = Path(args.campaign_path)
    slug = args.campaign_slug or derive_slug(export_dir)
    if not slug:
        print("Nao foi possivel determinar o slug da campanha.")
        return 1

    dry_run = args.dry_run or not args.apply
    print(f"Modo: {'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"Projeto: {args.project_url}")
    print(f"Bucket: {args.bucket}")
    print(f"Slug: {slug}")

    if not dry_run:
        ensure_bucket(args.project_url, args.bucket, token)

    url_maps: Dict[str, Dict[Tuple[Optional[str], Optional[str], str], str]] = {
        "cabeca": {},
        "assinatura": {},
        "background": {},
        "trilha": {},
    }

    allowed_categories = set(args.category) if args.category else None
    category_dirs = {
        "cabeca": find_category_dir(campaign_path, CATEGORY_FOLDERS["cabeca"]),
        "assinatura": find_category_dir(campaign_path, CATEGORY_FOLDERS["assinatura"]),
        "background": find_category_dir(campaign_path, CATEGORY_FOLDERS["background"]),
        "trilha": find_category_dir(campaign_path, CATEGORY_FOLDERS["trilha"]),
        "thumb": find_category_dir(campaign_path, CATEGORY_FOLDERS["thumb"]),
    }

    ext_map = {
        "cabeca": MEDIA_EXTS,
        "assinatura": MEDIA_EXTS,
        "background": BG_EXTS,
        "trilha": MEDIA_EXTS,
        "thumb": THUMB_EXTS,
    }

    for category, root in category_dirs.items():
        if allowed_categories and category not in allowed_categories:
            continue
        if not root:
            continue
        files = scan_files(root, category, ext_map[category])
        for file_path, rel_path, period, region in files:
            object_path = build_object_path(slug, category, rel_path)
            if not dry_run:
                try:
                    upload_file(args.project_url, args.bucket, object_path, file_path, token)
                except Exception as exc:
                    print(f"Erro upload {file_path.name}: {exc}")
                    continue
            if category in url_maps:
                key = (period, region, file_path.name)
                url_maps[category][key] = public_url(
                    args.project_url, args.bucket, object_path
                )

    if dry_run:
        print("Dry-run concluido (sem uploads e sem CSV).")
        return 0

    if not args.no_csv:
        for category, pattern in CSV_PATTERNS.items():
            if allowed_categories and category not in allowed_categories:
                continue
            csv_path = export_dir / pattern.format(slug=slug)
            if not csv_path.exists():
                continue
            updated = update_csv(
                csv_path,
                category,
                url_maps.get(category, {}),
                args.project_url,
                args.bucket,
            )
            print(f"CSV {csv_path.name}: {updated} URLs atualizadas")

    print("Concluido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
