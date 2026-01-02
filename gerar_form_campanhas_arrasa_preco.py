import os
import csv
from datetime import datetime

def gerar_form_campanhas_arrasa_preco():
    """
    Gera CSV de formCampanhas para a campanha ARRASA PRECO
    """

    # Configurações
    output_dir = r"C:\Users\Mauro\.cursor\automacaoAssai\exportados"
    os.makedirs(output_dir, exist_ok=True)

    # Nome do arquivo conforme padrão
    data_formatada = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_filename = f"export_All-formCampanhas-arrasaPreco-{data_formatada}.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    print(f"Gerando formCampanhas: {csv_filename}")

    # Definir as 6 campanhas ARRASA PRECO
    campanhas_form = [
        {
            "ajusteCampanha": "arrasaPreco",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",  # Cor padrão Assaí (vermelho)
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224335168x657639157486360500/THUMB-ARRASA-PRECO-AMANHA.png",
            "option": "Aniversario Arrasa Preco Amanha Nacional",
            "optionSheet": "aniversarioArrasaPrecoAmanha",
            "OS_materiais": "Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s",
            "OS_type_midia": "Tv , Rádio"
        },
        {
            "ajusteCampanha": "arrasaPreco",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224433749x325785459793999740/THUMB-ARRASA-PRECO-AMANHA-MG.png",
            "option": "Aniversario Arrasa Preco Amanha Mg",
            "optionSheet": "aniversarioArrasaPrecoAmanhaMg",
            "OS_materiais": "Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s",
            "OS_type_midia": "Tv , Rádio"
        },
        {
            "ajusteCampanha": "arrasaPreco",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224335168x657639157486360500/THUMB-ARRASA-PRECO-TA-ROLANDO.png",
            "option": "Aniversario Arrasa Preco Ta Rolando Nacional",
            "optionSheet": "aniversarioArrasaPrecoTaRolando",
            "OS_materiais": "Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s",
            "OS_type_midia": "Tv , Rádio"
        },
        {
            "ajusteCampanha": "arrasaPreco",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224433749x325785459793999740/THUMB-ARRASA-PRECO-TA-ROLANDO-MG.png",
            "option": "Aniversario Arrasa Preco Ta Rolando Mg",
            "optionSheet": "aniversarioArrasaPrecoTaRolandoMg",
            "OS_materiais": "Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s",
            "OS_type_midia": "Tv , Rádio"
        },
        {
            "ajusteCampanha": "arrasaPreco",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224335168x657639157486360500/THUMB-ARRASA-PRECO-HOJE.png",
            "option": "Aniversario Arrasa Preco Hoje Nacional",
            "optionSheet": "aniversarioArrasaPrecoHoje",
            "OS_materiais": "Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s",
            "OS_type_midia": "Tv , Rádio"
        },
        {
            "ajusteCampanha": "arrasaPreco",
            "ativo": "sim",
            "categoriaLiberacao": "",
            "colorLetras": "#d81510",
            "formCelebridade": "",
            "formSelo": "",
            "imagem": "//12a3388ae72b3046e48cc88a697af4c7.cdn.bubble.io/f1758224433749x325785459793999740/THUMB-ARRASA-PRECO-HOJE-MG.png",
            "option": "Aniversario Arrasa Preco Hoje Mg",
            "optionSheet": "aniversarioArrasaPrecoHojeMg",
            "OS_materiais": "Filme de 15s , Filme de 30s , Spot de Rádio 15s , Spot de Rádio 30s",
            "OS_type_midia": "Tv , Rádio"
        }
    ]

    # Gerar CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Cabeçalho conforme exemplo
        writer.writerow([
            "ajusteCampanha", "ativo", "categoriaLiberacao", "colorLetras",
            "formCelebridade", "formSelo", "imagem", "option", "optionSheet",
            "OS materiais", "OS type midia"
        ])

        # Escrever dados de cada campanha
        for campanha in campanhas_form:
            writer.writerow([
                campanha["ajusteCampanha"],
                campanha["ativo"],
                campanha["categoriaLiberacao"],
                campanha["colorLetras"],
                campanha["formCelebridade"],
                campanha["formSelo"],
                campanha["imagem"],
                campanha["option"],
                campanha["optionSheet"],
                campanha["OS_materiais"],
                campanha["OS_type_midia"]
            ])

    print(f"FormCampanhas gerado: {csv_path}")
    print(f"Total de campanhas: {len(campanhas_form)}")

    # Mostrar resumo
    print("\nCampanhas criadas:")
    for i, campanha in enumerate(campanhas_form, 1):
        print(f"  {i}. {campanha['option']} ({campanha['optionSheet']})")

if __name__ == "__main__":
    gerar_form_campanhas_arrasa_preco()