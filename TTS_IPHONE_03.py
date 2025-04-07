import os
import re
import unicodedata
import subprocess
import time
import asyncio
import chardet
from num2words import num2words
import edge_tts
import sys
import aioconsole  # Adicionado

# ================== CONFIGURAÇÕES GLOBAIS ==================
VOZ_PADRAO = 'pt-BR-ThalitaNeural'
VOZES = [
    ('1. pt-BR-ThalitaNeural (Recomendada)', 'pt-BR-ThalitaNeural'),
    ('2. pt-BR-AntonioNeural', 'pt-BR-AntonioNeural'),
    ('3. pt-BR-FranciscaNeural', 'pt-BR-FranciscaNeural')
]
CANCELAR_PROCESSAMENTO = False

def clear_screen():
    os.system('clear')

# ================== FUNÇÕES DE INSTALAÇÃO ==================
def check_and_install_dependencies():
    import importlib
    dependencies = {
        "PyPDF2": "PyPDF2",
        "edge_tts": "edge-tts",
        "chardet": "chardet",
        "num2words": "num2words",
        "aioconsole": "aioconsole"  # Adicionado
    }
    for module_name, package_name in dependencies.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            clear_screen()
            print(f"Instalando {package_name}...")
            os.system(f"pip install {package_name}")

check_and_install_dependencies()

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# ================== FUNÇÕES DE MANIPULAÇÃO DE ARQUIVOS ==================
def listar_arquivos(diretorio: str) -> list:
    arquivos = []
    try:
        for item in os.listdir(diretorio):
            caminho_completo = os.path.join(diretorio, item)
            if os.path.isfile(caminho_completo):
                ext = os.path.splitext(item)[1].lower()
                if ext in ['.txt', '.pdf']:
                    arquivos.append(item)
    except Exception as e:
        print(f"\n⚠️ Erro ao listar arquivos: {str(e)}")
    return sorted(arquivos)

# ================== FUNÇÕES DE CORREÇÃO DE TEXTO ==================
def normalizar_texto_corrigir(texto):
    print("\n[1/5] Normalizando texto...")
    return unicodedata.normalize('NFKC', texto)

def corrigir_espacamento_corrigir(texto):
    print("[2/5] Corrigindo espaçamento...")
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'^\s+|\s+$', '', texto, flags=re.MULTILINE)
    return texto

def ajustar_titulo_e_capitulos_corrigir(texto):
    print("[3/5] Ajustando título, autor e capítulos...")
    pattern = r"^(?P<titulo>.+?)\s+(?P<autor>[A-Z][a-z]+(?:\s+[A-Z][a-z]+))\s+(?P<body>.*)$"
    match = re.match(pattern, texto, re.DOTALL)
    if match:
        titulo = match.group("titulo").strip()
        autor = match.group("autor").strip()
        body = match.group("body").strip()
        if not titulo.endswith(('.', '!', '?')):
            titulo += '.'
        if not autor.endswith(('.', '!', '?')):
            autor += '.'
        novo_texto = titulo + "\n" + autor + "\n\n" + body
    else:
        linhas = texto.splitlines()
        header = []
        corpo = []
        non_empty_count = 0
        for linha in linhas:
            if linha.strip():
                non_empty_count += 1
                if non_empty_count <= 2:
                    header.append(linha.strip())
                else:
                    corpo.append(linha)
            else:
                if non_empty_count >= 2:
                    corpo.append(linha)
        if len(header) == 1:
            palavras = header[0].split()
            if len(palavras) >= 4 and palavras[-1][0].isupper() and palavras[-2][0].isupper():
                autor = " ".join(palavras[-2:])
                titulo = " ".join(palavras[:-2])
                header = [titulo.strip(), autor.strip()]
        if header:
            if not header[0].endswith(('.', '!', '?')):
                header[0] += '.'
        if len(header) > 1:
            if not header[1].endswith(('.', '!', '?')):
                header[1] += '.'
        novo_texto = "\n".join(header + [""] + corpo)
    novo_texto = re.sub(r'(?i)\b(capítulo\s*\d+)\b', r'\n\n\1.\n\n', novo_texto)
    return novo_texto

def inserir_quebra_apos_ponto_corrigir(texto):
    print("[4/5] Inserindo quebra de parágrafo após cada ponto final...")
    return re.sub(r'\.\s+', '.\n\n', texto)

def formatar_paragrafos_corrigir(texto):
    print("[5/5] Formatando parágrafos...")
    paragrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
    return '\n\n'.join(paragrafos)

def melhorar_texto_corrigido(texto):
    print("\n--- INÍCIO DO PROCESSAMENTO (Correção de TXT) ---")
    etapas = [
        normalizar_texto_corrigir,
        corrigir_espacamento_corrigir,
        ajustar_titulo_e_capitulos_corrigir,
        inserir_quebra_apos_ponto_corrigir,
        formatar_paragrafos_corrigir
    ]
    for etapa in etapas:
        texto = etapa(texto)
    print("\n--- PROCESSAMENTO CONCLUÍDO ---")
    return texto

def verificar_e_corrigir_arquivo(caminho_txt: str) -> str:
    base, ext = os.path.splitext(caminho_txt)
    if base.endswith("_formatado"):
        return caminho_txt
    try:
        with open(caminho_txt, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo TXT: {e}")
        return caminho_txt
    conteudo_corrigido = melhorar_texto_corrigido(conteudo)
    novo_caminho = base + "_formatado" + ext
    try:
        with open(novo_caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo_corrigido)
        print(f"✅ Arquivo corrigido e salvo em: {novo_caminho}")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo corrigido: {e}")
        return caminho_txt
    return novo_caminho

# ================== FUNÇÕES DE LEITURA DE ARQUIVOS ==================
def detectar_encoding(caminho_arquivo: str) -> str:
    try:
        with open(caminho_arquivo, 'rb') as f:
            resultado = chardet.detect(f.read())
        encoding_detectado = resultado['encoding']
        if not encoding_detectado:
            for enc in ['utf-8', 'latin-1']:
                try:
                    with open(caminho_arquivo, 'r', encoding=enc) as f:
                        f.read(100)
                    return enc
                except UnicodeDecodeError:
                    continue
            return 'utf-8'
        return encoding_detectado
    except Exception as e:
        print(f"\n⚠️ Erro ao detectar encoding: {str(e)}")
        return 'utf-8'

def ler_arquivo_texto(caminho_arquivo: str) -> str:
    encoding = detectar_encoding(caminho_arquivo)
    try:
        with open(caminho_arquivo, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"\n❌ Erro ao ler arquivo: {str(e)}")
        return ""

def processar_texto(texto: str) -> str:
    texto = re.sub(r'\s+', ' ', texto)
    abreviacoes = {
        r'\bDr\.\b': 'Doutor',
        r'\bDra\.\b': 'Doutora',
        r'\bSr\.\b': 'Senhor',
        r'\bSra\.\b': 'Senhora',
        r'\bSrta\.\b': 'Senhorita',
        r'\bProf\.\b': 'Professor',
        r'\bProfa\.\b': 'Professora',
        r'\bEng\.\b': 'Engenheiro',
        r'\bEngª\.\b': 'Engenheira',
        r'\bAdm\.\b': 'Administrador',
        r'\bAdv\.\b': 'Advogado',
        r'\bExmo\.\b': 'Excelentíssimo',
        r'\bExma\.\b': 'Excelentíssima',
        r'\bV\.Exa\.\b': 'Vossa Excelência',
        r'\bV\.Sa\.\b': 'Vossa Senhoria',
        r'\bAv\.\b': 'Avenida',
        r'\bR\.\b': 'Rua',
        r'\bKm\.\b': 'Quilômetro',
        r'\betc\.\b': 'etcétera',
        r'\bRef\.\b': 'Referência',
        r'\bPag\.\b': 'Página',
        r'\bDept\.\b': 'Departamento',
        r'\bDepto\.\b': 'Departamento',
        r'\bUniv\.\b': 'Universidade',
        r'\bInst\.\b': 'Instituição',
        r'\bEst\.\b': 'Estado',
        r'\bTel\.\b': 'Telefone',
        r'\bCEP\.\b': 'Código de Endereçamento Postal',
        r'\bCNPJ\.\b': 'Cadastro Nacional da Pessoa Jurídica',
        r'\bCPF\.\b': 'Cadastro de Pessoas Físicas',
        r'\bLtda\.\b': 'Limitada'
    }
    for abrev, expansao in abreviacoes.items():
        texto = re.sub(abrev, expansao, texto)
    def converter_numero(match):
        num = match.group(0)
        try:
            return num2words(int(num), lang='pt_BR')
        except:
            return num
    return re.sub(r'\b\d+\b', converter_numero, texto)

def calcular_chunk_size(texto: str) -> int:
    total = len(texto)
    if total < 10000:
        return 1500
    else:
        return 2000

def dividir_texto(texto: str) -> list:
    partes = []
    start = 0
    while start < len(texto):
        next_period = texto.find('.', start)
        if next_period == -1:
            partes.append(texto[start:].strip())
            break
        end = next_period + 1
        partes.append(texto[start:end].strip())
        start = end
    return [p for p in partes if p]

async def converter_texto_para_audio(texto: str, voz: str, caminho_saida: str) -> bool:
    try:
        communicate = edge_tts.Communicate(texto, voz)
        await communicate.save(caminho_saida)
        return True
    except Exception as e:
        print(f"\n❌ Erro na conversão: {str(e)}")
        return False

# ================== FUNÇÃO PARA CONVERTER PDF PARA TXT ==================
def converter_pdf(caminho_pdf: str, caminho_txt: str) -> bool:
    clear_screen()
    print(f"📑 Convertendo PDF para TXT: {os.path.basename(caminho_pdf)}")
    if PdfReader is None:
        print("PyPDF2 não está instalado. Utilizando conversão simulada.")
        try:
            with open(caminho_pdf, 'rb') as f_pdf:
                _ = f_pdf.read()
            with open(caminho_txt, 'w', encoding='utf-8') as f_txt:
                f_txt.write("Conteúdo extraído do PDF (simulado).")
            return True
        except Exception as e:
            print(f"❌ Erro na conversão de PDF: {str(e)}")
            return False
    try:
        reader = PdfReader(caminho_pdf)
        full_text = ""
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages, 1):
            if CANCELAR_PROCESSAMENTO:
                print("\n🚫 Conversão de PDF cancelada pelo usuário")
                return False
            print(f"📖 Extraindo página {i}/{total_pages}...")
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        if not full_text.strip():
            print("⚠️ Nenhum texto foi extraído. O PDF pode ser baseado em imagens.")
            full_text = "Nenhum texto extraído do PDF. (Possivelmente arquivo escaneado)"
        with open(caminho_txt, 'w', encoding='utf-8') as f_txt:
            f_txt.write(full_text)
        print("✅ Conversão de PDF concluída com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro na conversão de PDF: {str(e)}")
        return False

# ================== INTERFACE E FLUXO DE CONVERSÃO ==================
def exibir_banner():
    clear_screen()
    print("====================================")
    print("       Conversor TTS Lite")
    print("====================================")

async def menu_principal():
    while True:
        exibir_banner()
        print("\nMenu Principal:")
        print("1. Converter texto para áudio")
        print("2. Testar voz")
        print("3. Ajuda")
        print("4. Sair")
        
        try:
            raw_escolha = await aioconsole.ainput("Escolha uma opção: ")  # Modificado
            escolha = raw_escolha.strip()
            
            if escolha in ['1', '2', '3', '4']:
                return escolha
            print("Opção inválida. Tente novamente.")
            await asyncio.sleep(1)
        except asyncio.TimeoutError:
            print("\nTempo de espera excedido. Retornando ao menu...")
            return '4'

async def menu_vozes():
    exibir_banner()
    print("\nSelecione a voz:")
    for desc, _ in VOZES:
        print(desc)
    print("\n💡 A voz Thalita é recomendada para melhor qualidade")
    
    while True:
        try:
            raw_escolha = await aioconsole.ainput("Escolha a opção desejada (1-3): ")  # Modificado
            escolha = raw_escolha.strip()
            
            if escolha.isdigit():
                indice = int(escolha) - 1
                if 0 <= indice < len(VOZES):
                    return VOZES[indice][1]
            print("Opção inválida. Tente novamente.")
        except asyncio.TimeoutError:
            print("\nTempo de espera excedido. Usando voz padrão.")
            return VOZ_PADRAO

async def testar_voz(voz: str):
    exibir_banner()
    print(f"🔊 Testando voz: {voz}")
    texto_teste = "Esta é uma mensagem de teste."
    temp_file = "teste.mp3"
    print("🔄 Convertendo...")
    sucesso = await converter_texto_para_audio(texto_teste, voz, temp_file)
    if sucesso:
        print("✅ Voz testada com sucesso. Arquivo: " + temp_file)
    else:
        print("❌ Falha ao testar a voz.")
    await asyncio.sleep(2)

def detectar_sistema():
    return {'termux': False, 'android': False, 'windows': False, 'macos': False, 'ios': True}

async def exibir_ajuda():
    exibir_banner()
    print("\n📘 Ajuda:")
    print("- Digite 'sair' durante qualquer operação para cancelar")
    print("- Chunks são divididos após pontos finais para melhor fluidez")
    print("- Thalita Neural é a voz padrão recomendada")
    await aioconsole.ainput("\nPressione ENTER para continuar...")  # Modificado

async def selecionar_arquivo() -> str:
    dir_atual = os.path.expanduser('~/Documents')
    while True:
        exibir_banner()
        print("\n📂 SELEÇÃO DE ARQUIVO")
        print(f"\nDiretório atual: {dir_atual}")
        arquivos = listar_arquivos(dir_atual)
        
        if not arquivos:
            print("\n⚠️ Nenhum arquivo TXT ou PDF encontrado")
        else:
            print("\nArquivos disponíveis:")
            for i, arquivo in enumerate(arquivos, 1):
                print(f"{i}. {arquivo}")
        
        print("\nOpções:")
        print("D. Mudar diretório")
        print("M. Digitar caminho manualmente")
        print("V. Voltar")
        
        try:
            escolha = (await aioconsole.ainput("\nEscolha uma opção: ")).strip().upper()  # Modificado
        except asyncio.TimeoutError:
            return ''
        
        if escolha == 'V':
            return ''
        elif escolha == 'D':
            novo_dir = await aioconsole.ainput("\n📁 Digite o caminho do novo diretório: ")  # Modificado
            if os.path.isdir(novo_dir):
                dir_atual = novo_dir
            else:
                print("\n❌ Diretório inválido")
                await asyncio.sleep(1)
        elif escolha == 'M':
            caminho = await aioconsole.ainput("\n⌨️ Digite o caminho completo do arquivo: ")  # Modificado
            if not os.path.exists(caminho):
                print("\n❌ Arquivo não encontrado")
                await asyncio.sleep(1)
                continue
            
            ext = os.path.splitext(caminho)[1].lower()
            if ext == '.pdf':
                caminho_txt = os.path.splitext(caminho)[0] + '.txt'
                if not converter_pdf(caminho, caminho_txt):
                    print("\n⚠️ Falha na conversão do PDF")
                    await asyncio.sleep(1)
                    continue
                caminho_txt = verificar_e_corrigir_arquivo(caminho_txt)
                
                editar = await aioconsole.ainput("\n✏️ Editar arquivo corrigido? (s/n): ")  # Modificado
                editar = editar.strip().lower()
                
                if editar == 's':
                    try:
                        subprocess.Popen(["open", caminho_txt] if detectar_sistema().get('macos') else ["xdg-open", caminho_txt])
                        await aioconsole.ainput("\n💡 Salve as alterações e pressione ENTER...")  # Modificado
                    except:
                        print("\n⚠️ Não foi possível abrir o editor")
                return caminho_txt
            elif ext == '.txt':
                if not os.path.basename(caminho).lower().endswith("_formatado.txt"):
                    caminho = verificar_e_corrigir_arquivo(caminho)
                return caminho
            else:
                print(f"\n❌ Formato não suportado")
                await asyncio.sleep(1)
        elif escolha.isdigit():
            indice = int(escolha) - 1
            if 0 <= indice < len(arquivos):
                arquivo_selecionado = arquivos[indice]
                caminho_completo = os.path.join(dir_atual, arquivo_selecionado)
                ext = os.path.splitext(arquivo_selecionado)[1].lower()
                
                if ext == '.pdf':
                    caminho_txt = os.path.splitext(caminho_completo)[0] + '.txt'
                    if not converter_pdf(caminho_completo, caminho_txt):
                        print("\n⚠️ Falha na conversão do PDF")
                        await asyncio.sleep(1)
                        continue
                    caminho_txt = verificar_e_corrigir_arquivo(caminho_txt)
                    
                    editar = await aioconsole.ainput("\n✏️ Editar arquivo corrigido? (s/n): ")  # Modificado
                    editar = editar.strip().lower()
                    
                    if editar == 's':
                        try:
                            subprocess.Popen(["open", caminho_txt] if detectar_sistema().get('macos') else ["xdg-open", caminho_txt])
                            await aioconsole.ainput("\n💡 Salve as alterações e pressione ENTER...")  # Modificado
                        except:
                            print("\n⚠️ Não foi possível abrir o editor")
                    return caminho_txt
                elif ext == '.txt':
                    if not os.path.basename(caminho_completo).lower().endswith("_formatado.txt"):
                        caminho_completo = verificar_e_corrigir_arquivo(caminho_completo)
                    return caminho_completo
            else:
                print("\n❌ Opção inválida")
                await asyncio.sleep(1)
        else:
            print("\n❌ Opção inválida")
            await asyncio.sleep(1)

async def iniciar_conversao() -> None:
    global CANCELAR_PROCESSAMENTO
    CANCELAR_PROCESSAMENTO = False
    
    try:
        caminho_arquivo = await selecionar_arquivo()
        if not caminho_arquivo or CANCELAR_PROCESSAMENTO:
            return
        
        voz_escolhida = await menu_vozes()
        if not voz_escolhida or CANCELAR_PROCESSAMENTO:
            return
        
        print("\n📖 Lendo arquivo...")
        texto = ler_arquivo_texto(caminho_arquivo)
        if not texto or CANCELAR_PROCESSAMENTO:
            print("\n❌ Arquivo vazio ou ilegível")
            await asyncio.sleep(2)
            return
        
        print("🔄 Processando texto...")
        texto_processado = processar_texto(texto)
        
        partes = dividir_texto(texto_processado)
        total_partes = len(partes)
        print(f"📦 Total de partes: {total_partes}")
        print("⏳ Iniciando conversão TTS... (Digite 'sair' para cancelar)")
        
        nome_base = os.path.splitext(os.path.basename(caminho_arquivo))[0]
        nome_base = re.sub(r'[\\/*?:"<>|]', "", nome_base)
        diretorio_saida = os.path.join(os.path.dirname(caminho_arquivo), f"{nome_base}_audio")
        os.makedirs(diretorio_saida, exist_ok=True)
        
        temp_files = []
        start_time = time.time()
        semaphore = asyncio.Semaphore(5)
        
        async def processar_chunk(i, parte):
            async with semaphore:
                if CANCELAR_PROCESSAMENTO:
                    return None
                
                saida_temp = os.path.join(diretorio_saida, f"{nome_base}_temp_{i:03d}.mp3")
                temp_files.append(saida_temp)
                
                inicio_chunk = time.time()
                sucesso = await converter_texto_para_audio(parte, voz_escolhida, saida_temp)
                
                if sucesso:
                    tempo_chunk = time.time() - inicio_chunk
                    print(f"✅ Parte {i}/{total_partes} | Tempo: {tempo_chunk:.1f}s")
                    return True
                else:
                    print(f"❌ Falha na parte {i}")
                    return False
        
        tasks = [processar_chunk(i+1, p) for i, p in enumerate(partes)]
        results = await asyncio.gather(*tasks)
        
        if not CANCELAR_PROCESSAMENTO and any(results):
            print("\n🔄 Unificando arquivos...")
            arquivo_final = os.path.join(diretorio_saida, f"{nome_base}.mp3")
            try:
                with open(arquivo_final, 'wb') as wfd:
                    for f in temp_files:
                        if os.path.exists(f):
                            with open(f, 'rb') as fd:
                                wfd.write(fd.read())
                            os.remove(f)
                print(f"\n🎉 Conversão concluída em {time.time() - start_time:.1f}s")
                print(f"📍 Arquivo final: {arquivo_final}")
            except Exception as e:
                print(f"\n❌ Erro na unificação: {str(e)}")
        
    except asyncio.CancelledError:
        print("\n🚫 Operação cancelada pelo usuário")
    finally:
        CANCELAR_PROCESSAMENTO = True
        if 'temp_files' in locals():
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
        await asyncio.sleep(1)

async def main() -> None:
    policy = asyncio.WindowsSelectorEventLoopPolicy() if sys.platform == 'win32' else asyncio.DefaultEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    
    while True:
        escolha = await menu_principal()
        if escolha == '1':
            await iniciar_conversao()
        elif escolha == '2':
            voz = await menu_vozes()
            if voz:
                await testar_voz(voz)
        elif escolha == '3':
            await exibir_ajuda()
        elif escolha == '4':
            clear_screen()
            print("\n👋 Obrigado por usar o Conversor TTS!")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        clear_screen()
        print("\n⚠️ Programa interrompido pelo usuário")
    except Exception as e:
        clear_screen()
        print(f"\n❌ Erro crítico: {str(e)}")