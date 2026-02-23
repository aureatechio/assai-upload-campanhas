# Documentacao do repositorio automacaoAssai

## Objetivo
Este repositorio automatiza a leitura de midias de campanhas e gera arquivos CSV/JSON com URLs do Firebase para uso em automacoes internas da Assai. O fluxo principal roda via uma API Flask com uma interface web simples.

## Estrutura geral
```
automacaoAssai/
  backend/               # API Flask e regras de geracao
    app.py               # Rotas e logica principal
    requirements.txt     # Dependencias Python
  frontend/              # Interface web
    index.html
  exportados/            # Saida dos CSVs/JSONs gerados
  campanhas_aniversario/ # Dados locais de campanhas (quando usados)
  exemplos/              # Exemplos de insumo/saida
  gerar_*.py             # Scripts pontuais para campanhas especificas
  processar_*.py         # Scripts de tratamento/formatacao
  fix_*.py               # Correcoes em CSVs e campos
  converter_*.py         # Conversoes de formato
  run.bat                # Atalho para iniciar o servidor
```

## Fluxo principal (API + UI)
1. O backend lista as campanhas a partir de um diretorio configurado em `backend/app.py` (`CAMPAIGNS_DIR`).
2. O usuario escolhe uma campanha na UI (`frontend/index.html`).
3. O backend escaneia subpastas (CABECAS, BG, ASSINATURAS, TRILHA) e gera CSVs em `exportados/`.
4. As URLs apontam para o Firebase Storage com base em `get_firebase_url()`.

### Estrutura de pastas esperada (padrao)
```
<CAMPAIGNS_DIR>/
  NOME_DA_CAMPANHA/
    CABECAS/
    BG/
    ASSINATURAS/
    TRILHA/
```
Arquivos aceitos: `.mp4`, `.mp3`, `.wav`.

### Campanhas regionais
Para campanhas regionais, o backend assume uma estrutura com estados em `CABECAS` e subpastas especificas em `BG` e `ASSINATURAS`:
```
NOME_DA_CAMPANHA/
  CABECAS/
    MG/
    SP/
    ...
  BG/
    MG/
    NACIONAL/
  ASSINATURAS/
    MG/
    NACIONAL/
  TRILHA/
```
No modo regional, o CSV de abertura gera uma linha por arquivo; BG/ASSINATURA/TRILHA consolidam os nomes das campanhas em uma unica coluna.

## Arquivos gerados
Para cada campanha, o backend cria CSVs com o padrao:
```
<campanhaCamelCase>_abertura.csv
<campanhaCamelCase>_bg.csv
<campanhaCamelCase>_assinatura.csv
<campanhaCamelCase>_trilha.csv
```
Quando regional, tambem gera:
```
<campanhaCamelCase>_campanhas.csv
```

### Colunas principais dos CSVs
- `ligacaoCampanhaFieldName`
- `locucaoTranscrita`
- `nameFile`
- `OS Formato modelo`
- `urlFile`
- `Creation Date`

Colunas adicionais por categoria:
- BG: `formatoMidia`, `Modified Date`
- ASSINATURA: `Modified Date`
- TRILHA: `Modified Date`, `Slug`, `Creator`

## Fluxo FEIRASSAI (JSON + CSV)
Existe um fluxo separado para campanhas FEIRASSAI que le dados diretamente do Google Drive e gera:
- `feirassai_abertura.json`
- `feirassai_assinatura.json`
- `feirassai_bg.json`
- `feirassai_trilha.json`
- `feirassai_complete.json`
- `feirassai_form_campanha.csv`

Esse fluxo e disparado pela rota `POST /api/generate-feirassai-json` e usa o mesmo `CAMPAIGNS_DIR`.

## Como executar
Requisitos: Python 3.10+ e acesso ao drive configurado.

Opcao 1 - via script:
```bash
.\run.bat
```

Opcao 2 - manual:
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Depois acesse `http://localhost:5000`.

## Scripts auxiliares (root)
Ha diversos scripts `gerar_*.py`, `processar_*.py`, `fix_*.py` e `converter_*.py` usados para necessidades especificas de campanha ou limpeza de CSVs. Eles podem ser executados diretamente com `python <script>.py` e costumam ler/escrever arquivos em `exportados/`.

## Configuracao importante
- `backend/app.py`:
  - `CAMPAIGNS_DIR`: caminho base das campanhas.
  - `EXPORT_DIR`: pasta de saida.
  - `get_firebase_url()`: base URL e token do Firebase.

## Garantias
- O sistema apenas le midias no drive e escreve novos arquivos em `exportados/`.
- Nao altera nem apaga arquivos originais.
