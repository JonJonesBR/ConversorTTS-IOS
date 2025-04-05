# Conversor de Texto para Voz para iPhone 📲🔊

Conversor otimizado para iOS que transforma arquivos TXT/PDF em áudio MP3 usando o terminal a-Shell.

![Demonstração](https://via.placeholder.com/800x400.png?text=Demo+do+Conversor+TTS)

## 📋 Pré-requisitos
- iPhone/iPad com iOS 15+
- Aplicativo [a-Shell](https://apps.apple.com/br/app/a-shell/id1543537943)
- 50MB de espaço livre

## 🚀 Instalação Passo-a-Passo

### 1. Preparação Inicial
1. Abra o a-Shell
2. Toque no ícone ⚙️ > Advanced > Enable File Access > Permitir

### 2. Clonar Repositório
```bash
git clone https://github.com/JonJonesBR/ConversorTTS-iOS.git
cd ConversorTTS-iOS
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Criar Pasta Visível
```bash
touch arquivo_exemplo.txt
```

### 5. Adicionar Arquivos
1. Abra o app Arquivos do seu iPhone
2. Navegue até "a-Shell" > "ConversorTTS-iOS"
3. Segure o dedo nessa pasta e cole os arquivos pdfs ou txt que voce copiou de outra pasta

## 🎮 Como Usar
```bash
python TTS_IPHONE_03.py
```

**Fluxo de Uso:**
1. Selecione a opção 1 no menu
2. Escolha seu arquivo (D=Pastas, M=Caminho manual)
3. Selecione uma voz (1-3)
4. Aguarde a conversão (⏱️ 1-5 minutos por página)
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
```

### Link de Download Direto para Usuários:
`https://github.com/JonJonesBR/ConversorTTS-iOS/archive/refs/heads/main.zip`
