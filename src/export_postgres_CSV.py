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


# Criar engine de conexão
engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}') 

# Criando df_vendas
df_vendas = pd.read_csv('base_vendas.csv', sep=',', encoding='utf-8')

# Converte direto para datetime
df_vendas['data_venda'] = pd.to_datetime(
    df_vendas['data_venda'], errors='coerce'
)

# Formata no estilo YYYY-MM-DD
df_vendas['data_venda'] = df_vendas['data_venda'].dt.strftime("%Y-%m-%d")


# Enviar para o PostgreSQL 
df_vendas.to_sql('base_vendas_clientes', con=engine, if_exists='replace', index=False)

print("Tabela 'venda_homecare' enviada com sucesso ao PostgreSQL.")
