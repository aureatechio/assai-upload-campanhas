import os
import pandas as pd
import re
from datetime import datetime

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

def test_regional_concatenation():
    print("Testando concatenacao de campanhas regionais...")
    print()

    # Simular arquivos de multiplos estados
    regional_files = [
        # ALAGOAS
        {'name': 'cabAniversarioRegionaisAlagoas16x9.mp4', 'state': 'ALAGOAS', 'category': 'abertura', 'format': '16x9'},
        {'name': 'cabAniversarioRegionaisAlagoas9x16.mp4', 'state': 'ALAGOAS', 'category': 'abertura', 'format': '9x16'},
        {'name': 'cabAniversarioRegionaisAlagoas1x1.mp4', 'state': 'ALAGOAS', 'category': 'abertura', 'format': '1x1'},
        {'name': 'bgAniversarioRegionaisAlagoas16x9.mp4', 'state': 'ALAGOAS', 'category': 'bg', 'format': '16x9'},

        # BAHIA
        {'name': 'cabAniversarioRegionaisBahia16x9.mp4', 'state': 'BAHIA', 'category': 'abertura', 'format': '16x9'},
        {'name': 'cabAniversarioRegionaisBahia9x16.mp4', 'state': 'BAHIA', 'category': 'abertura', 'format': '9x16'},
        {'name': 'bgAniversarioRegionaisBahia16x9.mp4', 'state': 'BAHIA', 'category': 'bg', 'format': '16x9'},

        # CEARA
        {'name': 'cabAniversarioRegionaisCeara16x9.mp4', 'state': 'CEARA', 'category': 'abertura', 'format': '16x9'},
        {'name': 'trilhaAniversarioRegionaisCeara.mp3', 'state': 'CEARA', 'category': 'trilha', 'format': '16x9'},
    ]

    campaign_name = "ANIVERSARIO REGIONAIS"
    states = ['ALAGOAS', 'BAHIA', 'CEARA']

    print(f"Campanha: {campaign_name}")
    print(f"Estados encontrados: {', '.join(states)}")
    print()

    # Agrupar por categoria
    files_by_category = {}
    for file_info in regional_files:
        category = file_info['category']
        if category not in files_by_category:
            files_by_category[category] = []

        # Create campaign name with state
        campaign_with_state = to_camel_case(campaign_name, file_info['state'].lower())

        file_info['campaign_name'] = campaign_with_state
        file_info['url'] = get_firebase_url('cabeca' if category == 'abertura' else category, file_info['name'])
        files_by_category[category].append(file_info)

    export_dir = "../exportados"
    os.makedirs(export_dir, exist_ok=True)

    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    print("=== CSVs Gerados (Concatenados) ===")

    for category, files in files_by_category.items():
        print(f"--- Categoria: {category.upper()} ---")

        csv_filename = f"{to_camel_case(campaign_name)}_{category}.csv"
        csv_path = os.path.join(export_dir, csv_filename)

        csv_data = []
        for file_info in files:
            row = {
                'ligacaoCampanhaFieldName': file_info['campaign_name'],
                'locucaoTranscrita': '',
                'nameFile': file_info['name'],
                'OS Formato modelo': file_info['format'],
                'urlFile': file_info['url'],
                'Creation Date': current_date
            }

            # Add additional columns based on category
            if category == 'bg':
                row['formatoMidia'] = 'Vídeo'
                row['Modified Date'] = current_date

            if category == 'trilha':
                row['Modified Date'] = current_date
                row['Slug'] = ''
                row['Creator'] = '(App admin)'

            csv_data.append(row)

        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_path, index=False, encoding='utf-8')

            print(f"   Arquivo CSV: {csv_filename}")
            print(f"   Linhas: {len(csv_data)}")
            print(f"   Estados incluidos:")

            for file_info in files:
                print(f"     - {file_info['state']}: {file_info['campaign_name']} ({file_info['format']})")
            print()

    print("Teste de concatenacao concluido!")
    print()
    print("Exemplo de como ficara o CSV:")
    print("ligacaoCampanhaFieldName,nameFile,OS Formato modelo,urlFile")
    print("aniversarioRegionaisAlagoas,cabAniversarioRegionaisAlagoas16x9.mp4,16x9,https://...")
    print("aniversarioRegionaisBahia,cabAniversarioRegionaisBahia16x9.mp4,16x9,https://...")
    print("aniversarioRegionaisCeara,cabAniversarioRegionaisCeara16x9.mp4,16x9,https://...")

if __name__ == "__main__":
    test_regional_concatenation()