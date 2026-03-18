import os

def fix_csv_commas():
    """
    Corrige o problema de vírgulas nas datas que estão quebrando o CSV
    """

    files_to_fix = [
        r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_abertura.csv",
        r"C:\Users\Mauro\.cursor\automacaoAssai\exportados\feirassai_assinatura.csv"
    ]

    print("Corrigindo vírgulas nas datas dos CSVs...")

    for file_path in files_to_fix:
        fix_date_commas(file_path)

    print("Correção de vírgulas concluída!")

def fix_date_commas(file_path):
    """Corrige vírgulas nas datas que estão quebrando o formato CSV"""
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return

    # Ler dados usando CSV reader para lidar com vírgulas corretamente
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print(f"Arquivo vazio: {file_path}")
        return

    # Modificar datas para formato sem vírgulas
    for i, row in enumerate(rows):
        if i == 0:  # Pular header
            continue

        # Para cada campo de data, remover vírgulas
        for j, cell in enumerate(row):
            if "2025" in cell and "PM" in cell:  # Identificar campos de data
                # Trocar formato: "Sep 23, 2025 05:15 PM" -> "Sep-23-2025 05:15 PM"
                row[j] = cell.replace(", ", "-")

    # Reescrever arquivo com aspas onde necessário
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            writer.writerow(row)

    filename = os.path.basename(file_path)
    print(f"  Vírgulas corrigidas em: {filename}")

if __name__ == "__main__":
    try:
        fix_csv_commas()
        print("\nDatas corrigidas:")
        print("- Formato: 'Sep 23, 2025' -> 'Sep-23-2025'")
        print("- Remove vírgulas que quebram CSV")
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()