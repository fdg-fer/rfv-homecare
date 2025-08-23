CREATE TABLE dim_calendario AS
WITH base AS (
  SELECT d::date AS dt
  FROM generate_series('2023-01-01'::date, '2025-12-31'::date, '1 day') gs(d)
)
SELECT
  dt                                               AS data_calendario,
  EXTRACT(YEAR FROM dt)::int                       AS ano,
  EXTRACT(MONTH FROM dt)::int                      AS mes,
  CASE EXTRACT(MONTH FROM dt)::int
    WHEN 1 THEN 'Jan' WHEN 2 THEN 'Fev' WHEN 3 THEN 'Mar' WHEN 4 THEN 'Abr'
    WHEN 5 THEN 'Mai' WHEN 6 THEN 'Jun' WHEN 7 THEN 'Jul' WHEN 8 THEN 'Ago'
    WHEN 9 THEN 'Set' WHEN 10 THEN 'Out' WHEN 11 THEN 'Nov' ELSE 'Dez' END
                                                    AS mes_abrev,
  CASE EXTRACT(MONTH FROM dt)::int
    WHEN 1 THEN 'Janeiro'   WHEN 2 THEN 'Fevereiro' WHEN 3 THEN 'Março'
    WHEN 4 THEN 'Abril'     WHEN 5 THEN 'Maio'      WHEN 6 THEN 'Junho'
    WHEN 7 THEN 'Julho'     WHEN 8 THEN 'Agosto'    WHEN 9 THEN 'Setembro'
    WHEN 10 THEN 'Outubro'  WHEN 11 THEN 'Novembro' ELSE 'Dezembro' END
                                                    AS mes_nome,
  EXTRACT(QUARTER FROM dt)::int                    AS trimestre,
  'T' || EXTRACT(QUARTER FROM dt)::int             AS nome_trimestre
FROM base
ORDER BY 1;
