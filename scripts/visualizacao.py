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
    sns.barplot(data=df[df['tipo']=='Débito'], x='categoria', y='valor', estimator=sum, hue='categoria', palette='viridis', legend=False)
    plt.title("Gastos por Categoria & Detecção de Anomalias em Finanças")
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico.png'))
    plt.close()

    df.to_excel(os.path.join(OUTPUT_DIR, 'relatorio.xlsx'), index=False)

    gastos_atuais = df[df['tipo'] == 'Débito'].groupby('categoria')['valor'].sum()
    total_geral = gastos_atuais.sum()

    print("\n--- ANÁLISE DE IMPACTO NO BOLSO ---")
    if total_geral > 0:
        for categoria, valor in gastos_atuais.items():
            percentual = (valor / total_geral) * 100
            print(f"• {categoria}: {percentual:.1f}% (R$ {valor:.2f})")
    
    print("\n--- VERIFICAÇÃO DE ORÇAMENTO ---")
    for categoria, limite in METAS.items():
        gasto_real = gastos_atuais.get(categoria, 0)
        if gasto_real > limite:
            print(f" ALERTA:'{categoria}' estourou! (Excedeu R$ {gasto_real - limite:.2f})")
        elif gasto_real > (limite * 0.8):
            print(f" ATENÇÃO: '{categoria}' está em 80% do limite.")