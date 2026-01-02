import os
import shutil
import csv
from pathlib import Path

def processar_campanhas_aniversario():
    """
    Processa e organiza os arquivos de campanhas de aniversário do ASSAI
    """

    # Caminhos
    origem = r"C:\Users\Mauro\Downloads\ANIVERSARIO FEIRASSAI"
    destino = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_aniversario"

    # Estrutura de dados para organizar
    estrutura_campanhas = {
        "assinatura": {},
        "cabeca": {}
    }

    print("Iniciando processamento das campanhas de aniversario...")

    # Criar diretório de destino se não existir
    os.makedirs(destino, exist_ok=True)

    # Processar cada tipo (ASSINATURA e CABECA)
    for tipo in ["ASSINATURA", "CABECA"]:
        tipo_lower = tipo.lower()
        pasta_tipo = os.path.join(origem, tipo)

        if not os.path.exists(pasta_tipo):
            print(f"AVISO: Pasta {tipo} nao encontrada")
            continue

        print(f"\nProcessando {tipo}...")
        estrutura_campanhas[tipo_lower] = {}

        # Processar cada período (3a e 4a, 4a e 5a, 6a e Sab)
        for periodo in os.listdir(pasta_tipo):
            caminho_periodo = os.path.join(pasta_tipo, periodo)

            if not os.path.isdir(caminho_periodo):
                continue

            print(f"  Periodo: {periodo}")
            estrutura_campanhas[tipo_lower][periodo] = {}

            # Processar cada região dentro do período
            for regiao in os.listdir(caminho_periodo):
                caminho_regiao = os.path.join(caminho_periodo, regiao)

                if not os.path.isdir(caminho_regiao):
                    continue

                print(f"    Regiao: {regiao}")
                estrutura_campanhas[tipo_lower][periodo][regiao] = []

                # Criar estrutura de destino
                pasta_destino = os.path.join(destino, tipo_lower, periodo, regiao)
                os.makedirs(pasta_destino, exist_ok=True)

                # Copiar arquivos
                arquivos_copiados = 0
                for arquivo in os.listdir(caminho_regiao):
                    origem_arquivo = os.path.join(caminho_regiao, arquivo)
                    destino_arquivo = os.path.join(pasta_destino, arquivo)

                    if os.path.isfile(origem_arquivo):
                        try:
                            shutil.copy2(origem_arquivo, destino_arquivo)
                            estrutura_campanhas[tipo_lower][periodo][regiao].append({
                                "arquivo": arquivo,
                                "tamanho": os.path.getsize(origem_arquivo),
                                "caminho_origem": origem_arquivo,
                                "caminho_destino": destino_arquivo
                            })
                            arquivos_copiados += 1
                        except Exception as e:
                            print(f"      ERRO ao copiar {arquivo}: {e}")

                print(f"      {arquivos_copiados} arquivos copiados")

    # Gerar relatório CSV
    print("\nGerando relatorio de campanhas...")
    gerar_relatorio_csv(estrutura_campanhas, destino)

    # Gerar resumo
    print("\nResumo do processamento:")
    total_arquivos = 0
    for tipo in estrutura_campanhas:
        for periodo in estrutura_campanhas[tipo]:
            for regiao in estrutura_campanhas[tipo][periodo]:
                total_arquivos += len(estrutura_campanhas[tipo][periodo][regiao])

    print(f"  Total de arquivos processados: {total_arquivos}")
    print(f"  Tipos de campanha: {len(estrutura_campanhas)}")
    print(f"  Estrutura criada em: {destino}")
    print("  Relatorio CSV gerado: campanhas_inventario.csv")

    return estrutura_campanhas

def gerar_relatorio_csv(estrutura, destino):
    """
    Gera um relatório CSV com todos os arquivos processados
    """
    relatorio_path = os.path.join(destino, "campanhas_inventario.csv")

    with open(relatorio_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Tipo', 'Periodo', 'Regiao', 'Arquivo', 'Tamanho_KB',
            'Caminho_Origem', 'Caminho_Destino'
        ])

        for tipo in estrutura:
            for periodo in estrutura[tipo]:
                for regiao in estrutura[tipo][periodo]:
                    for arquivo_info in estrutura[tipo][periodo][regiao]:
                        writer.writerow([
                            tipo.upper(),
                            periodo,
                            regiao,
                            arquivo_info['arquivo'],
                            round(arquivo_info['tamanho'] / 1024, 2),  # Converter para KB
                            arquivo_info['caminho_origem'],
                            arquivo_info['caminho_destino']
                        ])

if __name__ == "__main__":
    try:
        resultado = processar_campanhas_aniversario()
        print("\nProcessamento concluido com sucesso!")
    except Exception as e:
        print(f"\nERRO durante o processamento: {e}")
        import traceback
        traceback.print_exc()