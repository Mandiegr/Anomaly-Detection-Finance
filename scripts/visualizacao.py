import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import database
from datetime import datetime

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
        
def comparar_meses(df_completo, mes_atual, mes_anterior):
    print(f"\n--- COMPARAÇÃO: MÊS {mes_anterior} vs MÊS {mes_atual} ---")
    df_completo = df_completo.copy()
    df_completo['mes_temp'] = pd.to_datetime(df_completo['data']).dt.strftime('%m')
    gastos_atual = df_completo[(df_completo['mes_temp'] == mes_atual) & (df_completo['tipo'] == 'Débito')]['valor'].sum()
    gastos_anterior = df_completo[(df_completo['mes_temp'] == mes_anterior) & (df_completo['tipo'] == 'Débito')]['valor'].sum()
    if gastos_anterior > 0:
        diferenca = gastos_anterior - gastos_atual
        percentual = (diferenca / gastos_anterior) * 100
        if diferenca > 0:
            print(f" Economia real de R$ {diferenca:.2f} ({percentual:.1f}% a menos que o mês anterior).")
        else:
            print(f" Aumento de gastos de R$ {abs(diferenca):.2f} ({abs(percentual):.1f}% a mais que o mês anterior).")
    else:
        print(" Dados insuficientes no mês anterior para comparação.")

def prever_gastos_anual(df):
    print("\n---PREVISÃO INTELIGENTE (IA Versão 2.0) ---")
    gastos = df[df['tipo'] == 'Débito'].copy()
    if len(gastos) < 2:
        print(" Dados insuficientes para criar uma tendência.")
        return

    gastos['data'] = pd.to_datetime(gastos['data'])
    total_real_acumulado = gastos['valor'].sum()
    
    media_unitaria = gastos['valor'].mean()
    desvio = gastos['valor'].std()
    limite_outlier = media_unitaria + (2 * desvio)
    
    gastos_comuns = gastos[gastos['valor'] <= limite_outlier]
    gastos_atipicos = gastos[gastos['valor'] > limite_outlier]
    
    data_min = gastos['data'].min()
    data_max = datetime.now()
    dias_passados = max((data_max - data_min).days + 1, 1)

    fim_do_ano = datetime(2026, 12, 31)
    dias_restantes = max((fim_do_ano - data_max).days, 0)
    
    media_diaria_realista = gastos_comuns['valor'].sum() / dias_passados
    previsao_restante = media_diaria_realista * dias_restantes
    final_do_ano_estimado = total_real_acumulado + previsao_restante

    print(f"• Analisados {len(gastos)} registros ({len(gastos_atipicos)} detectados como atípicos).")
    print(f"• Média diária ajustada (sem ruído): R$ {media_diaria_realista:.2f}")
    print(f"• PROJEÇÃO REALISTA FINAL: R$ {final_do_ano_estimado:.2f}")

    teto_seguro = 40000 
    if final_do_ano_estimado > teto_seguro:
        excesso = final_do_ano_estimado - teto_seguro
        print(f"\n INSIGHT: Você está R$ {excesso:.2f} acima do seu teto seguro.")
        div_dias = max(dias_restantes, 1)
        print(f" Sugestão: Reduza R$ {excesso/div_dias:.2f} nos gastos diários até Dezembro.")
    else: 
        print("\nParabéns! Seu ritmo atual está dentro de uma margem segura para o ano.")   

def gerar_relatorios(df, mes_selecionado=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_original = df.copy() 
    
    if mes_selecionado:
        df['mes_temp'] = pd.to_datetime(df['data']).dt.strftime('%m')
        df = df[df['mes_temp'] == mes_selecionado].copy()
        if df.empty:
            print(f"\n Não há gastos registrados para o mês {mes_selecionado}.")
            return
    
    metas_carregadas = carregar_metas()
    plt.figure(figsize=(10,6))
    sns.barplot(data=df[df['tipo']=='Débito'], x='categoria', y='valor', estimator=sum, hue='categoria', palette='viridis', legend=False)
    plt.title(f"Gastos por Categoria - Mês {mes_selecionado if mes_selecionado else 'Geral'}")
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(OUTPUT_DIR, f'grafico_mes_{mes_selecionado}.png'))
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
    if mes_selecionado and mes_selecionado.isdigit():
        mes_num = int(mes_selecionado)
        if mes_num > 1:
            mes_ant = str(mes_num - 1).zfill(2)
            comparar_meses(df_original, mes_selecionado, mes_ant)