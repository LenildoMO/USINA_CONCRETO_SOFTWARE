import sqlite3
import os
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='usina_concreto.db'):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
            return self.conn
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
            
    def close(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
            
    def criar_tabelas(self):
        """Cria todas as tabelas necessárias"""
        conn = self.connect()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        try:
            # Tabela de clientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cnpj_cpf TEXT,
                    endereco TEXT,
                    telefone TEXT,
                    email TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de traços (receitas de concreto)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    fck REAL,
                    slump REAL,
                    agregado_maximo TEXT,
                    observacoes TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de composição do traço
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traco_materiais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    traco_id INTEGER,
                    material TEXT NOT NULL,
                    quantidade REAL,
                    unidade TEXT,
                    FOREIGN KEY (traco_id) REFERENCES tracos(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabela de estoque
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material TEXT NOT NULL UNIQUE,
                    quantidade REAL DEFAULT 0,
                    unidade TEXT,
                    estoque_minimo REAL DEFAULT 0,
                    fornecedor TEXT,
                    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de pesagens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pesagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_pedido TEXT UNIQUE,
                    cliente_id INTEGER,
                    traco_id INTEGER,
                    quantidade_m3 REAL,
                    data_pesagem DATE,
                    hora_pesagem TIME,
                    placa_veiculo TEXT,
                    motorista TEXT,
                    status TEXT DEFAULT 'PENDENTE',
                    observacoes TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    FOREIGN KEY (traco_id) REFERENCES tracos(id)
                )
            ''')
            
            # Tabela de notas fiscais
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notas_fiscais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE,
                    pesagem_id INTEGER,
                    data_emissao DATE,
                    valor_total REAL,
                    chave_acesso TEXT,
                    arquivo_path TEXT,
                    FOREIGN KEY (pesagem_id) REFERENCES pesagens(id)
                )
            ''')
            
            # Tabela de configurações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT UNIQUE NOT NULL,
                    valor TEXT,
                    descricao TEXT
                )
            ''')
            
            # Inserir configurações padrão
            configs_iniciais = [
                ('empresa_nome', 'Usina de Concreto LTDA', 'Nome da empresa'),
                ('empresa_cnpj', '00.000.000/0000-00', 'CNPJ da empresa'),
                ('empresa_endereco', 'Rua Principal, 123', 'Endereço da empresa'),
                ('empresa_telefone', '(11) 9999-9999', 'Telefone da empresa'),
                ('balanca_porta', 'COM3', 'Porta da balança'),
                ('balanca_baudrate', '9600', 'Velocidade da balança'),
                ('email_notificacoes', 'admin@usina.com', 'Email para notificações'),
                ('estoque_alerta', '1000', 'Nível de alerta do estoque'),
                ('impressora_padrao', 'EPSON TM-T20', 'Impressora padrão')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO configuracoes (chave, valor, descricao)
                VALUES (?, ?, ?)
            ''', configs_iniciais)
            
            # Inserir materiais padrão no estoque
            materiais_iniciais = [
                ('Cimento', 0, 'kg', 10000, 'Votorantim'),
                ('Areia', 0, 'kg', 50000, 'Pedreira São Paulo'),
                ('Brita 0', 0, 'kg', 30000, 'Pedreira São Paulo'),
                ('Brita 1', 0, 'kg', 30000, 'Pedreira São Paulo'),
                ('Água', 0, 'litros', 10000, 'Companhia de Água'),
                ('Aditivo Plastificante', 0, 'litros', 500, 'BASF'),
                ('Aditivo Acelerador', 0, 'litros', 500, 'BASF')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO estoque (material, quantidade, unidade, estoque_minimo, fornecedor)
                VALUES (?, ?, ?, ?, ?)
            ''', materiais_iniciais)
            
            conn.commit()
            print("Banco de dados configurado com sucesso!")
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False
        finally:
            self.close()
    
    def executar_query(self, query, params=()):
        """Executa uma query SQL"""
        conn = self.connect()
        if not conn:
            return None
            
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro na query: {e}")
            return None
        finally:
            self.close()
    
    def buscar_todos(self, query, params=()):
        """Busca todos os registros"""
        return self.executar_query(query, params)
    
    def buscar_um(self, query, params=()):
        """Busca um único registro"""
        conn = self.connect()
        if not conn:
            return None
            
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro na busca: {e}")
            return None
        finally:
            self.close()
    
    def inserir(self, tabela, dados):
        """Insere um novo registro"""
        colunas = ', '.join(dados.keys())
        placeholders = ', '.join(['?' for _ in dados])
        valores = list(dados.values())
        
        query = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"
        return self.executar_query(query, valores)
    
    def atualizar(self, tabela, id_registro, dados):
        """Atualiza um registro existente"""
        sets = ', '.join([f"{k} = ?" for k in dados.keys()])
        valores = list(dados.values())
        valores.append(id_registro)
        
        query = f"UPDATE {tabela} SET {sets} WHERE id = ?"
        return self.executar_query(query, valores)
    
    def excluir(self, tabela, id_registro):
        """Exclui um registro"""
        query = f"DELETE FROM {tabela} WHERE id = ?"
        return self.executar_query(query, (id_registro,))

# Instância global do banco de dados
db = DatabaseManager()

# Funções de conveniência
def conectar_banco():
    """Conecta ao banco de dados"""
    return db.connect()

def criar_tabelas():
    """Cria todas as tabelas do sistema"""
    return db.criar_tabelas()

def executar_sql(query, params=()):
    """Executa uma query SQL"""
    return db.executar_query(query, params)

def buscar_todos(query, params=()):
    """Busca todos os registros"""
    return db.buscar_todos(query, params)

def buscar_um(query, params=()):
    """Busca um único registro"""
    return db.buscar_um(query, params)

def inserir_registro(tabela, dados):
    """Insere um novo registro"""
    return db.inserir(tabela, dados)

def atualizar_registro(tabela, id_registro, dados):
    """Atualiza um registro existente"""
    return db.atualizar(tabela, id_registro, dados)

def excluir_registro(tabela, id_registro):
    """Exclui um registro"""
    return db.excluir(tabela, id_registro)

def carregar_json(nome_arquivo):
    """Carrega dados de um arquivo JSON"""
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def salvar_json(nome_arquivo, dados):
    """Salva dados em um arquivo JSON"""
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")
        return False

# Inicializar arquivos JSON se não existirem
def inicializar_arquivos_json():
    """Inicializa arquivos JSON com dados padrão"""
    
    # Cadastro de motoristas
    if not os.path.exists('cad_motoristas.json'):
        motoristas_padrao = [
            {"id": 1, "nome": "João Silva", "cpf": "111.222.333-44", "cnh": "123456789", "telefone": "(11) 99999-9999"},
            {"id": 2, "nome": "Maria Santos", "cpf": "222.333.444-55", "cnh": "987654321", "telefone": "(11) 88888-8888"}
        ]
        salvar_json('cad_motoristas.json', motoristas_padrao)
    
    # Cadastro de placas
    if not os.path.exists('cad_placas.json'):
        placas_padrao = [
            {"id": 1, "placa": "ABC-1234", "modelo": "Mercedes-Benz", "cor": "Branco", "ano": 2020},
            {"id": 2, "placa": "DEF-5678", "modelo": "Volvo", "cor": "Azul", "ano": 2019}
        ]
        salvar_json('cad_placas.json', placas_padrao)
    
    print("Arquivos JSON inicializados com sucesso!")