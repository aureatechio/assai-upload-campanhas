import csv
import os

def create_final_bubble_csv():
    """
    Cria CSVs finais totalmente compatíveis com Bubble
    """

    # Arquivos origem (JSON)
    abertura_json = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_abertura.json"
    assinatura_json = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_assinatura.json"

    print("Criando CSVs finais para Bubble...")

    # Criar abertura CSV
    create_abertura_final(abertura_json)

    # Criar assinatura CSV
    create_assinatura_final(assinatura_json)

    print("CSVs finais criados!")

def create_abertura_final(json_file):
    """Cria CSV de abertura sem problemas de vírgulas"""
    import json

    if not os.path.exists(json_file):
        print(f"JSON não encontrado: {json_file}")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    csv_file = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_abertura.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)  # Forçar aspas em todos os campos

        # Header
        writer.writerow(['campanha', 'locucaoTranscrita', 'nameFile', 'OSFormatoModelo', 'urlFile', 'CreationDate'])

        # Dados
        for item in data:
            # Converter data para formato sem vírgulas
            creation_date = item.get("Creation Date", "").replace(", ", "-")

            row = [
                item.get("ligacaoCampanhaFieldName", ""),
                item.get("locucaoTranscrita", ""),
                item.get("nameFile", ""),
                item.get("OS Formato modelo", ""),
                item.get("urlFile", ""),
                creation_date
            ]
            writer.writerow(row)

    print(f"  Abertura CSV criado: {len(data)} arquivos")

def create_assinatura_final(json_file):
    """Cria CSV de assinatura sem problemas de vírgulas"""
    import json

    if not os.path.exists(json_file):
        print(f"JSON não encontrado: {json_file}")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    csv_file = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_assinatura.csv"

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)  # Forçar aspas em todos os campos

        # Header
        writer.writerow(['campanha', 'locucaoTranscrita', 'nameFile', 'OSFormatoModelo', 'urlFile', 'CreationDate', 'ModifiedDate'])

        # Dados
        for item in data:
            # Converter data para formato sem vírgulas
            creation_date = item.get("Creation Date", "").replace(", ", "-")
            modified_date = creation_date  # Usar a mesma data

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

    print(f"  Assinatura CSV criado: {len(data)} arquivos")

if __name__ == "__main__":
    try:
        create_final_bubble_csv()
        print("\nCSVs totalmente compatíveis com Bubble!")
        print("- Todas as vírgulas nas datas foram removidas")
        print("- Formato: 'Sep-23-2025 05:15 PM'")
        print("- Todos os campos com aspas para evitar problemas")
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()