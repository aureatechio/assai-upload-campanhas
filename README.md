# 🤖 Automação ASSAI - Gerador de CSVs

Sistema de automação para leitura de campanhas e geração de arquivos CSV com URLs do Firebase.

## 📁 Estrutura do Projeto

```
automacaoAssai/
├── backend/
│   ├── app.py              # Aplicação Flask principal
│   └── requirements.txt    # Dependências Python
├── frontend/
│   └── index.html         # Interface web simples
├── exportados/            # CSVs gerados (criado automaticamente)
└── README.md             # Documentação
```

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
# Navegue até a pasta backend
cd backend

# Instale as dependências Python
pip install -r requirements.txt
```

### 2. Executar o Sistema

```bash
# Na pasta backend, execute:
python app.py
```

O sistema estará disponível em: `http://localhost:5000`

### 3. Usar a Interface

1. Acesse `http://localhost:5000` no navegador
2. Selecione uma campanha no dropdown
3. Visualize as subpastas encontradas
4. Clique em "Gerar CSVs" para criar os arquivos

## ⚙️ Como Funciona

### Leitura de Campanhas
- O sistema lê automaticamente as pastas do diretório configurado
- Mostra todas as campanhas disponíveis em um dropdown

### Geração de CSVs
- Para cada campanha selecionada, gera 4 arquivos CSV:
  - `{campanhaEmCamelCase}_abertura.csv`
  - `{campanhaEmCamelCase}_bg.csv`
  - `{campanhaEmCamelCase}_assinatura.csv`
  - `{campanhaEmCamelCase}_trilha.csv`

### URLs do Firebase
- Cada CSV contém URLs formatadas para o Firebase Storage
- Os buckets são mapeados conforme as categorias:
  - `abertura` → bucket `cabeca`
  - `bg` → bucket `bg`
  - `assinatura` → bucket `assinatura`
  - `trilha` → bucket `trilha`

### Exemplo de URL Gerada
```
https://firebasestorage.googleapis.com/v0/b/geofast-38b6b.appspot.com/o/cabeca%2FCabSuperPromoAgostoSp16x9.mp4?alt=media&token=7d2e4acc-15fa-46f0-9d3d-7b026db1f96b
```

## 📊 Estrutura dos CSVs

Cada CSV contém as seguintes colunas:
- `campaign`: Nome original da campanha
- `category`: Categoria (abertura, bg, assinatura, trilha)
- `bucket`: Nome do bucket no Firebase
- `url`: URL completa do arquivo no Firebase
- `filename`: Nome do arquivo CSV

## 🔧 Configurações

### Alterar Diretório de Campanhas
Edite a variável `CAMPAIGNS_DIR` no arquivo `backend/app.py`:

```python
CAMPAIGNS_DIR = r"SEU_CAMINHO_AQUI"
```

### Alterar URLs do Firebase
Modifique a função `get_firebase_url()` para ajustar:
- Base URL do Firebase
- Padrões de nomenclatura dos arquivos
- Tokens de acesso

## 🛡️ Segurança

- ✅ O sistema **NUNCA** altera ou apaga arquivos das pastas originais
- ✅ Apenas **LÊ** os nomes das campanhas
- ✅ CSVs são salvos localmente na pasta `exportados/`
- ✅ Não há upload ou modificação no Firebase

## 🐛 Solução de Problemas

### Erro "Directory not found"
Verifique se o caminho em `CAMPAIGNS_DIR` está correto e acessível.

### Erro de Permissões
Execute o terminal como administrador ou verifique as permissões da pasta.

### Porta 5000 ocupada
Altere a porta no final do arquivo `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Mude para 5001
```

## 📝 Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5 + Bootstrap 5 + JavaScript
- **Dados**: Pandas para CSV
- **Estilo**: CSS3 com gradientes