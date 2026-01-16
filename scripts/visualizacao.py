import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

def gerar_relatorios(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    
    plt.figure(figsize=(10,6))
    sns.barplot(data=df[df['tipo']=='Débito'], x='categoria', y='valor', estimator=sum)
    plt.title("Gastos por Categoria - 2026")
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico.png'))
    plt.close()


    df.to_excel(os.path.join(OUTPUT_DIR, 'relatorio.xlsx'), index=False)