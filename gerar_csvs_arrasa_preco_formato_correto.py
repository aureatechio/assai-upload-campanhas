import os
import csv
from datetime import datetime

def gerar_csvs_arrasa_preco_formato_correto():
    """
    Gera CSVs da campanha ARRASA PRECO no formato correto conforme exemplos
    """

    # Configurações
    base_path = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_arrasa_preco"
    output_dir = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"
    os.makedirs(output_dir, exist_ok=True)

    # Data atual no formato dos exemplos
    creation_date = datetime.now().strftime("%b %d, %Y %I:%M %p").lower()

    print("Gerando CSVs ARRASA PRECO no formato correto...")

    # Definir todas as campanhas que precisam ser geradas
    campanhas_config = [
        {
            "timing": "AMANHA",
            "regiao": "NACIONAL",
            "campanha_nome": "aniversarioArrasaPrecoAmanha",
            "arquivo_base": "cabAniversarioArrasaPrecoNacionalAmanha"
        },
        {
            "timing": "AMANHA",
            "regiao": "MG",
            "campanha_nome": "aniversarioArrasaPrecoAmanhaMg",
            "arquivo_base": "cabAniversarioArrasaPrecoMgAmanha"
        },
        {
            "timing": "TA_ROLANDO",
            "regiao": "NACIONAL",
            "campanha_nome": "aniversarioArrasaPrecoTaRolando",
            "arquivo_base": "cabAniversarioArrasaPrecoNacionalTaRolando"
        },
        {
            "timing": "TA_ROLANDO",
            "regiao": "MG",
            "campanha_nome": "aniversarioArrasaPrecoTaRolandoMg",
            "arquivo_base": "cabAniversarioArrasaPrecoMgTaRolando"
        },
        {
            "timing": "HOJE",
            "regiao": "NACIONAL",
            "campanha_nome": "aniversarioArrasaPrecoHoje",
            "arquivo_base": "cabAniversarioArrasaPrecoNacionalHoje"
        },
        {
            "timing": "HOJE",
            "regiao": "MG",
            "campanha_nome": "aniversarioArrasaPrecoHojeMg",
            "arquivo_base": "cabAniversarioArrasaPrecoMgHoje"
        }
    ]

    # Gerar 5 CSVs únicos
    gerar_csv_cabecas_unico(campanhas_config, output_dir, creation_date)
    gerar_csv_assinaturas_unico(campanhas_config, output_dir, creation_date)
    gerar_csv_bg(output_dir, creation_date)
    gerar_csv_trilha(output_dir, creation_date)

    print("\\n5 CSVs gerados: CABEÇAS, ASSINATURAS, BG, TRILHA")

    print("Todos os CSVs foram gerados no formato correto!")

def gerar_csv_cabecas_unico(campanhas_config, output_dir, creation_date):
    """
    Gera UM CSV único para todas as cabeças conforme formato dos exemplos
    """
    print("\nGerando CSV único de CABEÇAS...")

    csv_filename = "export_All-mCabecas-arrasaPreco.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    print(f"  Gerando: {csv_filename}")

    formatos = ["1x1", "9x16", "16x9"]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Cabeçalho conforme exemplo
        writer.writerow([
            "ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile",
            "OS Formato modelo", "urlFile", "Creation Date"
        ])

        # Gerar linhas para todas as campanhas e formatos
        for campanha in campanhas_config:
            for formato in formatos:
                nome_arquivo = f"{campanha['arquivo_base']}{formato}.mp4"

                # URL do Firebase
                url_firebase = f"https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/cabeca%2F{nome_arquivo}?alt=media&token=7d2e4acc-15fa-46f0-9d3d-7b026db1f96b"

                writer.writerow([
                    campanha['campanha_nome'],
                    "",  # locucaoTranscrita vazia
                    nome_arquivo,
                    formato,
                    url_firebase,
                    creation_date
                ])

def gerar_csv_assinaturas_unico(campanhas_config, output_dir, creation_date):
    """
    Gera UM CSV único para todas as assinaturas conforme formato dos exemplos
    """
    print("\nGerando CSV único de ASSINATURAS...")

    csv_filename = "export_All-mAssinaturas-arrasaPreco.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    print(f"  Gerando: {csv_filename}")

    formatos = ["16x9", "9x16", "1x1"]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Cabeçalho conforme exemplo (assinaturas têm Modified Date)
        writer.writerow([
            "ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile",
            "OS Formato modelo", "urlFile", "Creation Date", "Modified Date"
        ])

        # Gerar linhas para todas as campanhas e formatos
        for campanha in campanhas_config:
            for formato in formatos:
                # Para assinaturas, usar prefixo 'ass'
                arquivo_base_ass = campanha['arquivo_base'].replace('cab', 'ass')
                nome_arquivo = f"{arquivo_base_ass}{formato}.mp4"

                # URL do Firebase para assinaturas
                url_firebase = f"https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/assinatura%2F{nome_arquivo}?alt=media&token=7d2e4acc-15fa-46f0-9d3d-7b026db1f96b"

                writer.writerow([
                    campanha['campanha_nome'],
                    "Vem para o Aniversário Assaí, arrasa preço!",  # Locução padrão
                    nome_arquivo,
                    formato,
                    url_firebase,
                    creation_date,
                    creation_date  # Modified Date igual ao Creation Date
                ])

def gerar_csv_bg(output_dir, creation_date):
    """
    Gera CSV para backgrounds
    """
    print("\nGerando CSV de BACKGROUNDS...")

    csv_filename = "export_All-mBackgroundOfertas-arrasaPreco.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    print(f"  Gerando: {csv_filename}")

    formatos = ["16x9", "1x1", "9x16"]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Cabeçalho
        writer.writerow([
            "ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile",
            "OS Formato modelo", "urlFile", "Creation Date"
        ])

        # BG Nacional
        for formato in formatos:
            nome_arquivo = f"bgAniversarioArrasaPreco{formato}.mp4"
            url_firebase = f"https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/bg%2F{nome_arquivo}?alt=media&token=7d2e4acc-15fa-46f0-9d3d-7b026db1f96b"

            writer.writerow([
                "bgAniversarioArrasaPreco",
                "",
                nome_arquivo,
                formato,
                url_firebase,
                creation_date
            ])

def gerar_csv_trilha(output_dir, creation_date):
    """
    Gera CSV para trilhas
    """
    print("\nGerando CSV de TRILHAS...")

    csv_filename = "export_All-mTrilhas-arrasaPreco.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    print(f"  Gerando: {csv_filename}")

    trilhas = ["trilhaAniversarioVsMilhao15s.wav", "trilhaAniversarioVsMilhao30s.wav"]

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Cabeçalho
        writer.writerow([
            "ligacaoCampanhaFieldName", "locucaoTranscrita", "nameFile",
            "OS Formato modelo", "urlFile", "Creation Date"
        ])

        for trilha in trilhas:
            duracao = "15s" if "15s" in trilha else "30s"
            url_firebase = f"https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/trilha%2F{trilha}?alt=media&token=7d2e4acc-15fa-46f0-9d3d-7b026db1f96b"

            writer.writerow([
                f"trilhaAniversarioArrasaPreco{duracao}",
                "",
                trilha,
                "audio",
                url_firebase,
                creation_date
            ])

if __name__ == "__main__":
    gerar_csvs_arrasa_preco_formato_correto()