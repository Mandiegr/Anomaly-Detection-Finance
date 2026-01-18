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
        print("6. Previsão de Gastos ")
        print("7. Adicionar Despesa Fixa (Recorrência)")
        
        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            desc = input("Descrição (ex: Café): ")
            cat = input("Categoria (ex: Alimentação): ")
            
            try: 
                val = float(input("Valor (ex: 15.50): "))
                print("Data: Pressione ENTER para hoje ou digite no formato AAAA-MM-DD")
                data_input = input("Data (ex: 2026-02-15): ")
                
                if data_input == "":
                    data_final = datetime.now().strftime("%Y-%m-%d")
                else:
                    datetime.strptime(data_input, "%Y-%m-%d")
                    data_final = data_input
                
             
                database.adicionar_transacao(data_final, desc, cat, val, 'Débito')
            except ValueError:
                print(" Erro: Formato de valor ou data inválido!")
            
        elif opcao == '2':
            print("\n--- RELATÓRIOS POR MÊS ---")
            mes = input("Mês (01-12) ou ENTER para Geral: ")
            
            conn = database.carregar_dados()
            df = pd.read_sql_query("SELECT * FROM transacoes", conn)
            conn.close()
            
            if not df.empty:
                visualizacao.gerar_relatorios(df, mes if mes != "" else None)
                visualizacao.exportar_plano_acao(df)
                print("\n Processo concluído! Verifique a pasta 'outputs'.")
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
        
        elif opcao == '6':
            conn = database.carregar_dados()
            df = pd.read_sql_query("SELECT * FROM transacoes", conn)
            conn.close()
            if not df.empty:
                visualizacao.prever_gastos_anual(df)
                visualizacao.simular_economia(df)
            else:
                print(" Adicione gastos primeiro para a IA analisar.")
        elif opcao == '7':
            desc = input("Descrição da despesa fixa: ")
            cat = input("Categoria: ")
            try:
                val = float(input("Valor mensal: "))
                m_inicio = input("Mês de início (01-12): ")
                m_fim = input("Mês de fim (01-12): ")
                
                database.adicionar_recorrencia(desc, cat, val, m_inicio, m_fim)
            except ValueError:
                print(" Erro nos dados informados!")

        else:
            print(" Opção inválida! Tente novamente.")
        
            

if __name__ == "__main__":
    menu()