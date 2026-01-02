from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import csv
import json
import re
from pathlib import Path
from datetime import datetime

app = Flask(__name__, template_folder='../frontend')
CORS(app)

CAMPAIGNS_DIR = r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\ANIVERSARIO FEIRASSAI"
EXPORT_DIR = "../exportados"

BUCKETS = {
    'abertura': 'cabeca',
    'bg': 'bg',
    'assinatura': 'assinatura',
    'trilha': 'trilha'
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

def get_firebase_url(bucket_name, filename):
    base_url = "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/"
    encoded_filename = filename.replace(' ', '%20')
    url = f"{base_url}{bucket_name}%2F{encoded_filename}?alt=media&token=7d2e4acc-15fa-46f0-9d3d-7b026db1f96b"
    return url

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

def scan_regional_states(campaign_path, campaign_name):
    """Scan regional campaign and return list of states found"""
    states = []
    cabecas_path = os.path.join(campaign_path, 'CABECAS')

    if os.path.exists(cabecas_path):
        for item in os.listdir(cabecas_path):
            item_path = os.path.join(cabecas_path, item)
            if os.path.isdir(item_path):
                states.append(item)

    return states

def scan_campaign_files_for_state(campaign_path, campaign_name, state):
    """Scan campaign folders for a specific state and extract files with formats"""
    campaign_name_camel = to_camel_case(campaign_name, state)
    results = []

    bucket_folders = {
        'CABECAS': 'cabeca',
        'BG': 'bg',
        'ASSINATURAS': 'assinatura',
        'TRILHA': 'trilha'
    }

    for folder_name, bucket_name in bucket_folders.items():
        base_folder_path = os.path.join(campaign_path, folder_name)

        if not os.path.exists(base_folder_path):
            continue

        # For regional campaigns, look inside state folder
        state_folder_path = os.path.join(base_folder_path, state)

        # Special handling for different folder structures
        if folder_name == 'CABECAS':
            # CABECAS has state-specific subfolders
            if os.path.exists(state_folder_path):
                folder_path = state_folder_path

                if os.path.exists(folder_path):
                    files_in_folder = os.listdir(folder_path)

                    for file in files_in_folder:
                        if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                            file_format = extract_format_from_filename(file)

                            results.append({
                                'campaign_name': campaign_name_camel,
                                'category': 'abertura',
                                'bucket': bucket_name,
                                'filename': file,
                                'format': file_format,
                                'url': get_firebase_url(bucket_name, file),
                                'state': state
                            })

        elif folder_name == 'TRILHA':
            # TRILHA has files directly in main folder
            folder_path = base_folder_path

            if os.path.exists(folder_path):
                files_in_folder = os.listdir(folder_path)

                for file in files_in_folder:
                    if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                        file_format = extract_format_from_filename(file)

                        results.append({
                            'campaign_name': campaign_name_camel,
                            'category': 'trilha',
                            'bucket': bucket_name,
                            'filename': file,
                            'format': file_format,
                            'url': get_firebase_url(bucket_name, file),
                            'state': state
                        })

        elif folder_name == 'BG':
            # BG has MG and NACIONAL subfolders - use both for all states
            for subfolder in ['MG', 'NACIONAL']:
                subfolder_path = os.path.join(base_folder_path, subfolder)

                if os.path.exists(subfolder_path):
                    files_in_folder = os.listdir(subfolder_path)

                    for file in files_in_folder:
                        if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                            file_format = extract_format_from_filename(file)

                            results.append({
                                'campaign_name': campaign_name_camel,
                                'category': 'bg',
                                'bucket': bucket_name,
                                'filename': file,
                                'format': file_format,
                                'url': get_firebase_url(bucket_name, file),
                                'state': state
                            })

        elif folder_name == 'ASSINATURAS':
            # ASSINATURAS has MG and NACIONAL subfolders - use both for all states
            for subfolder in ['MG', 'NACIONAL']:
                subfolder_path = os.path.join(base_folder_path, subfolder)

                if os.path.exists(subfolder_path):
                    files_in_folder = os.listdir(subfolder_path)

                    for file in files_in_folder:
                        if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                            file_format = extract_format_from_filename(file)

                            results.append({
                                'campaign_name': campaign_name_camel,
                                'category': 'assinatura',
                                'bucket': bucket_name,
                                'filename': file,
                                'format': file_format,
                                'url': get_firebase_url(bucket_name, file),
                                'state': state
                            })

    return results

def scan_campaign_files(campaign_path, campaign_name, state=None):
    """Scan campaign folders and extract files with formats"""
    if state:
        return scan_campaign_files_for_state(campaign_path, campaign_name, state)

    campaign_name_camel = to_camel_case(campaign_name)
    results = []

    bucket_folders = {
        'CABECAS': 'cabeca',
        'BG': 'bg',
        'ASSINATURAS': 'assinatura',
        'TRILHA': 'trilha'
    }

    for folder_name, bucket_name in bucket_folders.items():
        folder_path = os.path.join(campaign_path, folder_name)

        if not os.path.exists(folder_path):
            continue

        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.lower().endswith(('.mp4', '.mp3', '.wav')):
                    file_format = extract_format_from_filename(file)

                    results.append({
                        'campaign_name': campaign_name_camel,
                        'category': folder_name.lower().replace('cabecas', 'abertura'),
                        'bucket': bucket_name,
                        'filename': file,
                        'format': file_format,
                        'url': get_firebase_url(bucket_name, file)
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

@app.route('/api/generate-csv', methods=['POST'])
def generate_csv():
    try:
        data = request.get_json()
        campaign_name = data.get('campaign_name')
        is_regional = data.get('is_regional', False)

        if not campaign_name:
            return jsonify({'error': 'Campaign name is required'}), 400

        campaign_path = os.path.join(CAMPAIGNS_DIR, campaign_name)
        if not os.path.exists(campaign_path):
            return jsonify({'error': f'Campaign folder not found: {campaign_name}'}), 404

        all_campaign_files = []

        if is_regional:
            # For regional campaigns, scan all states and concatenate
            states = scan_regional_states(campaign_path, campaign_name)
            if not states:
                return jsonify({'error': 'No regional states found in campaign'}), 404

            for state in states:
                state_files = scan_campaign_files_for_state(campaign_path, campaign_name, state)
                all_campaign_files.extend(state_files)
        else:
            # For regular campaigns, scan normally
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
        if is_regional:
            states = scan_regional_states(campaign_path, campaign_name)
            for state in states:
                all_campaign_names.append(to_camel_case(campaign_name, state))

        generated_files = []
        current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

        for category, files in files_by_category.items():
            if not files:
                continue

            # For regional campaigns, use base campaign name + category
            if is_regional:
                csv_filename = f"{to_camel_case(campaign_name)}_{category}.csv"
            else:
                csv_filename = f"{to_camel_case(campaign_name)}_{category}.csv"

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
                # BG, ASSINATURA, TRILHA: Group by unique files, list all campaigns
                files_processed = set()

                for file_info in files:
                    file_key = (file_info['filename'], file_info['format'])

                    if file_key not in files_processed:
                        files_processed.add(file_key)

                        # Create comma-separated list of all campaign names
                        campaign_list = ', '.join(all_campaign_names) if is_regional else file_info['campaign_name']

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
                            row['Slug'] = ''
                            row['Creator'] = '(App admin)'

                        csv_data.append(row)

            if csv_data:
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if csv_data:
                        fieldnames = csv_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(csv_data)
                generated_files.append(csv_filename)

        # Generate campanhas CSV for regional campaigns
        if is_regional and all_campaign_names:
            campanhas_csv_filename = f"{to_camel_case(campaign_name)}_campanhas.csv"
            campanhas_csv_path = os.path.join(EXPORT_DIR, campanhas_csv_filename)

            campanhas_data = []
            states = scan_regional_states(campaign_path, campaign_name)

            for i, campaign_name_camel in enumerate(all_campaign_names):
                # Extract state name for display
                state_name = states[i] if i < len(states) else ""
                state_display = state_name.replace('_', ' ').title()

                # Create readable option name
                option_name = f"{campaign_name.title()} {state_display}"

                row = {
                    'ajusteCampanha': 'acelera',
                    'ativo': 'sim',
                    'categoriaLiberacao': '',
                    'colorLetras': '#d81510',
                    'formCelebridade': '',
                    'formSelo': '',
                    'imagem': '',
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

        states_info = scan_regional_states(campaign_path, campaign_name) if is_regional else []

        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_files)} CSV files with {len(all_campaign_files)} media files',
            'files': generated_files,
            'campaign_camel': to_camel_case(campaign_name),
            'is_regional': is_regional,
            'states': states_info,
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
                                'urlFile': get_firebase_url('cabeca', file),
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
                                'urlFile': get_firebase_url('assinatura', file),
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
                        'urlFile': get_firebase_url('bg', item),
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
                        'urlFile': get_firebase_url('trilha', item),
                        'Creation Date': datetime.now().strftime("%b %d, %Y %I:%M %p"),
                        'Modified Date': datetime.now().strftime("%b %d, %Y %I:%M %p"),
                        'Slug': '',
                        'Creator': '(App admin)'
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)