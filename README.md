## 🎯 Por que utilizar Análise RFV?

O objetivo desta análise é segmentar clientes de forma estratégica, permitindo que o marketing desenvolva ações mais precisas de relacionamento, retenção e fidelização.

Por meio dessa metodologia, é possível mapear padrões de comportamento, gerar insights valiosos e antecipar necessidades, tornando as estratégias mais assertivas e personalizadas. 

---

### As variáveis chaves utilizadas são:

---

#### 📆 Recência  
A variável mais determinante da RFV. Ela descreve a etapa em que o cliente se encontra, que pode ser definida em três ciclos:

1. **Clientes Futuros**  
2. **Clientes Potenciais**  
3. **Clientes Ativos**  

---

#### 🛍 Frequência  
Define o número de vezes que o cliente realizou uma compra. 

Esse indicador está altamente relacionado à **qualidade do produto ou serviço prestado**, demonstrando o quanto a empresa está presente na mente do cliente ao decidir fazer negócios novamente.  

---

#### 💰 Valor  
Corresponde ao **valor total gasto** em produtos ou serviços.  

Esse indicador permite identificar consumidores mais ou menos lucrativos.  
Somente a variável de Valor é capaz de estabelecer uma **hierarquia clara**, quando analisada em conjunto com Recência e Frequência.  

---

#### Conclusão  
A metodologia **RFV** é a base para qualquer modelo preditivo de comportamento de clientes, pois combina **baixo custo de aplicação** com **alto potencial de aumento de lucratividade**.<br>  

---

👉 E você, já utiliza RFV na sua estratégia de clientes?<br>
<br>

---
# 📊 Análise RFV – Indústria de Produtos Hospitalares

## 📌 Contexto do Projeto
Este projeto aplica a análise **RFV (Recência, Frequência e Valor)** para clientes de uma **indústria fictícia de produtos hospitalares**, que vende insumos, descartáveis e equipamentos médicos para **clínicas pequenas e hospitais grandes**.

A análise tem como objetivo **segmentar clientes por comportamento de compra**, permitindo identificar perfis estratégicos e definir ações de marketing e vendas mais assertivas.

📌 Recorte de tempo da base: **12 meses (último ano)**

---

### 🛠️ Tecnologias Utilizadas

- **Banco de Dados**: PostgreSQL
- **Linguagem**: Python (pandas, numpy, SQLAlchemy)
- **Visualização**: Power BI
- **Versionamento e Documentação**: GitHub

---

## ⚙️ Pipeline Analítico

### 1. Estrutura da Base
A base fictícia contém **1.000 registros de venda** e **67 clientes**.  
Cada registro inclui:

 ![Tabela_Base](<img/tabela_01.png>)

---

### 2. Construção da Tabela RFV
No **PostgreSQL**, foram geradas as variáveis principais:

- `recencia`: dias desde a última compra  
- `frequencia`: número total de pedidos  
- `valor_monetario`: soma total gasta pelo cliente  
- `ticket_medio`: valor médio gasto por pedido  

 ![Tabela_Base](<img/tabela_02.png>)

Exemplo do SQL:
```sql
CREATE OR REPLACE VIEW tabela_RFV AS (
	-- converte a coluna data_venda para data
	WITH convert_data as(
		SELECT id_cliente, nome_cliente, TO_DATE(data_venda, 'YYYY-MM-DD') AS data_venda
		FROM base_vendas_clientes
	),
	-- data mais recente da base
	data_final_base AS(
		SELECT 
		MAX(data_venda) AS data_final_base 
		FROM convert_data	
	),
	-- pegar a data mais recente de compra de cada cliente
	data_maxima AS (
		SELECT
		id_cliente,
		nome_cliente,
		MAX(data_venda) AS data_max
		FROM convert_data
		GROUP BY id_cliente, nome_cliente
	),	
	-- agregações 
	rfv AS (
		SELECT 
		id_cliente,
		nome_cliente,
		COUNT(*) AS qtd_pedidos,
		ROUND(SUM(valor_produto)::numeric, 2) AS valor_monetario
		FROM base_vendas_clientes
		GROUP BY id_cliente, nome_cliente
	)
	-- tabela final
	SELECT 
		rfv.id_cliente,
		rfv.nome_cliente,
		rfv.qtd_pedidos,  -- frequencia
		rfv.valor_monetario, -- valor monetario
		dm.data_max,
		df.data_final_base - dm.data_max AS recencia_dias, -- recencia
		round(rfv.valor_monetario::numeric/rfv.qtd_pedidos,2) AS ticket_medio,
		df.data_final_base
	FROM rfv 
	LEFT JOIN data_maxima AS dm ON rfv.nome_cliente = dm.nome_cliente
	CROSS JOIN data_final_base AS df
)
````

### 3. Scores RFV (Python)

A definição dos scores de 1 a 5 não foi criada de forma deliberada, cada varíável passou por uma análise exploratória e com base na distribuição. 

**Recência (R)**: cortes dinâmicos por quantis (quanto mais recente, maior o score).
- **Nota 5** = O primeiro quartil da  distribuição foi de aprox. 16 dias. Definição com recência **≤ 20 dias**, arredondando para cima para não penalizar clientes muito próximos do corte.
- **Nota 4** = Definido com base na mediana que foi em torno de **33 dias**.
- **Nota 3** = Defini com base no terceiro quartil que foi de **64 dias**.
- **Nota 2** = Essa nota foi baseada no critério de média + desvio-padrão, que resultou em **146 dias**.
- **Nota 1** = Tudo que for **maior** que **146 dias**.



**Frequência (F)**: cortes baseados na distribuição observada (clientes recorrentes = maior score).



**Valor Monetário (V)**: abordagem híbrida, usando média ± desvio padrão para definir faixas.

Exemplo aplicado ao Valor Monetário:

````python
def calcular_vm(vm):
    if vm <= 120000: return 1
    if vm <= 288000: return 2
    if vm <= 460000: return 3
    if vm <= 630000: return 4
    else: return 5 
````




### 4. Segmentação Final

A partir dos scores e quintis, os clientes foram classificados em **7 segmentos**:

1. **Campeões** – muito recentes, alta frequência e alto valor.  
2. **Clientes Leais** – recentes, compras regulares, valor médio/alto.  
3. **Promissores** – recentes, mas baixo valor/frequência.  
4. **Necessitam de Atenção** – recência média, frequência/valor medianos.  
5. **Em Risco** – gastavam alto, mas estão há muito tempo sem comprar.  
6. **Prestes a Hibernar** – baixa recência, baixo/médio valor.  
7. **Hibernando** – muito tempo sem comprar, baixo valor e frequência.  


### 📊 Visualização – Power BI
#### Aba 1 – RFV (Clientes)

- **KPIs (cards)**: total de clientes, ticket médio, valor acumulado, percentual de campeões
- **Gráfico de dispersão**: recência × frequência/valor (cores por segmento)
- **Tabela detalhada**: cliente, recência, frequência, valor e segmento
- **Barras horizontais**: distribuição por segmento

#### Aba 2 – Produtos

- **Ranking de produtos mais vendidos** (volume e valor)
- **Filtro por segmento de cliente** (ex.: o que os Campeões mais compram)
- **Comparativo Hospitais × Clínicas** por categoria de produto
- **Distribuição por categoria**: descartáveis, insumos e equipamentos

### 📌 Insights de Negócio por Segmento

- **Campeões** → manter engajamento com benefícios exclusivos, early access a novos produtos, suporte diferenciado.
- **Clientes Leais** → estimular upsell (kits, pacotes), programas de fidelidade.
- **Promissores** → nutrir relacionamento (promoções de entrada, descontos progressivos).
- **Necessitam de Atenção** → campanhas personalizadas para aumentar frequência (ex.: kits emergenciais).
- **Em Risco** → ações de reativação (ofertas agressivas, contato direto do comercial).
- **Prestes a Hibernar** → monitoramento e alertas para não perder clientes (descontos de   retenção).
- **Hibernando** → avaliar custo de reativar vs. aquisição de novos clientes.


### 🚀 Conclusão

A análise RFV permitiu **segmentar os clientes e identificar perfis estratégicos**, trazendo clareza sobre quem são os campeões, quem está em risco e quem pode ser perdido.
Além disso, a segunda aba focada em **produtos** mostrou **padrões de consumo** relevantes para apoiar **estratégias comerciais**.


