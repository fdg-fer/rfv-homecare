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