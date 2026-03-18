from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import csv
import json
import mimetypes
import re
import unicodedata
import uuid
import threading
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from urllib.request import Request as URLRequest, urlopen
from urllib.error import HTTPError, URLError
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from bubble_uploader import (
    CATEGORY_TO_TABLE,
    CATEGORY_TO_FILE_SUFFIX,
    DEFAULT_BASE_URL,
    upload_csv_to_bubble,
)

app = Flask(__name__, template_folder='../frontend')
CORS(app)

CAMPAIGNS_DIR = os.getenv('CAMPAIGNS_DIR', r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS")
EXPORT_DIR = os.getenv('EXPORT_DIR', "../exportados")

# In-memory store for background upload tasks
_upload_tasks: dict = {}
_upload_tasks_lock = threading.Lock()

# ── Supabase Storage ─────────────────────────────────────────────────
SUPABASE_PROJECT_URL = os.getenv('SUPABASE_PROJECT_URL', 'https://xhzgscezaaekbaqrkddu.supabase.co')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'assai-midias')

SUPABASE_CATEGORY_MAP = {
    'cabeca': 'cabeca',
    'bg': 'background',
    'assinatura': 'assinatura',
    'trilha': 'trilha',
    'thumb': 'thumb',
}

def to_camel_case(text, state=None):
    words = re.sub(r'[^a-zA-Z0-9\s]', '', text).split()
    if not words:
        return ''

    camel_case = words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    if state:
        state_camel = to_camel_case_simple(state)
        camel_case += state_camel.capitalize()

    return camel_case

def to_camel_case_simple(text):
    words = re.sub(r'[^a-zA-Z0-9\s]', '', text).split()
    if not words:
        return ''
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

def normalize_segment(text):
    """Normalize text for Supabase Storage paths."""
    normalized = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    stripped = stripped.replace(" ", "_")
    stripped = re.sub(r"[^A-Za-z0-9._-]+", "", stripped)
    stripped = re.sub(r"_+", "_", stripped).strip("_")
    return stripped or "segment"

def build_supabase_object_path(slug, bucket_name, filename, state=None):
    """Build the Supabase Storage object path for a media file."""
    supabase_cat = SUPABASE_CATEGORY_MAP.get(bucket_name, bucket_name)
    stem, ext = os.path.splitext(filename)
    safe_file = f"{normalize_segment(stem)}{ext.lower()}"
    if state:
        parts = re.split(r'[/\\]', state)
        safe_parts = [normalize_segment(p) for p in parts if p]
        safe_state = "/".join(safe_parts)
        return f"campanhas/{slug}/{supabase_cat}/{safe_state}/{safe_file}"
    return f"campanhas/{slug}/{supabase_cat}/{safe_file}"

def get_supabase_url(bucket_name, filename, slug, state=None):
    """Generate Supabase Storage public URL for a media file."""
    object_path = build_supabase_object_path(slug, bucket_name, filename, state)
    url_path = quote(object_path, safe="/")
    return f"{SUPABASE_PROJECT_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{url_path}"

# Explicit MIME types – Windows mimetypes DB is often incomplete
_MIME_OVERRIDES = {
    '.mp4': 'video/mp4',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.webm': 'video/webm',
    '.svg': 'image/svg+xml',
}

def _guess_mime(file_path):
    """Guess MIME type with reliable fallbacks for Windows."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in _MIME_OVERRIDES:
        return _MIME_OVERRIDES[ext]
    mime, _ = mimetypes.guess_type(file_path)
    return mime or "application/octet-stream"

_UPLOAD_MAX_RETRIES = 3
_UPLOAD_BACKOFF_BASE = 3  # seconds

def _supabase_upload_file(file_path, object_path, token):
    """Upload a single file to Supabase Storage with retry + backoff."""
    url_encoded = quote(object_path, safe="/")
    url = f"{SUPABASE_PROJECT_URL}/storage/v1/object/{SUPABASE_BUCKET}/{url_encoded}"
    content_type = _guess_mime(file_path)

    file_size = os.path.getsize(file_path)
    if file_size > 50 * 1024 * 1024:
        raise RuntimeError(
            f"Arquivo muito grande ({file_size / (1024*1024):.1f} MB). "
            f"Limite do Supabase REST API e 50 MB."
        )

    with open(file_path, 'rb') as f:
        data = f.read()

    last_error = None

    for attempt in range(_UPLOAD_MAX_RETRIES):
        # Try POST first; on 400 fall through to PUT
        for method in ("POST", "PUT"):
            req = URLRequest(url, data=data, method=method)
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("apikey", token)
            req.add_header("Content-Type", content_type)
            req.add_header("x-upsert", "true")
            req.add_header("cache-control", "3600")
            try:
                with urlopen(req, timeout=300) as resp:
                    resp.read()
                return  # success
            except HTTPError as exc:
                body = ""
                try:
                    body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                # POST 400 → retry with PUT (duplicate)
                if method == "POST" and exc.code == 400:
                    continue
                last_error = RuntimeError(
                    f"HTTP {exc.code} – {body or 'sem detalhes'}"
                )
                break  # don't try PUT, go to retry
            except (URLError, OSError, ConnectionError) as exc:
                # Covers 10054 (WSAECONNRESET), timeouts, etc.
                last_error = RuntimeError(
                    f"Erro de conexao (tentativa {attempt + 1}/{_UPLOAD_MAX_RETRIES}): {exc}"
                )
                break  # go to retry
        else:
            # Both POST and PUT failed with 400 — no point retrying
            if last_error:
                raise last_error
            raise RuntimeError("Falha no upload: POST e PUT retornaram 400")

        # Backoff before retry
        if attempt < _UPLOAD_MAX_RETRIES - 1:
            wait = _UPLOAD_BACKOFF_BASE * (2 ** attempt)  # 3s, 6s, 12s
            time.sleep(wait)

    # All retries exhausted
    raise last_error or RuntimeError("Upload falhou apos todas as tentativas")

def extract_format_from_filename(filename):
    """Extract format from filename (16x9, 9x16, 1x1)"""
    formats = ['16x9', '9x16', '1x1']
    filename_lower = filename.lower()

    for fmt in formats:
        if fmt in filename_lower:
            return fmt

    # Default format if not found
    return '16x9'

def extract_campaign_name_from_filename(filename):
    """Extract campaign name from filename"""
    # Remove extension
    name_without_ext = os.path.splitext(filename)[0]

    # Remove format suffixes (16x9, 9x16, 1x1)
    name_clean = name_without_ext
    formats = ['16x9', '9x16', '1x1']
    for fmt in formats:
        if fmt in name_clean:
            name_clean = name_clean.replace(fmt, '')

    # Remove common prefixes
    prefixes_to_remove = ['cab', 'ass']
    for prefix in prefixes_to_remove:
        if name_clean.lower().startswith(prefix):
            name_clean = name_clean[len(prefix):]

    # Convert to camelCase and add aniversario prefix
    # Examples: FeirassaiTercaeQuarta -> aniversarioFeirassaiTercaeQuarta
    if name_clean:
        base_name = name_clean[0].lower() + name_clean[1:] if len(name_clean) > 1 else name_clean.lower()
        return 'aniversario' + base_name.capitalize()

    return 'aniversarioFeirassai'  # fallback

def find_folder(campaign_path, candidates):
    """Find the first existing folder from a list of candidate names"""
    for name in candidates:
        folder_path = os.path.join(campaign_path, name)
        if os.path.exists(folder_path):
            return folder_path
    return None

CABECA_NAMES = ['CABECA', 'CABEÇA', 'CABECAS', 'CABEÇAS']
ASSINATURA_NAMES = ['ASSINATURA', 'ASSINATURAS']
BG_NAMES = ['BG']
TRILHA_NAMES = ['TRILHA']
THUMB_NAMES = ['THUMB', 'THUMBS']
IMAGE_EXTS = ('.png', '.jpg', '.jpeg')

def scan_regional_states(campaign_path, campaign_name):
    """Scan regional campaign and return list of states found.

    Checks all media folders (CABECA, BG, ASSINATURA) for subfolders
    and returns the union of all states/regions found.
    """
    states_set = set()

    for folder_candidates in [CABECA_NAMES, BG_NAMES, ASSINATURA_NAMES]:
        folder_path = find_folder(campaign_path, folder_candidates)
        if folder_path:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    states_set.add(item)

    return sorted(states_set)

def scan_campaign_files_for_state(campaign_path, campaign_name, state):
    """Scan campaign folders for a specific state and extract files with formats"""
    campaign_name_camel = to_camel_case(campaign_name, state)
    slug = to_camel_case(campaign_name)
    results = []

    bucket_folders = [
        (CABECA_NAMES, 'cabeca', 'CABECAS'),
        (BG_NAMES, 'bg', 'BG'),
        (ASSINATURA_NAMES, 'assinatura', 'ASSINATURAS'),
        (TRILHA_NAMES, 'trilha', 'TRILHA'),
    ]

    for folder_candidates, bucket_name, folder_key in bucket_folders:
        base_folder_path = find_folder(campaign_path, folder_candidates)

        if not base_folder_path:
            continue

        state_folder_path = os.path.join(base_folder_path, state)

        if folder_key == 'CABECAS':
            if os.path.exists(state_folder_path):
                for file in os.listdir(state_folder_path):
                    if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                        results.append({
                            'campaign_name': campaign_name_camel,
                            'category': 'abertura',
                            'bucket': bucket_name,
                            'filename': file,
                            'format': extract_format_from_filename(file),
                            'url': get_supabase_url(bucket_name, file, slug, state),
                            'file_path': os.path.join(state_folder_path, file),
                            'state': state
                        })

        elif folder_key == 'TRILHA':
            # Trilha is unique (no MG/Nacional subfolders) – use base campaign name
            for root_dir, _dirs, files_in_dir in os.walk(base_folder_path):
                for file in files_in_dir:
                    if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                        results.append({
                            'campaign_name': slug,
                            'category': 'trilha',
                            'bucket': bucket_name,
                            'filename': file,
                            'format': extract_format_from_filename(file),
                            'url': get_supabase_url(bucket_name, file, slug),
                            'file_path': os.path.join(root_dir, file),
                            'state': None
                        })

        elif folder_key in ('BG', 'ASSINATURAS'):
            category = 'bg' if folder_key == 'BG' else 'assinatura'
            if os.path.exists(state_folder_path):
                for file in os.listdir(state_folder_path):
                    if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                        results.append({
                            'campaign_name': campaign_name_camel,
                            'category': category,
                            'bucket': bucket_name,
                            'filename': file,
                            'format': extract_format_from_filename(file),
                            'url': get_supabase_url(bucket_name, file, slug, state),
                            'file_path': os.path.join(state_folder_path, file),
                            'state': state
                        })

    # Scan THUMB folder - walk recursively to handle subfolders like NACIONAL/
    thumb_folder = find_folder(campaign_path, THUMB_NAMES)
    if thumb_folder:
        for root_dir, _dirs, files_in_dir in os.walk(thumb_folder):
            # Detect state from subfolder name or filename
            rel_dir = os.path.relpath(root_dir, thumb_folder)
            subfolder = None if rel_dir == '.' else rel_dir.split(os.sep)[0]
            for file in files_in_dir:
                if file.lower().endswith(IMAGE_EXTS):
                    # State priority: subfolder name > filename pattern > NACIONAL
                    if subfolder:
                        file_state = subfolder
                    elif '_mg' in file.lower():
                        file_state = 'MG'
                    else:
                        file_state = 'NACIONAL'
                    if file_state == state:
                        results.append({
                            'campaign_name': campaign_name_camel,
                            'category': 'thumb',
                            'bucket': 'thumb',
                            'filename': file,
                            'format': '1x1',
                            'url': get_supabase_url('thumb', file, slug, file_state),
                            'file_path': os.path.join(root_dir, file),
                            'state': state
                        })

    return results

def scan_campaign_files(campaign_path, campaign_name, state=None):
    """Scan campaign folders and extract files with formats"""
    if state:
        return scan_campaign_files_for_state(campaign_path, campaign_name, state)

    campaign_name_camel = to_camel_case(campaign_name)
    slug = campaign_name_camel
    results = []

    bucket_folders = [
        (CABECA_NAMES, 'cabeca', 'abertura'),
        (BG_NAMES, 'bg', 'bg'),
        (ASSINATURA_NAMES, 'assinatura', 'assinatura'),
        (TRILHA_NAMES, 'trilha', 'trilha'),
    ]

    for folder_candidates, bucket_name, category in bucket_folders:
        folder_path = find_folder(campaign_path, folder_candidates)

        if not folder_path:
            continue

        for root_dir, dirs, files_in_dir in os.walk(folder_path):
            for file in files_in_dir:
                if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                    rel_dir = os.path.relpath(root_dir, folder_path)
                    subfolder = None if rel_dir == '.' else rel_dir

                    results.append({
                        'campaign_name': campaign_name_camel,
                        'category': category,
                        'bucket': bucket_name,
                        'filename': file,
                        'format': extract_format_from_filename(file),
                        'url': get_supabase_url(bucket_name, file, slug, subfolder),
                        'file_path': os.path.join(root_dir, file),
                        'state': subfolder,
                    })

    # Scan THUMB folder for images (walk recursively for subfolders like NACIONAL/)
    thumb_folder = find_folder(campaign_path, THUMB_NAMES)
    if thumb_folder:
        for root_dir, _dirs, files_in_dir in os.walk(thumb_folder):
            rel_dir = os.path.relpath(root_dir, thumb_folder)
            subfolder = None if rel_dir == '.' else rel_dir.split(os.sep)[0]
            for file in files_in_dir:
                if file.lower().endswith(IMAGE_EXTS):
                    results.append({
                        'campaign_name': campaign_name_camel,
                        'category': 'thumb',
                        'bucket': 'thumb',
                        'filename': file,
                        'format': '1x1',
                        'state': subfolder,
                        'url': get_supabase_url('thumb', file, slug, subfolder),
                        'file_path': os.path.join(root_dir, file)
                    })

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/campaigns')
def get_campaigns():
    try:
        if not os.path.exists(CAMPAIGNS_DIR):
            return jsonify({'error': f'Directory not found: {CAMPAIGNS_DIR}'}), 404

        campaigns = []
        for item in os.listdir(CAMPAIGNS_DIR):
            item_path = os.path.join(CAMPAIGNS_DIR, item)
            if os.path.isdir(item_path):
                campaigns.append(item)

        return jsonify({'campaigns': sorted(campaigns)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_name>/folders')
def get_campaign_folders(campaign_name):
    try:
        campaign_path = os.path.join(CAMPAIGNS_DIR, campaign_name)

        if not os.path.exists(campaign_path):
            return jsonify({'error': 'Campaign not found'}), 404

        folders = []
        for item in os.listdir(campaign_path):
            item_path = os.path.join(campaign_path, item)
            if os.path.isdir(item_path):
                folders.append(item)

        return jsonify({'folders': sorted(folders)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<campaign_name>/variants')
def get_campaign_variants(campaign_name):
    """Return available variants (nacional + detected regional states)."""
    try:
        campaign_path = os.path.join(CAMPAIGNS_DIR, campaign_name)
        if not os.path.exists(campaign_path):
            return jsonify({'error': 'Campaign not found'}), 404

        states = scan_regional_states(campaign_path, campaign_name)
        # Filter out "nacional" variants from states (case-insensitive) since
        # "nacional" is always included as a fixed option
        states = [s for s in states if s.lower() != 'nacional']
        variants = ['nacional'] + states
        return jsonify({'variants': variants, 'states': states})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-csv', methods=['POST'])
def generate_csv():
    try:
        data = request.get_json()
        campaign_name = data.get('campaign_name')
        # New: selected_variants is a list like ["nacional", "mg", ...]
        # Backward compat: if is_regional is sent, treat as all states selected
        selected_variants = data.get('selected_variants')
        is_regional = data.get('is_regional', False)

        if not campaign_name:
            return jsonify({'error': 'Campaign name is required'}), 400

        campaign_path = os.path.join(CAMPAIGNS_DIR, campaign_name)
        if not os.path.exists(campaign_path):
            return jsonify({'error': f'Campaign folder not found: {campaign_name}'}), 404

        # Determine which variants to generate
        all_states = scan_regional_states(campaign_path, campaign_name)

        if selected_variants is not None:
            # New flow: explicit variant selection
            include_nacional = 'nacional' in selected_variants
            selected_states = [v for v in selected_variants if v != 'nacional' and v in all_states]
            is_regional = include_nacional and len(selected_states) > 0
        elif is_regional:
            # Backward compat: regional=true means nacional + all states
            include_nacional = True
            selected_states = all_states
        else:
            # Backward compat: regional=false means only nacional
            include_nacional = True
            selected_states = []

        all_campaign_files = []

        if selected_states:
            seen_file_paths = set()
            for state in selected_states:
                state_files = scan_campaign_files_for_state(campaign_path, campaign_name, state)
                for f in state_files:
                    fp = f.get('file_path', '')
                    if fp not in seen_file_paths:
                        seen_file_paths.add(fp)
                        all_campaign_files.append(f)
            if include_nacional:
                # Also include nacional files (non-state-specific)
                nacional_files = scan_campaign_files(campaign_path, campaign_name)
                seen_file_paths_set = {f.get('file_path', '') for f in all_campaign_files}
                for f in nacional_files:
                    fp = f.get('file_path', '')
                    if fp and fp not in seen_file_paths_set:
                        seen_file_paths_set.add(fp)
                        all_campaign_files.append(f)
        elif include_nacional:
            # Only nacional, no states
            all_campaign_files = scan_campaign_files(campaign_path, campaign_name)

        if not all_campaign_files:
            return jsonify({'error': 'No media files found in campaign folders'}), 404

        os.makedirs(EXPORT_DIR, exist_ok=True)

        # Group files by category
        files_by_category = {}
        for file_info in all_campaign_files:
            category = file_info['category']
            if category not in files_by_category:
                files_by_category[category] = []
            files_by_category[category].append(file_info)

        # Collect all campaign names for shared files
        all_campaign_names = []
        if selected_states:
            for state in selected_states:
                all_campaign_names.append(to_camel_case(campaign_name, state))

        generated_files = []
        current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

        slug = to_camel_case(campaign_name)

        # Build thumb URL mapping (state -> url) for formCampanhas imagem field
        thumb_urls = {}
        for f in files_by_category.get('thumb', []):
            # Key by state name (e.g. 'NACIONAL', 'MG') or '' for root-level thumbs
            key = f.get('state') or ''
            thumb_urls[key] = f['url']

        for category, files in files_by_category.items():
            if not files:
                continue

            # Skip thumb – no Bubble table; thumbs go into formCampanha.imagem
            if category == 'thumb':
                continue

            bubble_suffix = CATEGORY_TO_FILE_SUFFIX.get(category, category)
            csv_filename = f"export_All-{bubble_suffix}-{slug}.csv"

            csv_path = os.path.join(EXPORT_DIR, csv_filename)

            # Create DataFrame with the expected CSV format
            csv_data = []

            if category == 'abertura':
                # ABERTURA: Each state gets individual rows
                for file_info in files:
                    row = {
                        'ligacaoCampanhaFieldName': file_info['campaign_name'],
                        'locucaoTranscrita': '',
                        'nameFile': file_info['filename'],
                        'OS Formato modelo': file_info['format'],
                        'urlFile': file_info['url'],
                        'Creation Date': current_date
                    }
                    csv_data.append(row)

            elif category in ['bg', 'assinatura', 'trilha']:
                files_processed = set()

                for file_info in files:
                    file_key = (file_info['filename'], file_info['format'])

                    if file_key not in files_processed:
                        files_processed.add(file_key)

                        # TRILHA is shared across all campaigns;
                        # BG and ASSINATURA are state-specific
                        if category == 'trilha' and selected_states and all_campaign_names:
                            campaign_list = ', '.join(all_campaign_names)
                        else:
                            campaign_list = file_info['campaign_name']

                        row = {
                            'ligacaoCampanhaFieldName': campaign_list,
                            'locucaoTranscrita': '',
                            'nameFile': file_info['filename'],
                            'OS Formato modelo': file_info['format'],
                            'urlFile': file_info['url'],
                            'Creation Date': current_date
                        }

                        # Add additional columns based on category
                        if category == 'bg':
                            row['formatoMidia'] = 'Vídeo'
                            row['Modified Date'] = current_date

                        if category == 'assinatura':
                            row['Modified Date'] = current_date

                        if category == 'trilha':
                            row['Modified Date'] = current_date

                        csv_data.append(row)

            if csv_data:
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if csv_data:
                        fieldnames = csv_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(csv_data)
                generated_files.append(csv_filename)

        # Generate campanhas CSV
        campanhas_csv_filename = f"export_All-formCampanhas-{slug}.csv"
        campanhas_csv_path = os.path.join(EXPORT_DIR, campanhas_csv_filename)
        campanhas_data = []

        # Generate campaign entries for each selected variant
        if include_nacional:
            thumb_url = (thumb_urls.get('NACIONAL')
                         or thumb_urls.get('Nacional')
                         or thumb_urls.get('')
                         or next(iter(thumb_urls.values()), ''))
            option_name = campaign_name.replace('_', ' ').title()
            row = {
                'ajusteCampanha': 'acelera',
                'ativo': 'sim',
                'categoriaLiberacao': '',
                'colorLetras': '#d81510',
                'formCelebridade': '',
                'formSelo': '',
                'imagem': thumb_url,
                'option': option_name,
                'optionSheet': slug,
                'OS materiais': 'Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s',
                'OS type midia': 'Tv , Rádio'
            }
            campanhas_data.append(row)

        for i, state in enumerate(selected_states):
            state_display = state.replace('_', ' ').title()
            option_name = f"{campaign_name.title()} {state_display}"
            campaign_name_camel = to_camel_case(campaign_name, state)
            row = {
                'ajusteCampanha': 'acelera',
                'ativo': 'sim',
                'categoriaLiberacao': '',
                'colorLetras': '#d81510',
                'formCelebridade': '',
                'formSelo': '',
                'imagem': thumb_urls.get(state, ''),
                'option': option_name,
                'optionSheet': campaign_name_camel,
                'OS materiais': 'Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s',
                'OS type midia': 'Tv , Rádio'
            }
            campanhas_data.append(row)

        if campanhas_data:
            with open(campanhas_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = campanhas_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(campanhas_data)
            generated_files.append(campanhas_csv_filename)

        generated_variants = []
        if include_nacional:
            generated_variants.append('nacional')
        generated_variants.extend(selected_states)

        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_files)} CSV files with {len(all_campaign_files)} media files',
            'files': generated_files,
            'campaign_camel': to_camel_case(campaign_name),
            'is_regional': bool(selected_states),
            'states': selected_states,
            'selected_variants': generated_variants,
            'total_files': len(all_campaign_files)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def scan_feirassai_campaigns():
    """Scan the FEIRASSAI Google Drive folder and extract all campaigns"""
    results = {
        'abertura': [],
        'assinatura': [],
        'bg': [],
        'trilha': []
    }

    try:
        base_path = CAMPAIGNS_DIR
        print(f"Scanning base path: {base_path}")

        # Check if base path exists
        if not os.path.exists(base_path):
            print(f"Base path does not exist: {base_path}")
            return results

        # List all folders in base path
        print(f"Folders in base path: {os.listdir(base_path)}")

        # CABECA scanning
        cabeca_path = os.path.join(base_path, 'CABECA')
        if os.path.exists(cabeca_path):
            print(f"Scanning CABECA folder: {cabeca_path}")
            for periodo in os.listdir(cabeca_path):
                periodo_path = os.path.join(cabeca_path, periodo)
                if not os.path.isdir(periodo_path):
                    continue

                print(f"  Processing period: {periodo}")
                for regiao in os.listdir(periodo_path):
                    regiao_path = os.path.join(periodo_path, regiao)
                    if not os.path.isdir(regiao_path):
                        continue

                    print(f"    Processing region: {regiao}")
                    for file in os.listdir(regiao_path):
                        if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                            file_format = extract_format_from_filename(file)
                            campaign_name = extract_campaign_name_from_filename(file)
                            print(f"      Found file: {file} (format: {file_format}, campaign: {campaign_name})")

                            results['abertura'].append({
                                'ligacaoCampanhaFieldName': campaign_name,
                                'locucaoTranscrita': '',
                                'nameFile': file,
                                'OS Formato modelo': file_format,
                                'urlFile': get_supabase_url('cabeca', file, 'feirassai', f"{periodo}/{regiao}"),
                                'Creation Date': datetime.now().strftime("%b %d, %Y %I:%M %p"),
                                'periodo': periodo,
                                'regiao': regiao
                            })

        # ASSINATURA scanning
        assinatura_path = os.path.join(base_path, 'ASSINATURA')
        if os.path.exists(assinatura_path):
            print(f"Scanning ASSINATURA folder: {assinatura_path}")
            for periodo in os.listdir(assinatura_path):
                periodo_path = os.path.join(assinatura_path, periodo)
                if not os.path.isdir(periodo_path):
                    continue

                print(f"  Processing period: {periodo}")
                for regiao in os.listdir(periodo_path):
                    regiao_path = os.path.join(periodo_path, regiao)
                    if not os.path.isdir(regiao_path):
                        continue

                    print(f"    Processing region: {regiao}")
                    for file in os.listdir(regiao_path):
                        if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                            file_format = extract_format_from_filename(file)
                            campaign_name = extract_campaign_name_from_filename(file)
                            print(f"      Found file: {file} (format: {file_format}, campaign: {campaign_name})")

                            results['assinatura'].append({
                                'ligacaoCampanhaFieldName': campaign_name,
                                'locucaoTranscrita': '',
                                'nameFile': file,
                                'OS Formato modelo': file_format,
                                'urlFile': get_supabase_url('assinatura', file, 'feirassai', f"{periodo}/{regiao}"),
                                'Creation Date': datetime.now().strftime("%b %d, %Y %I:%M %p"),
                                'periodo': periodo,
                                'regiao': regiao
                            })

        # BG scanning (if exists)
        bg_path = os.path.join(base_path, 'BG')
        if os.path.exists(bg_path):
            print(f"Scanning BG folder: {bg_path}")
            for item in os.listdir(bg_path):
                item_path = os.path.join(bg_path, item)
                if os.path.isfile(item_path) and item.lower().endswith(('.mp4', '.mp3', '.wav')):
                    file_format = extract_format_from_filename(item)
                    print(f"  Found BG file: {item} (format: {file_format})")

                    results['bg'].append({
                        'ligacaoCampanhaFieldName': 'feirassai',
                        'locucaoTranscrita': '',
                        'nameFile': item,
                        'OS Formato modelo': file_format,
                        'urlFile': get_supabase_url('bg', item, 'feirassai'),
                        'Creation Date': datetime.now().strftime("%b %d, %Y %I:%M %p"),
                        'formatoMidia': 'Vídeo',
                        'Modified Date': datetime.now().strftime("%b %d, %Y %I:%M %p")
                    })

        # TRILHA scanning (if exists)
        trilha_path = os.path.join(base_path, 'TRILHA')
        if os.path.exists(trilha_path):
            print(f"Scanning TRILHA folder: {trilha_path}")
            for item in os.listdir(trilha_path):
                item_path = os.path.join(trilha_path, item)
                if os.path.isfile(item_path) and item.lower().endswith(('.mp4', '.mp3', '.wav')):
                    file_format = extract_format_from_filename(item)
                    print(f"  Found TRILHA file: {item} (format: {file_format})")

                    results['trilha'].append({
                        'ligacaoCampanhaFieldName': 'feirassai',
                        'locucaoTranscrita': '',
                        'nameFile': item,
                        'OS Formato modelo': file_format,
                        'urlFile': get_supabase_url('trilha', item, 'feirassai'),
                        'Creation Date': datetime.now().strftime("%b %d, %Y %I:%M %p"),
                        'Modified Date': datetime.now().strftime("%b %d, %Y %I:%M %p")
                    })

        print(f"Scan complete. Results: {[(k, len(v)) for k, v in results.items()]}")

    except Exception as e:
        print(f"Error scanning FEIRASSAI campaigns: {e}")
        import traceback
        traceback.print_exc()

    return results

@app.route('/api/generate-feirassai-json', methods=['POST'])
def generate_feirassai_json():
    """Generate complete JSON files for FEIRASSAI campaigns"""
    try:
        # Scan all FEIRASSAI campaigns
        campaigns_data = scan_feirassai_campaigns()

        os.makedirs(EXPORT_DIR, exist_ok=True)

        generated_files = []
        total_files = 0

        # Generate JSON for each category
        for category, files in campaigns_data.items():
            if files:
                json_filename = f"feirassai_{category}.json"
                json_path = os.path.join(EXPORT_DIR, json_filename)

                with open(json_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(files, jsonfile, ensure_ascii=False, indent=2)

                generated_files.append(json_filename)
                total_files += len(files)

        # Generate complete consolidated JSON
        complete_json_filename = "feirassai_complete.json"
        complete_json_path = os.path.join(EXPORT_DIR, complete_json_filename)

        with open(complete_json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(campaigns_data, jsonfile, ensure_ascii=False, indent=2)

        generated_files.append(complete_json_filename)

        # Generate form_campanha CSV
        form_campanha_filename = "feirassai_form_campanha.csv"
        form_campanha_path = os.path.join(EXPORT_DIR, form_campanha_filename)

        # Collect unique campaign names
        unique_campaigns = set()
        for category_files in campaigns_data.values():
            for file_info in category_files:
                unique_campaigns.add(file_info['ligacaoCampanhaFieldName'])

        form_campanha_data = []
        for campaign_name in sorted(unique_campaigns):
            # Create readable option name from campaign name
            # aniversarioFeirassaiTercaeQuarta -> Aniversario Feirassai Terca e Quarta
            option_display = campaign_name.replace('aniversario', 'Aniversario ')
            option_display = option_display.replace('Feirassai', 'Feirassai ')

            # Fix specific patterns
            option_display = option_display.replace('TercaeQuarta', 'Terca e Quarta')
            option_display = option_display.replace('QuartaeQuinta', 'Quarta e Quinta')
            option_display = option_display.replace('SextaeSabado', 'Sexta e Sabado')
            option_display = option_display.replace('Mg', ' MG')

            # Clean multiple spaces
            option_display = ' '.join(option_display.split())

            form_campanha_data.append({
                'ajusteCampanha': 'acelera',
                'ativo': 'sim',
                'categoriaLiberacao': '',
                'colorLetras': '#d81510',
                'formCelebridade': '',
                'formSelo': '',
                'imagem': '',
                'option': option_display,
                'optionSheet': campaign_name,
                'OS materiais': 'Video 1x1 , Video 9x16 , Video 16x9',
                'OS type midia': 'Social Media , Stories , TV'
            })

        with open(form_campanha_path, 'w', newline='', encoding='utf-8') as csvfile:
            if form_campanha_data:
                fieldnames = form_campanha_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(form_campanha_data)

        generated_files.append(form_campanha_filename)

        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_files)} JSON files with {total_files} media files',
            'files': generated_files,
            'total_files': total_files,
            'categories': {category: len(files) for category, files in campaigns_data.items()}
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Supabase upload routes ───────────────────────────────────────────

@app.route('/api/supabase-config-status')
def supabase_config_status():
    token = os.environ.get('SUPABASE_SERVICE_ROLE', '')
    return jsonify({
        'configured': bool(token),
        'project_url': SUPABASE_PROJECT_URL,
        'bucket': SUPABASE_BUCKET,
    })


@app.route('/api/upload-supabase', methods=['POST'])
def upload_supabase():
    token = os.environ.get('SUPABASE_SERVICE_ROLE', '')
    if not token:
        return jsonify({'error': 'SUPABASE_SERVICE_ROLE nao configurado no servidor.'}), 400

    data = request.get_json()
    campaign_name = data.get('campaign_name')
    selected_variants = data.get('selected_variants')
    is_regional = data.get('is_regional', False)

    if not campaign_name:
        return jsonify({'error': 'campaign_name obrigatorio.'}), 400

    campaign_path = os.path.join(CAMPAIGNS_DIR, campaign_name)
    if not os.path.exists(campaign_path):
        return jsonify({'error': f'Pasta nao encontrada: {campaign_name}'}), 404

    slug = to_camel_case(campaign_name)

    # Determine which variants to upload
    all_states = scan_regional_states(campaign_path, campaign_name)

    if selected_variants is not None:
        include_nacional = 'nacional' in selected_variants
        selected_states = [v for v in selected_variants if v != 'nacional' and v in all_states]
    elif is_regional:
        include_nacional = True
        selected_states = all_states
    else:
        include_nacional = True
        selected_states = []

    # Collect all files to upload
    all_files = []
    if selected_states:
        for state in selected_states:
            state_files = scan_campaign_files_for_state(campaign_path, campaign_name, state)
            all_files.extend(state_files)
        if include_nacional:
            nacional_files = scan_campaign_files(campaign_path, campaign_name)
            existing_paths = {f.get('file_path', '') for f in all_files}
            for f in nacional_files:
                fp = f.get('file_path', '')
                if fp and fp not in existing_paths:
                    existing_paths.add(fp)
                    all_files.append(f)
    elif include_nacional:
        all_files = scan_campaign_files(campaign_path, campaign_name)

    # Deduplicate by file_path (e.g. shared TRILHA)
    seen_paths = set()
    upload_list = []
    for f in all_files:
        fp = f.get('file_path', '')
        if fp and fp not in seen_paths:
            seen_paths.add(fp)
            upload_list.append(f)

    task_id = str(uuid.uuid4())
    task_state = {
        'status': 'running',
        'total': len(upload_list),
        'uploaded': 0,
        'failed': 0,
        'current_file': None,
        'errors': [],
    }
    with _upload_tasks_lock:
        _upload_tasks[task_id] = task_state

    def _run():
        for file_info in upload_list:
            task_state['current_file'] = file_info['filename']
            # Determine state subfolder (None for trilha only)
            cat = file_info.get('category', '')
            state = file_info.get('state') if cat not in ('trilha',) else None
            object_path = build_supabase_object_path(
                slug, file_info['bucket'], file_info['filename'], state
            )
            try:
                _supabase_upload_file(file_info['file_path'], object_path, token)
                task_state['uploaded'] += 1
            except Exception as e:
                task_state['failed'] += 1
                if len(task_state['errors']) < 20:
                    task_state['errors'].append(f"{file_info['filename']}: {e}")
        task_state['current_file'] = None
        task_state['status'] = 'completed'

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return jsonify({'task_id': task_id})


@app.route('/api/task-status/<task_id>')
def task_status(task_id):
    with _upload_tasks_lock:
        task = _upload_tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task nao encontrada.'}), 404
    return jsonify(task)


# ── Bubble upload routes ─────────────────────────────────────────────

def _infer_table_from_filename(filename: str):
    """Extract the Bubble table name from an export_All-{suffix}-*.csv filename."""
    suffix_to_table = {v: k for k, v in CATEGORY_TO_FILE_SUFFIX.items()}
    # filename like export_All-mCabecas-carnaval2026.csv
    parts = filename.replace(".csv", "").split("-", 2)
    if len(parts) >= 2:
        suffix = parts[1]
        category = suffix_to_table.get(suffix)
        if category:
            return CATEGORY_TO_TABLE.get(category)
    return None


@app.route('/api/bubble-config-status')
def bubble_config_status():
    token = os.environ.get('BUBBLE_API_TOKEN', '')
    return jsonify({
        'configured': bool(token),
        'base_url': DEFAULT_BASE_URL,
    })


@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.get_json()
    role = data.get('role', '')
    password = data.get('password', '')

    if role == 'user':
        user_password = os.environ.get('USER_PASSWORD', '')
        if not user_password:
            return jsonify({'authorized': False, 'message': 'USER_PASSWORD nao configurado no servidor.'})
        if password == user_password:
            return jsonify({'authorized': True, 'role': 'user'})
        return jsonify({'authorized': False, 'message': 'Senha incorreta.'})

    elif role == 'admin':
        admin_password = os.environ.get('ADMIN_PASSWORD', '')
        if not admin_password:
            return jsonify({'authorized': False, 'message': 'ADMIN_PASSWORD nao configurado no servidor.'})
        if password == admin_password:
            return jsonify({'authorized': True, 'role': 'admin'})
        return jsonify({'authorized': False, 'message': 'Senha incorreta.'})

    return jsonify({'authorized': False, 'message': 'Role invalido.'})


@app.route('/api/upload-bubble', methods=['POST'])
def upload_bubble():
    token = os.environ.get('BUBBLE_API_TOKEN', '')
    if not token:
        return jsonify({'error': 'BUBBLE_API_TOKEN nao configurado no servidor.'}), 400

    data = request.get_json()
    files = data.get('files', [])
    env = data.get('env', 'test')  # "test" or "prod"

    # Proteger upload PROD com senha admin
    if env == 'prod':
        admin_password = os.environ.get('ADMIN_PASSWORD', '')
        provided_password = request.headers.get('X-Admin-Password', '')
        if not admin_password or provided_password != admin_password:
            return jsonify({'error': 'Acesso negado. Senha de admin invalida ou nao configurada para upload PROD.'}), 403
    if not files:
        return jsonify({'error': 'Nenhum arquivo informado.'}), 400

    # Build base URL based on environment
    if env == 'prod':
        base_url = DEFAULT_BASE_URL.replace('/version-test/', '/')
    else:
        base_url = DEFAULT_BASE_URL

    # Validate all files exist and have a known table
    file_table_pairs = []
    for fname in files:
        table = _infer_table_from_filename(fname)
        if not table:
            return jsonify({'error': f'Tabela nao identificada para {fname}'}), 400
        fpath = os.path.join(EXPORT_DIR, fname)
        if not os.path.isfile(fpath):
            return jsonify({'error': f'Arquivo nao encontrado: {fname}'}), 404
        file_table_pairs.append((fname, fpath, table))

    task_id = str(uuid.uuid4())
    task_state = {
        'status': 'running',
        'total_files': len(file_table_pairs),
        'completed_files': 0,
        'current_file': None,
        'results': {},
        'env': env,
    }
    with _upload_tasks_lock:
        _upload_tasks[task_id] = task_state

    def _run_upload():
        for fname, fpath, table in file_table_pairs:
            task_state['current_file'] = fname
            # Per-row progress stored under each file key
            task_state['results'][fname] = {
                'status': 'uploading',
                'current': 0,
                'total': 0,
            }

            def _progress(current, total, error_msg, _fname=fname):
                task_state['results'][_fname]['current'] = current
                task_state['results'][_fname]['total'] = total

            result = upload_csv_to_bubble(
                csv_path=fpath,
                table=table,
                base_url=base_url,
                token=token,
                delay=0.2,
                progress_callback=_progress,
            )
            task_state['results'][fname] = {
                'status': 'done',
                'total': result['total'],
                'success': result['success'],
                'failed': result['failed'],
                'errors': result['errors'],
            }
            task_state['completed_files'] += 1

        task_state['current_file'] = None
        task_state['status'] = 'completed'

    thread = threading.Thread(target=_run_upload, daemon=True)
    thread.start()

    return jsonify({'task_id': task_id})


@app.route('/api/upload-bubble/status/<task_id>')
def upload_bubble_status(task_id):
    with _upload_tasks_lock:
        task = _upload_tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task nao encontrada.'}), 404
    return jsonify(task)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)