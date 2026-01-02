import os
import csv
from datetime import datetime

def gerar_campanhas_arrasa_preco():
    """
    Gera 6 campanhas da ARRASA PRECO em formato CSV com nomenclatura camelCase
    """

    # Configurações
    base_path = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_arrasa_preco"
    output_dir = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"
    os.makedirs(output_dir, exist_ok=True)

    # Data atual formatada
    creation_date = datetime.now().strftime("%b %d-%Y %I:%M %p")

    # Definição das campanhas
    campanhas = [
        {
            "nome": "aniversarioArrasaPrecoAmanha",
            "nome_mg": "aniversarioArrasaPrecoAmanhaMg",
            "timing": "AMANHA",
            "arquivo_base": "cabAniversarioArrasaPrecoNacionalAmanha",
            "arquivo_mg": "cabAniversarioArrasaPrecoMgAmanha"
        },
        {
            "nome": "aniversarioArrasaPrecoTaRolando",
            "nome_mg": "aniversarioArrasaPrecoTaRolandoMg",
            "timing": "TA_ROLANDO",
            "arquivo_base": "cabAniversarioArrasaPrecoNacionalTaRolando",
            "arquivo_mg": "cabAniversarioArrasaPrecoMgTaRolando"
        },
        {
            "nome": "aniversarioArrasaPrecoHoje",
            "nome_mg": "aniversarioArrasaPrecoHojeMg",
            "timing": "HOJE",
            "arquivo_base": "cabAniversarioArrasaPrecoNacionalHoje",
            "arquivo_mg": "cabAniversarioArrasaPrecoMgHoje"
        }
    ]

    # Formatos de arquivo
    formatos = ["16x9", "1x1", "9x16"]

    print("Gerando campanhas ARRASA PRECO...")

    for campanha in campanhas:
        # Campanha NACIONAL
        gerar_csv_campanha(
            nome_campanha=campanha["nome"],
            timing=campanha["timing"],
            regiao="NACIONAL",
            arquivo_base=campanha["arquivo_base"],
            formatos=formatos,
            base_path=base_path,
            output_dir=output_dir,
            creation_date=creation_date
        )

        # Campanha MG
        gerar_csv_campanha(
            nome_campanha=campanha["nome_mg"],
            timing=campanha["timing"],
            regiao="MG",
            arquivo_base=campanha["arquivo_mg"],
            formatos=formatos,
            base_path=base_path,
            output_dir=output_dir,
            creation_date=creation_date
        )

    print("Todas as 6 campanhas foram geradas com sucesso!")

def gerar_csv_campanha(nome_campanha, timing, regiao, arquivo_base, formatos, base_path, output_dir, creation_date):
    """
    Gera um CSV para uma campanha específica
    """

    # Nome do arquivo CSV
    csv_filename = f"{nome_campanha}_abertura.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    print(f"Gerando: {csv_filename}")

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Cabeçalho
        writer.writerow([
            "campanha", "locucaoTranscrita", "nameFile", "OSFormatoModelo", "urlFile", "CreationDate"
        ])

        # Gerar linhas para cada formato
        for formato in formatos:
            nome_arquivo = f"{arquivo_base}{formato}.mp4"

            # URL do Firebase (padrão baseado no exemplo)
            url_firebase = f"https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/cabeca%2F{nome_arquivo}?alt=media&token=7d2e4acc-15fa-46f0-9d3d-7b026db1f96b"

            writer.writerow([
                nome_campanha,
                "",  # locucaoTranscrita vazia
                nome_arquivo,
                formato,
                url_firebase,
                creation_date
            ])

    print(f"  OK CSV criado: {csv_path}")

def verificar_arquivos_existem():
    """
    Verifica se os arquivos de vídeo realmente existem na estrutura
    """
    base_path = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_arrasa_preco\cabeca"

    timings = ["AMANHA", "TA_ROLANDO"]
    regioes = ["NACIONAL", "MG"]
    formatos = ["16x9", "1x1", "9x16"]

    print("\nVerificando arquivos existentes:")

    for timing in timings:
        for regiao in regioes:
            pasta_abertura = os.path.join(base_path, timing, regiao, "ABERTURA")

            if os.path.exists(pasta_abertura):
                print(f"\n{timing} - {regiao}:")
                for arquivo in os.listdir(pasta_abertura):
                    print(f"  OK {arquivo}")
            else:
                print(f"\nERRO Pasta nao encontrada: {pasta_abertura}")

    # Verificar se HOJE existe (pode não existir ainda)
    for regiao in regioes:
        pasta_hoje = os.path.join(base_path, "HOJE", regiao, "ABERTURA")
        if os.path.exists(pasta_hoje):
            print(f"\nHOJE - {regiao}:")
            for arquivo in os.listdir(pasta_hoje):
                print(f"  OK {arquivo}")
        else:
            print(f"\nAVISO HOJE - {regiao}: Pasta nao encontrada (pode precisar ser criada)")

if __name__ == "__main__":
    # Primeiro verificar os arquivos
    verificar_arquivos_existem()

    print("\n" + "="*50)

    # Gerar as campanhas
    gerar_campanhas_arrasa_preco()