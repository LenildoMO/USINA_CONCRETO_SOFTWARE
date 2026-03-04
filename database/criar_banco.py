# Adicione ao seu script de criação do banco de dados
conn = sqlite3.connect('usina_concreto.db')
cursor = conn.cursor()

# Adicione status à tabela de pesagens (se já existir)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pesagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        placa_veiculo TEXT,
        peso_bruto REAL,
        peso_tara REAL,
        peso_liquido REAL,
        status TEXT DEFAULT 'PENDENTE',
        telefone_motorista TEXT,
        observacoes TEXT
    )
''')

conn.commit()
conn.close()
import sqlite3

# Caminho do banco
caminho = "database/banco.db"

# Conexão com o banco
con = sqlite3.connect(caminho)
cur = con.cursor()

# ============================
#       TABELA CLIENTES
# ============================
cur.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cnpj TEXT,
    endereco TEXT,
    telefone TEXT,
    observacoes TEXT
)
""")

# ============================
#       TABELA TRACOS
# ============================
cur.execute("""
CREATE TABLE IF NOT EXISTS tracos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    fck INTEGER,
    slump TEXT,
    brita0 REAL,
    brita1 REAL,
    areia REAL,
    po_brita REAL,
    cimento REAL,
    aditivo REAL,
    umidade_areia REAL,
    umidade_po REAL
)
""")

# ============================
#       TABELA PESAGENS
# ============================
cur.execute("""
CREATE TABLE IF NOT EXISTS pesagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    hora TEXT,
    cliente_id INTEGER,
    traco_id INTEGER,
    peso_total REAL,
    peso_b0 REAL,
    peso_b1 REAL,
    peso_areia REAL,
    peso_po REAL,
    peso_cimento REAL,
    peso_aditivo REAL,
    modo TEXT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id),
    FOREIGN KEY(traco_id) REFERENCES tracos(id)
)
""")

# ============================
#       TABELA ESTOQUE
# ============================
cur.execute("""
CREATE TABLE IF NOT EXISTS estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material TEXT NOT NULL,
    quantidade REAL DEFAULT 0,
    unidade TEXT DEFAULT 'kg'
)
""")

# ============================
#       TABELA NOTAS FISCAIS
# ============================
cur.execute("""
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT,
    fornecedor TEXT,
    data TEXT,
    valor REAL,
    material TEXT,
    quantidade REAL,
    observacoes TEXT
)
""")

# ============================
#       TABELA USUÁRIOS
# ============================
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    senha TEXT
)
""")

# ============================
#       HISTÓRICO DE ALTERAÇÕES
# ============================
cur.execute("""
CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    hora TEXT,
    usuario TEXT,
    acao TEXT
)
""")

con.commit()
con.close()

print("Banco de dados criado/atualizado com sucesso!")

