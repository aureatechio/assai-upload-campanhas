import os
import shutil
import csv
from pathlib import Path

def processar_campanha_arrasa_preco():
    """
    Processa e organiza os arquivos da campanha ANIVERSARIO ARRASA PRECO do ASSAI
    """

    # Caminhos
    origem = r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\ANIVERSARIO ARRASA PRECO"
    destino = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_arrasa_preco"

    # Estrutura de dados para organizar
    estrutura_campanhas = {
        "assinatura": {},
        "cabeca": {},
        "bg": {},
        "thumb": [],
        "trilha": []
    }

    print("Iniciando processamento da campanha ARRASA PRECO...")

    # Criar diretório de destino se não existir
    os.makedirs(destino, exist_ok=True)

    # Processar ASSINATURA e CABEÇA (estrutura similar)
    for tipo in ["ASSINATURA", "CABEÇA"]:
        tipo_key = "assinatura" if tipo == "ASSINATURA" else "cabeca"
        pasta_tipo = os.path.join(origem, tipo)

        if not os.path.exists(pasta_tipo):
            print(f"AVISO: Pasta {tipo} não encontrada")
            continue

        print(f"\nProcessando {tipo}...")
        estrutura_campanhas[tipo_key] = {}

        # Processar cada timing (AMANHA, GENERICO, TA_ROLANDO)
        for timing in os.listdir(pasta_tipo):
            caminho_timing = os.path.join(pasta_tipo, timing)

            if not os.path.isdir(caminho_timing):
                continue

            print(f"  Timing: {timing}")
            estrutura_campanhas[tipo_key][timing] = {}

            # Processar cada região (MG, NACIONAL)
            for regiao in os.listdir(caminho_timing):
                caminho_regiao = os.path.join(caminho_timing, regiao)

                if not os.path.isdir(caminho_regiao):
                    continue

                print(f"    Região: {regiao}")
                estrutura_campanhas[tipo_key][timing][regiao] = {}

                # Processar cada momento (ABERTURA, ENCERRAMENTO para alguns)
                for momento in os.listdir(caminho_regiao):
                    caminho_momento = os.path.join(caminho_regiao, momento)

                    if not os.path.isdir(caminho_momento):
                        continue

                    print(f"      Momento: {momento}")
                    estrutura_campanhas[tipo_key][timing][regiao][momento] = []

                    # Criar estrutura de destino
                    pasta_destino = os.path.join(destino, tipo_key, timing, regiao, momento)
                    os.makedirs(pasta_destino, exist_ok=True)

                    # Copiar arquivos
                    arquivos_copiados = 0
                    for arquivo in os.listdir(caminho_momento):
                        origem_arquivo = os.path.join(caminho_momento, arquivo)
                        destino_arquivo = os.path.join(pasta_destino, arquivo)

                        if os.path.isfile(origem_arquivo):
                            try:
                                shutil.copy2(origem_arquivo, destino_arquivo)
                                estrutura_campanhas[tipo_key][timing][regiao][momento].append({
                                    "arquivo": arquivo,
                                    "tamanho": os.path.getsize(origem_arquivo),
                                    "caminho_origem": origem_arquivo,
                                    "caminho_destino": destino_arquivo,
                                    "formato": arquivo.split('.')[-1] if '.' in arquivo else 'unknown'
                                })
                                arquivos_copiados += 1
                            except Exception as e:
                                print(f"        ERRO ao copiar {arquivo}: {e}")

                    print(f"        {arquivos_copiados} arquivos copiados")

    # Processar BG (Background)
    pasta_bg = os.path.join(origem, "BG")
    if os.path.exists(pasta_bg):
        print(f"\nProcessando BG...")
        estrutura_campanhas["bg"] = {}

        for item in os.listdir(pasta_bg):
            caminho_item = os.path.join(pasta_bg, item)

            if os.path.isdir(caminho_item):
                # É uma pasta (ex: NACIONAL, MG)
                estrutura_campanhas["bg"][item] = []
                pasta_destino = os.path.join(destino, "bg", item)
                os.makedirs(pasta_destino, exist_ok=True)

                for arquivo in os.listdir(caminho_item):
                    origem_arquivo = os.path.join(caminho_item, arquivo)
                    destino_arquivo = os.path.join(pasta_destino, arquivo)

                    if os.path.isfile(origem_arquivo):
                        try:
                            shutil.copy2(origem_arquivo, destino_arquivo)
                            estrutura_campanhas["bg"][item].append({
                                "arquivo": arquivo,
                                "tamanho": os.path.getsize(origem_arquivo),
                                "caminho_origem": origem_arquivo,
                                "caminho_destino": destino_arquivo,
                                "formato": arquivo.split('.')[-1] if '.' in arquivo else 'unknown'
                            })
                        except Exception as e:
                            print(f"    ERRO ao copiar {arquivo}: {e}")

    # Processar THUMB
    pasta_thumb = os.path.join(origem, "THUMB")
    if os.path.exists(pasta_thumb):
        print(f"\nProcessando THUMB...")
        pasta_destino = os.path.join(destino, "thumb")
        os.makedirs(pasta_destino, exist_ok=True)

        for arquivo in os.listdir(pasta_thumb):
            origem_arquivo = os.path.join(pasta_thumb, arquivo)
            destino_arquivo = os.path.join(pasta_destino, arquivo)

            if os.path.isfile(origem_arquivo):
                try:
                    shutil.copy2(origem_arquivo, destino_arquivo)
                    estrutura_campanhas["thumb"].append({
                        "arquivo": arquivo,
                        "tamanho": os.path.getsize(origem_arquivo),
                        "caminho_origem": origem_arquivo,
                        "caminho_destino": destino_arquivo,
                        "formato": arquivo.split('.')[-1] if '.' in arquivo else 'unknown'
                    })
                except Exception as e:
                    print(f"  ERRO ao copiar {arquivo}: {e}")

    # Processar TRILHA
    pasta_trilha = os.path.join(origem, "TRILHA")
    if os.path.exists(pasta_trilha):
        print(f"\nProcessando TRILHA...")
        pasta_destino = os.path.join(destino, "trilha")
        os.makedirs(pasta_destino, exist_ok=True)

        for arquivo in os.listdir(pasta_trilha):
            origem_arquivo = os.path.join(pasta_trilha, arquivo)
            destino_arquivo = os.path.join(pasta_destino, arquivo)

            if os.path.isfile(origem_arquivo):
                try:
                    shutil.copy2(origem_arquivo, destino_arquivo)
                    estrutura_campanhas["trilha"].append({
                        "arquivo": arquivo,
                        "tamanho": os.path.getsize(origem_arquivo),
                        "caminho_origem": origem_arquivo,
                        "caminho_destino": destino_arquivo,
                        "formato": arquivo.split('.')[-1] if '.' in arquivo else 'unknown'
                    })
                except Exception as e:
                    print(f"  ERRO ao copiar {arquivo}: {e}")

    # Gerar relatório CSV
    print("\nGerando relatório da campanha ARRASA PRECO...")
    gerar_relatorio_csv_arrasa_preco(estrutura_campanhas, destino)

    # Gerar resumo
    print("\nResumo do processamento:")
    total_arquivos = 0

    # Contar arquivos de assinatura e cabeça
    for tipo in ["assinatura", "cabeca"]:
        for timing in estrutura_campanhas[tipo]:
            for regiao in estrutura_campanhas[tipo][timing]:
                for momento in estrutura_campanhas[tipo][timing][regiao]:
                    total_arquivos += len(estrutura_campanhas[tipo][timing][regiao][momento])

    # Contar arquivos de BG
    for regiao in estrutura_campanhas["bg"]:
        total_arquivos += len(estrutura_campanhas["bg"][regiao])

    # Contar thumb e trilha
    total_arquivos += len(estrutura_campanhas["thumb"])
    total_arquivos += len(estrutura_campanhas["trilha"])

    print(f"  Total de arquivos processados: {total_arquivos}")
    print(f"  Estrutura criada em: {destino}")
    print("  Relatório CSV gerado: arrasa_preco_inventario.csv")

    return estrutura_campanhas

def gerar_relatorio_csv_arrasa_preco(estrutura, destino):
    """
    Gera um relatório CSV com todos os arquivos da campanha ARRASA PRECO
    """
    relatorio_path = os.path.join(destino, "arrasa_preco_inventario.csv")

    with open(relatorio_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Tipo', 'Timing', 'Regiao', 'Momento', 'Arquivo', 'Formato', 'Tamanho_KB',
            'Caminho_Origem', 'Caminho_Destino'
        ])

        # Processar assinatura e cabeça
        for tipo in ["assinatura", "cabeca"]:
            for timing in estrutura[tipo]:
                for regiao in estrutura[tipo][timing]:
                    for momento in estrutura[tipo][timing][regiao]:
                        for arquivo_info in estrutura[tipo][timing][regiao][momento]:
                            writer.writerow([
                                tipo.upper(),
                                timing,
                                regiao,
                                momento,
                                arquivo_info['arquivo'],
                                arquivo_info['formato'],
                                round(arquivo_info['tamanho'] / 1024, 2),
                                arquivo_info['caminho_origem'],
                                arquivo_info['caminho_destino']
                            ])

        # Processar BG
        for regiao in estrutura["bg"]:
            for arquivo_info in estrutura["bg"][regiao]:
                writer.writerow([
                    'BG',
                    '-',
                    regiao,
                    '-',
                    arquivo_info['arquivo'],
                    arquivo_info['formato'],
                    round(arquivo_info['tamanho'] / 1024, 2),
                    arquivo_info['caminho_origem'],
                    arquivo_info['caminho_destino']
                ])

        # Processar THUMB
        for arquivo_info in estrutura["thumb"]:
            writer.writerow([
                'THUMB',
                '-',
                '-',
                '-',
                arquivo_info['arquivo'],
                arquivo_info['formato'],
                round(arquivo_info['tamanho'] / 1024, 2),
                arquivo_info['caminho_origem'],
                arquivo_info['caminho_destino']
            ])

        # Processar TRILHA
        for arquivo_info in estrutura["trilha"]:
            writer.writerow([
                'TRILHA',
                '-',
                '-',
                '-',
                arquivo_info['arquivo'],
                arquivo_info['formato'],
                round(arquivo_info['tamanho'] / 1024, 2),
                arquivo_info['caminho_origem'],
                arquivo_info['caminho_destino']
            ])

if __name__ == "__main__":
    try:
        resultado = processar_campanha_arrasa_preco()
        print("\nProcessamento da campanha ARRASA PRECO concluído com sucesso!")
    except Exception as e:
        print(f"\nERRO durante o processamento: {e}")
        import traceback
        traceback.print_exc()