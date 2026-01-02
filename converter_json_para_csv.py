import json
import csv
import os

def converter_jsons_para_csvs():
    """
    Converte os JSONs gerados para CSVs no formato dos exemplos
    """

    pasta_exportados = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"

    print("Convertendo JSONs para CSVs...")

    # Converter abertura
    converter_abertura_json_para_csv(pasta_exportados)

    # Converter assinatura
    converter_assinatura_json_para_csv(pasta_exportados)

    # Converter bg (se existir)
    converter_bg_json_para_csv(pasta_exportados)

    # Converter trilha (se existir)
    converter_trilha_json_para_csv(pasta_exportados)

    print("Conversao concluida!")

def converter_abertura_json_para_csv(pasta_exportados):
    """Converte feirassai_abertura.json para CSV"""
    json_path = os.path.join(pasta_exportados, "feirassai_abertura.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_abertura.csv")

    if not os.path.exists(json_path):
        print(f"Arquivo nao encontrado: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    # Cabecalho igual ao exemplo
    cabecalho = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)

        for item in data:
            row = [
                item["ligacaoCampanhaFieldName"],
                item["locucaoTranscrita"],
                item["nameFile"],
                item["OS Formato modelo"],
                item["urlFile"],
                item["Creation Date"]
            ]
            writer.writerow(row)

        # Linha vazia no final
        writer.writerow([])

    print(f"  Abertura CSV criado: {len(data)} arquivos")

def converter_assinatura_json_para_csv(pasta_exportados):
    """Converte feirassai_assinatura.json para CSV"""
    json_path = os.path.join(pasta_exportados, "feirassai_assinatura.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_assinatura.csv")

    if not os.path.exists(json_path):
        print(f"Arquivo nao encontrado: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    # Cabecalho igual ao exemplo (assinatura tem Modified Date)
    cabecalho = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
        "Modified Date"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)

        for item in data:
            row = [
                item["ligacaoCampanhaFieldName"],
                item["locucaoTranscrita"],
                item["nameFile"],
                item["OS Formato modelo"],
                item["urlFile"],
                item["Creation Date"],
                item["Creation Date"]  # Modified Date = Creation Date
            ]
            writer.writerow(row)

        # Linha vazia no final
        writer.writerow([])

    print(f"  Assinatura CSV criado: {len(data)} arquivos")

def converter_bg_json_para_csv(pasta_exportados):
    """Converte feirassai_bg.json para CSV (se existir)"""
    json_path = os.path.join(pasta_exportados, "feirassai_bg.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_bg.csv")

    if not os.path.exists(json_path):
        print("  BG JSON nao existe, criando CSV vazio...")

        # Criar CSV vazio com cabecalho
        cabecalho = [
            "ligacaoCampanhaFieldName",
            "locucaoTranscrita",
            "nameFile",
            "OS Formato modelo",
            "urlFile",
            "Creation Date",
            "formatoMidia",
            "Modified Date"
        ]

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(cabecalho)
            writer.writerow([])

        print(f"  BG CSV criado (vazio)")
        return

    with open(json_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    cabecalho = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
        "formatoMidia",
        "Modified Date"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)

        for item in data:
            row = [
                item["ligacaoCampanhaFieldName"],
                item["locucaoTranscrita"],
                item["nameFile"],
                item["OS Formato modelo"],
                item["urlFile"],
                item["Creation Date"],
                item.get("formatoMidia", "Video"),
                item.get("Modified Date", item["Creation Date"])
            ]
            writer.writerow(row)

        writer.writerow([])

    print(f"  BG CSV criado: {len(data)} arquivos")

def converter_trilha_json_para_csv(pasta_exportados):
    """Converte feirassai_trilha.json para CSV (se existir)"""
    json_path = os.path.join(pasta_exportados, "feirassai_trilha.json")
    csv_path = os.path.join(pasta_exportados, "feirassai_trilha.csv")

    if not os.path.exists(json_path):
        print("  Trilha JSON nao existe, criando CSV vazio...")

        # Criar CSV vazio com cabecalho
        cabecalho = [
            "ligacaoCampanhaFieldName",
            "locucaoTranscrita",
            "nameFile",
            "OS Formato modelo",
            "urlFile",
            "Creation Date",
            "Modified Date",
            "Slug",
            "Creator"
        ]

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(cabecalho)
            writer.writerow([])

        print(f"  Trilha CSV criado (vazio)")
        return

    with open(json_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    cabecalho = [
        "ligacaoCampanhaFieldName",
        "locucaoTranscrita",
        "nameFile",
        "OS Formato modelo",
        "urlFile",
        "Creation Date",
        "Modified Date",
        "Slug",
        "Creator"
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)

        for item in data:
            row = [
                item["ligacaoCampanhaFieldName"],
                item["locucaoTranscrita"],
                item["nameFile"],
                item["OS Formato modelo"],
                item["urlFile"],
                item["Creation Date"],
                item.get("Modified Date", item["Creation Date"]),
                item.get("Slug", ""),
                item.get("Creator", "(App admin)")
            ]
            writer.writerow(row)

        writer.writerow([])

    print(f"  Trilha CSV criado: {len(data)} arquivos")

if __name__ == "__main__":
    try:
        converter_jsons_para_csvs()
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()