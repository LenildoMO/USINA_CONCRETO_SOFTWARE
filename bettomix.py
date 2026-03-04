# ===========================================
# BETTO MIX CONCRETO - Sistema Simplificado
# ===========================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
import json
from datetime import datetime

class BettoMixSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BETTO MIX CONCRETO - Sistema Profissional")
        self.root.geometry("1000x600")
        
        # Configurar cores
        self.colors = {
            'primary': '#e67e22',
            'secondary': '#2c3e50',
            'background': '#ecf0f1',
            'text': '#2c3e50',
            'button': '#3498db',
            'success': '#27ae60',
            'danger': '#e74c3c'
        }
        
        # Configurar ícone (opcional)
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # Criar interface
        self.setup_ui()
        
        # Centralizar janela
        self.center_window()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = tk.Frame(main_frame, bg=self.colors['secondary'], height=100)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Logo e título
        title_label = tk.Label(header_frame, 
                             text="🏗️ BETTO MIX CONCRETO",
                             font=("Arial", 24, "bold"),
                             fg="white",
                             bg=self.colors['secondary'])
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(header_frame,
                                text="Sistema Profissional de Gerenciamento",
                                font=("Arial", 10),
                                fg="#bdc3c7",
                                bg=self.colors['secondary'])
        subtitle_label.pack()
        
        # Frame de conteúdo
        content_frame = tk.Frame(main_frame, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Painel esquerdo - Menu
        left_panel = tk.Frame(content_frame, bg=self.colors['secondary'], width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Itens do menu
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("🏭 Produção", self.show_production),
            ("💰 Orçamentos", self.show_budget),
            ("👥 Clientes", self.show_clients),
            ("📦 Estoque", self.show_stock),
            ("📈 Relatórios", self.show_reports),
            ("💻 Sistema", self.show_system)
        ]
        
        for text, command in menu_items:
            btn = tk.Button(left_panel, 
                          text=text,
                          command=command,
                          font=("Arial", 11),
                          bg=self.colors['secondary'],
                          fg="white",
                          bd=0,
                          padx=20,
                          pady=10,
                          anchor="w",
                          relief=tk.FLAT,
                          cursor="hand2")
            btn.pack(fill=tk.X, pady=2)
            
            # Efeito hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#34495e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['secondary']))
        
        # Painel direito - Conteúdo
        self.right_panel = tk.Frame(content_frame, bg="white")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Mostrar dashboard inicial
        self.show_dashboard()
        
        # Barra de status
        status_frame = tk.Frame(main_frame, bg=self.colors['secondary'], height=30)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame,
                              text=f"Usuário: {os.environ.get('USERNAME', 'Convidado')} | Sistema: {sys.platform}",
                              font=("Arial", 9),
                              fg="#bdc3c7",
                              bg=self.colors['secondary'])
        status_label.pack(side=tk.LEFT, padx=10)
        
        time_label = tk.Label(status_frame,
                            text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            font=("Arial", 9),
                            fg="#bdc3c7",
                            bg=self.colors['secondary'])
        time_label.pack(side=tk.RIGHT, padx=10)
        
        # Atualizar hora
        def update_time():
            time_label.config(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            self.root.after(1000, update_time)
        
        update_time()
    
    def show_dashboard(self):
        """Mostra o dashboard principal"""
        self.clear_right_panel()
        
        # Título
        title = tk.Label(self.right_panel,
                        text="📊 Dashboard BETTO MIX",
                        font=("Arial", 20, "bold"),
                        bg="white",
                        fg=self.colors['text'])
        title.pack(pady=(20, 10))
        
        # Cards de informações
        cards_frame = tk.Frame(self.right_panel, bg="white")
        cards_frame.pack(pady=10)
        
        cards = [
            ("Produção Diária", "125 m³", "#e67e22"),
            ("Orçamentos Ativos", "8", "#3498db"),
            ("Clientes", "24", "#2ecc71"),
            ("Estoque Crítico", "3", "#e74c3c")
        ]
        
        for i, (title_text, value, color) in enumerate(cards):
            card = tk.Frame(cards_frame, 
                          bg=color, 
                          relief=tk.RAISED, 
                          bd=2,
                          width=180,
                          height=120)
            card.grid(row=0, column=i, padx=10, pady=10)
            card.grid_propagate(False)
            
            # Conteúdo do card
            tk.Label(card, 
                    text=title_text,
                    font=("Arial", 11, "bold"),
                    bg=color,
                    fg="white").pack(pady=(15, 5))
            
            tk.Label(card,
                    text=value,
                    font=("Arial", 18, "bold"),
                    bg=color,
                    fg="white").pack(pady=5)
        
        # Botões de ação rápida
        actions_frame = tk.Frame(self.right_panel, bg="white")
        actions_frame.pack(pady=30)
        
        tk.Label(actions_frame,
                text="🚀 Ações Rápidas",
                font=("Arial", 16, "bold"),
                bg="white",
                fg=self.colors['text']).pack(pady=(0, 15))
        
        actions = [
            ("📁 Abrir Desktop", self.open_desktop),
            ("🔍 Abrir Explorer", self.open_explorer),
            ("💻 Abrir Terminal", self.open_terminal),
            ("📂 Abrir Documentos", self.open_documents),
            ("🧹 Limpar Sistema", self.clean_system),
            ("📊 Info Sistema", self.show_system_info)
        ]
        
        for i in range(0, len(actions), 3):
            row_frame = tk.Frame(actions_frame, bg="white")
            row_frame.pack(pady=5)
            
            for j in range(3):
                if i + j < len(actions):
                    text, command = actions[i + j]
                    btn = tk.Button(row_frame,
                                  text=text,
                                  command=command,
                                  font=("Arial", 11),
                                  bg=self.colors['button'],
                                  fg="white",
                                  width=20,
                                  height=2,
                                  cursor="hand2")
                    btn.grid(row=0, column=j, padx=5)
    
    def clear_right_panel(self):
        """Limpa o painel direito"""
        for widget in self.right_panel.winfo_children():
            widget.destroy()
    
    def show_production(self):
        self.clear_right_panel()
        tk.Label(self.right_panel,
                text="🏭 Controle de Produção",
                font=("Arial", 20, "bold"),
                bg="white").pack(pady=50)
    
    def show_budget(self):
        self.clear_right_panel()
        tk.Label(self.right_panel,
                text="💰 Gestão de Orçamentos",
                font=("Arial", 20, "bold"),
                bg="white").pack(pady=50)
    
    def show_clients(self):
        self.clear_right_panel()
        tk.Label(self.right_panel,
                text="👥 Cadastro de Clientes",
                font=("Arial", 20, "bold"),
                bg="white").pack(pady=50)
    
    def show_stock(self):
        self.clear_right_panel()
        tk.Label(self.right_panel,
                text="📦 Controle de Estoque",
                font=("Arial", 20, "bold"),
                bg="white").pack(pady=50)
    
    def show_reports(self):
        self.clear_right_panel()
        tk.Label(self.right_panel,
                text="📈 Relatórios do Sistema",
                font=("Arial", 20, "bold"),
                bg="white").pack(pady=50)
    
    def show_system(self):
        self.clear_right_panel()
        tk.Label(self.right_panel,
                text="⚙️ Configurações do Sistema",
                font=("Arial", 20, "bold"),
                bg="white").pack(pady=50)
    
    # Funções de ação
    def open_desktop(self):
        try:
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            subprocess.Popen(f'explorer "{desktop_path}"')
            messagebox.showinfo("Sucesso", "Desktop aberto com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o desktop: {e}")
    
    def open_explorer(self):
        try:
            subprocess.Popen('explorer')
            messagebox.showinfo("Sucesso", "Explorador de arquivos aberto!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o explorer: {e}")
    
    def open_terminal(self):
        try:
            subprocess.Popen('powershell')
            messagebox.showinfo("Sucesso", "Terminal PowerShell aberto!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o terminal: {e}")
    
    def open_documents(self):
        try:
            docs_path = os.path.join(os.environ['USERPROFILE'], 'Documents')
            subprocess.Popen(f'explorer "{docs_path}"')
            messagebox.showinfo("Sucesso", "Pasta Documentos aberta!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir os documentos: {e}")
    
    def clean_system(self):
        try:
            # Limpar arquivos temporários
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', '')
            ]
            
            for path in temp_paths:
                if os.path.exists(path):
                    for file in os.listdir(path):
                        try:
                            os.remove(os.path.join(path, file))
                        except:
                            pass
            
            messagebox.showinfo("Sucesso", "Sistema limpo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível limpar o sistema: {e}")
    
    def show_system_info(self):
        info = f"""
        Informações do Sistema BETTO MIX:
        
        • Usuário: {os.environ.get('USERNAME', 'N/A')}
        • Sistema Operacional: {sys.platform}
        • Diretório Atual: {os.getcwd()}
        • Python: {sys.version}
        • Ambiente Virtual: {'Ativo (.venv)' if hasattr(sys, 'real_prefix') or sys.prefix != sys.base_prefix else 'Não ativo'}
        
        Caminhos Importantes:
        • Desktop: {os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')}
        • Documentos: {os.path.join(os.environ.get('USERPROFILE', ''), 'Documents')}
        """
        
        messagebox.showinfo("Informações do Sistema", info)
    
    def run(self):
        self.root.mainloop()

# Execução principal
if __name__ == "__main__":
    print("=" * 50)
    print("Iniciando BETTO MIX CONCRETO - Sistema Profissional")
    print("=" * 50)
    
    try:
        app = BettoMixSystem()
        app.run()
        print("Sistema finalizado com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar sistema: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
