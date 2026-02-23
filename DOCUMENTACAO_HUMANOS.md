# Documentacao para humanos (processo de campanha)

## O que este repositorio faz
Gera CSVs com dados de campanhas e envia as midias para o Supabase, trocando as URLs (antes eram Firebase). Depois sobe os CSVs no Bubble.

## Passo a passo resumido
1) Gerar CSVs da campanha.
2) Subir midias para o Supabase (bucket publico).
3) Atualizar URLs nos CSVs.
4) Subir CSVs no Bubble (teste e depois producao).

## 1) Gerar CSVs
Exemplo para campanha 30.01:
```
python gerar_dia_imbativel_3001.py
```
Os CSVs sao criados em `exportados/`.

## 2) Subir midias no Supabase
Script: `upload_supabase_midias.py`

Configure o token:
```
$env:SUPABASE_SERVICE_ROLE='SEU_TOKEN'
python upload_supabase_midias.py --apply
```
Isso:
- cria/usa o bucket `assai-midias`,
- envia midias para `campanhas/<slug>/<categoria>/...`,
- atualiza os CSVs com URLs do Supabase.

## 3) Ajustar thumbs no formCampanha
O campo `imagem` do CSV `formCampanha` precisa apontar para o THUMB no Supabase.
Para a campanha 30.01 isso foi feito automaticamente.

## 4) Subir CSVs no Bubble
Script: `bubble_upload_csvs.py`

Teste:
```
$env:BUBBLE_API_TOKEN='SEU_TOKEN'
python bubble_upload_csvs.py --campaign-slug dia-imbativel-30-01 --apply --base-url https://assai.geofast.ai/version-test/api/1.1/obj
```

Producao:
```
$env:BUBBLE_API_TOKEN='SEU_TOKEN'
python bubble_upload_csvs.py --campaign-slug dia-imbativel-30-01 --apply --base-url https://assai.geofast.ai/api/1.1/obj
```

## Estrutura de URLs no Supabase
Exemplo:
```
https://xhzgscezaaekbaqrkddu.supabase.co/storage/v1/object/public/assai-midias/campanhas/dia-imbativel-30-01/cabeca/...
```

## Campos importantes
- Midias: `ligacaoCampanhaFieldName`, `nameFile`, `urlFile`.
- Form: `option`, `optionSheet`, `imagem`, `OS materiais`, `OS type midia`.

## Cuidados
- Nunca salvar tokens em arquivos.
- Sempre verificar se as URLs do CSV sao do Supabase antes do upload no Bubble.
- O Bubble cria registros novos (POST). Pode haver duplicados se subir mais de uma vez.

## Onde estao os arquivos
- CSVs: `exportados/`
- Scripts: raiz do repositorio
