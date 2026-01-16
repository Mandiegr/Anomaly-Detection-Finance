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
        print("3. Listar e Excluir Gasto")
        print("4. Configurar Metas")
        print("5. Sair")
        
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
                print(" Sucesso! Verifique a pasta 'outputs'.")
            else:
                print("Sem dados para gerar relatórios.")
                
        elif opcao == '3':

            conn = database.carregar_dados()
            df = pd.read_sql_query("SELECT id, data, descricao, valor FROM transacoes", conn)
            conn.close()
            
            if not df.empty:
                print("\n--- TRANSAÇÕES REGISTRADAS ---")
                print(df.to_string(index=False)) 
                
                try:
                    id_del = int(input("\nDigite o ID para excluir (ou 0 para cancelar): "))
                    if id_del != 0:
                        database.excluir_transacao(id_del)
                except ValueError:
                    print(" Digite um número de ID válido.")
            else:
                print(" Nada para excluir.") 
        elif opcao == '4':
        
            print("\n--- CONFIGURAR METAS DE ORÇAMENTO ---")
            metas = visualizacao.carregar_metas()
            print("Metas atuais:", metas)
            
            categoria = input("Qual categoria deseja alterar (ex: Alimentação)? ")
            try:
                novo_limite = float(input(f"Qual o novo limite para {categoria}? "))
                metas[categoria] = novo_limite
                visualizacao.salvar_metas(metas)
                print(f" Meta de {categoria} atualizada para R$ {novo_limite:.2f}!")
            except ValueError:
                print(" Valor inválido.")
        
        elif opcao == '5':
            print("Até logo!")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu()
    
    