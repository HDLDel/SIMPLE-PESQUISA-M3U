import sys
from cx_Freeze import setup, Executable

# Dependências
build_exe_options = {
    "packages": [
        "tkinter",
        "sqlite3",
        "re",
        "requests",
        "threading",
        "concurrent.futures",
        "vlc",
        "customtkinter"
    ],
    "includes": [],
    "include_files": [
        "Banco.db",  # Banco de dados
        "assets/icon.ico",  # Ícone do aplicativo
    ],
    "excludes": [],
    "build_exe": "dist/PesquisaPlaylist",
    "optimize": 2
}

# Configuração base
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="PesquisaPlaylist",
    version="1.0.0",
    description="Programa para pesquisa de vídeos e playlists",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "pesquisa_playlist.py",
            base=base,
            target_name="PesquisaPlaylist.exe",
            icon="icon.ico"  # Adicione um ícone se desejar
        )
    ]
) 