import os
import csv
from pathlib import Path

def gerar_csvs_campanhas():
    """
    Gera CSVs formatados para campanhas de assinatura e cabeca
    baseados na estrutura da pasta campanhas_aniversario
    """

    pasta_campanhas = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_aniversario"
    pasta_exportados = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"

    print("Gerando CSVs formatados para campanhas...")

    # Criar pasta exportados se não existir
    os.makedirs(pasta_exportados, exist_ok=True)

    # Processar ASSINATURA
    print("\nProcessando campanhas de ASSINATURA...")
    gerar_csv_assinatura(pasta_campanhas, pasta_exportados)

    # Processar CABECA
    print("Processando campanhas de CABECA...")
    gerar_csv_cabeca(pasta_campanhas, pasta_exportados)

    print("\nCSVs gerados com sucesso!")

def gerar_csv_assinatura(pasta_campanhas, pasta_exportados):
    """
    Gera CSV para campanhas de assinatura (encerramento)
    """
    csv_path = os.path.join(pasta_exportados, "campanhas_assinatura.csv")
    pasta_assinatura = os.path.join(pasta_campanhas, "assinatura")

    # Cabeçalho baseado no formato existente
    cabecalho = [
        "ajusteCampanha", "ativo", "categoriaLiberacao", "colorLetras",
        "formCelebridade", "formSelo", "imagem", "option", "optionSheet",
        "OS materiais", "OS type midia"
    ]

    campanhas = []

    if os.path.exists(pasta_assinatura):
        # Processar cada período
        for periodo in os.listdir(pasta_assinatura):
            caminho_periodo = os.path.join(pasta_assinatura, periodo)

            if not os.path.isdir(caminho_periodo):
                continue

            # Processar cada região
            for regiao in os.listdir(caminho_periodo):
                caminho_regiao = os.path.join(caminho_periodo, regiao)

                if not os.path.isdir(caminho_regiao):
                    continue

                # Gerar nome da campanha
                periodo_clean = periodo.replace(" e ", "").replace(" ", "")
                regiao_clean = regiao.replace(" ", "").replace("ENCERRAMENTO", "").strip()

                if regiao_clean == "NACIONAL":
                    nome_campanha = f"Assinatura Feirassai {periodo}"
                    option_sheet = f"assinaturaFeirassai{periodo_clean}"
                else:
                    nome_campanha = f"Assinatura Feirassai {periodo} {regiao_clean}"
                    option_sheet = f"assinaturaFeirassai{periodo_clean}{regiao_clean}"

                # Verificar arquivos disponíveis
                arquivos = [f for f in os.listdir(caminho_regiao) if f.endswith('.mp4')]

                if arquivos:
                    # Determinar materiais baseado nos formatos disponíveis
                    materiais = []
                    tipos_midia = []

                    for arquivo in arquivos:
                        if "1x1" in arquivo:
                            materiais.append("Video 1x1")
                            tipos_midia.append("Social Media")
                        elif "9x16" in arquivo:
                            materiais.append("Video 9x16")
                            tipos_midia.append("Stories")
                        elif "16x9" in arquivo:
                            materiais.append("Video 16x9")
                            tipos_midia.append("TV")

                    # Remover duplicatas mantendo ordem
                    materiais = list(dict.fromkeys(materiais))
                    tipos_midia = list(dict.fromkeys(tipos_midia))

                    campanhas.append([
                        "acelera",  # ajusteCampanha
                        "sim",      # ativo
                        "",         # categoriaLiberacao
                        "#d81510",  # colorLetras
                        "",         # formCelebridade
                        "",         # formSelo
                        "",         # imagem
                        nome_campanha,  # option
                        option_sheet,   # optionSheet
                        " , ".join(materiais),     # OS materiais
                        " , ".join(tipos_midia)    # OS type midia
                    ])

    # Escrever CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        writer.writerows(campanhas)

        # Linha vazia no final
        writer.writerow([])

    print(f"  CSV de assinatura gerado: {csv_path}")
    print(f"  Total de campanhas: {len(campanhas)}")

def gerar_csv_cabeca(pasta_campanhas, pasta_exportados):
    """
    Gera CSV para campanhas de cabeça (abertura)
    """
    csv_path = os.path.join(pasta_exportados, "campanhas_cabeca.csv")
    pasta_cabeca = os.path.join(pasta_campanhas, "cabeca")

    # Cabeçalho baseado no formato existente
    cabecalho = [
        "ajusteCampanha", "ativo", "categoriaLiberacao", "colorLetras",
        "formCelebridade", "formSelo", "imagem", "option", "optionSheet",
        "OS materiais", "OS type midia"
    ]

    campanhas = []

    if os.path.exists(pasta_cabeca):
        # Processar cada período
        for periodo in os.listdir(pasta_cabeca):
            caminho_periodo = os.path.join(pasta_cabeca, periodo)

            if not os.path.isdir(caminho_periodo):
                continue

            # Processar cada região
            for regiao in os.listdir(caminho_periodo):
                caminho_regiao = os.path.join(caminho_periodo, regiao)

                if not os.path.isdir(caminho_regiao):
                    continue

                # Gerar nome da campanha
                periodo_clean = periodo.replace(" e ", "").replace(" ", "")
                regiao_clean = regiao.replace("CABECA", "").replace(" ", "").strip()

                if regiao_clean == "NACIONAL":
                    nome_campanha = f"Cabeca Feirassai {periodo}"
                    option_sheet = f"cabecaFeirassai{periodo_clean}"
                else:
                    nome_campanha = f"Cabeca Feirassai {periodo} {regiao_clean}"
                    option_sheet = f"cabecaFeirassai{periodo_clean}{regiao_clean}"

                # Verificar arquivos disponíveis
                arquivos = [f for f in os.listdir(caminho_regiao) if f.endswith('.mp4')]

                if arquivos:
                    # Determinar materiais baseado nos formatos disponíveis
                    materiais = []
                    tipos_midia = []

                    for arquivo in arquivos:
                        if "1x1" in arquivo:
                            materiais.append("Video 1x1")
                            tipos_midia.append("Social Media")
                        elif "9x16" in arquivo:
                            materiais.append("Video 9x16")
                            tipos_midia.append("Stories")
                        elif "16x9" in arquivo:
                            materiais.append("Video 16x9")
                            tipos_midia.append("TV")

                    # Remover duplicatas mantendo ordem
                    materiais = list(dict.fromkeys(materiais))
                    tipos_midia = list(dict.fromkeys(tipos_midia))

                    campanhas.append([
                        "acelera",  # ajusteCampanha
                        "sim",      # ativo
                        "",         # categoriaLiberacao
                        "#d81510",  # colorLetras
                        "",         # formCelebridade
                        "",         # formSelo
                        "",         # imagem
                        nome_campanha,  # option
                        option_sheet,   # optionSheet
                        " , ".join(materiais),     # OS materiais
                        " , ".join(tipos_midia)    # OS type midia
                    ])

    # Escrever CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cabecalho)
        writer.writerows(campanhas)

        # Linha vazia no final
        writer.writerow([])

    print(f"  CSV de cabeca gerado: {csv_path}")
    print(f"  Total de campanhas: {len(campanhas)}")

if __name__ == "__main__":
    try:
        gerar_csvs_campanhas()
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()