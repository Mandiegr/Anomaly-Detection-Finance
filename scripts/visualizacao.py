import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

METAS = {
    'Alimentação': 500.0,
    'Transporte': 300.0,
    'Lazer': 200.0,
    'Moradia': 1500.0
}

def gerar_relatorios(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    
    plt.figure(figsize=(10,6))
    sns.barplot(data=df[df['tipo']=='Débito'], x='categoria', y='valor', estimator=sum,palette='viridis')
    plt.title("Gastos por Categoria & Detecção de Anomalias em Finanças")
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico.png'))
    plt.close()


    df.to_excel(os.path.join(OUTPUT_DIR, 'relatorio.xlsx'), index=False)
    
    
    print("\n--- VERIFICAÇÃO DE ORÇAMENTO ---")
    gastos_atuais = df[df['tipo'] == 'Débito'].groupby('categoria')['valor'].sum()
    
    for categoria, limite in METAS.items():
        gasto_real = gastos_atuais.get(categoria, 0)
        if gasto_real > limite:
            print(f" ALERTA: Você ultrapassou o limite em '{categoria}'!")
            print(f" Gasto: R$ {gasto_real:.2f} / Limite: R$ {limite:.2f}")
        elif gasto_real > (limite * 0.8):
            print(f" ATENÇÃO: '{categoria}' está chegando perto do limite (80%+).")
        else:
            print(f" '{categoria}' está dentro do planejado.")