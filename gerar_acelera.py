import os
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurações
CAMPAIGN_BASE_PATH = os.getenv('CAMPAIGNS_DIR', r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\ANIVERSARIO ACELERA")
EXPORT_DIR = os.getenv('EXPORT_DIR', "exportados")
BASE_FIREBASE_URL = os.getenv('FIREBASE_BASE_URL', "https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/")
TOKEN = os.getenv('FIREBASE_TOKEN', "7d2e4acc-15fa-46f0-9d3d-7b026db1f96b")

def get_firebase_url(bucket_name, filename):
    """Gera URL do Firebase Storage"""
    encoded_filename = filename.replace(' ', '%20')
    url = f"{BASE_FIREBASE_URL}{bucket_name}%2F{encoded_filename}?alt=media&token={TOKEN}"
    return url

def extract_format_from_filename(filename):
    """Extrai formato do nome do arquivo (16x9, 9x16, 1x1)"""
    if '16x9' in filename.lower():
        return '16x9'
    elif '9x16' in filename.lower():
        return '9x16'
    elif '1x1' in filename.lower():
        return '1x1'
    return '16x9'

def scan_folder_files(folder_path):
    """Escaneia pasta e retorna lista de arquivos de mídia"""
    files = []
    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            if item.lower().endswith(('.mp4', '.mp3', '.wav')):
                files.append(item)
    return files

def generate_cabecas_csv():
    """Gera CSV de cabeças com 4 campanhas diferentes"""
    print("Gerando CSV de cabeças...")

    csv_data = []
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p").lower()

    # Estrutura: CABEÇAS/[E AMANHA ou TA ROLANDO]/[MG ou NACIONAL]/arquivos
    periodos = ['E AMANHA', 'TA ROLANDO']
    regioes = ['MG', 'NACIONAL']

    for periodo in periodos:
        for regiao in regioes:
            folder_path = os.path.join(CAMPAIGN_BASE_PATH, 'CABEÇAS', periodo, regiao)

            if not os.path.exists(folder_path):
                print(f"  Pasta não encontrada: {folder_path}")
                continue

            files = scan_folder_files(folder_path)
            print(f"  {periodo} - {regiao}: {len(files)} arquivos")

            # Define nome da campanha
            periodo_camel = 'Amanha' if 'AMANHA' in periodo else 'TaRolando'
            regiao_suffix = 'Mg' if regiao == 'MG' else ''
            campaign_name = f"aniversarioAcelera{periodo_camel}{regiao_suffix}"

            for file in files:
                file_format = extract_format_from_filename(file)

                row = {
                    'ligacaoCampanhaFieldName': campaign_name,
                    'locucaoTranscrita': '',
                    'nameFile': file,
                    'OS Formato modelo': file_format,
                    'urlFile': get_firebase_url('cabeca', file),
                    'Creation Date': current_date
                }
                csv_data.append(row)

    # Salvar CSV
    os.makedirs(EXPORT_DIR, exist_ok=True)
    csv_path = os.path.join(EXPORT_DIR, 'export_All-mCabecas-acelera.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ligacaoCampanhaFieldName', 'locucaoTranscrita', 'nameFile', 'OS Formato modelo', 'urlFile', 'Creation Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"OK - Gerado: export_All-mCabecas-acelera.csv ({len(csv_data)} arquivos)")
    return len(csv_data)

def generate_bg_csv():
    """Gera CSV de backgrounds"""
    print("\nGerando CSV de backgrounds...")

    csv_data = []
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p").lower()

    # BG tem pastas MG e NACIONAL
    regioes = ['MG', 'NACIONAL']
    all_files = set()

    for regiao in regioes:
        folder_path = os.path.join(CAMPAIGN_BASE_PATH, 'BG', regiao)

        if not os.path.exists(folder_path):
            print(f"  Pasta não encontrada: {folder_path}")
            continue

        files = scan_folder_files(folder_path)
        print(f"  BG - {regiao}: {len(files)} arquivos")

        for file in files:
            if file not in all_files:
                all_files.add(file)
                file_format = extract_format_from_filename(file)

                row = {
                    'ligacaoCampanhaFieldName': 'bgAniversarioAcelera',
                    'locucaoTranscrita': '',
                    'nameFile': file,
                    'OS Formato modelo': file_format,
                    'urlFile': get_firebase_url('bg', file),
                    'Creation Date': current_date
                }
                csv_data.append(row)

    # Salvar CSV
    csv_path = os.path.join(EXPORT_DIR, 'export_All-mBackgroundOfertas-acelera.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ligacaoCampanhaFieldName', 'locucaoTranscrita', 'nameFile', 'OS Formato modelo', 'urlFile', 'Creation Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"OK - Gerado: export_All-mBackgroundOfertas-acelera.csv ({len(csv_data)} arquivos)")
    return len(csv_data)

def generate_encerramento_csv():
    """Gera CSV de encerramentos (assinaturas)"""
    print("\nGerando CSV de encerramentos...")

    csv_data = []
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p").lower()

    # ENCERRAMENTO tem estrutura similar às cabeças
    periodos = ['E AMANHA', 'TA ROLANDO']
    regioes = ['MG', 'NACIONAL']
    all_files = set()

    for periodo in periodos:
        for regiao in regioes:
            folder_path = os.path.join(CAMPAIGN_BASE_PATH, 'ENCERRAMENTO', periodo, regiao)

            if not os.path.exists(folder_path):
                print(f"  Pasta não encontrada: {folder_path}")
                continue

            files = scan_folder_files(folder_path)
            print(f"  ENCERRAMENTO - {periodo} - {regiao}: {len(files)} arquivos")

            for file in files:
                if file not in all_files:
                    all_files.add(file)
                    file_format = extract_format_from_filename(file)

                    row = {
                        'ligacaoCampanhaFieldName': 'assinaturaAniversarioAcelera',
                        'locucaoTranscrita': '',
                        'nameFile': file,
                        'OS Formato modelo': file_format,
                        'urlFile': get_firebase_url('assinatura', file),
                        'Creation Date': current_date
                    }
                    csv_data.append(row)

    # Salvar CSV
    csv_path = os.path.join(EXPORT_DIR, 'export_All-mAssinaturas-acelera.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ligacaoCampanhaFieldName', 'locucaoTranscrita', 'nameFile', 'OS Formato modelo', 'urlFile', 'Creation Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"OK - Gerado: export_All-mAssinaturas-acelera.csv ({len(csv_data)} arquivos)")
    return len(csv_data)

def generate_trilha_csv():
    """Gera CSV de trilhas"""
    print("\nGerando CSV de trilhas...")

    csv_data = []
    current_date = datetime.now().strftime("%b %d, %Y %I:%M %p").lower()

    folder_path = os.path.join(CAMPAIGN_BASE_PATH, 'TRILHA')

    if not os.path.exists(folder_path):
        print(f"  Pasta não encontrada: {folder_path}")
        return 0

    files = scan_folder_files(folder_path)
    print(f"  TRILHA: {len(files)} arquivos")

    for file in files:
        file_format = extract_format_from_filename(file)

        row = {
            'ligacaoCampanhaFieldName': 'trilhaAniversarioAcelera',
            'locucaoTranscrita': '',
            'nameFile': file,
            'OS Formato modelo': file_format,
            'urlFile': get_firebase_url('trilha', file),
            'Creation Date': current_date
        }
        csv_data.append(row)

    # Salvar CSV
    csv_path = os.path.join(EXPORT_DIR, 'export_All-mTrilhas-acelera.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ligacaoCampanhaFieldName', 'locucaoTranscrita', 'nameFile', 'OS Formato modelo', 'urlFile', 'Creation Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"OK - Gerado: export_All-mTrilhas-acelera.csv ({len(csv_data)} arquivos)")
    return len(csv_data)

def generate_form_campanhas_csv():
    """Gera CSV de form campanhas com as 4 campanhas"""
    print("\nGerando CSV de form campanhas...")

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 4 campanhas: E Amanha (Nacional e MG) + Ta Rolando (Nacional e MG)
    campanhas = [
        {
            'option': 'Aniversario Acelera E Amanha Nacional',
            'optionSheet': 'aniversarioAceleraAmanha',
            'imagem': '//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224335168x657639157486360500/1080X1080_AMANHA.png'
        },
        {
            'option': 'Aniversario Acelera E Amanha Mg',
            'optionSheet': 'aniversarioAceleraAmanhaMg',
            'imagem': '//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224433749x325785459793999740/1080X1080_AMANHA.png'
        },
        {
            'option': 'Aniversario Acelera Ta Rolando Nacional',
            'optionSheet': 'aniversarioAceleraTaRolando',
            'imagem': '//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224335168x657639157486360500/1080X1080_HOJE.png'
        },
        {
            'option': 'Aniversario Acelera Ta Rolando Mg',
            'optionSheet': 'aniversarioAceleraTaRolandoMg',
            'imagem': '//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224433749x325785459793999740/1080X1080_HOJE.png'
        }
    ]

    csv_data = []
    for campanha in campanhas:
        row = {
            'ajusteCampanha': 'acelera',
            'ativo': 'sim',
            'categoriaLiberacao': '',
            'colorLetras': '#d81510',
            'formCelebridade': '',
            'formSelo': '',
            'imagem': campanha['imagem'],
            'option': campanha['option'],
            'optionSheet': campanha['optionSheet'],
            'OS materiais': 'Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s',
            'OS type midia': 'Tv , Rádio'
        }
        csv_data.append(row)

    # Salvar CSV
    csv_path = os.path.join(EXPORT_DIR, f'export_All-formCampanhas-acelera-{current_date}.csv')

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ajusteCampanha', 'ativo', 'categoriaLiberacao', 'colorLetras', 'formCelebridade',
                     'formSelo', 'imagem', 'option', 'optionSheet', 'OS materiais', 'OS type midia']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"OK - Gerado: export_All-formCampanhas-acelera-{current_date}.csv ({len(csv_data)} campanhas)")
    return len(csv_data)

def main():
    print("=" * 60)
    print("GERADOR DE CSVs - ANIVERSARIO ACELERA")
    print("=" * 60)

    total_cabecas = generate_cabecas_csv()
    total_bg = generate_bg_csv()
    total_encerramento = generate_encerramento_csv()
    total_trilha = generate_trilha_csv()
    total_campanhas = generate_form_campanhas_csv()

    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"  Cabeças: {total_cabecas} arquivos")
    print(f"  Backgrounds: {total_bg} arquivos")
    print(f"  Encerramentos: {total_encerramento} arquivos")
    print(f"  Trilhas: {total_trilha} arquivos")
    print(f"  Campanhas: {total_campanhas} campanhas")
    print(f"\nTotal de mídias: {total_cabecas + total_bg + total_encerramento + total_trilha}")
    print(f"CSVs gerados: 5 arquivos na pasta '{EXPORT_DIR}'")
    print("=" * 60)

if __name__ == '__main__':
    main()
