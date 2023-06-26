-- models/marts/customer_behavior.sql
{{
    config(
        materialized='view'
    )
}}

SELECT 
    c.*,
    g.geolocation_lat,
    g.geolocation_lng,
    od.product_id,
    od.seller_id,
    od.price,
    od.freight_value,
    op.payment_type,
    op.payment_installments,
    op.payment_value,
    orv.review_score
FROM {{ ref('olist_customers') }} c
LEFT JOIN {{ ref('customers_geolocation') }} g ON c.customer_zip_code_prefix = g.customer_zip_code_prefix
LEFT JOIN {{ ref('orders_details') }} od ON c.customer_id = od.customer_id
LEFT JOIN {{ ref('order_payments') }} op ON c.customer_id = op.customer_id
LEFT JOIN {{ ref('order_reviews') }} orv ON c.customer_id = orv.customer_id
