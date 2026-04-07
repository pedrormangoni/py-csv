-- Arquivo: 00_vw_base_transacoes.sql
-- Objetivo: Definir a view base de transações com atributos derivados para BI.
-- Dependência: Tabela `stg_credit_card_transactions`.
-- Saída: View `vw_base_transacoes` pronta para Power BI, KPIs e consultas analíticas.

CREATE OR REPLACE VIEW vw_base_transacoes AS
WITH base AS (
	SELECT
		id,
		batch_id,
		row_number,
		row_hash,
		purchase_date,
		EXTRACT(YEAR FROM purchase_date)::INTEGER AS purchase_year,
		EXTRACT(MONTH FROM purchase_date)::INTEGER AS purchase_month_number,
		DATE_TRUNC('month', purchase_date)::DATE AS purchase_month,
		DATE_TRUNC('week', purchase_date)::DATE AS purchase_week,
		TO_CHAR(purchase_date, 'YYYY-MM') AS purchase_year_month,
		CONCAT(
			EXTRACT(ISOYEAR FROM purchase_date)::INTEGER,
			'-',
			LPAD(EXTRACT(WEEK FROM purchase_date)::INTEGER::TEXT, 2, '0')
		) AS purchase_year_week,
		EXTRACT(QUARTER FROM purchase_date)::INTEGER AS purchase_quarter,
		EXTRACT(ISODOW FROM purchase_date)::INTEGER AS weekday_number,
		TO_CHAR(purchase_date, 'TMDay') AS weekday_name,
		CASE
			WHEN EXTRACT(ISODOW FROM purchase_date) IN (6, 7) THEN TRUE
			ELSE FALSE
		END AS is_weekend,
		cardholder_name,
		card_last4,
		CONCAT(cardholder_name, ' • ', card_last4) AS card_key,
		category,
		LOWER(REGEXP_REPLACE(TRIM(category), '\s+', ' ', 'g')) AS category_key,
		description,
		LOWER(REGEXP_REPLACE(TRIM(description), '\s+', ' ', 'g')) AS description_key,
		installment_raw,
		COALESCE(installment_number, 1) AS installment_number,
		COALESCE(installment_total, 1) AS installment_total,
		CASE
			WHEN COALESCE(installment_total, 1) > 1 THEN TRUE
			ELSE FALSE
		END AS is_installment,
		CASE
			WHEN COALESCE(installment_total, 1) > 1 THEN 'parcelada'
			ELSE 'a_vista'
		END AS purchase_type,
		amount_usd,
		fx_rate_brl,
		amount_brl,
		CASE
			WHEN amount_usd > 0 THEN ROUND(amount_brl - (amount_usd * fx_rate_brl), 2)
			ELSE 0
		END AS fx_impact_brl,
		source_file_name,
		loaded_at,
		MD5(
			CONCAT_WS(
				'|',
				LOWER(REGEXP_REPLACE(TRIM(description), '\s+', ' ', 'g')),
				LOWER(REGEXP_REPLACE(TRIM(category), '\s+', ' ', 'g')),
				card_last4,
				ROUND(amount_brl, 2)::TEXT
			)
		) AS recurring_signature
	FROM stg_credit_card_transactions
	WHERE amount_brl > 0
)
SELECT
	base.*, 
	COUNT(*) OVER (PARTITION BY recurring_signature) AS recurring_occurrences,
	CASE
		WHEN COUNT(*) OVER (PARTITION BY recurring_signature) > 1 THEN TRUE
		ELSE FALSE
	END AS is_recurring_candidate,
	MIN(purchase_date) OVER (PARTITION BY recurring_signature) AS recurring_first_purchase_date,
	MAX(purchase_date) OVER (PARTITION BY recurring_signature) AS recurring_last_purchase_date
FROM base;
