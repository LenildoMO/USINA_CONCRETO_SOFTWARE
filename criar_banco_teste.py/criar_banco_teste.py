import sqlite3
import json

def criar_banco_teste():
    """Cria um banco de dados de teste"""
    
    conn = sqlite3.connect('usina_concreto.db')
    cursor = conn.cursor()
    
    # Criar tabela de traços
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nome TEXT NOT NULL,
            brita0 REAL DEFAULT 0,
            brita1 REAL DEFAULT 0,
            areia_media REAL DEFAULT 0,
            po_brita REAL DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela de pesagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pesagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            traco_id INTEGER,
            quantidade REAL DEFAULT 0,
            materiais_json TEXT DEFAULT '{}',
            status TEXT DEFAULT 'PENDENTE',
            data_pesagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (traco_id) REFERENCES tracos (id)
        )
    ''')
    
    # Inserir dados de exemplo
    cursor.execute('''
        INSERT OR IGNORE INTO tracos (codigo, nome, brita0, brita1, areia_media, po_brita)
        VALUES 
            ('T001', 'Traço Padrão 25MPa', 1050, 850, 750, 350),
            ('T002', 'Traço Especial 30MPa', 1150, 900, 800, 400),
            ('T003', 'Traço Fundação', 1000, 800, 700, 300)
    ''')
    
    # Inserir pesagens de exemplo
    materiais_exemplo = json.dumps({
        "Brita 0": {"quantidade": 2100, "unidade": "kg"},
        "Brita 1": {"quantidade": 1700, "unidade": "kg"},
        "Areia Média": {"quantidade": 1500, "unidade": "kg"},
        "Pó de Brita": {"quantidade": 700, "unidade": "kg"}
    })
    
    cursor.execute('''
        INSERT INTO pesagens (traco_id, quantidade, materiais_json, status)
        VALUES 
            (1, 2.0, ?, 'PENDENTE'),
            (2, 1.5, ?, 'PENDENTE'),
            (3, 3.0, ?, 'PENDENTE')
    ''', (materiais_exemplo, materiais_exemplo, materiais_exemplo))
    
    conn.commit()
    conn.close()
    
    print("✅ Banco de dados criado com sucesso!")
    print("📊 Dados de exemplo inseridos:")
    print("   - 3 traços diferentes")
    print("   - 3 pesagens pendentes")
    print("\n🎯 Execute o sistema principal:")
    print("   python arquivo_completo_corrigido.py")

if __name__ == "__main__":
    criar_banco_teste()