import sys
import os
import pandas as pd
from datetime import datetime

folder_path = os.path.dirname(os.path.abspath(__file__))
if folder_path not in sys.path:
    sys.path.insert(0, folder_path)

import database
import visualizacao

def menu():
    database.criar_banco()
    
    while True:
        print("\n--- ANALISADOR DE GASTOS 2026 ---")
        print("1. Adicionar Novo Gasto")
        print("2. Gerar Gráficos e Relatórios")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            desc = input("Descrição (ex: Café): ")
            cat = input("Categoria (ex: Alimentação): ")
            val = float(input("Valor (ex: 15.50): "))
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            
            database.adicionar_transacao(data_hoje, desc, cat, val, 'Débito')
            
        elif opcao == '2':
            print(" Processando relatórios...")
            conn = database.carregar_dados()
            df = pd.read_sql_query("SELECT * FROM transacoes", conn)
            conn.close()
            
            if not df.empty:
                visualizacao.gerar_relatorios(df)
                print("✅ Sucesso! Verifique a pasta 'outputs'.")
            else:
                print("Sem dados para gerar relatórios.")
                
        elif opcao == '3':
            print("Até logo!")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu()