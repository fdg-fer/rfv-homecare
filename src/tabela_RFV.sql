create or replace view tabela_RFV AS (
	-- Converte a coluna data_venda para data
	WITH convert_data as(
		select nome_cliente, TO_DATE(data_venda, 'YYYY-MM-DD') as data_venda
		from base_vendas_clientes

	),
	
	data_final_base as(
		select 
		max(data_venda) as data_final_base 
		from convert_data	

	),
	-- pegar a data mais recente de compra de cada cliente
	data_maxima as (
		select
		nome_cliente,
		max(data_venda) as data_max
		--current_date - max(data_venda) as recencia_dias
		from convert_data
		group by nome_cliente
		
	
	),	
	rfv as (
		select 
		nome_cliente,
		count(*) as qtd_pedidos,
		ROUND(SUM(valor_produto)::numeric, 2) AS valor_monetario
		from base_vendas_clientes
		group by nome_cliente
	)
	
	select 
		rfv.nome_cliente,
		rfv.qtd_pedidos,
		rfv.valor_monetario,
		dm.data_max,
		df.data_final_base - dm.data_max as recencia_dias,
		--dm.recencia_dias,
		round(rfv.valor_monetario::numeric/rfv.qtd_pedidos,2) as ticket_medio,
		df.data_final_base
	from rfv 
	left join data_maxima as dm on rfv.nome_cliente = dm.nome_cliente

	cross join data_final_base as df
)