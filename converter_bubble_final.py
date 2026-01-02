import json
import csv
import os

def convert_json_to_bubble_csv():
    """
    Converte JSONs para CSVs compatíveis com Bubble:
    - Nomes de colunas sem espaços
    - Datas sem aspas duplas
    - Formato limpo
    """

    pasta_exportados = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"

    print("Convertendo JSONs para CSVs compatíveis com Bubble...")

    # Converter abertura
    convert_abertura_bubble(pasta_exportados)

    # Converter assinatura
    convert_assinatura_bubble(pasta_exportados)

    print("Conversão concluída!")

def convert_abertura_bubble(pasta_exportados):
    """Converte abertura JSON para CSV otimizado para Bubble"""
    json_path = os.path.join(pasta_exportados, "feirassai_abertura.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_abertura.csv")

    if not os.path.exists(json_path):
        print(f"JSON não encontrado: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Headers sem espaços
    headers = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OSFormatoModelo",
        "urlFile",
        "CreationDate"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)

        for item in data:
            # Limpar data (remover aspas se houver)
            creation_date = str(item.get("Creation Date", "")).replace('"', '')

            row = [
                item.get("ligacaoCampanhaFieldName", ""),
                item.get("locucaoTranscrita", ""),
                item.get("nameFile", ""),
                item.get("OS Formato modelo", ""),
                item.get("urlFile", ""),
                creation_date
            ]
            writer.writerow(row)

    print(f"  Abertura CSV: {len(data)} arquivos")

def convert_assinatura_bubble(pasta_exportados):
    """Converte assinatura JSON para CSV otimizado para Bubble"""
    json_path = os.path.join(pasta_exportados, "feirassai_assinatura.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_assinatura.csv")

    if not os.path.exists(json_path):
        print(f"JSON não encontrado: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Headers sem espaços
    headers = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OSFormatoModelo",
        "urlFile",
        "CreationDate",
        "ModifiedDate"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)

        for item in data:
            # Limpar datas (remover aspas se houver)
            creation_date = str(item.get("Creation Date", "")).replace('"', '')
            modified_date = creation_date  # Usar a mesma data para Modified

            row = [
                item.get("ligacaoCampanhaFieldName", ""),
                item.get("locucaoTranscrita", ""),
                item.get("nameFile", ""),
                item.get("OS Formato modelo", ""),
                item.get("urlFile", ""),
                creation_date,
                modified_date
            ]
            writer.writerow(row)

    print(f"  Assinatura CSV: {len(data)} arquivos")

if __name__ == "__main__":
    try:
        convert_json_to_bubble_csv()
        print("\nCSVs prontos para upload no Bubble!")
        print("Arquivos gerados:")
        print("- exportados/feirassai_abertura.csv")
        print("- exportados/feirassai_assinatura.csv")
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()