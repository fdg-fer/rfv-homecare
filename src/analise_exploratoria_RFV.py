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

# Consulta com pandas
df = pd.read_sql(f'SELECT * FROM tabela_RFV', con=engine)


import matplotlib.pyplot as plt
import seaborn as sns
import numpy

 
recencia = df['recencia_dias']
frequencia = df['qtd_pedidos']
valor = df['valor_monetario']
#%%

def plot_boxplot(df, title='', ax=None, figsize=(9, 4)):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    sns.boxplot(x=df, ax=ax)
    ax.set_title(title)
    
    
fig, axes = plt.subplots(1, 1, dpi=120, figsize=(8, 4))
plot_boxplot(recencia, title='Análise de Outliers', ax=axes)
plt.show()


fig, axes = plt.subplots(1, 1, dpi=120, figsize=(8, 4))
plot_boxplot(frequencia, title='Análise de Outliers', ax=axes)
plt.show()


fig, axes = plt.subplots(1, 1, dpi=120, figsize=(8, 4))
plot_boxplot(valor, title='Análise de Outliers', ax=axes)
plt.show()

#%%
recencia.describe()
#%%
frequencia.describe()
#%%
valor.describe()
