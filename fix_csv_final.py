import csv
import os

def fix_csv_final():
    """
    Remove completamente as aspas das datas nos CSVs
    """
    pasta_exportados = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"

    print("Removendo aspas das datas nos CSVs...")

    # Corrigir abertura
    fix_abertura_final(pasta_exportados)

    # Corrigir assinatura
    fix_assinatura_final(pasta_exportados)

    print("CSVs finalmente corrigidos!")

def fix_abertura_final(pasta_exportados):
    """Remove aspas do CSV de abertura"""
    csv_path = os.path.join(pasta_exportados, "feirassai_abertura.csv")

    # Ler o arquivo atual
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 6:  # Garantir que tem todas as colunas
                # Limpar aspas da data (coluna 5 = CreationDate)
                row[5] = row[5].replace('"', '')
            rows.append(row)

    # Reescrever sem aspas desnecessárias
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow(row)

    print(f"  Abertura CSV - aspas removidas")

def fix_assinatura_final(pasta_exportados):
    """Remove aspas do CSV de assinatura"""
    csv_path = os.path.join(pasta_exportados, "feirassai_assinatura.csv")

    # Ler o arquivo atual
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 7:  # Garantir que tem todas as colunas
                # Limpar aspas das datas (colunas 5 e 6)
                row[5] = row[5].replace('"', '')  # CreationDate
                row[6] = row[6].replace('"', '')  # ModifiedDate
            rows.append(row)

    # Reescrever sem aspas desnecessárias
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow(row)

    print(f"  Assinatura CSV - aspas removidas")

if __name__ == "__main__":
    try:
        fix_csv_final()
        print("\nCSVs prontos para upload no Bubble!")
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()