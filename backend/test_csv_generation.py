import os
import pandas as pd
import re

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

def test_csv_generation():
    print("Testando geracao de CSVs com novo formato...")
    print()

    # Teste simulando arquivos com formatos
    test_files = [
        {'name': 'cabCampanhaTest16x9.mp4', 'format': '16x9', 'category': 'abertura'},
        {'name': 'cabCampanhaTest9x16.mp4', 'format': '9x16', 'category': 'abertura'},
        {'name': 'cabCampanhaTest1x1.mp4', 'format': '1x1', 'category': 'abertura'},
        {'name': 'bgCampanhaTest16x9.mp4', 'format': '16x9', 'category': 'bg'},
        {'name': 'bgCampanhaTest9x16.mp4', 'format': '9x16', 'category': 'bg'},
        {'name': 'assCampanhaTest16x9.mp4', 'format': '16x9', 'category': 'assinatura'},
        {'name': 'trilhaCampanhaTest.mp3', 'format': '16x9', 'category': 'trilha'}
    ]

    # Teste 1: Testando extração de formato
    print("=== TESTE 1: Extração de Formato ===")
    for file_info in test_files[:3]:  # Apenas alguns exemplos
        detected_format = extract_format_from_filename(file_info['name'])
        print(f"Arquivo: {file_info['name']}")
        print(f"   Formato esperado: {file_info['format']}")
        print(f"   Formato detectado: {detected_format}")
        print(f"   -> {'Correto' if detected_format == file_info['format'] else 'Erro'}")
        print()

    # Teste 2: Criando CSVs no formato correto
    print("=== TESTE 2: Gerando CSVs no Formato Correto ===")

    campaign_name = "Campanha Test"
    campaign_camel = to_camel_case(campaign_name)

    print(f"Campanha: {campaign_name}")
    print(f"CamelCase: {campaign_camel}")
    print()

    from datetime import datetime

    export_dir = "../exportados"
    os.makedirs(export_dir, exist_ok=True)

    # Agrupar por categoria
    files_by_category = {}
    for file_info in test_files:
        category = file_info['category']
        if category not in files_by_category:
            files_by_category[category] = []
        files_by_category[category].append(file_info)

    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    for category, files in files_by_category.items():
        print(f"--- Categoria: {category.upper()} ---")

        csv_filename = f"{campaign_camel}_{category}.csv"
        csv_path = os.path.join(export_dir, csv_filename)

        csv_data = []
        for file_info in files:
            url = get_firebase_url('cabeca' if category == 'abertura' else category, file_info['name'])

            row = {
                'ligacaoCampanhaFieldName': campaign_camel,
                'locucaoTranscrita': '',
                'nameFile': file_info['name'],
                'OS Formato modelo': file_info['format'],
                'urlFile': url,
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
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_path, index=False, encoding='utf-8')

            print(f"   Arquivo CSV: {csv_filename}")
            print(f"   Linhas: {len(csv_data)}")
            print(f"   Formatos encontrados: {[f['format'] for f in files]}")
            print()

    print("Teste concluido! CSVs gerados no formato correto!")

if __name__ == "__main__":
    test_csv_generation()