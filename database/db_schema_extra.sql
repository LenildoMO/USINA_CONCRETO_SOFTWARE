-- database/db_schema_extra.sql
PRAGMA foreign_keys = ON;

-- Tabela para registrar, por carregamento, a quantidade de cada material (facilita relatórios)
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

-- Se já tem estoque/entradas/carregamentos, ok. Senão, as tabelas básicas já foram fornecidas antes.
