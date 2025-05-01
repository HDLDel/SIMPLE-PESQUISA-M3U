import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
import requests
import threading
import concurrent.futures
import customtkinter as ctk
import vlc
import os
import subprocess
import json
import webbrowser

class PesquisaPlaylist:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Pesquisa de Servidores")
        self.root.geometry("1200x800")
        
        # Configuração do tema escuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Variáveis
        self.dados_m3u = []
        self.dados_db = []
        self.conn = None
        self.cursor = None
        
        # Configuração do player
        self.player_type = "vlc"  # Padrão é VLC
        self.mpv_path = r"C:\Users\del\Downloads\pesquisa-V1.2\mpv\mpv.exe"
        self.mpv_process = None
        
        # User-Agent padrão
        self.user_agent = "VLC/3.0.18 LibVLC/3.0.18"
        
        # Inicializa VLC
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        self.is_playing = False
        
        # Configura o volume inicial
        self.player.audio_set_volume(100)
        
        # Inicializa o banco de dados
        self.init_database()
        
        # Criar interface
        self.criar_interface()
        
        # Bind do evento de redimensionamento
        self.root.bind("<Configure>", self.on_window_resize)
        
    def criar_interface(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior para botões e entrada
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para configurações
        self.settings_frame = ctk.CTkFrame(self.top_frame)
        self.settings_frame.pack(side=tk.LEFT, padx=5)
        
        # Frame para User-Agent
        self.ua_frame = ctk.CTkFrame(self.settings_frame)
        self.ua_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        
        # Label User-Agent
        self.ua_label = ctk.CTkLabel(self.ua_frame, text="User-Agent:")
        self.ua_label.pack(side=tk.LEFT, padx=5)
        
        # Combobox para User-Agent predefinidos
        self.ua_combo = ctk.CTkOptionMenu(
            self.ua_frame,
            values=[
                "VLC/3.0.18 LibVLC/3.0.18",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Lavf/58.76.100",
                "Mozilla/5.0 (SMART-TV; Linux; Tizen 2.4.0) AppleWebkit/538.1",
                "Custom..."
            ],
            command=self.change_user_agent
        )
        self.ua_combo.pack(side=tk.LEFT, padx=5)
        self.ua_combo.set("VLC/3.0.18 LibVLC/3.0.18")
        
        # Campo de entrada para User-Agent personalizado (inicialmente oculto)
        self.ua_entry = ctk.CTkEntry(
            self.ua_frame,
            placeholder_text="Digite o User-Agent personalizado"
        )
        
        # Opção de player
        self.player_option = ctk.CTkOptionMenu(
            self.settings_frame,
            values=["VLC", "MPV"],
            command=self.change_player
        )
        self.player_option.pack(side=tk.LEFT, padx=5)
        self.player_option.set("VLC")
        
        # Botão Carregar DB
        self.btn_carregar_db = ctk.CTkButton(
            self.top_frame,
            text="Carregar Banco de Dados",
            command=self.carregar_banco
        )
        self.btn_carregar_db.pack(side=tk.LEFT, padx=5)
        
        # Frame para URL e botão M3U
        self.url_frame = ctk.CTkFrame(self.top_frame)
        self.url_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Entrada de URL
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Digite a URL do arquivo M3U"
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botão Carregar M3U
        self.btn_carregar_m3u = ctk.CTkButton(
            self.url_frame,
            text="Carregar M3U",
            command=self.carregar_m3u
        )
        self.btn_carregar_m3u.pack(side=tk.LEFT, padx=5)
        
        # Botão Adicionar Links
        self.btn_adicionar_links = ctk.CTkButton(
            self.url_frame,
            text="Adicionar Links",
            command=self.load_multiple_links
        )
        self.btn_adicionar_links.pack(side=tk.LEFT, padx=5)
        
        # Frame para pesquisa
        self.search_frame = ctk.CTkFrame(self.main_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campo de pesquisa
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Digite o termo de pesquisa"
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botão Pesquisar
        self.btn_pesquisar = ctk.CTkButton(
            self.search_frame,
            text="Pesquisar",
            command=self.filtrar_resultados
        )
        self.btn_pesquisar.pack(side=tk.LEFT, padx=5)
        
        # Frame para conteúdo (lista e player)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame esquerdo para lista (50% da largura)
        self.left_frame = ctk.CTkFrame(self.content_frame, width=600)  # Largura inicial
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)
        self.left_frame.pack_propagate(False)  # Impede que o frame encolha
        
        # Frame direito para player (50% da largura)
        self.right_frame = ctk.CTkFrame(self.content_frame, width=600)  # Largura inicial
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        self.right_frame.pack_propagate(False)  # Impede que o frame encolha
        
        # Força o redimensionamento inicial
        self.content_frame.update_idletasks()
        width = self.content_frame.winfo_width()
        if width > 0:  # Só ajusta se a largura for válida
            self.left_frame.configure(width=width//2)
            self.right_frame.configure(width=width//2)
        
        # Frame dos botões de ação
        self.action_buttons_frame = ctk.CTkFrame(self.left_frame)
        self.action_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botão Copiar Link
        self.btn_copy = ctk.CTkButton(
            self.action_buttons_frame,
            text="Copiar Link",
            command=self.copy_link
        )
        self.btn_copy.pack(side=tk.LEFT, padx=5)
        
        # Botão Abrir no Navegador
        self.btn_browser = ctk.CTkButton(
            self.action_buttons_frame,
            text="Abrir no Navegador",
            command=self.open_in_browser
        )
        self.btn_browser.pack(side=tk.LEFT, padx=5)
        
        # Treeview para resultados
        self.tree = ttk.Treeview(
            self.left_frame,
            columns=("Nome", "Tipo", "Temporada", "Servidor", "Link de Origem"),
            show="headings"
        )
        
        # Configurar colunas
        self.tree.heading("Nome", text="Nome", command=lambda: self.sort_treeview("Nome"))
        self.tree.heading("Tipo", text="Tipo", command=lambda: self.sort_treeview("Tipo"))
        self.tree.heading("Temporada", text="Temporada", command=lambda: self.sort_treeview("Temporada"))
        self.tree.heading("Servidor", text="Servidor", command=lambda: self.sort_treeview("Servidor"))
        self.tree.heading("Link de Origem", text="Link de Origem", command=lambda: self.sort_treeview("Link de Origem"))
        
        # Configurar larguras das colunas
        self.tree.column("Nome", width=400)
        self.tree.column("Tipo", width=100)
        self.tree.column("Temporada", width=100)
        self.tree.column("Servidor", width=200)
        self.tree.column("Link de Origem", width=300)
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar Treeview e Scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame do player VLC
        self.vlc_frame = tk.Frame(self.right_frame, bg="black")
        self.vlc_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame dos controles do player
        self.controls_frame = ctk.CTkFrame(self.right_frame)
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botões de controle do player
        self.play_button = ctk.CTkButton(
            self.controls_frame,
            text="▶",
            width=30,
            command=self.toggle_play
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ctk.CTkButton(
            self.controls_frame,
            text="⏹",
            width=30,
            command=self.stop_video
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Barra de progresso do vídeo
        self.video_progress = ctk.CTkProgressBar(self.controls_frame)
        self.video_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.video_progress.set(0)
        
        # Label de tempo
        self.time_label = ctk.CTkLabel(self.controls_frame, text="00:00 / 00:00")
        self.time_label.pack(side=tk.LEFT, padx=5)
        
        # Controle de volume
        self.volume_slider = ctk.CTkSlider(
            self.controls_frame,
            from_=0,
            to=100,
            command=self.set_volume
        )
        self.volume_slider.pack(side=tk.LEFT, padx=5)
        self.volume_slider.set(100)
        
        # Configurar estilo para tema escuro
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading",
                       background="#1f538d",
                       foreground="white")
        
        # Bind eventos
        self.search_entry.bind("<Return>", lambda e: self.filtrar_resultados())
        self.tree.bind("<Double-Button-1>", self.on_tree_double_click)
        
        # Variável para controlar a ordenação
        self.sort_reverse = False
        self.last_sort_column = None
        
    def on_tree_double_click(self, event):
        """Manipula duplo clique na treeview"""
        try:
            item = self.tree.selection()[0]
            values = self.tree.item(item)['values']
            
            # Procura a URL do vídeo
            url = None
            nome_video = values[0]
            
            # Procura nos dados do banco
            for item in self.dados_db:
                if item[0] == nome_video:
                    url = item[3]
                    break
            
            # Se não encontrou no banco, procura nos dados M3U
            if not url:
                for item in self.dados_m3u:
                    if item[0] == nome_video:
                        url = item[4]  # O índice 4 contém a URL no formato M3U
                        break
            
            if url and self.validar_url(url):
                self.play_video(url)
            else:
                messagebox.showerror("Erro", "URL inválida ou não encontrada para este vídeo.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao reproduzir vídeo: {str(e)}")
    
    def play_video(self, url):
        """Reproduz um vídeo"""
        try:
            print(f"Tentando reproduzir URL: {url}")
            print(f"User-Agent atual: {self.user_agent}")
            
            # Headers padrão para streaming
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "*/*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
                "Referer": url
            }
            
            if self.player_type == "vlc":
                # Para qualquer reprodução atual
                self.player.stop()
                
                # Cria media com opções específicas para streaming ao vivo
                print("Criando media VLC para streaming...")
                media = self.instance.media_new(url)
                
                # Configurações otimizadas para streaming ao vivo
                media.add_option(":network-caching=1000")  # Reduz o cache para streaming ao vivo
                media.add_option(":live-caching=1000")     # Cache específico para conteúdo ao vivo
                media.add_option(":sout-mux-caching=1000") # Cache de multiplexação
                media.add_option(":clock-jitter=0")        # Reduz jitter
                media.add_option(":clock-synchro=0")       # Sincronização de clock
                media.add_option(":no-video-title-show")   # Não mostra título
                media.add_option(f":http-user-agent={self.user_agent}")
                media.add_option(":http-reconnect")        # Reconexão automática
                media.add_option(":rtsp-tcp")              # Força TCP para RTSP
                
                print("Configurando media player...")
                self.player.set_media(media)
                
                # Configura janela de reprodução
                if os.name == 'nt':  # Windows
                    print("Configurando janela de reprodução (Windows)...")
                    self.player.set_hwnd(self.vlc_frame.winfo_id())
                else:  # Linux/Mac
                    print("Configurando janela de reprodução (Linux/Mac)...")
                    self.player.set_xwindow(self.vlc_frame.winfo_id())
                
                # Inicia reprodução
                print("Iniciando reprodução do stream...")
                result = self.player.play()
                print(f"Resultado do play: {result}")
                
                self.is_playing = True
                self.play_button.configure(text="⏸")
                
            else:  # MPV
                print("Usando player MPV para streaming...")
                # Para qualquer reprodução atual
                if self.mpv_process:
                    print("Parando reprodução anterior...")
                    self.mpv_process.terminate()
                    self.mpv_process = None
                
                # Configura o comando MPV otimizado para streaming ao vivo
                mpv_command = [
                    self.mpv_path,
                    '--no-border',
                    '--no-osc',
                    '--no-osd-bar',
                    '--profile=low-latency',
                    '--no-cache',                    # Desativa cache para streaming ao vivo
                    '--untimed',                     # Desativa sincronização de tempo
                    '--no-demuxer-thread',          # Desativa thread de demuxer
                    '--vd-lavc-threads=1',          # Reduz threads de decodificação
                    '--stream-buffer-size=4k',      # Buffer pequeno para menor latência
                    f'--user-agent={self.user_agent}',
                    '--force-window=yes',
                    '--keep-open=yes',
                    '--wid=' + str(self.vlc_frame.winfo_id()),
                    '--msg-level=all=v',
                    url
                ]
                
                print(f"Iniciando MPV com comando: {' '.join(mpv_command)}")
                
                # Inicia o MPV com saída redirecionada para capturar erros
                self.mpv_process = subprocess.Popen(
                    mpv_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Verifica se o processo iniciou corretamente
                if self.mpv_process.poll() is None:
                    self.is_playing = True
                    self.play_button.configure(text="⏸")
                else:
                    error = self.mpv_process.stderr.read()
                    print(f"Erro ao iniciar MPV: {error}")
                    raise Exception(f"Falha ao iniciar MPV: {error}")
                
        except Exception as e:
            print(f"Erro ao reproduzir stream: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao reproduzir stream: {str(e)}")
            # Tenta limpar o estado
            self.stop_video()
    
    def toggle_play(self):
        """Alterna entre play e pause"""
        if self.player_type == "vlc":
            if self.player.is_playing():
                self.player.pause()
                self.is_playing = False
                self.play_button.configure(text="▶")
            else:
                self.player.play()
                self.is_playing = True
                self.play_button.configure(text="⏸")
        else:  # MPV
            if self.mpv_process:
                # Envia comando de pause/play para o MPV
                subprocess.run([self.mpv_path, '--input-ipc-server=/tmp/mpv-socket', 'cycle', 'pause'])
                self.is_playing = not self.is_playing
                self.play_button.configure(text="⏸" if self.is_playing else "▶")
    
    def stop_video(self):
        """Para a reprodução"""
        if self.player_type == "vlc":
            self.player.stop()
            self.is_playing = False
            self.play_button.configure(text="▶")
            self.video_progress.set(0)
            self.time_label.configure(text="00:00 / 00:00")
        else:  # MPV
            if self.mpv_process:
                self.mpv_process.terminate()
                self.mpv_process = None
            self.is_playing = False
            self.play_button.configure(text="▶")
    
    def set_volume(self, value):
        """Ajusta o volume"""
        if self.player_type == "vlc":
            self.player.audio_set_volume(int(value))
        else:  # MPV
            if self.mpv_process:
                subprocess.run([self.mpv_path, '--input-ipc-server=/tmp/mpv-socket', 'set', 'volume', str(int(value))])
    
    def update_video_progress(self):
        """Atualiza a barra de progresso e o tempo"""
        if self.player_type == "vlc":
            if self.player.is_playing():
                # Atualiza progresso
                length = self.player.get_length()
                time = self.player.get_time()
                
                if length > 0:
                    progress = time / length
                    self.video_progress.set(progress)
                    
                    # Formata tempo
                    current = time // 1000  # Converte para segundos
                    total = length // 1000
                    current_str = f"{current//60:02d}:{current%60:02d}"
                    total_str = f"{total//60:02d}:{total%60:02d}"
                    self.time_label.configure(text=f"{current_str} / {total_str}")
                
                # Agenda próxima atualização
                self.root.after(1000, self.update_video_progress)
        else:  # MPV
            if self.mpv_process:
                # Atualiza progresso
                length = self.mpv_process.stdout.readline().decode().strip()
                if length:
                    progress = float(length.split('/')[0]) / float(length.split('/')[1])
                    self.video_progress.set(progress)
                    
                    # Formata tempo
                    current = int(float(length.split('/')[0]) // 1000)
                    total = int(float(length.split('/')[1]) // 1000)
                    current_str = f"{current//60:02d}:{current%60:02d}"
                    total_str = f"{total//60:02d}:{total%60:02d}"
                    self.time_label.configure(text=f"{current_str} / {total_str}")
                
                # Agenda próxima atualização
                self.root.after(1000, self.update_video_progress)
    
    def conectar_banco(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = sqlite3.connect('Banco.db')
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            return False
            
    def carregar_banco(self):
        """Carrega dados do banco de dados"""
        if not self.conectar_banco():
            return
            
        try:
            self.cursor.execute("SELECT name, type, season, url, username FROM videos")
            self.dados_db = self.cursor.fetchall()
            messagebox.showinfo("Sucesso", "Banco de dados carregado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
            
    def carregar_m3u(self):
        """Carrega dados do arquivo M3U via URL"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira uma URL válida.")
            return
            
        try:
            # Configuração da sessão com retry
            session = requests.Session()
            session.verify = False  # Desativa verificação SSL
            
            # Headers personalizados
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "*/*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
            
            print(f"Tentando carregar M3U de: {url}")
            print(f"User-Agent: {self.user_agent}")
            
            # Tenta fazer a requisição com timeout e retry
            for attempt in range(3):  # Tenta 3 vezes
                try:
                    response = session.get(
                        url,
                        headers=headers,
                        timeout=30,
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Tentativa {attempt + 1} falhou: {str(e)}")
                    if attempt == 2:  # Última tentativa
                        raise
                    continue
            
            # Limpar dados M3U anteriores
            self.dados_m3u = []
            
            # Processar arquivo M3U
            linhas = response.text.split('\n')
            nome_atual = ""
            url_atual = ""
            
            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue
                    
                if linha.startswith('#EXTINF:'):
                    # Extrair nome do vídeo
                    nome_atual = re.search(r',(.*?)$', linha)
                    if nome_atual:
                        nome_atual = nome_atual.group(1)
                elif linha.startswith('http'):
                    url_atual = linha
                    # Adicionar entrada à lista
                    if nome_atual:
                        tipo = "Filme"
                        temporada = ""
                        if "S0" in nome_atual or "S1" in nome_atual:
                            tipo = "Série"
                            temp = re.search(r'S(\d+)', nome_atual)
                            if temp:
                                temporada = f"Temporada {temp.group(1)}"
                        
                        # Extrai servidor
                        servidor, _ = self.extrair_servidor_e_username(url_atual)
                        
                        print(f"Processando entrada: {nome_atual}")
                        print(f"URL: {url_atual}")
                        
                        self.dados_m3u.append((nome_atual, tipo, temporada, servidor, url_atual))
                        nome_atual = ""
                        url_atual = ""
            
            if self.dados_m3u:
                messagebox.showinfo("Sucesso", f"Arquivo M3U carregado com sucesso! {len(self.dados_m3u)} itens encontrados.")
                self.filtrar_resultados()
            else:
                messagebox.showwarning("Aviso", "Nenhum item encontrado no arquivo M3U.")
            
        except requests.exceptions.SSLError:
            print("Erro SSL - Tentando novamente sem verificação SSL")
            messagebox.showerror("Erro SSL", "Erro de certificado SSL. Tentando novamente sem verificação...")
            
        except requests.exceptions.ConnectionError as e:
            print(f"Erro de conexão: {str(e)}")
            messagebox.showerror("Erro de Conexão", 
                               "Não foi possível conectar ao servidor. Verifique sua conexão e se o endereço está correto.")
            
        except requests.exceptions.Timeout:
            print("Timeout na requisição")
            messagebox.showerror("Erro de Timeout", 
                               "A requisição demorou muito para responder. Tente novamente.")
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            messagebox.showerror("Erro", 
                               f"Erro ao carregar arquivo M3U:\n{str(e)}")
            
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            messagebox.showerror("Erro", 
                               f"Erro inesperado ao carregar arquivo M3U:\n{str(e)}")
            
    def extrair_servidor_e_username(self, url):
        """Extrai o nome do servidor e username da URL"""
        try:
            # Remove o protocolo (http:// ou https://)
            url_sem_protocolo = re.sub(r'^https?://', '', url)
            
            # Divide a URL em partes
            partes = url_sem_protocolo.split('/')
            
            # Pega o servidor (primeira parte)
            servidor = partes[0].split(':')[0]
            
            # Tenta extrair o username da URL
            username = "N/A"
            if "username=" in url:
                # Procura por username= seguido de números
                match = re.search(r'username=(\d+)', url)
                if match:
                    username = match.group(1)
                else:
                    # Se não encontrou números, tenta pegar qualquer valor após username=
                    match = re.search(r'username=([^&]+)', url)
                    if match:
                        username = match.group(1)
            
            return servidor, username
        except:
            return "Desconhecido", "N/A"
            
    def validar_url(self, url):
        """Valida se a URL é válida para reprodução"""
        try:
            # Verifica se é uma URL válida
            if not url.startswith(('http://', 'https://')):
                print(f"URL inválida (não começa com http:// ou https://): {url}")
                return False
                
            # Aceita qualquer URL que tenha um domínio válido e termine com extensão de vídeo ou parâmetros
            if re.match(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:\d+)?(/[^/]+)*(/[^/]+\.(m3u8|ts|mp4|mkv|avi|mov|flv|webm)|/.*)?$', url):
                return True
                
            # Aceita URLs com tokens ou hashes no final
            if re.match(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(:\d+)?(/[^/]+)*/play/[A-Za-z0-9_-]+(/.*)?$', url):
                return True
                
            # Aceita URLs de streaming comuns
            stream_keywords = ('m3u8', 'stream', 'playlist', 'live', 'hls', 'dash', 'rtmp', 'rtsp', 'play')
            if any(keyword in url.lower() for keyword in stream_keywords):
                return True
                
            print(f"URL não corresponde a nenhum padrão conhecido: {url}")
            return False
        except Exception as e:
            print(f"Erro ao validar URL {url}: {str(e)}")
            return True  # Em caso de erro, aceita a URL para evitar falsos negativos
            
    def filtrar_resultados(self):
        """Filtra e exibe os resultados com base no termo de pesquisa"""
        # Limpar resultados anteriores
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Obter termo de pesquisa
        termo = self.search_entry.get().strip().lower()
        
        # Se não houver termo de pesquisa, não mostra nada
        if not termo:
            return
            
        # Combinar dados do banco de dados e do M3U
        todos_dados = []
        
        # Adicionar dados do banco de dados
        for item in self.dados_db:
            nome, tipo, temporada, url, link_origem = item
            servidor, _ = self.extrair_servidor_e_username(url)
            if termo in nome.lower():
                todos_dados.append((nome, tipo, temporada, servidor, link_origem))
        
        # Adicionar dados do M3U
        for item in self.dados_m3u:
            nome, tipo, temporada, servidor, link_origem = item
            if termo in nome.lower():
                todos_dados.append((nome, tipo, temporada, servidor, link_origem))
        
        # Ordenar resultados por nome
        todos_dados.sort(key=lambda x: x[0].lower())
        
        # Inserir resultados na treeview
        for item in todos_dados:
            self.tree.insert("", tk.END, values=item)
            
    def load_multiple_links(self):
        """Carrega múltiplos links M3U ao mesmo tempo"""
        try:
            # Cria uma nova janela
            multi_url_window = tk.Toplevel(self.root)
            multi_url_window.title("Adicionar Múltiplos Links")
            multi_url_window.geometry("1200x600")
            
            # Frame principal com split
            main_frame = ttk.Frame(multi_url_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Frame esquerdo para links
            left_frame = ttk.Frame(main_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            
            # Frame direito para terminal
            right_frame = ttk.Frame(main_frame)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            # Adiciona um texto explicativo
            ttk.Label(left_frame, 
                     text="Cole aqui seus links M3U (um por linha):",
                     wraplength=550,
                     padding=10).pack(fill=tk.X)
            
            # Cria um campo de texto com barra de rolagem para links
            text_frame = ttk.Frame(left_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_area = tk.Text(text_frame, 
                               wrap=tk.WORD, 
                               yscrollcommand=text_scroll.set,
                               height=15)
            text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            text_scroll.config(command=text_area.yview)

            # Frame para progresso
            progress_frame = ttk.LabelFrame(left_frame, text="Progresso", padding="5")
            progress_frame.pack(fill=tk.X, padx=5, pady=5)

            # Barra de progresso
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
            progress_bar.pack(fill=tk.X, pady=5)

            # Labels para informações
            info_frame = ttk.Frame(progress_frame)
            info_frame.pack(fill=tk.X)

            progress_label = ttk.Label(info_frame, text="0%")
            progress_label.pack(side=tk.LEFT, padx=5)

            status_label = ttk.Label(info_frame, text="", wraplength=500)
            status_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Frame para os botões
            button_frame = ttk.Frame(left_frame)
            button_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Frame para o terminal
            terminal_frame = ttk.LabelFrame(right_frame, text="Terminal", padding="5")
            terminal_frame.pack(fill=tk.BOTH, expand=True)
            
            # Terminal
            terminal_scroll = ttk.Scrollbar(terminal_frame)
            terminal_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            terminal = tk.Text(terminal_frame,
                             wrap=tk.WORD,
                             yscrollcommand=terminal_scroll.set,
                             bg='black',
                             fg='white',
                             font=('Consolas', 10),
                             height=20)
            terminal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            terminal_scroll.config(command=terminal.yview)
            
            # Configura o terminal como somente leitura
            terminal.config(state='disabled')
            
            # Função para adicionar texto ao terminal
            def append_to_terminal(text, color='white'):
                try:
                    if multi_url_window.winfo_exists() and terminal.winfo_exists():
                        terminal.config(state='normal')
                        terminal.tag_configure(color, foreground=color)
                        terminal.insert(tk.END, f"{text}\n", color)
                        terminal.see(tk.END)
                        terminal.config(state='disabled')
                        terminal.update_idletasks()
                except Exception as e:
                    print(f"Erro ao atualizar terminal: {str(e)}")

            # Variável para controlar o cancelamento
            cancel_process = False
            
            # Função para atualizar a interface de forma segura
            def safe_update_interface(text, progress=None):
                try:
                    if multi_url_window.winfo_exists():
                        if text:
                            status_label.config(text=text)
                            append_to_terminal(text)
                        if progress is not None:
                            progress_var.set(progress)
                            progress_label.config(text=f"{progress:.1f}%")
                        multi_url_window.update_idletasks()
                except Exception as e:
                    print(f"Erro ao atualizar interface: {str(e)}")
            
            # Função para processar os links
            def process_links():
                nonlocal cancel_process
                cancel_process = False
                
                try:
                    # Cria uma nova conexão com o banco de dados para esta thread
                    thread_conn = sqlite3.connect('Banco.db')
                    thread_cursor = thread_conn.cursor()
                    
                    # Verifica se a tabela existe, se não, cria
                    thread_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS videos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            url TEXT NOT NULL UNIQUE,
                            type TEXT NOT NULL,
                            season TEXT NOT NULL,
                            username TEXT,
                            downloaded INTEGER DEFAULT 0
                        )
                    ''')
                    thread_conn.commit()
                    
                    # Verifica o tamanho inicial do banco
                    thread_cursor.execute("SELECT COUNT(*) FROM videos")
                    initial_count = thread_cursor.fetchone()[0]
                    if multi_url_window.winfo_exists():
                        append_to_terminal(f"Total de vídeos no banco antes: {initial_count}", 'cyan')
                    
                    # Obtém os links
                    links = text_area.get("1.0", tk.END).strip().split("\n")
                    links = [link.strip() for link in links if link.strip()]
                    
                    if not links:
                        if multi_url_window.winfo_exists():
                            safe_update_interface("Nenhum link encontrado!", 'yellow')
                        return
                    
                    # Desabilita os botões durante o processamento
                    if multi_url_window.winfo_exists():
                        if process_button.winfo_exists():
                            process_button.config(state="disabled")
                        if cancel_button.winfo_exists():
                            cancel_button.config(state="normal")
                    
                    total_links = len(links)
                    if multi_url_window.winfo_exists():
                        append_to_terminal(f"Iniciando download de {total_links} links M3U...", 'cyan')
                    
                    # Configuração otimizada do requests
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Accept": "*/*",
                        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Connection": "keep-alive",
                        "Cache-Control": "no-cache",
                        "Pragma": "no-cache"
                    }
                    
                    # Baixa todas as M3U em paralelo
                    m3u_contents = {}  # Dicionário para armazenar conteúdo por URL
                    
                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        future_to_url = {executor.submit(requests.get, url, headers=headers, timeout=30, verify=False): url 
                                       for url in links}
                        
                        for future in concurrent.futures.as_completed(future_to_url):
                            url = future_to_url[future]
                            try:
                                response = future.result()
                                response.raise_for_status()
                                m3u_contents[url] = response.text.splitlines()
                                if multi_url_window.winfo_exists():
                                    append_to_terminal(f"Download concluído: {url}", 'green')
                            except Exception as e:
                                if multi_url_window.winfo_exists():
                                    append_to_terminal(f"Erro ao baixar {url}: {str(e)}", 'red')
                    
                    if not m3u_contents:
                        if multi_url_window.winfo_exists():
                            safe_update_interface("Nenhum conteúdo encontrado nos links!", 'red')
                        return
                    
                    if multi_url_window.winfo_exists():
                        append_to_terminal(f"\nProcessando {sum(len(content) for content in m3u_contents.values())} linhas...", 'cyan')
                    
                    # Desabilita temporariamente as restrições do banco de dados
                    thread_cursor.execute("PRAGMA foreign_keys=OFF")
                    thread_cursor.execute("PRAGMA synchronous=OFF")
                    thread_cursor.execute("PRAGMA journal_mode=MEMORY")
                    
                    # Prepara a query de inserção em lote
                    insert_query = '''
                        INSERT OR IGNORE INTO videos (name, url, type, season, username)
                        VALUES (?, ?, ?, ?, ?)
                    '''
                    
                    # Lista para armazenar os dados em lote
                    batch_data = []
                    batch_size = 1000
                    total_processed = 0
                    total_added = 0
                    last_save = 0
                    
                    # Processa cada M3U separadamente
                    for m3u_url, content in m3u_contents.items():
                        if cancel_process:
                            break
                            
                        if multi_url_window.winfo_exists():
                            append_to_terminal(f"\nProcessando M3U: {m3u_url}", 'cyan')
                        
                        # Processa em chunks para melhor performance
                        chunk_size = 10000
                        for i in range(0, len(content), chunk_size):
                            if cancel_process:
                                break
                                
                            chunk = content[i:i + chunk_size]
                            progress = (i / len(content)) * 100
                            
                            # Atualiza a interface em uma thread separada
                            def update_ui():
                                if multi_url_window.winfo_exists():
                                    safe_update_interface(f"Processando chunk {i//chunk_size + 1}...", progress)
                            
                            threading.Thread(target=update_ui, daemon=True).start()
                            
                            # Processa o chunk
                            for j in range(len(chunk)):
                                if chunk[j].startswith("#EXTINF:"):
                                    try:
                                        # Extrai informações do vídeo
                                        name = None
                                        if 'tvg-name="' in chunk[j]:
                                            name = chunk[j].split('tvg-name="')[1].split('"')[0]
                                        elif ',' in chunk[j]:
                                            name = chunk[j].split(',', 1)[1].strip()
                                        
                                        if not name or j + 1 >= len(chunk):
                                            continue
                                            
                                        url_video = chunk[j + 1].strip()
                                        if not url_video or url_video.startswith('#'):
                                            continue
                                        
                                        # Determina o tipo e temporada
                                        content_type = "Filme"
                                        season = "-"
                                        
                                        match = re.search(r"(.*?)\s*(S\d{2})\s*E\d{2}", name)
                                        if match:
                                            content_type = "Série"
                                            season = match.group(2)
                                        
                                        total_processed += 1
                                        batch_data.append((name, url_video, content_type, season, m3u_url))
                                        
                                        # Quando o lote atinge o tamanho definido, insere no banco
                                        if len(batch_data) >= batch_size:
                                            thread_cursor.executemany(insert_query, batch_data)
                                            thread_conn.commit()
                                            total_added += len(batch_data)
                                            batch_data = []
                                            
                                        # Salva a cada 10% do progresso
                                        current_progress = (i + j) / len(content) * 100
                                        if current_progress - last_save >= 10:
                                            thread_conn.commit()
                                            last_save = current_progress
                                            
                                            # Atualiza o terminal em uma thread separada
                                            def update_terminal():
                                                if multi_url_window.winfo_exists():
                                                    append_to_terminal(f"Progresso: {current_progress:.1f}% - Salvando...", 'cyan')
                                            
                                            threading.Thread(target=update_terminal, daemon=True).start()
                                            
                                    except Exception as e:
                                        if multi_url_window.winfo_exists():
                                            append_to_terminal(f"Erro ao processar item: {str(e)}", 'red')
                                        continue
                    
                    # Insere o lote restante
                    if batch_data:
                        thread_cursor.executemany(insert_query, batch_data)
                        thread_conn.commit()
                        total_added += len(batch_data)
                    
                    # Reativa as restrições do banco de dados
                    thread_cursor.execute("PRAGMA foreign_keys=ON")
                    thread_cursor.execute("PRAGMA synchronous=NORMAL")
                    thread_cursor.execute("PRAGMA journal_mode=DELETE")
                    
                    # Verifica o tamanho final do banco
                    thread_cursor.execute("SELECT COUNT(*) FROM videos")
                    final_count = thread_cursor.fetchone()[0]
                    
                    # Atualiza interface após conclusão
                    if multi_url_window.winfo_exists():
                        if process_button.winfo_exists():
                            process_button.config(state="normal")
                        if cancel_button.winfo_exists():
                            cancel_button.config(state="disabled")
                    
                    if not cancel_process:
                        if multi_url_window.winfo_exists():
                            append_to_terminal(f"\n{'='*50}", 'cyan')
                            append_to_terminal("RESUMO DO PROCESSAMENTO", 'cyan')
                            append_to_terminal(f"{'='*50}", 'cyan')
                            append_to_terminal(f"Total de vídeos no banco antes: {initial_count}", 'cyan')
                            append_to_terminal(f"Total de vídeos no banco após: {final_count}", 'cyan')
                            append_to_terminal(f"Novos vídeos adicionados: {final_count - initial_count}", 'green')
                            append_to_terminal(f"Total de itens processados: {total_processed}", 'yellow')
                            append_to_terminal(f"{'='*50}\n", 'cyan')
                            
                            final_msg = (f"Processamento concluído!\n"
                                       f"Total processado: {total_processed}\n"
                                       f"Novos itens: {total_added}\n"
                                       f"Total no banco: {final_count}")
                            safe_update_interface(final_msg, 'green')
                            
                            if total_processed > 0:
                                # Aguarda 3 segundos antes de fechar
                                multi_url_window.after(3000, multi_url_window.destroy)
                
                finally:
                    # Garante que todas as alterações foram salvas
                    try:
                        thread_conn.commit()
                    except:
                        pass
                    # Fecha a conexão da thread
                    thread_conn.close()
            
            def cancel_processing():
                nonlocal cancel_process
                cancel_process = True
                safe_update_interface("Cancelando...", 'yellow')
                append_to_terminal("Cancelando processamento...", 'yellow')
                if multi_url_window.winfo_exists():
                    cancel_button.config(state="disabled")
            
            # Botões
            process_button = ttk.Button(button_frame, 
                                      text="Processar Links", 
                                      command=lambda: threading.Thread(target=process_links).start())
            process_button.pack(side=tk.RIGHT, padx=5)
            
            cancel_button = ttk.Button(button_frame, 
                                     text="Cancelar", 
                                     command=cancel_processing,
                                     state="disabled")
            cancel_button.pack(side=tk.RIGHT, padx=5)
            
            # Torna a janela modal
            multi_url_window.transient(self.root)
            multi_url_window.grab_set()
            
            # Centraliza a janela
            multi_url_window.update_idletasks()
            width = multi_url_window.winfo_width()
            height = multi_url_window.winfo_height()
            x = (multi_url_window.winfo_screenwidth() // 2) - (width // 2)
            y = (multi_url_window.winfo_screenheight() // 2) - (height // 2)
            multi_url_window.geometry(f'+{x}+{y}')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir janela de múltiplos links: {str(e)}")
            
    def init_database(self):
        """Inicializa o banco de dados"""
        try:
            # Verifica se o arquivo do banco existe
            db_exists = os.path.exists('Banco.db')
            
            # Conecta ao banco de dados
            self.conn = sqlite3.connect('Banco.db')
            self.cursor = self.conn.cursor()
            
            # Cria tabela se não existir
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    season TEXT NOT NULL,
                    username TEXT,
                    downloaded INTEGER DEFAULT 0
                )
            ''')
            
            self.conn.commit()
            
            if not db_exists:
                print("Banco de dados criado com sucesso")
            else:
                print("Banco de dados conectado com sucesso")
            
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {str(e)}")
            raise
            
    def run(self):
        """Inicia o programa"""
        self.root.mainloop()

    def sort_treeview(self, col):
        """Ordena a Treeview pela coluna clicada"""
        # Obtém todos os itens
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Se clicou na mesma coluna, inverte a ordem
        if self.last_sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.last_sort_column = col
        
        # Ordena os itens
        items.sort(reverse=self.sort_reverse)
        
        # Reordena os itens na Treeview
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
            
        # Atualiza o indicador de ordenação nas colunas
        for column in self.tree['columns']:
            if column == col:
                self.tree.heading(column, text=f"{column} {'↓' if self.sort_reverse else '↑'}")
            else:
                self.tree.heading(column, text=column)

    def on_window_resize(self, event=None):
        """Ajusta os frames quando a janela é redimensionada"""
        if hasattr(self, 'content_frame') and hasattr(self, 'left_frame') and hasattr(self, 'right_frame'):
            # Atualiza as medidas
            self.content_frame.update_idletasks()
            width = self.content_frame.winfo_width()
            
            if width > 0:  # Só ajusta se a largura for válida
                # Calcula a metade da largura disponível
                half_width = width // 2
                
                # Configura larguras iguais com margem para padding
                self.left_frame.configure(width=half_width - 5)  # -5 para o padding
                self.right_frame.configure(width=half_width - 5)  # -5 para o padding
                
                # Força atualização
                self.left_frame.update_idletasks()
                self.right_frame.update_idletasks()

    def change_player(self, choice):
        """Muda o player entre VLC e MPV"""
        self.player_type = choice.lower()
        if self.is_playing:
            self.stop_video()
        
        # Atualiza a interface do player
        self.update_player_interface()
        
    def update_player_interface(self):
        """Atualiza a interface do player baseado no tipo selecionado"""
        # Limpa os controles existentes
        for widget in self.controls_frame.winfo_children():
            widget.destroy()
            
        if self.player_type == "vlc":
            # Botões de controle do player VLC
            self.play_button = ctk.CTkButton(
                self.controls_frame,
                text="▶",
                width=30,
                command=self.toggle_play
            )
            self.play_button.pack(side=tk.LEFT, padx=5)
            
            self.stop_button = ctk.CTkButton(
                self.controls_frame,
                text="⏹",
                width=30,
                command=self.stop_video
            )
            self.stop_button.pack(side=tk.LEFT, padx=5)
            
            # Barra de progresso do vídeo
            self.video_progress = ctk.CTkProgressBar(self.controls_frame)
            self.video_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.video_progress.set(0)
            
            # Label de tempo
            self.time_label = ctk.CTkLabel(self.controls_frame, text="00:00 / 00:00")
            self.time_label.pack(side=tk.LEFT, padx=5)
            
            # Controle de volume
            self.volume_slider = ctk.CTkSlider(
                self.controls_frame,
                from_=0,
                to=100,
                command=self.set_volume
            )
            self.volume_slider.pack(side=tk.LEFT, padx=5)
            self.volume_slider.set(100)
        else:  # MPV
            # Botões de controle do player MPV
            self.play_button = ctk.CTkButton(
                self.controls_frame,
                text="▶",
                width=30,
                command=self.toggle_play
            )
            self.play_button.pack(side=tk.LEFT, padx=5)
            
            self.stop_button = ctk.CTkButton(
                self.controls_frame,
                text="⏹",
                width=30,
                command=self.stop_video
            )
            self.stop_button.pack(side=tk.LEFT, padx=5)
            
            # Controle de volume
            self.volume_slider = ctk.CTkSlider(
                self.controls_frame,
                from_=0,
                to=100,
                command=self.set_volume
            )
            self.volume_slider.pack(side=tk.LEFT, padx=5)
            self.volume_slider.set(100)
            
    def change_user_agent(self, choice):
        """Muda o User-Agent"""
        if choice == "Custom...":
            # Mostra o campo de entrada personalizado
            self.ua_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.ua_entry.bind("<Return>", lambda e: self.set_custom_user_agent())
        else:
            # Esconde o campo de entrada personalizado
            self.ua_entry.pack_forget()
            self.user_agent = choice
            
    def set_custom_user_agent(self):
        """Define um User-Agent personalizado"""
        custom_ua = self.ua_entry.get().strip()
        if custom_ua:
            self.user_agent = custom_ua
            
    def copy_link(self):
        """Copia o link do item selecionado para a área de transferência"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione um item primeiro.")
                return
                
            # Pega os valores do item selecionado
            values = self.tree.item(selection[0])['values']
            url = values[4]  # O link está na quinta coluna
            
            # Copia para a área de transferência
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            
            messagebox.showinfo("Sucesso", "Link copiado para a área de transferência!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar link: {str(e)}")
            
    def open_in_browser(self):
        """Abre o link do item selecionado no navegador padrão"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione um item primeiro.")
                return
                
            # Pega os valores do item selecionado
            values = self.tree.item(selection[0])['values']
            url = values[4]  # O link está na quinta coluna
            
            # Abre no navegador padrão
            webbrowser.open(url)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir no navegador: {str(e)}")

if __name__ == "__main__":
    app = PesquisaPlaylist()
    app.run()