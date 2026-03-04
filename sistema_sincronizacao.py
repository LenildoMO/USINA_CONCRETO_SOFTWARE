# ============================================================================
# SISTEMA DE SINCRONIZAÇÃO BETTO MIX MEGA
# ============================================================================
# Sincronização automática PyQt6 ↔ Web
# ============================================================================

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

class SistemaSincronizacaoMega:
    """Sistema avançado de sincronização entre PyQt6 e Web"""
    
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.config = self.carregar_configuracao()
        self.stats = {
            'telas_sincronizadas': 0,
            'arquivos_processados': 0,
            'ultima_sincronizacao': None,
            'erros': []
        }
    
    def carregar_configuracao(self):
        """Carrega ou cria configuração do sistema"""
        config_path = self.base_dir / 'config' / 'sincronizacao.json'
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            config = {
                'ativo': True,
                'modo': 'automático',
                'intervalo_minutos': 5,
                'backup_antes_sinc': True,
                'max_backups': 10,
                'pastas_monitoradas': [
                    'ui/pages',
                    'ui/styles',
                    'ui/images'
                ],
                'extensoes_permitidas': ['.py', '.ui', '.qrc'],
                'ignorar_pastas': ['__pycache__', '.git', 'venv', '.vscode']
            }
            
            # Criar diretório de config se não existir
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return config
    
    def salvar_configuracao(self):
        """Salva configuração atual"""
        config_path = self.base_dir / 'config' / 'sincronizacao.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def detectar_telas_pyqt6(self):
        """Detecta todas as telas PyQt6 no sistema"""
        telas_encontradas = []
        
        for pasta in self.config['pastas_monitoradas']:
            pasta_path = self.base_dir / pasta
            
            if not pasta_path.exists():
                continue
            
            # Buscar arquivos .py
            for arquivo in pasta_path.rglob('*.py'):
                # Verificar se deve ser ignorado
                if any(ignorar in str(arquivo) for ignorar in self.config['ignorar_pastas']):
                    continue
                
                # Ler conteúdo para verificar se é PyQt6
                try:
                    with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                        conteudo = f.read(1000)  # Ler apenas início
                        
                        if any(keyword in conteudo for keyword in ['PyQt6', 'from PyQt', 'import PyQt']):
                            tela_info = self.analisar_tela_pyqt6(arquivo)
                            if tela_info:
                                telas_encontradas.append(tela_info)
                except Exception as e:
                    print(f"Erro ao ler {arquivo}: {e}")
        
        return telas_encontradas
    
    def analisar_tela_pyqt6(self, caminho_arquivo):
        """Analisa uma tela PyQt6 em detalhes"""
        try:
            arquivo = Path(caminho_arquivo)
            nome_arquivo = arquivo.name
            nome_tela = nome_arquivo.replace('tela_', '').replace('.py', '')
            
            with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                conteudo = f.read()
            
            # Informações básicas
            info = {
                'nome': nome_tela,
                'arquivo': nome_arquivo,
                'caminho': str(arquivo.relative_to(self.base_dir)),
                'tamanho_bytes': arquivo.stat().st_size,
                'modificacao': datetime.fromtimestamp(arquivo.stat().st_mtime).isoformat(),
                'hash': hashlib.md5(conteudo.encode()).hexdigest(),
                'widgets': [],
                'classes': [],
                'funcoes': [],
                'imports': [],
                'estrutura': {}
            }
            
            import re
            
            # Detectar classes
            classes = re.findall(r'class\s+(\w+)', conteudo)
            info['classes'] = classes
            
            # Detectar widgets PyQt6
            padroes_widgets = [
                r'self\.(\w+)\s*=\s*(Q\w+)',
                r'(\w+)\s*=\s*(Q\w+)\(',
                r'def\s+\w+\s*\([^)]*\):\s*\n\s*(\w+)\s*=\s*(Q\w+)\('
            ]
            
            widgets_detectados = []
            for padrao in padroes_widgets:
                matches = re.findall(padrao, conteudo, re.MULTILINE)
                for match in matches:
                    if len(match) == 2:
                        nome_widget, tipo_widget = match
                        widgets_detectados.append({
                            'nome': nome_widget,
                            'tipo': tipo_widget
                        })
            
            info['widgets'] = widgets_detectados
            
            # Detectar funções
            funcoes = re.findall(r'def\s+(\w+)\s*\(', conteudo)
            info['funcoes'] = [f for f in funcoes if not f.startswith('_')]
            
            # Detectar imports
            imports = re.findall(r'import\s+(\w+)', conteudo) + re.findall(r'from\s+(\w+)', conteudo)
            info['imports'] = list(set(imports))
            
            # Analisar estrutura do arquivo
            linhas = conteudo.split('\n')
            estrutura = {
                'total_linhas': len(linhas),
                'linhas_codigo': sum(1 for linha in linhas if linha.strip() and not linha.strip().startswith('#')),
                'linhas_comentarios': sum(1 for linha in linhas if linha.strip().startswith('#')),
                'linhas_vazias': sum(1 for linha in linhas if not linha.strip())
            }
            info['estrutura'] = estrutura
            
            # Detectar título da janela
            titulo_match = re.search(r'setWindowTitle\s*\(\s*["\']([^"\']+)["\']', conteudo)
            if titulo_match:
                info['titulo'] = titulo_match.group(1)
            else:
                info['titulo'] = nome_tela.replace('_', ' ').title()
            
            return info
            
        except Exception as e:
            print(f"Erro ao analisar {caminho_arquivo}: {e}")
            return None
    
    def sincronizar_tela(self, tela_info, forcar=False):
        """Sincroniza uma tela específica"""
        try:
            # Caminhos
            nome_tela = tela_info['nome']
            template_path = self.base_dir / 'templates' / f'{nome_tela}.html'
            meta_path = self.base_dir / 'templates' / f'{nome_tela}_meta.json'
            backup_path = self.base_dir / 'backup' / 'telas' / f'{nome_tela}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
            
            # Criar backup se configurado
            if self.config['backup_antes_sinc']:
                arquivo_original = self.base_dir / tela_info['caminho']
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(arquivo_original, backup_path)
            
            # Gerar HTML da tela
            html = self.gerar_html_tela(tela_info)
            
            # Salvar template HTML
            template_path.parent.mkdir(parents=True, exist_ok=True)
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Salvar metadados
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(tela_info, f, indent=2, ensure_ascii=False, default=str)
            
            # Atualizar estatísticas
            self.stats['telas_sincronizadas'] += 1
            self.stats['ultima_sincronizacao'] = datetime.now().isoformat()
            
            print(f"✅ Tela sincronizada: {nome_tela}")
            print(f"   📄 Widgets: {len(tela_info['widgets'])}")
            print(f"   ⚙️ Funções: {len(tela_info['funcoes'])}")
            print(f"   🏗️ Classes: {len(tela_info['classes'])}")
            
            return {
                'status': 'success',
                'tela': nome_tela,
                'arquivo_html': str(template_path),
                'arquivo_meta': str(meta_path),
                'backup': str(backup_path) if self.config['backup_antes_sinc'] else None
            }
            
        except Exception as e:
            erro_msg = f"Erro ao sincronizar {tela_info['nome']}: {str(e)}"
            print(f"❌ {erro_msg}")
            
            self.stats['erros'].append({
                'data': datetime.now().isoformat(),
                'tela': tela_info['nome'],
                'erro': str(e)
            })
            
            return {
                'status': 'error',
                'tela': tela_info['nome'],
                'erro': str(e)
            }
    
    def gerar_html_tela(self, tela_info):
        """Gera HTML completo para uma tela PyQt6"""
        
        # Gerar lista de widgets formatada
        widgets_html = ""
        for i, widget in enumerate(tela_info['widgets'][:30]):  # Limitar a 30 widgets
            widget_icon = self.get_widget_icon(widget['tipo'])
            widgets_html += f'''
            <div class="widget-item" style="animation-delay: {i * 0.05}s;">
                <div class="widget-icon">{widget_icon}</div>
                <div class="widget-details">
                    <strong>{widget['nome']}</strong>
                    <small>{widget['tipo']}</small>
                </div>
            </div>
            '''
        
        # Gerar lista de funções
        funcoes_html = ""
        for funcao in tela_info['funcoes'][:20]:  # Limitar a 20 funções
            funcoes_html += f'<span class="badge">{funcao}()</span>'
        
        # HTML completo
        html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tela_info['titulo']} - Betto Mix Mega</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .tela-mega-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            animation: fadeIn 0.5s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .tela-header {{
            background: linear-gradient(135deg, #003366 0%, #0056b3 100%);
            color: white;
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .tela-header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        
        .tela-header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        
        .info-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .info-card h3 {{
            color: #003366;
            margin-top: 0;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }}
        
        .widgets-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .widget-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
            animation: slideIn 0.3s ease-out forwards;
            opacity: 0;
        }}
        
        @keyframes slideIn {{
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        .widget-icon {{
            font-size: 1.5em;
            color: #0056b3;
        }}
        
        .widget-details {{
            flex: 1;
        }}
        
        .widget-details strong {{
            display: block;
            color: #333;
        }}
        
        .widget-details small {{
            color: #666;
            font-size: 0.85em;
        }}
        
        .badge {{
            display: inline-block;
            background: #6c757d;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            margin: 5px;
            font-size: 0.9em;
        }}
        
        .stats-bar {{
            display: flex;
            justify-content: space-around;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #003366;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 40px 0;
        }}
        
        .btn {{
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .widgets-container {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }}
            
            .action-buttons {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="tela-mega-container">
        <div class="tela-header">
            <h1><i class="fas fa-desktop"></i> {tela_info['titulo']}</h1>
            <p>Tela sincronizada automaticamente do PyQt6 - Sistema Betto Mix Mega</p>
            <div style="margin-top: 20px; display: flex; gap: 15px; flex-wrap: wrap;">
                <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px;">
                    <i class="fas fa-file-code"></i> {tela_info['arquivo']}
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px;">
                    <i class="fas fa-cube"></i> {len(tela_info['widgets'])} widgets
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px;">
                    <i class="fas fa-code"></i> {len(tela_info['funcoes'])} funções
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px;">
                    <i class="fas fa-cogs"></i> {len(tela_info['classes'])} classes
                </span>
            </div>
        </div>
        
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-number">{tela_info['estrutura']['total_linhas']}</div>
                <div class="stat-label">Linhas totais</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{tela_info['estrutura']['linhas_codigo']}</div>
                <div class="stat-label">Linhas de código</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{tela_info['estrutura']['linhas_comentarios']}</div>
                <div class="stat-label">Comentários</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{tela_info['tamanho_bytes']:,}</div>
                <div class="stat-label">Bytes</div>
            </div>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3><i class="fas fa-cubes"></i> Widgets Detectados ({len(tela_info['widgets'])})</h3>
                <div class="widgets-container">
                    {widgets_html}
                </div>
            </div>
            
            <div class="info-card">
                <h3><i class="fas fa-info-circle"></i> Informações Técnicas</h3>
                <p><strong>Arquivo:</strong> {tela_info['arquivo']}</p>
                <p><strong>Caminho:</strong> {tela_info['caminho']}</p>
                <p><strong>Modificado:</strong> {datetime.fromisoformat(tela_info['modificacao']).strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Hash MD5:</strong> <code>{tela_info['hash'][:16]}...</code></p>
                
                <h4 style="margin-top: 20px;">Classes:</h4>
                <p>{', '.join(tela_info['classes'])}</p>
                
                <h4>Imports:</h4>
                <p>{', '.join(tela_info['imports'])}</p>
            </div>
        </div>
        
        <div class="info-card">
            <h3><i class="fas fa-code"></i> Funções Disponíveis ({len(tela_info['funcoes'])})</h3>
            <div style="margin-top: 15px;">
                {funcoes_html if funcoes_html else '<p>Nenhuma função pública detectada</p>'}
            </div>
        </div>
        
        <div class="action-buttons">
            <button class="btn btn-primary" onclick="location.href='/dashboard'">
                <i class="fas fa-home"></i> Voltar ao Dashboard
            </button>
            <button class="btn btn-secondary" onclick="location.href='/monitor'">
                <i class="fas fa-desktop"></i> Ver Monitor
            </button>
            <button class="btn" style="background: #28a745; color: white;" onclick="location.href='/api/sync/tela/{tela_info['nome']}'">
                <i class="fas fa-sync"></i> Sincronizar Novamente
            </button>
        </div>
    </div>
    
    <script>
        // Animar entrada dos widgets
        document.addEventListener('DOMContentLoaded', function() {{
            const widgets = document.querySelectorAll('.widget-item');
            widgets.forEach((widget, index) => {{
                widget.style.animationDelay = (index * 0.05) + 's';
            }});
            
            console.log('Tela {tela_info['nome']} carregada com sucesso!');
            console.log('Total de widgets: {len(tela_info['widgets'])}');
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def get_widget_icon(self, widget_type):
        """Retorna ícone apropriado para o tipo de widget"""
        icons = {
            'QPushButton': '🔼',
            'QLabel': '🏷️',
            'QLineEdit': '📝',
            'QTextEdit': '📄',
            'QComboBox': '📋',
            'QTableWidget': '📊',
            'QTreeWidget': '🌳',
            'QListWidget': '📜',
            'QGroupBox': '📦',
            'QTabWidget': '📑',
            'QProgressBar': '📈',
            'QSlider': '🎚️',
            'QSpinBox': '🔢',
            'QDateEdit': '📅',
            'QCheckBox': '☑️',
            'QRadioButton': '🔘',
            'QMenu': '🍔',
            'QToolBar': '🛠️',
            'QStatusBar': '📊',
            'QSplitter': '↔️',
            'QFrame': '🖼️',
            'QWidget': '🎨'
        }
        
        # Procurar por padrões
        for key, icon in icons.items():
            if key in widget_type:
                return icon
        
        return '🎯'  # Ícone padrão
    
    def sincronizar_todas(self):
        """Sincroniza todas as telas detectadas"""
        print("🔄 Iniciando sincronização completa...")
        
        telas = self.detectar_telas_pyqt6()
        resultados = []
        
        print(f"🔍 {len(telas)} telas detectadas")
        
        for tela_info in telas:
            resultado = self.sincronizar_tela(tela_info)
            resultados.append(resultado)
            self.stats['arquivos_processados'] += 1
        
        # Salvar estatísticas
        self.salvar_estatisticas()
        
        print(f"✅ Sincronização completa!")
        print(f"   📊 Total: {len(resultados)} telas processadas")
        print(f"   ✅ Sucessos: {sum(1 for r in resultados if r['status'] == 'success')}")
        print(f"   ❌ Erros: {sum(1 for r in resultados if r['status'] == 'error')}")
        
        return resultados
    
    def salvar_estatisticas(self):
        """Salva estatísticas do sistema"""
        stats_path = self.base_dir / 'logs' / 'sincronizacao_stats.json'
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False, default=str)
    
    def limpar_backups_antigos(self):
        """Remove backups antigos mantendo apenas os mais recentes"""
        if not self.config['backup_antes_sinc']:
            return
        
        backup_dir = self.base_dir / 'backup' / 'telas'
        if not backup_dir.exists():
            return
        
        # Listar arquivos de backup
        arquivos_backup = list(backup_dir.glob('*.py'))
        arquivos_backup.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Manter apenas os mais recentes
        if len(arquivos_backup) > self.config['max_backups']:
            for arquivo in arquivos_backup[self.config['max_backups']:]:
                try:
                    arquivo.unlink()
                    print(f"🗑️ Backup removido: {arquivo.name}")
                except Exception as e:
                    print(f"❌ Erro ao remover backup {arquivo}: {e}")

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    sinc = SistemaSincronizacaoMega(base_dir)
    
    if len(sys.argv) > 2 and sys.argv[2] == '--todas':
        resultados = sinc.sincronizar_todas()
        print(f"\n🎉 Sincronização completa finalizada!")
    else:
        telas = sinc.detectar_telas_pyqt6()
        print(f"\n🔍 Telas PyQt6 detectadas: {len(telas)}")
        for tela in telas:
            print(f"   • {tela['nome']} ({len(tela['widgets'])} widgets)")
        
        print(f"\n💡 Use '--todas' para sincronizar todas as telas")
