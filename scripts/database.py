import sqlite3
import os
import logging


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'financas.db')

def criar_banco():
    try:
     
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data DATE, 
                    descricao TEXT, 
                    categoria TEXT, 
                    valor REAL, 
                    tipo TEXT
                )
            ''')
          
            cursor.execute("SELECT COUNT(*) FROM transacoes")
            if cursor.fetchone()[0] == 0:
                
                seed_data = [
                    ('2026-01-01', 'Aluguel', 'Moradia', 1200.00, 'Débito'),
                    ('2026-01-05', 'Salário', 'Renda', 5000.00, 'Crédito'),
                    ('2026-01-10', 'Mercado', 'Alimentação', 450.00, 'Débito')
                ]
                cursor.executemany('''
                    INSERT INTO transacoes (data, descricao, categoria, valor, tipo) 
                    VALUES (?,?,?,?,?)
                ''', seed_data)
                conn.commit()
                logging.info("Banco de dados inicializado com dados fictícios.")
    except sqlite3.Error as e:
        logging.error(f"Erro ao interagir com o banco de dados: {e}")     
        
def carregar_dados():
    
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        logging.error(f"Erro ao conectar para leitura: {e}")
        return None
    

def adicionar_transacao(data, descricao, categoria, valor, tipo):

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transacoes (data, descricao, categoria, valor, tipo)
                VALUES (?, ?, ?, ?, ?)
            ''', (data, descricao, categoria, valor, tipo))
            conn.commit()
            logging.info(f"Transação '{descricao}' registrada com sucesso!")
    except sqlite3.Error as e:
        logging.error(f"Falha ao registrar transação: {e}")
        
        
        
def excluir_transacao(id_transacao):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
            if cursor.rowcount > 0:
                logging.info(f"Transação ID {id_transacao} removida.")
                return True
            else:
                logging.warning(f"ID {id_transacao} não encontrado.")
                return False
    except sqlite3.Error as e:
        logging.error(f"Erro ao excluir: {e}")
        return False
    
def adicionar_recorrencia(descricao, categoria, valor, mes_inicio, mes_fim):
    conn = carregar_dados()
    cursor = conn.cursor()
    
    for mes in range(int(mes_inicio), int(mes_fim) + 1):
        
        data_fixa = f"2026-{str(mes).zfill(2)}-05"
        
        cursor.execute('''
            INSERT INTO transacoes (data, descricao, categoria, valor, tipo)
            VALUES (?, ?, ?, ?, ?)
        ''', (data_fixa, descricao, categoria, valor, 'Débito'))
    
    conn.commit()
    conn.close()
    print(f" Recorrência de '{descricao}' adicionada do mês {mes_inicio} ao {mes_fim}!")