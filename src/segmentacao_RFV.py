#%%
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import numpy as np


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


#--------------------------------------------------------------------------------------------------------------#

recencia = df['recencia_dias']


def calcular_recencia(recencia):
    if recencia <= 20:   
        return 5
    if recencia <= 33:  
        return 4
    if recencia <= 64:  
        return 3
    if recencia <= 146: 
        return 2     
    else:
        return 1
    

df['recencia_score'] = df['recencia_dias'].apply(calcular_recencia)

#--------------------------------------------------------------------------------------------------------------#

frequencia = df['qtd_pedidos']


def calcular_frequencia(frequencia):
    if frequencia >= 18: 
        return 5
    elif frequencia >= 16:
        return 4
    elif frequencia >= 13:
        return 3
    elif frequencia >= 11:
        return 2
    else:
        return 1


df['frequencia_score'] = df['qtd_pedidos'].apply(calcular_frequencia)
    
#---------------------------------------------------------------------------------------------------------------#

vm = df['valor_monetario']


def calcular_vm(vm):
    if vm <= 120000: 
        return 1  
    if vm <= 250000:
        return 2 
    if vm <= 420000:
        return 3  
    if vm <= 543000: 
        return 4  
    else:
        return 5  
 
 
df['vm_score'] = df['valor_monetario'].apply(calcular_vm)

#---------------------------------------------------------------------------------------------------------------#


# Y_FM: quintil sobre o score contínuo Y_FM_score
df['Y_FM_score']  = (df['frequencia_score'] + df['vm_score']) / 2.0   # contínuo (pode ter 1.5, 2.0, 2.5, ...)

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

#---------------------------------------------------------------------------------------------------------------#

#df['recency_5X'] = df['recencia_score']


df['Y_FM_5X'] = pd.cut(
    df['Y_FM_score'],
    bins=quintis_Y_FM_edges,
    labels=[1, 2, 3, 4, 5],
    right=True,
    include_lowest=True
)

# Coagir para inteiro (cuidando de NaN)
df['recencia_score'] = df['recencia_score'].astype('Int64')
df['Y_FM_5X']    = df['Y_FM_5X'].astype('Int64')

#---------------------------------------------------------------------------------------------------------------#

def segmentacao(row):
    r = row['recencia_score']
    fm = row['Y_FM_5X']

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

#---------------------------------------------------------------------------------------------------------------#

df.to_sql('tabela_RFV', con=engine, if_exists='replace', index=False)

print("Tabela 'tabela_RFV' enviada com sucesso ao PostgreSQL.")

