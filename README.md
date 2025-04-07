# Conversor de Texto para Voz para iPhone 📲🔊

Conversor otimizado para iOS que transforma arquivos TXT/PDF em áudio MP3 usando o terminal a-Shell.

## 📋 Pré-requisitos

- iPhone/iPad
  
- Aplicativo [a-Shell](https://apps.apple.com/br/app/a-shell/id1543537943)
 
- 50MB de espaço livre

## 🚀 Instalação Passo-a-Passo

### 1. Preparação Inicial

1. Abra o a-Shell

### 2. Baixar e Extrair:  

   ```bash
   curl -LO https://github.com/JonJonesBR/ConversorTTS-iOS/archive/refs/heads/main.zip
```
  ```bash
   python -c "import zipfile; zipfile.ZipFile('main.zip', 'r').extractall()"
```
  ```bash
   cd ConversorTTS-IOS-main
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Adicionar Arquivos PDF ou TXT para converter em voz

1. Abra o app Arquivos do seu iPhone

2. Navegue até "a-Shell"

3. Segure o dedo nessa pasta e cole os arquivos pdfs ou txt que voce copiou de outra pasta

## 🎮 Como Usar

```bash
python TTS_IPHONE_03.py
```

**Fluxo de Uso:**

1. Selecione a opção 1 no menu
   
2. Escolha seu arquivo (Deve estar listado)
   
3. Selecione uma voz (1-3)
   
4. Aguarde a conversão (⏱️ normalmente de 1-5 minutos por página, mas pode demorar mais ou menos, dependendo do livro a ser convertido)

5. Encontre o áudio em: `No Meu Iphone/a-Shell/`

## ❓ Ajuda Comum

```markdown
Q: Não consigo ver meus arquivos!
R: Execute `touch visivel.txt` e espere 1 minuto antes de verificar

Q: Erro de instalação!
R: Execute `pip install --force-reinstall -r requirements.txt`

Q: Como parar a conversão?
R: Digite `sair` durante qualquer operação
```

## 📄 Licença
MIT License - Livre para uso e modificação

## Link de Download Direto:
`https://github.com/JonJonesBR/ConversorTTS-iOS/archive/refs/heads/main.zip`
