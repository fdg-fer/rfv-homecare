#%%
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Carregar variáveis do .env
load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')


# Criação da engine de conexão
engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')

# Faz a leitura da tabela no postgres com pandas 
df = pd.read_sql(f'SELECT * FROM tabela_RFV', con=engine)


recencia = df['recencia_dias']


def calcular_recencia_dinamica(recencia):
    if recencia <= 16:   # 1 quartil
        return 5
    if recencia <= 33:  # abaixo da mediana
        return 4
    if recencia <= 64:  # abaixo do 3 quartil
        return 3
    if recencia <= 146: # 4 desvios padrao
        return 2     
    else:
        return 1
    

# Depois aplica a função que atribui a pontuação, para cada valor da coluna
df['recencia_score'] = df['recencia_dias'].apply(calcular_recencia_dinamica)

#df.head(10)

#--------------------------------------------------------------------------------------------------------------#

frequencia = df['qtd_pedidos']
frequencia.describe()


def calcular_frequencia_dinamica(frequencia):
    if frequencia > 18:
        return 5
    elif frequencia >= 16:
        return 4
    elif frequencia >= 13:
        return 3
    elif frequencia >= 11:
        return 2
    else:
        return 1

# Aplicação
#q1_freq, q2_freq, q3_freq, limite_alto_freq = calcular_frequencia(df, 'qtd_pedidos'
df['frequencia_score'] = df['qtd_pedidos'].apply(calcular_frequencia_dinamica)
    
#---------------------------------------------------------------------------------------------------------------#

vm = df['valor_monetario']


def calcular_vm_dinamica(vm):
    if vm <= 120000: # média - 1 desvio
        return 1  
    if vm <= 250000: # até a média
        return 2 
    if vm <= 400000: # média + 1 desvio
        return 3  
    if vm <= 600000: # média + 2 desvios
        return 4  
    else:
        return 5     # acima de 630k 

# Aplicaçâo
import numpy as np

df['vm_score'] = df['valor_monetario'].apply(calcular_vm_dinamica)


df['rfv_score']   = df['recencia_score'] + df['frequencia_score'] + df['vm_score']
df['Y_FM_score']  = (df['frequencia_score'] + df['vm_score']) / 2.0   # contínuo (pode ter 1.5, 2.0, 2.5, ...)

# -------------------------------------------
# 1) QUINTIS: calcule sobre o CONTÍNUO
#    (não sobre as colunas já discretizadas 1..5)
# -------------------------------------------

# Recency: se quiser quintil do score 1..5, melhor usar as bordas fixas
# Caso queira quintil "de verdade", use a MÉTRICA CONTÍNUA (ex.: dias de recência)
# Exemplo abaixo usa bordas fixas para o score 1..5:
quintis_recency_edges = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]

# Y_FM: quintil sobre o score contínuo Y_FM_score
quintis_Y_FM = np.percentile(df['Y_FM_score'], [20, 40, 60, 80, 100])
quintis_Y_FM = np.unique(quintis_Y_FM)
if len(quintis_Y_FM) < 6:
    # fallback para bins estáveis cobrindo notas 1..5
    quintis_Y_FM_edges = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
else:
    # quando vierem 5 cortes únicos, precisamos de 6 arestas.
    # Acrescente a aresta inferior. Como Y_FM_score vai de 1..5 (média de scores 1..5),
    # use 0.5 como limite inferior "seguro".
    quintis_Y_FM_edges = np.concatenate(([0.5], quintis_Y_FM))

# -------------------------------------------
# 2) APLICAR cortes (labels 1..5)
# -------------------------------------------

df['recency_5X'] = pd.cut(
    df['recencia_score'],
    bins=quintis_recency_edges,
    labels=[1, 2, 3, 4, 5],
    right=True,
    include_lowest=True
)

df['Y_FM_5X'] = pd.cut(
    df['Y_FM_score'],
    bins=quintis_Y_FM_edges,
    labels=[1, 2, 3, 4, 5],
    right=True,
    include_lowest=True
)

# Coagir para inteiro (cuidando de NaN)
df['recency_5X'] = df['recency_5X'].astype('Int64')
df['Y_FM_5X']    = df['Y_FM_5X'].astype('Int64')

# -------------------------------------------
# 3) SEGMENTAÇÃO
# -------------------------------------------

def segmentacao(row):
    r = row['recency_5X']
    fm = row['Y_FM_5X']
    if pd.isna(r) or pd.isna(fm):
        return 'Sem Classificação'
    r, fm = int(r), int(fm)

    # 1) Campeões: muito recentes e alto FM
    if r >= 4 and fm >= 4:
        return 'Campeões'
    # 2) Cliente Leal: recente e FM médio
    elif r >= 4 and fm == 3:
        return 'Cliente Leal'
    # 3) Promissores: muito recentes mas FM baixo
    elif r == 5 and fm <= 2:
        return 'Promissores'
    # 4) Necessitam de Atenção: recência média e FM médio
    elif r == 3 and fm == 3:
        return 'Necessitam de Atenção'
    # 5) Em Risco: FM bom/alto, mas recência caiu
    elif r <= 2 and fm >= 4:
        return 'Em Risco'
    # 6) Prestes a Hibernar: recência baixa, FM baixo/médio
    elif r == 2 and fm <= 3:
        return 'Prestes a Hibernar'
    # 7) Hibernando: pior recência
    elif r == 1:
        return 'Hibernando'
    else:
        return 'Necessitam de Atenção'

df['Segmento'] = df.apply(segmentacao, axis=1)
#print(df['Segmento'].value_counts(dropna=False))



df.to_sql('tabela_RFV', con=engine, if_exists='replace', index=False)

print("Tabela 'tabela_RFV' enviada com sucesso ao PostgreSQL.")

