import json
import csv
import os

def fix_csv_for_bubble():
    """
    Corrige os CSVs para serem compatíveis com Bubble:
    1. Remove espaços dos nomes das colunas
    2. Remove aspas duplas das datas
    3. Remove linhas vazias no final
    4. Usa apenas aspas quando necessário
    """

    pasta_exportados = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"

    print("Corrigindo CSVs para compatibilidade com Bubble...")

    # Corrigir abertura
    fix_abertura_csv(pasta_exportados)

    # Corrigir assinatura
    fix_assinatura_csv(pasta_exportados)

    print("CSVs corrigidos para Bubble!")

def fix_abertura_csv(pasta_exportados):
    """Corrige o CSV de abertura"""
    json_path = os.path.join(pasta_exportados, "feirassai_abertura.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_abertura.csv")

    if not os.path.exists(json_path):
        print(f"JSON não encontrado: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    # Cabeçalho sem espaços
    cabecalho = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OSFormatoModelo",
        "urlFile",
        "CreationDate"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cabecalho)

        for item in data:
            # Remove aspas duplas da data
            creation_date = item["Creation Date"].replace('"', '') if item.get("Creation Date") else ''

            row = [
                item["ligacaoCampanhaFieldName"],
                item["locucaoTranscrita"],
                item["nameFile"],
                item["OS Formato modelo"],
                item["urlFile"],
                creation_date
            ]
            writer.writerow(row)

    print(f"  Abertura CSV corrigido: {len(data)} arquivos")

def fix_assinatura_csv(pasta_exportados):
    """Corrige o CSV de assinatura"""
    json_path = os.path.join(pasta_exportados, "feirassai_assinatura.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_assinatura.csv")

    if not os.path.exists(json_path):
        print(f"JSON não encontrado: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    # Cabeçalho sem espaços
    cabecalho = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OSFormatoModelo",
        "urlFile",
        "CreationDate",
        "ModifiedDate"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cabecalho)

        for item in data:
            # Remove aspas duplas das datas
            creation_date = item["Creation Date"].replace('"', '') if item.get("Creation Date") else ''
            modified_date = item.get("Modified Date", creation_date).replace('"', '') if item.get("Modified Date") else creation_date

            row = [
                item["ligacaoCampanhaFieldName"],
                item["locucaoTranscrita"],
                item["nameFile"],
                item["OS Formato modelo"],
                item["urlFile"],
                creation_date,
                modified_date
            ]
            writer.writerow(row)

    print(f"  Assinatura CSV corrigido: {len(data)} arquivos")

if __name__ == "__main__":
    try:
        fix_csv_for_bubble()
        print("\nVerifique os CSVs corrigidos em exportados/")
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()