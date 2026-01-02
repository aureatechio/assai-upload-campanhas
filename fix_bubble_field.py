import csv
import os

def fix_bubble_field_issue():
    """
    Corrige o problema do campo sendo interpretado como lista no Bubble
    Simplifica o nome do campo e garante formato correto
    """

    files_to_fix = [
        r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_abertura.csv",
        r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_assinatura.csv"
    ]

    print("Corrigindo problema do campo lista no Bubble...")

    for file_path in files_to_fix:
        fix_single_file(file_path)

    print("Correção concluída!")

def fix_single_file(file_path):
    """Corrige um arquivo específico"""
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return

    # Ler dados
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print(f"Arquivo vazio: {file_path}")
        return

    # Modificar header - simplificar nome do campo
    header = rows[0]
    if 'ligacaoCampanhaFieldName' in header:
        header_index = header.index('ligacaoCampanhaFieldName')
        header[header_index] = 'campanha'  # Nome mais simples

    # Reescrever arquivo
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow(row)

    filename = os.path.basename(file_path)
    print(f"  Campo renomeado para 'campanha' em: {filename}")

if __name__ == "__main__":
    try:
        fix_bubble_field_issue()
        print("\nArquivos corrigidos:")
        print("- Campo 'ligacaoCampanhaFieldName' → 'campanha'")
        print("- Formato simplificado para Bubble")
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()