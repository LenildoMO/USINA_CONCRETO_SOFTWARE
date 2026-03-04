import sys
import os
import sqlite3
import json

# Adiciona o diretório atual ao PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== CONFIGURAÇÃO DO BANCO DE DADOS ===")

def criar_banco():
    """Cria o banco de dados e tabelas"""
    try:
        conn = sqlite3.connect('usina_concreto.db')
        cursor = conn.cursor()
        
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
        
        # Tabela de traços
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nome TEXT NOT NULL,
                descricao TEXT,
                fck REAL,
                slump REAL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de pesagens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                traco_id INTEGER,
                quantidade REAL,
                placa_veiculo TEXT,
                motorista TEXT,
                data_pesagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'PENDENTE',
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (traco_id) REFERENCES tracos(id)
            )
        ''')
        
        # Inserir materiais padrão
        materiais = [
            ('Cimento', 0, 'kg', 10000),
            ('Areia', 0, 'kg', 50000),
            ('Brita', 0, 'kg', 30000),
            ('Água', 0, 'litros', 10000),
            ('Aditivo', 0, 'litros', 1000)
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO estoque (material, quantidade, unidade, estoque_minimo)
            VALUES (?, ?, ?, ?)
        ''', materiais)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao criar banco: {e}")
        return False

def criar_arquivos_json():
    """Cria os arquivos JSON padrão"""
    try:
        # Arquivo de motoristas
        motoristas = [
            {"id": 1, "nome": "João Silva", "cpf": "111.222.333-44", "cnh": "12345678901", "telefone": "(11) 99999-9999"},
            {"id": 2, "nome": "Maria Santos", "cpf": "222.333.444-55", "cnh": "98765432109", "telefone": "(11) 88888-8888"}
        ]
        
        with open('cad_motoristas.json', 'w', encoding='utf-8') as f:
            json.dump(motoristas, f, indent=4, ensure_ascii=False)
        print("✓ Arquivo cad_motoristas.json criado")
        
        # Arquivo de placas
        placas = [
            {"id": 1, "placa": "ABC-1234", "modelo": "Mercedes-Benz", "cor": "Branco", "ano": 2020},
            {"id": 2, "placa": "DEF-5678", "modelo": "Volvo", "cor": "Azul", "ano": 2019}
        ]
        
        with open('cad_placas.json', 'w', encoding='utf-8') as f:
            json.dump(placas, f, indent=4, ensure_ascii=False)
        print("✓ Arquivo cad_placas.json criado")
        
        return True
        
    except Exception as e:
        print(f"Erro ao criar arquivos JSON: {e}")
        return False

if __name__ == '__main__':
    print("1. Criando banco de dados...")
    if criar_banco():
        print("✓ Banco de dados criado com sucesso!")
    else:
        print("✗ Falha ao criar banco de dados")
    
    print("\n2. Criando arquivos JSON...")
    if criar_arquivos_json():
        print("✓ Arquivos JSON criados com sucesso!")
    else:
        print("✗ Falha ao criar arquivos JSON")
    
    print("\n=== CONFIGURAÇÃO CONCLUÍDA ===")
    print("Execute: python main.py")
    input("\nPressione Enter para sair...")