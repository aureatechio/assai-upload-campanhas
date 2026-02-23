# Documentacao tecnica para IA (automacaoAssai)

## Objetivo
Esta documentacao guia agentes de IA para gerar CSVs de campanhas, subir midias no Supabase Storage e publicar os dados no Bubble Data API, mantendo os CSVs como fonte de verdade para URLs.

## Conceitos principais
- **CSV gerado**: base para upload no Bubble. O campo `urlFile` deve apontar para Supabase (nao Firebase).
- **Supabase Storage**: bucket publico `assai-midias` com paths padronizados por campanha/categoria.
- **Bubble Data API**: recebe linhas dos CSVs; certos campos precisam de transformacao.

## Estrutura de pastas esperada
Exemplo (campanha Dia Imbativel 30.01):
```
G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\DIA IMBATIVEL 30.01\
  CABECA\EH HOJE\CABECA\NACIONAL|MG\
  CABECA\EH AMANHA\CABECA\NACIONAL|MG\
  CABECA\GENERICO\CABECA\NACIONAL|MG\
  ENCERRAMENTO\EH HOJE\ENCERRAMENTO\NACIONAL|MG\
  ENCERRAMENTO\EH AMANHA\ENCERRAMENTO\NACIONAL|MG\
  ENCERRAMENTO\GENERICO\ENCERRAMENTO\NACIONAL|MG\
  BG\NAC|MG\
  TRILHA\
  THUMB\
```

## Scripts principais
- `gerar_dia_imbativel_1601.py`
- `gerar_dia_imbativel_3001.py`
- `upload_supabase_midias.py`
- `bubble_upload_csvs.py`

## Geracao de CSVs
Exemplo para 30.01:
```
python gerar_dia_imbativel_3001.py
```
Saidas em `exportados/`:
- `export_All-mCabecas-<slug>.csv`
- `export_All-mAssinaturas-<slug>.csv`
- `export_All-mBackground-<slug>.csv`
- `export_All-mTrilhas-<slug>.csv`
- `export_All-formCampanhas-<slug>-<timestamp>.csv`

## Supabase Storage (upload e substituicao das URLs)
Script: `upload_supabase_midias.py`

### Variaveis
- `SUPABASE_SERVICE_ROLE`: token **nao** deve ser versionado.
- bucket: `assai-midias` (publico)

### Estrutura de objetos
```
campanhas/<slug>/<categoria>/<subpastas>/<arquivo>
```
Categorias: `cabeca`, `assinatura`, `background`, `trilha`, `thumb`

### Execucao
```
$env:SUPABASE_SERVICE_ROLE='SEU_TOKEN'
python upload_supabase_midias.py --apply
```
Opcoes:
- `--category background` (restrito)
- `--category thumb --no-csv` (thumb nao altera CSV)

### Observacoes
- Para arquivos >50MB, o script usa TUS (resumable upload).
- `THUMB` renomeia arquivos com caracteres invalidos.
- O script atualiza `urlFile` nos CSVs das categorias de midia.

## Bubble Data API (upload)
Script: `bubble_upload_csvs.py`

### Variaveis
- `BUBBLE_API_TOKEN` (nao versionar)
- Base URL teste: `https://assai.geofast.ai/version-test/api/1.1/obj`
- Base URL prod: `https://assai.geofast.ai/api/1.1/obj`

### Mapeamento de tabelas
- `export_All-mCabecas-*.csv` -> `mCabeca`
- `export_All-mAssinaturas-*.csv` -> `mAssinatura`
- `export_All-mBackground-*.csv` -> `mBackgroundOferta`
- `export_All-mTrilhas-*.csv` -> `mTrilha`
- `export_All-formCampanhas-*.csv` -> `formCampanha`

### Transformacoes de campos
- `Creation Date` removido.
- `ativo` -> boolean.
- `ligacaoCampanhaFieldName` -> lista em `mAssinatura`, `mBackgroundOferta`, `mTrilha`.
- `locucaoTranscrita` e `OS Formato modelo` removidos em `mBackgroundOferta` e `mTrilha`.
- `mTrilha` usa campo `nameFIle` (I maiusculo) no Bubble.
- `formCampanha.ajusteCampanha` fixo em `AJUSTE_CAMPANHA_ID` no script.
- `OS materiais` e `OS type midia` sao listas com acentos corretos.

### Execucao (teste)
```
$env:BUBBLE_API_TOKEN='SEU_TOKEN'
python bubble_upload_csvs.py --campaign-slug dia-imbativel-30-01 --apply --base-url https://assai.geofast.ai/version-test/api/1.1/obj
```

### Execucao (prod)
```
$env:BUBBLE_API_TOKEN='SEU_TOKEN'
python bubble_upload_csvs.py --campaign-slug dia-imbativel-30-01 --apply --base-url https://assai.geofast.ai/api/1.1/obj
```

### Duplicidade
O Bubble usa POST, entao cria duplicados. Se precisar, criar modo de update/limpeza por `nameFile`/`optionSheet`.

## Fluxo recomendado (fim a fim)
1) Gerar CSVs.
2) Subir midias no Supabase e atualizar URLs nos CSVs.
3) Ajustar `imagem` do `formCampanha` para o thumb do Supabase.
4) Subir CSVs no Bubble (teste).
5) Subir CSVs no Bubble (producao).

## Campos importantes nos CSVs
- Midias: `ligacaoCampanhaFieldName`, `nameFile`, `urlFile`, `OS Formato modelo`, `locucaoTranscrita`, `Creation Date`.
- Form: `ajusteCampanha`, `ativo`, `option`, `optionSheet`, `OS materiais`, `OS type midia`, `imagem`.

## Cuidados
- Nunca versionar tokens.
- Sempre confirmar URLs do Supabase nos CSVs antes de subir no Bubble.
- Ao renomear THUMB, atualizar `imagem` no `formCampanha`.
