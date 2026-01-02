# 🤖 Automação ASSAI - FEIRASSAI

Sistema para processar campanhas FEIRASSAI diretamente do Google Drive e gerar JSONs/CSVs automaticamente.

## 🚀 **Novidades**

### ✨ **Acesso Direto ao Google Drive**
- O sistema agora acessa diretamente: `G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS\ANIVERSARIO FEIRASSAI`
- Não precisa mais de localhost ou arquivos locais

### 📁 **Estrutura Suportada**
O sistema processa automaticamente:
- **CABECA** → `abertura` (com períodos: 3ª e 4ª, 4ª e 5ª, 6ª e Sab)
- **ASSINATURA** → `assinatura` (com períodos e regiões)
- **BG** → `bg` (placeholder para futura implementação)
- **TRILHA** → `trilha` (placeholder para futura implementação)

## 🔧 **Como Usar**

### 1. **Iniciar o Sistema**
```bash
cd backend
python app.py
```

### 2. **Acessar o Front-end**
Abra no navegador: `http://localhost:5000`

### 3. **Gerar JSONs FEIRASSAI**
- Clique no botão verde **"Gerar JSONs FEIRASSAI (Google Drive)"**
- O sistema vai:
  1. Acessar o Google Drive automaticamente
  2. Escanear todas as pastas CABECA e ASSINATURA
  3. Gerar JSONs individuais por categoria
  4. Criar um JSON completo consolidado

## 📄 **Arquivos Gerados**

### **JSONs Individuais:**
- `feirassai_abertura.json` - Todos os vídeos de abertura/cabeça
- `feirassai_assinatura.json` - Todos os vídeos de assinatura/encerramento
- `feirassai_bg.json` - Backgrounds (quando disponível)
- `feirassai_trilha.json` - Trilhas sonoras (quando disponível)

### **JSON Completo:**
- `feirassai_complete.json` - Consolidado com todas as categorias

### **Local dos Arquivos:**
📁 `C:\Users\Mauro\.cursor\automacaoAssai\exportados\`

## 🎯 **Formato JSON**

Cada entrada contém:
```json
{
  "ligacaoCampanhaFieldName": "feirassai",
  "locucaoTranscrita": "",
  "nameFile": "cabFeirassaiTercaeQuarta1x1.mp4",
  "OS Formato modelo": "1x1",
  "urlFile": "https://firebasestorage.googleapis.com/...",
  "Creation Date": "Sep 23, 2025 04:29 PM",
  "periodo": "3a e 4a",
  "regiao": "CABECA NACIONAL"
}
```

## 📊 **Formatos Detectados Automaticamente**
- **1x1** → Social Media (Instagram/Facebook posts)
- **9x16** → Stories (Instagram/TikTok)
- **16x9** → TV/YouTube

## 🔄 **Funcionalidades Anteriores**
O sistema mantém todas as funcionalidades anteriores:
- Geração de CSVs para campanhas locais
- Suporte a campanhas regionais
- Interface web amigável

## 🎉 **Resultado**
Agora você tem acesso direto às campanhas FEIRASSAI do Google Drive com geração automática de JSONs estruturados para uso na automação do ASSAI!