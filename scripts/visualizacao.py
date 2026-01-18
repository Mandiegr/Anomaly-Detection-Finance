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
    print("\n---PREVISÃO INTELIGENTE ---")
    
    gastos = df[df['tipo'] == 'Débito'].copy()
    if len(gastos) < 2:
        print(" Dados insuficientes.")
        return

    gastos['data'] = pd.to_datetime(gastos['data'])
    data_hoje = datetime.now()
    
    resumo_fixos = gastos.groupby('descricao').agg(
        valor=('valor', 'mean'),
        ultima_data=('data', 'max'),
        contagem=('id', 'count')
    )
    
    fixos = resumo_fixos[resumo_fixos['contagem'] > 1]
    
    total_fixo_futuro = 0
    print(" Compromissos fixos identificados:")
    for desc, row in fixos.iterrows():
       
        meses_faltantes = 0
        if row['ultima_data'] > data_hoje:
           
            meses_faltantes = (row['ultima_data'].year - data_hoje.year) * 12 + (row['ultima_data'].month - data_hoje.month)
            if meses_faltantes < 0: meses_faltantes = 0
            
        total_fixo_futuro += (row['valor'] * meses_faltantes)
        status = f"Faltam {meses_faltantes} meses" if meses_faltantes > 0 else "Finalizado"
        print(f"  • {desc}: R$ {row['valor']:.2f} ({status})")

    variaveis = gastos[~gastos['descricao'].isin(fixos.index)].copy()
    
    media_v = variaveis['valor'].mean()
    desvio_v = variaveis['valor'].std()
   
    variaveis_normais = variaveis[variaveis['valor'] <= (media_v + 1.5 * desvio_v)]
    
    dias_passados_ano = (data_hoje - datetime(2026, 1, 1)).days + 1
    dias_restantes_ano = (datetime(2026, 12, 31) - data_hoje).days
    
    media_diaria_variavel = variaveis_normais['valor'].sum() / dias_passados_ano
    total_variavel_projetado = media_diaria_variavel * dias_restantes_ano

    total_ja_gasto = gastos['valor'].sum()
    projecao_final = total_ja_gasto + total_fixo_futuro + total_variavel_projetado

    print("-" * 45)
    print(f" Gasto Total até hoje: R$ {total_ja_gasto:.2f}")
    print(f" Total de Fixos a vencer: R$ {total_fixo_futuro:.2f}")
    print(f" Estimativa de Variáveis até Dez: R$ {total_variavel_projetado:.2f}")
    print(f" PROJEÇÃO FINAL 2026: R$ {projecao_final:.2f}")
    
    if projecao_final > 40000:
        print(f"\n DICA: Você terminará o ano com R$ {projecao_final:.2f}.")
        print(f"Lembre-se: em Junho você terá um 'alívio' de R$ {valor_fixo_mensal:.2f} no orçamento!")
    print("\n--- IA ESPECIALISTA EM FINANÇAS  ---")
    
    gastos = df[df['tipo'] == 'Débito'].copy()
    if len(gastos) < 2:
        print(" Dados insuficientes para uma análise realista.")
        return

    gastos['data'] = pd.to_datetime(gastos['data'])
    data_hoje = datetime.now()
    
    recorrentes = gastos.groupby('descricao').filter(lambda x: len(x) > 1 and x['valor'].nunique() == 1)
    valor_fixo_mensal = recorrentes.groupby('descricao')['valor'].mean().sum()
   
    variaveis = gastos[~gastos.index.isin(recorrentes.index)].copy()
    
    media_v = variaveis['valor'].mean()
    desvio_v = variaveis['valor'].std()

    variaveis_normais = variaveis[variaveis['valor'] <= (media_v + 2 * desvio_v)]
    

    meses_restantes = 12 - data_hoje.month
    dias_passados_ano = (data_hoje - datetime(2026, 1, 1)).days + 1
    dias_restantes_ano = (datetime(2026, 12, 31) - data_hoje).days
    
  
    total_fixo_ano = valor_fixo_mensal * 12 
    
  
    media_diaria_variavel = variaveis_normais['valor'].sum() / dias_passados_ano
    total_variavel_projetado = media_diaria_variavel * 365
    

    outliers = variaveis[variaveis['valor'] > (media_v + 2 * desvio_v)]
    total_outliers = outliers['valor'].sum()

    projecao_final = total_fixo_ano + total_variavel_projetado + total_outliers

    print(f" Gastos Fixos (Pós, etc): R$ {valor_fixo_mensal:.2f}/mês")
    print(f" Gastos Variáveis (Dia a dia): R$ {media_diaria_variavel:.2f}/dia")
    print(f" Gastos Extraordinários já feitos: R$ {total_outliers:.2f}")
    print("-" * 45)
    print(f" PROJEÇÃO FINAL 2026: R$ {projecao_final:.2f}")
    
    gasto_mensal_est = valor_fixo_mensal + (media_diaria_variavel * 30)
    print(f"\n Seu custo de vida estimado é de R$ {gasto_mensal_est:.2f} por mês.")
    
    if projecao_final > 40000:
        print(" DICA: Seus gastos variáveis estão acima do planejado. Revise as 'anomalias' no relatório.")
    else:
        print("Seu ritmo financeiro está saudável para 2026!")


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