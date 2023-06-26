-- models/marts/geographical_performance.sql
{{
    config(
        materialized='view'
    )
}}

SELECT 
    g.*,
    od.product_id,
    od.seller_id,
    od.price,
    od.freight_value,
    op.payment_type,
    op.payment_installments,
    op.payment_value,
    orv.review_score
FROM {{ ref('customers_geolocation') }} g
LEFT JOIN {{ ref('orders_details') }} od ON g.customer_id = od.customer_id
LEFT JOIN {{ ref('order_payments') }} op ON g.customer_id = op.customer_id
LEFT JOIN {{ ref('order_reviews') }} orv ON g.customer_id = orv.customer_id
