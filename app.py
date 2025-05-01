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
import sys

# Adiciona o diretório atual ao path do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from player import Player
from database import Database

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
        
        # Inicializa componentes
        self.db = Database()
        self.player = Player()
        
        # Criar interface
        self.criar_interface()
        
    def criar_interface(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior para botões e entrada
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botão Carregar DB
        self.btn_carregar_db = ctk.CTkButton(
            self.top_frame,
            text="Carregar Banco de Dados",
            command=self.carregar_banco
        )
        self.btn_carregar_db.pack(side=tk.LEFT, padx=5)
        
        # Botão Carregar Vários Links
        self.btn_carregar_links = ctk.CTkButton(
            self.top_frame,
            text="Carregar Vários Links",
            command=self.carregar_varios_links
        )
        self.btn_carregar_links.pack(side=tk.LEFT, padx=5)
        
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
        
        # Frame esquerdo para lista
        self.left_frame = ctk.CTkFrame(self.content_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Frame direito para player
        self.right_frame = ctk.CTkFrame(self.content_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Treeview para resultados
        self.tree = ttk.Treeview(
            self.left_frame,
            columns=("Nome", "Tipo", "Temporada", "Servidor"),
            show="headings"
        )
        
        # Configurar colunas
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Temporada", text="Temporada")
        self.tree.heading("Servidor", text="Servidor")
        
        # Configurar larguras das colunas
        self.tree.column("Nome", width=400)
        self.tree.column("Tipo", width=100)
        self.tree.column("Temporada", width=100)
        self.tree.column("Servidor", width=200)
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar Treeview e Scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar player
        self.player.setup_player(self.right_frame)
        
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
        
    def carregar_varios_links(self):
        """Abre janela para carregar vários links"""
        # Criar janela
        janela = ctk.CTk()
        janela.title("Carregar Vários Links")
        janela.geometry("600x400")
        
        # Frame principal
        frame = ctk.CTkFrame(janela)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label de instrução
        label = ctk.CTkLabel(
            frame,
            text="Cole os links M3U (um por linha):"
        )
        label.pack(pady=5)
        
        # Área de texto
        text_area = ctk.CTkTextbox(frame)
        text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para botões
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Barra de progresso
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            btn_frame,
            variable=progress_var,
            maximum=100
        )
        progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Label de status
        status_label = ctk.CTkLabel(btn_frame, text="")
        status_label.pack(pady=5)
        
        def processar_links():
            """Processa os links inseridos"""
            links = text_area.get("1.0", tk.END).strip().split("\n")
            total = len(links)
            processados = 0
            
            # Limpar dados M3U anteriores
            self.dados_m3u = []
            
            for link in links:
                if not link.strip():
                    continue
                    
                try:
                    response = requests.get(link.strip())
                    response.raise_for_status()
                    
                    # Processar arquivo M3U
                    linhas = response.text.split('\n')
                    nome_atual = ""
                    
                    for linha in linhas:
                        linha = linha.strip()
                        if linha.startswith('#EXTINF:'):
                            # Extrair nome do vídeo
                            nome_atual = re.search(r',(.*?)$', linha)
                            if nome_atual:
                                nome_atual = nome_atual.group(1)
                        elif linha.startswith('http'):
                            # Adicionar entrada à lista
                            if nome_atual:
                                tipo = "Filme"
                                temporada = ""
                                if "S0" in nome_atual or "S1" in nome_atual:
                                    tipo = "Série"
                                    temp = re.search(r'S(\d+)', nome_atual)
                                    if temp:
                                        temporada = f"Temporada {temp.group(1)}"
                                
                                self.dados_m3u.append((nome_atual, tipo, temporada, linha))
                                nome_atual = ""
                    
                    processados += 1
                    progress = (processados / total) * 100
                    progress_var.set(progress)
                    status_label.configure(text=f"Processando... {processados}/{total}")
                    janela.update()
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao processar link: {str(e)}")
            
            # Atualizar interface
            status_label.configure(text="Concluído!")
            self.filtrar_resultados()
            
        # Botão Processar
        btn_processar = ctk.CTkButton(
            btn_frame,
            text="Processar Links",
            command=processar_links
        )
        btn_processar.pack(side=tk.LEFT, padx=5)
        
        # Botão Cancelar
        btn_cancelar = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=janela.destroy
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Iniciar janela
        janela.mainloop()
        
    def on_tree_double_click(self, event):
        """Manipula duplo clique na treeview"""
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
                    url = item[3]
                    break
        
        if url:
            self.player.play_video(url)
            
    def carregar_banco(self):
        """Carrega dados do banco de dados"""
        try:
            self.dados_db = self.db.carregar_videos()
            messagebox.showinfo("Sucesso", "Banco de dados carregado com sucesso!")
            self.filtrar_resultados()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
            
    def carregar_m3u(self):
        """Carrega dados do arquivo M3U via URL"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira uma URL válida.")
            return
            
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Limpar dados M3U anteriores
            self.dados_m3u = []
            
            # Processar arquivo M3U
            linhas = response.text.split('\n')
            nome_atual = ""
            
            for linha in linhas:
                linha = linha.strip()
                if linha.startswith('#EXTINF:'):
                    # Extrair nome do vídeo
                    nome_atual = re.search(r',(.*?)$', linha)
                    if nome_atual:
                        nome_atual = nome_atual.group(1)
                elif linha.startswith('http'):
                    # Adicionar entrada à lista
                    if nome_atual:
                        tipo = "Filme"
                        temporada = ""
                        if "S0" in nome_atual or "S1" in nome_atual:
                            tipo = "Série"
                            temp = re.search(r'S(\d+)', nome_atual)
                            if temp:
                                temporada = f"Temporada {temp.group(1)}"
                        
                        self.dados_m3u.append((nome_atual, tipo, temporada, linha))
                        nome_atual = ""
            
            messagebox.showinfo("Sucesso", "Arquivo M3U carregado com sucesso!")
            self.filtrar_resultados()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo M3U: {str(e)}")
            
    def extrair_servidor(self, url):
        """Extrai o nome do servidor da URL"""
        try:
            # Remove o protocolo (http:// ou https://)
            url_sem_protocolo = re.sub(r'^https?://', '', url)
            
            # Pega a primeira parte da URL (antes da primeira barra)
            servidor = url_sem_protocolo.split('/')[0]
            
            # Remove a porta se existir
            servidor = servidor.split(':')[0]
            
            return servidor
        except:
            return "Desconhecido"
            
    def filtrar_resultados(self):
        """Filtra e exibe os resultados com base no termo de pesquisa"""
        # Limpar resultados anteriores
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Obter termo de pesquisa
        termo = self.search_entry.get().strip().lower()
        
        # Combinar dados do banco de dados e do M3U
        todos_dados = []
        
        # Adicionar dados do banco de dados
        for item in self.dados_db:
            nome, tipo, temporada, url = item
            servidor = self.extrair_servidor(url)
            if not termo or termo in nome.lower():
                todos_dados.append((nome, tipo, temporada, servidor))
        
        # Adicionar dados do M3U
        for item in self.dados_m3u:
            nome, tipo, temporada, url = item
            servidor = self.extrair_servidor(url)
            if not termo or termo in nome.lower():
                todos_dados.append((nome, tipo, temporada, servidor))
        
        # Ordenar resultados por nome
        todos_dados.sort(key=lambda x: x[0].lower())
        
        # Inserir resultados na treeview
        for item in todos_dados:
            self.tree.insert("", tk.END, values=item)
            
    def run(self):
        """Inicia o programa"""
        self.root.mainloop() 