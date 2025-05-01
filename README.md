# Pesquisa de Servidores

Um programa em Python para pesquisar vídeos e seus servidores em um banco de dados local ou arquivo M3U remoto.

## Características

- Interface gráfica moderna e intuitiva
- Pesquisa em banco de dados SQLite local
- Carregamento de arquivos M3U remotos
- Player de vídeo integrado com controles de reprodução
- Tema escuro por padrão

## Requisitos

- Python 3.8 ou superior
- VLC Media Player instalado no sistema
- Dependências Python listadas em `requirements.txt`

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute o programa:
```bash
python src/main.py
```

2. A interface apresentará:
   - Botão para carregar banco de dados local
   - Campo para URL de arquivo M3U e botão para carregar
   - Campo de pesquisa para filtrar vídeos
   - Lista de vídeos com informações
   - Player de vídeo integrado

3. Funcionalidades:
   - Clique em "Carregar Banco de Dados" para carregar vídeos do banco local
   - Cole uma URL de arquivo M3U e clique em "Carregar M3U" para carregar vídeos remotos
   - Use o campo de pesquisa para filtrar vídeos por nome
   - Clique duplo em um vídeo para reproduzir no player integrado

## Banco de Dados

O programa espera um arquivo `Banco.db` com uma tabela `videos` contendo:
- name: Nome do vídeo
- type: Tipo (Filme/Série)
- season: Temporada (para séries)
- url: URL do vídeo

## Notas

- O banco de dados deve estar no mesmo diretório do executável
- É necessário ter o VLC Media Player instalado para reprodução de vídeos
- Certifique-se de ter uma conexão com a internet para carregar arquivos M3U remotos 