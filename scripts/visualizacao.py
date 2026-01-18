import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
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
            print(f"   (Fugiu do padrão da média de R$ {media:.2f})")
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
        print(f" Resultado: {'Economia' if diferenca > 0 else 'Aumento'} de R$ {abs(diferenca):.2f} ({abs(percentual):.1f}%)")
    else:
        print(" Dados insuficientes para comparar.")

def simular_economia(df):
    print("\n--- SIMULADOR DE ECONOMIA (Cenário de -10%) ---")
    recorrentes = df.groupby('descricao').filter(lambda x: len(x) > 1 and x['valor'].nunique() == 1)
    variaveis = df[(df['tipo'] == 'Débito') & (~df['descricao'].isin(recorrentes['descricao']))].copy()
    
    if variaveis.empty:
        print("  Sem gastos variáveis suficientes para simular.")
        return

    hoje = datetime.now()
    dias_passados = max((hoje - datetime(2026, 1, 1)).days, 1)
    dias_restantes = (datetime(2026, 12, 31) - hoje).days
    
    gastos_por_cat = variaveis.groupby('categoria')['valor'].sum()
    
    for cat, valor_total in gastos_por_cat.items():
        media_diaria = valor_total / dias_passados
        economia_estimada = (media_diaria * 0.10) * dias_restantes
        if economia_estimada > 1.0:
            print(f"  • {cat}: Cortar 10% poupa R$ {economia_estimada:.2f} até Dezembro")

def prever_gastos_anual(df):
    print("\n--- PREVISÃO INTELIGENTE ---")
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
            meses_faltantes = max(meses_faltantes, 0)
        total_fixo_futuro += (row['valor'] * meses_faltantes)
        print(f"  • {desc}: R$ {row['valor']:.2f} ({'Faltam ' + str(meses_faltantes) + ' meses' if meses_faltantes > 0 else 'Finalizado'})")

    variaveis = gastos[~gastos['descricao'].isin(fixos.index)].copy()
    media_v = variaveis['valor'].mean()
    desvio_v = variaveis['valor'].std()
    variaveis_normais = variaveis[variaveis['valor'] <= (media_v + 1.5 * desvio_v)]
    
    dias_passados_ano = max((data_hoje - datetime(2026, 1, 1)).days + 1, 1)
    dias_restantes_ano = (datetime(2026, 12, 31) - data_hoje).days
    
    media_diaria_v = variaveis_normais['valor'].sum() / dias_passados_ano
    total_v_projetado = media_diaria_v * dias_restantes_ano

    total_ja_gasto = gastos['valor'].sum()
    projecao_final = total_ja_gasto + total_fixo_futuro + total_v_projetado

    print("-" * 45)
    print(f" Gasto acumulado: R$ {total_ja_gasto:.2f}")
    print(f" Fixos a vencer : R$ {total_fixo_futuro:.2f}")
    print(f" Variáveis est. : R$ {total_v_projetado:.2f}")
    print(f" PROJEÇÃO FINAL: R$ {projecao_final:.2f}")
    
    gasto_mensal_est = (total_v_projetado / 11) + (total_fixo_futuro / 11 if total_fixo_futuro > 0 else 0)
    print(f"\n Custo de vida estimado: R$ {gasto_mensal_est:.2f}/mês")
    
    
def verificar_alertas_orcamento(gastos_atuais, metas):
    print("\n--- CENTRAL DE ALERTAS ---")
    avisos = 0
    for categoria, limite in metas.items():
        gasto_real = gastos_atuais.get(categoria, 0)
        
        if limite > 0:
            percentual = (gasto_real / limite) * 100
            
            if percentual >= 100:
                print(f" CRÍTICO: Você estourou {categoria}! ({percentual:.1f}% do limite)")
                avisos += 1
            elif percentual >= 80:
                print(f" ATENÇÃO: {categoria} está em {percentual:.1f}%. Quase no limite!")
                avisos += 1
    
    if avisos == 0:
        print("  Tudo sob controle. Nenhuma meta em risco por enquanto.")
        

def gerar_relatorios(df, mes_selecionado=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_original = df.copy()
    
    if mes_selecionado:
        df['mes_temp'] = pd.to_datetime(df['data']).dt.strftime('%m')
        df = df[df['mes_temp'] == mes_selecionado].copy()
        if df.empty:
            print(f" Sem dados para o mês {mes_selecionado}.")
            return
    
    plt.figure(figsize=(10,6))
    sns.barplot(data=df[df['tipo']=='Débito'], x='categoria', y='valor', estimator=sum, palette='viridis', hue='categoria', legend=False)
    plt.title(f"Gastos por Categoria - Mês {mes_selecionado if mes_selecionado else 'Geral'}")
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(OUTPUT_DIR, f'grafico_mes_{mes_selecionado}.png'))
    plt.close()
    df.to_excel(os.path.join(OUTPUT_DIR, 'relatorio.xlsx'), index=False)

    gastos_atuais = df[df['tipo'] == 'Débito'].groupby('categoria')['valor'].sum()
    
    print("\n--- ANÁLISE DE IMPACTO NO BOLSO ---")
    total_geral = gastos_atuais.sum()
    if total_geral > 0:
        for cat, val in gastos_atuais.items():
            print(f" • {cat}: {(val/total_geral)*100:.1f}% (R$ {val:.2f})")

    verificar_alertas_orcamento(gastos_atuais, carregar_metas())
    detectar_anomalias(df)

           
def exportar_plano_acao(df):
     plano_path = os.path.join(OUTPUT_DIR, 'plano_de_acao_2026.txt')
     hoje = datetime.now().strftime('%d/%m/%Y')
   
     metas = carregar_metas()
     gastos_atuais = df[df['tipo'] == 'Débito'].groupby('categoria')['valor'].sum()
    
     with open(plano_path, 'w', encoding='utf-8') as f:
        f.write(f"--- PLANO DE AÇÃO FINANCEIRA 2026 ---\n")
        f.write(f"Gerado em: {hoje}\n\n")
        
        f.write("1. DIAGNÓSTICO ATUAL\n")
        for cat, valor in gastos_atuais.items():
            f.write(f" • {cat}: R$ {valor:.2f}\n")
            
        f.write("\n2. ALERTAS CRÍTICOS\n")
        avisos = False
        for cat, limite in metas.items():
            real = gastos_atuais.get(cat, 0)
            if real > limite:
                f.write(f" REDUZIR IMEDIATAMENTE: {cat} (R$ {real-limite:.2f} acima da meta)\n")
                avisos = True
        if not avisos: f.write(" Nenhuma meta estourada no momento.\n")

        f.write("\n3. ESTRATÉGIA DE ECONOMIA (Meta -10%)\n")
        
        dias_restantes = (datetime(2026, 12, 31) - datetime.now()).days
        dias_passados = max((datetime.now() - datetime(2026, 1, 1)).days, 1)
        
        for cat, valor in gastos_atuais.items():
            economia = ((valor / dias_passados) * 0.10) * dias_restantes
            if economia > 5:
                f.write(f" Se cortar 10% de {cat}, você salva R$ {economia:.2f} até o fim do ano.\n")

        f.write("\n--- FIM DO PLANO ---\n")
     
     print(f"\n Plano de ação exportado com sucesso para: {plano_path}")
     