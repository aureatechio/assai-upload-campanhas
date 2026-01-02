import csv
import re

def clean_csv_dates():
    """Remove aspas das datas nos CSVs gerados"""

    files_to_clean = [
        r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_abertura.csv",
        r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_assinatura.csv"
    ]

    for file_path in files_to_clean:
        print(f"Limpando: {file_path}")
        clean_single_csv(file_path)

    print("Limpeza concluída!")

def clean_single_csv(file_path):
    """Limpa um CSV específico"""
    try:
        # Ler conteúdo completo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remover aspas duplas das datas (padrão "Sep 23, 2025 05:15 PM")
        # Use regex para encontrar datas entre aspas
        content = re.sub(r'"([A-Za-z]{3} \d{1,2}, \d{4} \d{1,2}:\d{2} [AP]M)"', r'\1', content)

        # Escrever de volta
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Datas limpas em {file_path}")

    except Exception as e:
        print(f"  ✗ Erro ao limpar {file_path}: {e}")

if __name__ == "__main__":
    clean_csv_dates()