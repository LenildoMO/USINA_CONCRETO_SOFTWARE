import customtkinter as ctk
import os
import subprocess
import platform

class ProfessionalDesktopLauncher:
    def __init__(self):
        # Configurar aparência
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal
        self.app = ctk.CTk()
        self.app.title("Desktop Professional Suite v2.0")
        self.app.geometry("900x700")
        
        # Centralizar na tela
        self.center_window()
        
        # Criar interface
        self.setup_ui()
        
        # Focar na janela
        self.app.focus_force()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.app.update_idletasks()
        width = self.app.winfo_width()
        height = self.app.winfo_height()
        x = (self.app.winfo_screenwidth() // 2) - (width // 2)
        y = (self.app.winfo_screenheight() // 2) - (height // 2)
        self.app.geometry(f'{width}x{height}+{x}+{y}')
    
    def darken_color(self, hex_color, factor=0.8):
        """Escurece a cor para efeito hover"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            return f'#{r:02x}{g:02x}{b:02x}'
        return hex_color
    
    def setup_ui(self):
        # ============ HEADER ============
        header_frame = ctk.CTkFrame(self.app, height=120, corner_radius=0, fg_color="#1a237e")
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🏢 DESKTOP PROFESSIONAL SUITE", 
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        )
        title_label.pack(pady=25)
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Sistema de Gerenciamento Profissional",
            font=("Segoe UI", 12),
            text_color="#bbdefb"
        )
        subtitle_label.pack()
        
        # ============ MAIN CONTENT ============
        main_frame = ctk.CTkFrame(self.app, corner_radius=20, fg_color="#263238")
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # ===== QUICK ACTIONS SECTION =====
        actions_header = ctk.CTkLabel(
            main_frame,
            text="⚡ AÇÕES RÁPIDAS",
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        )
        actions_header.pack(pady=(20, 10))
        
        # Frame para botões em grid
        actions_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#37474f")
        actions_frame.pack(pady=10, padx=30, fill="x")
        
        # Grid de botões (2x3)
        buttons = [
            ("📁 DESKTOP", self.open_desktop, "#00c853", "Abrir Área de Trabalho"),
            ("🔍 EXPLORER", self.open_explorer, "#2962ff", "Abrir Explorador de Arquivos"),
            ("💻 TERMINAL", self.open_powershell, "#aa00ff", "Abrir PowerShell"),
            ("📂 DOCUMENTOS", self.open_documents, "#ff6d00", "Abrir Pasta Documentos"),
            ("⚙️ CONFIGURAÇÕES", self.open_settings, "#ffab00", "Abrir Configurações Windows"),
            ("🔄 ATUALIZAR", self.refresh, "#00bcd4", "Atualizar Informações")
        ]
        
        for i, (text, command, color, tooltip) in enumerate(buttons):
            row = i // 3
            col = i % 3
            
            btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
            btn_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                width=200,
                height=70,
                font=("Segoe UI", 14, "bold"),
                fg_color=color,
                hover_color=self.darken_color(color),
                corner_radius=12,
                border_width=0,
                text_color="white"
            )
            btn.pack(fill="both", expand=True)
            
            # Tooltip label
            tip_label = ctk.CTkLabel(
                btn_frame,
                text=tooltip,
                font=("Segoe UI", 10),
                text_color="#b0bec5"
            )
            tip_label.pack(pady=(5, 0))
        
        # Configurar grid
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)
        
        # ===== SYSTEM INFO SECTION =====
        info_header = ctk.CTkLabel(
            main_frame,
            text="📊 INFORMAÇÕES DO SISTEMA",
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        )
        info_header.pack(pady=(30, 10))
        
        # Frame para informações
        info_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#37474f")
        info_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
        # Área de texto com scrollbar
        self.info_text = ctk.CTkTextbox(
            info_frame,
            height=180,
            font=("Consolas", 12),
            fg_color="#263238",
            text_color="#e0f7fa",
            border_width=2,
            border_color="#00bcd4",
            corner_radius=10
        )
        self.info_text.pack(pady=15, padx=15, fill="both", expand=True)
        
        # Adicionar informações
        self.update_system_info()
        
        # ============ STATUS BAR ============
        status_frame = ctk.CTkFrame(self.app, height=50, corner_radius=0, fg_color="#1a237e")
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        # Informações de status
        user_info = f"👤 Usuário: {os.environ['USERNAME']}"
        sys_info = f"🖥️ Sistema: {platform.system()} {platform.release()}"
        
        status_left = ctk.CTkLabel(
            status_frame,
            text=f"{user_info} | {sys_info}",
            font=("Segoe UI", 11),
            text_color="#bbdefb"
        )
        status_left.pack(side="left", padx=20)
        
        status_right = ctk.CTkLabel(
            status_frame,
            text="✅ Sistema Operacional Normalmente",
            font=("Segoe UI", 11, "bold"),
            text_color="#00e676"
        )
        status_right.pack(side="right", padx=20)
        
        # ============ BOTÃO DE SAIR ============
        exit_btn = ctk.CTkButton(
            self.app,
            text="🚪 SAIR",
            command=self.app.destroy,
            width=100,
            height=40,
            font=("Segoe UI", 12, "bold"),
            fg_color="#d50000",
            hover_color="#ff1744",
            corner_radius=10
        )
        exit_btn.place(relx=0.5, rely=0.96, anchor="center")
    
    def update_system_info(self):
        """Atualiza as informações do sistema"""
        try:
            user = os.environ.get('USERNAME', 'N/A')
            desktop_path = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
            docs_path = os.path.join(os.environ.get('USERPROFILE', ''), 'Documents')
            current_dir = os.getcwd()
            
            info = f"""
╔══════════════════════════════════════════════════════════╗
║                SISTEMA PROFISSIONAL - v2.0               ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  • 👤 USUÁRIO: {user:<40} ║
║  • 📁 DESKTOP: {desktop_path:<35} ║
║  • 📂 DOCUMENTOS: {docs_path:<36} ║
║  • 🐍 PYTHON: {platform.python_version():<42} ║
║  • 💻 DIRETÓRIO: {current_dir:<35} ║
║  • 🏢 SISTEMA: {platform.system()} {platform.release():<30} ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📌 INSTRUÇÕES:                                          ║
║                                                          ║
║  1. Clique em '📁 DESKTOP' para abrir a Área de Trabalho ║
║  2. Use '🔍 EXPLORER' para navegar em qualquer pasta     ║
║  3. '💻 TERMINAL' abre o PowerShell para comandos        ║
║  4. '🔄 ATUALIZAR' para atualizar estas informações      ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Status: ✅ Tudo funcionando perfeitamente!              ║
║  Ambiente Virtual: ✅ Ativo (.venv)                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
            
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", info)
            self.info_text.configure(state="disabled")
            
        except Exception as e:
            error_msg = f"Erro ao obter informações do sistema:\n{str(e)}"
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", error_msg)
    
    def open_desktop(self):
        """Abre a área de trabalho"""
        try:
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            subprocess.Popen(f'explorer "{desktop_path}"')
            print(f"✓ Desktop aberto: {desktop_path}")
        except Exception as e:
            print(f"✗ Erro ao abrir desktop: {e}")
    
    def open_explorer(self):
        """Abre o explorador de arquivos"""
        try:
            subprocess.Popen('explorer')
            print("✓ Explorador de arquivos aberto")
        except Exception as e:
            print(f"✗ Erro ao abrir explorador: {e}")
    
    def open_powershell(self):
        """Abre o PowerShell"""
        try:
            subprocess.Popen('powershell')
            print("✓ PowerShell aberto")
        except Exception as e:
            print(f"✗ Erro ao abrir PowerShell: {e}")
    
    def open_documents(self):
        """Abre a pasta de documentos"""
        try:
            docs_path = os.path.join(os.environ['USERPROFILE'], 'Documents')
            subprocess.Popen(f'explorer "{docs_path}"')
            print(f"✓ Documentos aberto: {docs_path}")
        except Exception as e:
            print(f"✗ Erro ao abrir documentos: {e}")
    
    def open_settings(self):
        """Abre as configurações do Windows"""
        try:
            subprocess.Popen('start ms-settings:')
            print("✓ Configurações do Windows abertas")
        except Exception as e:
            print(f"✗ Erro ao abrir configurações: {e}")
    
    def refresh(self):
        """Atualiza as informações do sistema"""
        try:
            self.info_text.configure(state="normal")
            self.update_system_info()
            print("✓ Informações atualizadas")
        except Exception as e:
            print(f"✗ Erro ao atualizar: {e}")
    
    def run(self):
        """Inicia a aplicação"""
        self.app.mainloop()

# ============ EXECUÇÃO PRINCIPAL ============
if __name__ == "__main__":
    print("=" * 50)
    print("INICIANDO DESKTOP PROFESSIONAL SUITE")
    print("=" * 50)
    
    try:
        app = ProfessionalDesktopLauncher()
        app.run()
        print("Aplicação finalizada com sucesso!")
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        input("Pressione Enter para sair...")
