PRAGMA foreign_keys = ON;

-- ==============================
-- TABELA CLIENTES
-- ==============================
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT,
    telefone TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- TABELA MATERIAIS
-- ==============================
CREATE TABLE IF NOT EXISTS materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    unidade TEXT NOT NULL
);

-- ==============================
-- TABELA TRACOS
-- ==============================
CREATE TABLE IF NOT EXISTS tracos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    fck INTEGER,
    cimento_kg REAL,
    brita0_kg REAL,
    brita1_kg REAL,
    areia_kg REAL,
    pobrita_kg REAL,
    aditivo_kg REAL,
    umidade_areia REAL DEFAULT 0,
    umidade_pobrita REAL DEFAULT 0
);

-- ==============================
-- TABELA CARREGAMENTOS (SAÍDA DE CONCRETO)
-- ==============================
CREATE TABLE IF NOT EXISTS carregamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    cliente_id INTEGER,
    traco_id INTEGER,
    volume_m3 REAL NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (traco_id) REFERENCES tracos(id)
);

-- ==============================
-- REGISTRO DE MATERIAL POR CARREGAMENTO
-- ==============================
CREATE TABLE IF NOT EXISTS carregamento_materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carregamento_id INTEGER,
    material_id INTEGER,
    nome_material TEXT,
    quantidade_kg REAL,
    unidade TEXT,
    FOREIGN KEY (carregamento_id) REFERENCES carregamentos(id),
    FOREIGN KEY (material_id) REFERENCES materiais(id)
);

-- ==============================
-- TABELA DE ESTOQUE
-- ==============================
CREATE TABLE IF NOT EXISTS estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER,
    quantidade_atual REAL DEFAULT 0,
    FOREIGN KEY (material_id) REFERENCES materiais(id)
);

-- ==============================
-- ENTRADAS DE ESTOQUE
-- ==============================
CREATE TABLE IF NOT EXISTS entradas_estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER,
    quantidade REAL,
    data DATE,
    FOREIGN KEY (material_id) REFERENCES materiais(id)
);
