import PyInstaller.__main__
import os
import shutil
import sys

def build_executable():
    # Nome do executável
    exe_name = "PesquisaPlaylist"
    
    # Obtém o caminho absoluto do arquivo principal
    main_file = os.path.abspath("pesquisa_playlist.py")
    
    # Lista de arquivos ocultos (hidden imports)
    hidden_imports = [
        'tkinter',
        'tkinter.ttk',
        'sqlite3',
        're',
        'requests',
        'threading',
        'concurrent.futures',
        'vlc',
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'charset_normalizer',
        'certifi',
        'idna',
        'urllib3',
        'multidict',
        'attrs',
        'frozenlist',
        'aiosignal',
        'async_timeout',
        'yarl',
        'colorama',
        'win32_setctime',
    ]
    
    # Configurações do PyInstaller
    options = [
        main_file,  # Arquivo principal com caminho absoluto
        f'--name={exe_name}',  # Nome do executável
        '--onefile',  # Criar um único arquivo executável
        '--noconsole',  # Não mostrar console
        '--clean',  # Limpar cache antes de construir
        '--windowed',  # Modo janela (sem console)
        '--add-binary=C:\\Windows\\System32\\vcruntime140.dll;.',  # DLL necessária
        '--add-binary=C:\\Windows\\System32\\msvcp140.dll;.',  # DLL necessária
    ]
    
    # Adiciona imports ocultos
    for imp in hidden_imports:
        options.append(f'--hidden-import={imp}')
    
    try:
        # Executa o PyInstaller
        PyInstaller.__main__.run(options)
        
        # Cria pasta dist se não existir
        if not os.path.exists('dist'):
            os.makedirs('dist')
        
        print("\nBuild concluído com sucesso!")
        print(f"O executável está na pasta 'dist': {exe_name}.exe")
        
    except Exception as e:
        print(f"\nErro durante o build: {str(e)}")
        print("Verifique se todos os arquivos necessários existem e tente novamente.")

if __name__ == "__main__":
    build_executable() 