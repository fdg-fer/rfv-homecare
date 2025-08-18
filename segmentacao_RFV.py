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
    if recencia <= 15:   # 1 quartil
        return 5
    if recencia <= 25:  # abaixo da mediana
        return 4
    if recencia <= 40:  # abaixo do 3 quartil
        return 3
    if recencia <= 60: # 4 desvios padrao
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
    if frequencia >= 40:
        return 5
    elif frequencia >= 19:
        return 4
    elif frequencia >= 10:
        return 3
    elif frequencia >= 8:
        return 2
    else:
        return 1

# Aplicação
#q1_freq, q2_freq, q3_freq, limite_alto_freq = calcular_frequencia(df, 'qtd_pedidos'
df['frequencia_score'] = df['qtd_pedidos'].apply(calcular_frequencia_dinamica)
    
#---------------------------------------------------------------------------------------------------------------#

vm = df['valor_monetario']


def calcular_vm_dinamica(vm):
    if vm >= 30000:
        return 5  
    if vm >= 18000:
        return 4  
    if vm >= 13000:
        return 3   
    if vm >= 7300:
        return 2   
    else:
        return 1

# Aplicaçâo

df['vm_score'] = df['valor_monetario'].apply(calcular_vm_dinamica)


df['rfv_score'] = df['recencia_score'] + df['frequencia_score'] + df['vm_score']
df['Y_FM_quintis'] = (df['frequencia_score'] + df['vm_score']) / 2

#----------------------------------------------------------------------------------------------------------------#

import numpy as np

# Calculando os quintis dos scores
quintis_recency = np.percentile(df['recencia_score'], [20, 40, 60, 80, 100])
quintis_Y_FM = np.percentile(df['Y_FM_quintis'], [20, 40, 60, 80, 100])

# Garantir que os bins são únicos (caso haja repetição de valores)
quintis_recency = np.unique(quintis_recency)
quintis_Y_FM = np.unique(quintis_Y_FM)

# Em caso de pouca variação, define manualmente os limites
if len(quintis_recency) < 6:
    quintis_recency = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]

if len(quintis_Y_FM) < 6:
    quintis_Y_FM = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]

df['recency_quintis'] = pd.cut(
    df['recencia_score'],
    bins=quintis_recency,
    labels=[1, 2, 3, 4, 5],
    right=True,
    include_lowest=True
)

df['Y_FM_quintis'] = pd.cut(
    df['Y_FM_quintis'],
    bins=quintis_Y_FM,
    labels=[1, 2, 3, 4, 5],
    right=True,
    include_lowest=True
)

def segmentacao(row):
    r = row['recency_quintis']
    fm = row['Y_FM_quintis']

    # Campeões (recente + alto valor/freq)
    if r >= 4 and fm >= 4:
        return 'Campeões'
    # Cliente Leal (recência média/alta + freq/valor médio/alto)
    elif r >= 4 and fm >= 3:
        return 'Cliente Leal'
    # Promissores (recente, mas freq/valor baixo)
    elif r >= 4 and fm <= 2:
        return 'Promissores'
    # Necessitam de Atenção (recência média + freq/valor baixo)
    elif r >= 3 and fm >= 3:
        return 'Necessitam de Atenção'
    # Em risco (freq/valor alto, mas recência baixa)
    elif r == 3 and 1 <= fm <= 2:
        return 'Em Risco'
    # Prestes a Hibernar (recência baixa + freq/valor médio)
    elif r == 2 and 1 <= fm <= 5:
        return 'Prestes a Hibernar'
    # Hibernando (recência baixa + freq/valor baixo)
    elif r == 1 and 1 <= fm <= 5:
        return 'Hibernando'




df['Segmento'] = df.apply(segmentacao, axis=1)


df.to_sql('tabela_RFV', con=engine, if_exists='replace', index=False)

print("Tabela 'tabela_RFV' enviada com sucesso ao PostgreSQL.")

