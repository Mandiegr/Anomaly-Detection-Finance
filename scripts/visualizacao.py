import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')
METAS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'metas.json')

def carregar_metas():
    if not os.path.exists(METAS_FILE):
        padrao = {'Alimentação': 500.0, 'Moradia': 1500.0, 'Transporte': 300.0}
        with open(METAS_FILE, 'w') as f:
            json.dump(padrao, f)
        return padrao
    with open(METAS_FILE, 'r') as f:
        return json.load(f)

def salvar_metas(novas_metas):
    with open(METAS_FILE, 'w') as f:
        json.dump(novas_metas, f, indent=4)
        
def detectar_anomalias(df):
    print("\n--- DETECÇÃO DE ANOMALIAS (Z-Score) ---")
    gastos = df[df['tipo'] == 'Débito'].copy()
    
    if len(gastos) < 3:
        print(" Dados insuficientes para criar um padrão estatístico.")
        return      
        
    media = gastos['valor'].mean()
    desvio = gastos['valor'].std()
    
  
    limite_anomalia = media + (1.5 * desvio)
    
    anomalias = gastos[gastos['valor'] > limite_anomalia]
    
    if not anomalias.empty:
        for _, row in anomalias.iterrows():
            print(f" ANOMALIA: '{row['descricao']}' custou R$ {row['valor']:.2f}")
            print(f"   (Sua média é R$ {media:.2f}. Este valor fugiu muito do padrão!)")
    else:
        print(" Nenhum comportamento fora do padrão detectado.")

def gerar_relatorios(df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    metas_carregadas = carregar_metas()
    
    plt.figure(figsize=(10,6))
    sns.barplot(data=df[df['tipo']=='Débito'], x='categoria', y='valor', estimator=sum, hue='categoria', palette='viridis', legend=False)
    plt.title("Gastos por Categoria & Detecção de Anomalias")
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
    for categoria, limite in metas_carregadas.items():
        gasto_real = gastos_atuais.get(categoria, 0)
        if gasto_real > limite:
            print(f" ALERTA: '{categoria}' estourou! (Excedeu R$ {gasto_real - limite:.2f})")

    detectar_anomalias(df)