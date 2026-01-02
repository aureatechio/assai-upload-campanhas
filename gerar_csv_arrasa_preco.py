import os
import csv
from pathlib import Path

def gerar_csv_arrasa_preco():
    """
    Gera CSV com inventário da campanha ARRASA PRECO
    """
    base_dir = r"C:\Users\Mauro\.cursor\automacaoAssai\campanhas_arrasa_preco"
    csv_path = os.path.join(base_dir, "arrasa_preco_inventario.csv")

    print("Gerando CSV da campanha ARRASA PRECO...")

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Tipo', 'Timing', 'Regiao', 'Momento', 'Arquivo', 'Formato', 'Tamanho_KB', 'Caminho'
        ])

        # Processar todas as pastas e arquivos
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.csv'):
                    continue  # Pular o próprio CSV

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_dir)
                path_parts = rel_path.split(os.sep)

                # Determinar categorias baseado no caminho
                if len(path_parts) >= 2:
                    tipo = path_parts[0].upper()
                    timing = path_parts[1] if len(path_parts) > 1 else '-'
                    regiao = path_parts[2] if len(path_parts) > 2 else '-'
                    momento = path_parts[3] if len(path_parts) > 3 else '-'
                else:
                    tipo = 'ROOT'
                    timing = '-'
                    regiao = '-'
                    momento = '-'

                # Obter informações do arquivo
                try:
                    size_kb = round(os.path.getsize(file_path) / 1024, 2)
                    formato = file.split('.')[-1] if '.' in file else 'unknown'

                    writer.writerow([
                        tipo,
                        timing,
                        regiao,
                        momento,
                        file,
                        formato,
                        size_kb,
                        file_path
                    ])
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {e}")

    print(f"CSV gerado em: {csv_path}")

    # Contar arquivos por tipo
    print("\nResumo:")
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pular cabeçalho

        tipos = {}
        total_files = 0
        total_size = 0

        for row in reader:
            tipo = row[0]
            size_kb = float(row[6])

            if tipo not in tipos:
                tipos[tipo] = {'count': 0, 'size': 0}

            tipos[tipo]['count'] += 1
            tipos[tipo]['size'] += size_kb
            total_files += 1
            total_size += size_kb

        for tipo, info in tipos.items():
            print(f"  {tipo}: {info['count']} arquivos, {info['size']:.2f} KB")

        print(f"\nTotal: {total_files} arquivos, {total_size:.2f} KB ({total_size/1024:.2f} MB)")

if __name__ == "__main__":
    gerar_csv_arrasa_preco()