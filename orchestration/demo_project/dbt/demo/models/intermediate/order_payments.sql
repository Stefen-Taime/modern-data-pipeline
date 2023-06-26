-- models/intermediate/order_payments.sql
{{
    config(
        materialized='view'
    )
}}

SELECT 
    o.*, 
    p.payment_sequential, 
    p.payment_type, 
    p.payment_installments, 
    p.payment_value
FROM {{ ref('olist_orders') }} o
LEFT JOIN {{ ref('olist_order_payments') }} p ON o.order_id = p.order_id
