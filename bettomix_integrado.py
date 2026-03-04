# ===========================================
# BETTO MIX CONCRETO - Sistema Integrado
# Diretório Atual: $(Get-Location)
# ===========================================

import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import platform
import psutil

class SistemaBettoMixIntegrado:
    def __init__(self):
        # Informações do sistema atual
        self.diretorio_atual = os.getcwd()
        self.usuario = os.environ.get('USERNAME', 'Usuário')
        self.data_inicio = datetime.now()
        
        # Verificar ambiente virtual
        self.venv_ativo = self.verificar_venv()
        
        # Criar janela principal
        self.root = tk.Tk()
        self.root.title(f"BETTO MIX CONCRETO - {self.diretorio_atual}")
        self.root.geometry("1200x700")
        
        # Configurar tema
        self.setup_theme()
        
        # Criar interface
        self.setup_ui()
        
        # Carregar dados locais
        self.carregar_dados_locais()
        
    def verificar_venv(self):
        """Verifica se está em ambiente virtual"""
        return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    def setup_theme(self):
        """Configura o tema da interface"""
        self.root.configure(bg='#2c3e50')
        
    def carregar_dados_locais(self):
        """Carrega dados do diretório atual"""
        self.arquivos_locais = []
        self.pastas_locais = []
        
        try:
            for item in os.listdir(self.diretorio_atual):
                caminho = os.path.join(self.diretorio_atual, item)
                if os.path.isfile(caminho):
                    self.arquivos_locais.append(item)
                elif os.path.isdir(caminho):
                    self.pastas_locais.append(item)
        except Exception as e:
            print(f"Erro ao listar diretório: {e}")
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cabeçalho
        self.criar_cabecalho(main_frame)
        
        # Painel esquerdo (Informações do sistema)
        self.criar_painel_esquerdo(main_frame)
        
        # Painel central (Controles)
        self.criar_painel_central(main_frame)
        
        # Painel direito (Informações do diretório)
        self.criar_painel_direito(main_frame)
        
        # Rodapé
        self.criar_rodape(main_frame)
    
    def criar_cabecalho(self, parent):
        """Cria o cabeçalho da interface"""
        header = tk.Frame(parent, bg='#e67e22', height=80)
        header.pack(fill=tk.X, pady=(0, 10))
        header.pack_propagate(False)
        
        # Logo e título
        tk.Label(header, text="🏗️ BETTO MIX CONCRETO", 
                font=("Arial", 24, "bold"), 
                bg='#e67e22', fg='white').pack(pady=20)
        
        # Subtítulo
        tk.Label(header, text=f"Diretório: {os.path.basename(self.diretorio_atual)}", 
                font=("Arial", 10), 
                bg='#e67e22', fg='#f1c40f').pack()
    
    def criar_painel_esquerdo(self, parent):
        """Cria o painel esquerdo com informações do sistema"""
        left_frame = tk.Frame(parent, bg='#34495e', width=300, relief=tk.RAISED, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Título do painel
        tk.Label(left_frame, text="📊 SISTEMA ATUAL", 
                font=("Arial", 14, "bold"), 
                bg='#34495e', fg='white').pack(pady=15)
        
        # Informações do sistema
        info_frame = tk.Frame(left_frame, bg='#2c3e50')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        infos = [
            ("👤 Usuário:", self.usuario),
            ("📁 Diretório:", os.path.basename(self.diretorio_atual)),
            ("🐍 Python:", platform.python_version()),
            ("💻 Sistema:", f"{platform.system()} {platform.release()}"),
            ("🏭 Ambiente:", "Virtual (.venv)" if self.venv_ativo else "Local"),
            ("📅 Início:", self.data_inicio.strftime("%d/%m/%Y %H:%M"))
        ]
        
        for label, valor in infos:
            frame = tk.Frame(info_frame, bg='#2c3e50')
            frame.pack(fill=tk.X, pady=3)
            
            tk.Label(frame, text=label, font=("Arial", 10, "bold"), 
                    bg='#2c3e50', fg='#3498db', width=12, anchor="w").pack(side=tk.LEFT)
            tk.Label(frame, text=valor, font=("Arial", 10), 
                    bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Status do ambiente
        status_frame = tk.Frame(left_frame, bg='#2c3e50')
        status_frame.pack(pady=10)
        
        status_text = "✅ AMBIENTE VIRTUAL ATIVO" if self.venv_ativo else "⚠️ AMBIENTE LOCAL"
        status_color = '#2ecc71' if self.venv_ativo else '#f39c12'
        
        tk.Label(status_frame, text=status_text, 
                font=("Arial", 11, "bold"), 
                bg='#2c3e50', fg=status_color).pack()
    
    def criar_painel_central(self, parent):
        """Cria o painel central com controles principais"""
        center_frame = tk.Frame(parent, bg='#2c3e50')
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Título
        tk.Label(center_frame, text="🚀 CONTROLES PRINCIPAIS", 
                font=("Arial", 16, "bold"), 
                bg='#2c3e50', fg='white').pack(pady=(0, 15))
        
        # Frame para botões
        buttons_frame = tk.Frame(center_frame, bg='#2c3e50')
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botões de ação
        botoes = [
            ("📁 ABRIR DESKTOP", self.abrir_desktop_profissional, "#e67e22"),
            ("🔍 ABRIR EXPLORER", self.abrir_explorer, "#3498db"),
            ("💻 ABRIR TERMINAL", self.abrir_terminal, "#9b59b6"),
            ("📂 ABRIR DIRETÓRIO", self.abrir_diretorio_atual, "#2ecc71"),
            ("⚙️ CONFIGURAÇÕES", self.abrir_configuracoes, "#f39c12"),
            ("📊 INFORMAÇÕES", self.mostrar_info_completa, "#1abc9c"),
            ("🧹 LIMPEZA", self.limpar_sistema, "#e74c3c"),
            ("💾 BACKUP", self.criar_backup, "#34495e")
        ]
        
        for i in range(0, len(botoes), 2):
            row_frame = tk.Frame(buttons_frame, bg='#2c3e50')
            row_frame.pack(fill=tk.X, pady=5)
            
            for j in range(2):
                if i + j < len(botoes):
                    texto, comando, cor = botoes[i + j]
                    
                    btn = tk.Button(row_frame, text=texto, command=comando,
                                  font=("Arial", 11, "bold"),
                                  bg=cor, fg='white',
                                  height=2, width=20,
                                  cursor='hand2',
                                  relief=tk.RAISED,
                                  bd=2)
                    btn.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Área de status
        self.status_area = scrolledtext.ScrolledText(center_frame, 
                                                    height=8,
                                                    font=("Consolas", 9),
                                                    bg='#1a1a2e',
                                                    fg='#00ff00')
        self.status_area.pack(fill=tk.X, pady=(15, 0))
        self.status_area.insert(tk.END, "Sistema BETTO MIX inicializado...\n")
        self.status_area.insert(tk.END, f"Diretório: {self.diretorio_atual}\n")
        self.status_area.insert(tk.END, f"Ambiente Virtual: {'Ativo' if self.venv_ativo else 'Inativo'}\n")
        self.status_area.configure(state='disabled')
        
        # Botão para atualizar status
        tk.Button(center_frame, text="🔄 ATUALIZAR STATUS", 
                 command=self.atualizar_status,
                 font=("Arial", 10),
                 bg='#7f8c8d', fg='white').pack(pady=10)
    
    def criar_painel_direito(self, parent):
        """Cria o painel direito com informações do diretório"""
        right_frame = tk.Frame(parent, bg='#34495e', width=300, relief=tk.RAISED, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Título
        tk.Label(right_frame, text="📂 CONTEÚDO LOCAL", 
                font=("Arial", 14, "bold"), 
                bg='#34495e', fg='white').pack(pady=15)
        
        # Frame com scroll para arquivos
        file_frame = tk.Frame(right_frame, bg='#2c3e50')
        file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Área de arquivos
        tk.Label(file_frame, text="📁 Pastas:", 
                font=("Arial", 11, "bold"), 
                bg='#2c3e50', fg='#3498db').pack(anchor="w")
        
        self.pastas_listbox = tk.Listbox(file_frame, 
                                        height=8,
                                        font=("Consolas", 9),
                                        bg='#1a1a2e',
                                        fg='#ffffff',
                                        selectbackground='#e67e22')
        self.pastas_listbox.pack(fill=tk.X, pady=(5, 10))
        
        # Arquivos
        tk.Label(file_frame, text="📄 Arquivos:", 
                font=("Arial", 11, "bold"), 
                bg='#2c3e50', fg='#3498db').pack(anchor="w")
        
        self.arquivos_listbox = tk.Listbox(file_frame, 
                                          height=8,
                                          font=("Consolas", 9),
                                          bg='#1a1a2e',
                                          fg='#ffffff',
                                          selectbackground='#e67e22')
        self.arquivos_listbox.pack(fill=tk.X, pady=(5, 0))
        
        # Atualizar listas
        self.atualizar_listas_arquivos()
        
        # Botões para ações no diretório
        btn_frame = tk.Frame(right_frame, bg='#2c3e50')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Abrir Pasta", 
                 command=self.abrir_pasta_selecionada,
                 font=("Arial", 9),
                 bg='#27ae60', fg='white',
                 width=12).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Atualizar", 
                 command=self.atualizar_listas_arquivos,
                 font=("Arial", 9),
                 bg='#3498db', fg='white',
                 width=12).pack(side=tk.LEFT, padx=2)
    
    def criar_rodape(self, parent):
        """Cria o rodapé da interface"""
        footer = tk.Frame(parent, bg='#1a1a2e', height=40)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        footer.pack_propagate(False)
        
        # Informações no rodapé
        tk.Label(footer, text=f"BETTO MIX CONCRETO | Diretório: {self.diretorio_atual}", 
                font=("Arial", 9), 
                bg='#1a1a2e', fg='#7f8c8d').pack(side=tk.LEFT, padx=10, pady=10)
        
        # Hora atual
        self.hora_label = tk.Label(footer, 
                                  font=("Arial", 9), 
                                  bg='#1a1a2e', fg='#f1c40f')
        self.hora_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Iniciar atualização da hora
        self.atualizar_hora()
    
    def atualizar_listas_arquivos(self):
        """Atualiza as listas de arquivos e pastas"""
        self.pastas_listbox.delete(0, tk.END)
        self.arquivos_listbox.delete(0, tk.END)
        
        try:
            for item in os.listdir(self.diretorio_atual):
                caminho = os.path.join(self.diretorio_atual, item)
                if os.path.isdir(caminho):
                    self.pastas_listbox.insert(tk.END, f"📁 {item}")
                elif os.path.isfile(caminho):
                    tamanho = os.path.getsize(caminho)
                    tamanho_str = self.formatar_tamanho(tamanho)
                    self.arquivos_listbox.insert(tk.END, f"📄 {item} ({tamanho_str})")
        except Exception as e:
            self.adicionar_status(f"Erro ao listar diretório: {e}")
    
    def formatar_tamanho(self, tamanho):
        """Formata o tamanho do arquivo"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if tamanho < 1024.0:
                return f"{tamanho:.1f} {unit}"
            tamanho /= 1024.0
        return f"{tamanho:.1f} TB"
    
    def atualizar_hora(self):
        """Atualiza a hora no rodapé"""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.hora_label.config(text=agora)
        self.root.after(1000, self.atualizar_hora)
    
    def adicionar_status(self, mensagem):
        """Adiciona mensagem à área de status"""
        self.status_area.configure(state='normal')
        self.status_area.insert(tk.END, f"\n{datetime.now().strftime('%H:%M:%S')} - {mensagem}")
        self.status_area.see(tk.END)
        self.status_area.configure(state='disabled')
    
    def atualizar_status(self):
        """Atualiza o status do sistema"""
        try:
            # Informações do sistema
            cpu = psutil.cpu_percent()
            memoria = psutil.virtual_memory()
            disco = psutil.disk_usage(self.diretorio_atual)
            
            self.status_area.configure(state='normal')
            self.status_area.delete(1.0, tk.END)
            
            self.status_area.insert(tk.END, "=== STATUS DO SISTEMA ===\n")
            self.status_area.insert(tk.END, f"CPU: {cpu}%\n")
            self.status_area.insert(tk.END, f"Memória: {memoria.percent}%\n")
            self.status_area.insert(tk.END, f"Disco: {disco.percent}%\n")
            self.status_area.insert(tk.END, f"Diretório: {self.diretorio_atual}\n")
            self.status_area.insert(tk.END, f"Arquivos: {len(self.arquivos_locais)}\n")
            self.status_area.insert(tk.END, f"Pastas: {len(self.pastas_locais)}\n")
            self.status_area.insert(tk.END, f"Ambiente Virtual: {'Ativo' if self.venv_ativo else 'Inativo'}\n")
            
            self.status_area.configure(state='disabled')
            self.adicionar_status("Status atualizado com sucesso!")
            
        except Exception as e:
            self.adicionar_status(f"Erro ao atualizar status: {e}")
    
    # ============ FUNÇÕES DE AÇÃO ============
    
    def abrir_desktop_profissional(self):
        """Abre a área de trabalho de forma profissional"""
        try:
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            subprocess.Popen(f'explorer "{desktop_path}"')
            self.adicionar_status("Área de trabalho aberta")
            messagebox.showinfo("Sucesso", "Desktop aberto em modo profissional!")
        except Exception as e:
            self.adicionar_status(f"Erro ao abrir desktop: {e}")
            messagebox.showerror("Erro", f"Não foi possível abrir o desktop: {e}")
    
    def abrir_explorer(self):
        """Abre o explorador de arquivos"""
        try:
            subprocess.Popen('explorer')
            self.adicionar_status("Explorador de arquivos aberto")
        except Exception as e:
            self.adicionar_status(f"Erro ao abrir explorer: {e}")
    
    def abrir_terminal(self):
        """Abre o terminal PowerShell no diretório atual"""
        try:
            subprocess.Popen(['powershell', '-NoExit', '-Command', f'cd "{self.diretorio_atual}"'])
            self.adicionar_status("Terminal PowerShell aberto no diretório atual")
        except Exception as e:
            self.adicionar_status(f"Erro ao abrir terminal: {e}")
    
    def abrir_diretorio_atual(self):
        """Abre o diretório atual no explorador"""
        try:
            subprocess.Popen(f'explorer "{self.diretorio_atual}"')
            self.adicionar_status("Diretório atual aberto no explorador")
        except Exception as e:
            self.adicionar_status(f"Erro ao abrir diretório: {e}")
    
    def abrir_configuracoes(self):
        """Abre as configurações do Windows"""
        try:
            subprocess.Popen('start ms-settings:')
            self.adicionar_status("Configurações do Windows abertas")
        except Exception as e:
            self.adicionar_status(f"Erro ao abrir configurações: {e}")
    
    def mostrar_info_completa(self):
        """Mostra informações completas do sistema"""
        try:
            info = f"""
            ╔══════════════════════════════════════════════╗
            ║      BETTO MIX CONCRETO - INFORMAÇÕES       ║
            ╠══════════════════════════════════════════════╣
            
            📊 SISTEMA:
            • Usuário: {self.usuario}
            • Diretório: {self.diretorio_atual}
            • Python: {platform.python_version()}
            • Sistema: {platform.system()} {platform.release()}
            
            📁 CONTEÚDO LOCAL:
            • Pastas: {len(self.pastas_locais)} itens
            • Arquivos: {len(self.arquivos_locais)} itens
            • Ambiente Virtual: {'✅ ATIVO (.venv)' if self.venv_ativo else '❌ INATIVO'}
            
            ╠══════════════════════════════════════════════╣
            
            🚀 COMANDOS DISPONÍVEIS:
            • Abrir Desktop: Modo profissional
            • Abrir Explorer: Navegador de arquivos
            • Abrir Terminal: PowerShell no diretório
            • Limpeza: Arquivos temporários
            • Backup: Cópia de segurança
            
            ╚══════════════════════════════════════════════╝
            """
            
            # Criar janela de informações
            info_window = tk.Toplevel(self.root)
            info_window.title("Informações Completas")
            info_window.geometry("600x500")
            info_window.configure(bg='#2c3e50')
            
            text_area = scrolledtext.ScrolledText(info_window, 
                                                 font=("Consolas", 10),
                                                 bg='#1a1a2e',
                                                 fg='#00ff00',
                                                 wrap=tk.WORD)
            text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_area.insert(tk.END, info)
            text_area.configure(state='disabled')
            
            self.adicionar_status("Informações do sistema exibidas")
            
        except Exception as e:
            self.adicionar_status(f"Erro ao mostrar informações: {e}")
    
    def limpar_sistema(self):
        """Limpa arquivos temporários"""
        try:
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp')
            ]
            
            limpos = 0
            for path in temp_paths:
                if os.path.exists(path):
                    for item in os.listdir(path):
                        try:
                            item_path = os.path.join(path, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                limpos += 1
                        except:
                            pass
            
            self.adicionar_status(f"Limpeza concluída: {limpos} arquivos removidos")
            messagebox.showinfo("Limpeza", f"{limpos} arquivos temporários removidos!")
            
        except Exception as e:
            self.adicionar_status(f"Erro na limpeza: {e}")
            messagebox.showerror("Erro", f"Não foi possível limpar: {e}")
    
    def criar_backup(self):
        """Cria um backup do diretório atual"""
        try:
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_bettomix_{data_str}.zip"
            backup_path = os.path.join(desktop_path, backup_name)
            
            import zipfile
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.diretorio_atual):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.diretorio_atual)
                        zipf.write(file_path, arcname)
            
            self.adicionar_status(f"Backup criado: {backup_path}")
            messagebox.showinfo("Backup", f"Backup criado com sucesso!\n\nLocal: {backup_path}")
            
            # Abrir local do backup
            subprocess.Popen(f'explorer /select,"{backup_path}"')
            
        except Exception as e:
            self.adicionar_status(f"Erro no backup: {e}")
            messagebox.showerror("Erro", f"Não foi possível criar backup: {e}")
    
    def abrir_pasta_selecionada(self):
        """Abre a pasta selecionada na lista"""
        try:
            selecao = self.pastas_listbox.curselection()
            if selecao:
                nome_pasta = self.pastas_listbox.get(selecao[0])
                nome_pasta = nome_pasta.replace("📁 ", "").strip()
                caminho_pasta = os.path.join(self.diretorio_atual, nome_pasta)
                
                if os.path.exists(caminho_pasta):
                    subprocess.Popen(f'explorer "{caminho_pasta}"')
                    self.adicionar_status(f"Pasta aberta: {nome_pasta}")
                else:
                    messagebox.showwarning("Aviso", f"Pasta não encontrada: {nome_pasta}")
            else:
                messagebox.showinfo("Info", "Selecione uma pasta primeiro")
        except Exception as e:
            self.adicionar_status(f"Erro ao abrir pasta: {e}")
    
    def run(self):
        """Executa o sistema"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"O sistema encontrou um erro:\n{e}")

# ===========================================
# EXECUÇÃO PRINCIPAL
# ===========================================
if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO BETTO MIX CONCRETO - SISTEMA INTEGRADO")
    print("=" * 60)
    print(f"Diretório: {os.getcwd()}")
    print(f"Usuário: {os.environ.get('USERNAME', 'N/A')}")
    print(f"Ambiente Virtual: {'Ativo' if hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix else 'Inativo'}")
    print("=" * 60)
    
    try:
        app = SistemaBettoMixIntegrado()
        app.run()
        print("Sistema finalizado com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar sistema: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
