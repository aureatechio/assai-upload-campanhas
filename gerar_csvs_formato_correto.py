import os
import csv
from datetime import datetime

def gerar_csvs_formato_correto():
    """
    Gera CSVs no formato correto baseado nos exemplos
    """
    pasta_campanhas = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_aniversario"
    pasta_exportados = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"

    print("Gerando CSVs no formato correto...")

    os.makedirs(pasta_exportados, exist_ok=True)

    # Data de criação atual
    creation_date = datetime.now().strftime("%b %d, %Y %I:%M %p")

    # Gerar CSVs separados
    gerar_csv_abertura(pasta_campanhas, pasta_exportados, creation_date)
    gerar_csv_assinatura(pasta_campanhas, pasta_exportados, creation_date)
    gerar_csv_bg(pasta_campanhas, pasta_exportados, creation_date)
    gerar_csv_trilha(pasta_campanhas, pasta_exportados, creation_date)

    print("CSVs gerados com sucesso!")

def gerar_csv_abertura(pasta_campanhas, pasta_exportados, creation_date):
    """Gera CSV para abertura (cabeça)"""
    csv_path = os.path.join(pasta_exportados, "feirassai_abertura.csv")
    pasta_cabeca = os.path.join(pasta_campanhas, "cabeca")

    cabecalho = ["ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile", "OS Formato modelo", "urlFile", "Creation Date"]

    dados = []

    if os.path.exists(pasta_cabeca):
        for periodo in os.listdir(pasta_cabeca):
            caminho_periodo = os.path.join(pasta_cabeca, periodo)
            if not os.path.isdir(caminho_periodo):
                continue

            for regiao in os.listdir(caminho_periodo):
                caminho_regiao = os.path.join(caminho_periodo, regiao)
                if not os.path.isdir(caminho_regiao):
                    continue

                # Nome da campanha
                campanha_nome = "feirassai"

                for arquivo in os.listdir(caminho_regiao):
                    if arquivo.endswith('.mp4'):
                        # Determinar formato
                        if "1x1" in arquivo:
                            formato = "1x1"
                        elif "9x16" in arquivo:
                            formato = "9x16"
                        elif "16x9" in arquivo:
                            formato = "16x9"
                        else:
                            formato = "16x9"  # default

                        # URL Firebase placeholder
                        url = f"https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/cabeca%2F{arquivo}?alt=media&token=placeholder"

                        dados.append([
                            campanha_nome,  # ligacaoCampanhaFieldName
                            "",             # locucaoTranscrita
                            arquivo,        # nameFile
                            formato,        # OS Formato modelo
                            url,            # urlFile
                            creation_date   # Creation Date
                        ])

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        writer.writerows(dados)
        writer.writerow([])

    print(f"  Abertura CSV: {len(dados)} arquivos")

def gerar_csv_assinatura(pasta_campanhas, pasta_exportados, creation_date):
    """Gera CSV para assinatura"""
    csv_path = os.path.join(pasta_exportados, "feirassai_assinatura.csv")
    pasta_assinatura = os.path.join(pasta_campanhas, "assinatura")

    cabecalho = ["ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile", "OS Formato modelo", "urlFile", "Creation Date"]

    dados = []

    if os.path.exists(pasta_assinatura):
        for periodo in os.listdir(pasta_assinatura):
            caminho_periodo = os.path.join(pasta_assinatura, periodo)
            if not os.path.isdir(caminho_periodo):
                continue

            for regiao in os.listdir(caminho_periodo):
                caminho_regiao = os.path.join(caminho_periodo, regiao)
                if not os.path.isdir(caminho_regiao):
                    continue

                campanha_nome = "feirassai"

                for arquivo in os.listdir(caminho_regiao):
                    if arquivo.endswith('.mp4'):
                        if "1x1" in arquivo:
                            formato = "1x1"
                        elif "9x16" in arquivo:
                            formato = "9x16"
                        elif "16x9" in arquivo:
                            formato = "16x9"
                        else:
                            formato = "16x9"

                        url = f"https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/assinatura%2F{arquivo}?alt=media&token=placeholder"

                        dados.append([
                            campanha_nome,
                            "",
                            arquivo,
                            formato,
                            url,
                            creation_date
                        ])

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        writer.writerows(dados)
        writer.writerow([])

    print(f"  Assinatura CSV: {len(dados)} arquivos")

def gerar_csv_bg(pasta_campanhas, pasta_exportados, creation_date):
    """Gera CSV para background (placeholder)"""
    csv_path = os.path.join(pasta_exportados, "feirassai_bg.csv")

    cabecalho = ["ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile", "OS Formato modelo", "urlFile", "Creation Date", "formatoMidia", "Modified Date"]

    # Placeholder - sem arquivos de background nas campanhas atuais
    dados = []

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        writer.writerows(dados)
        writer.writerow([])

    print(f"  Background CSV: {len(dados)} arquivos (placeholder)")

def gerar_csv_trilha(pasta_campanhas, pasta_exportados, creation_date):
    """Gera CSV para trilha (placeholder)"""
    csv_path = os.path.join(pasta_exportados, "feirassai_trilha.csv")

    cabecalho = ["ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile", "OS Formato modelo", "urlFile", "Creation Date", "Modified Date", "Slug", "Creator"]

    # Placeholder - sem arquivos de trilha nas campanhas atuais
    dados = []

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        writer.writerows(dados)
        writer.writerow([])

    print(f"  Trilha CSV: {len(dados)} arquivos (placeholder)")

if __name__ == "__main__":
    try:
        gerar_csvs_formato_correto()
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()