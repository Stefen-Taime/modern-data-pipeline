-- models/marts/product_performance.sql
{{
    config(
        materialized='view'
    )
}}

SELECT 
    p.*,
    od.order_id,
    od.seller_id,
    od.price,
    od.freight_value,
    op.payment_type,
    op.payment_installments,
    op.payment_value,
    orv.review_score
FROM {{ ref('olist_products') }} p
LEFT JOIN {{ ref('orders_details') }} od ON p.product_id = od.product_id
LEFT JOIN {{ ref('order_payments') }} op ON p.product_id = op.order_id
LEFT JOIN {{ ref('order_reviews') }} orv ON p.product_id = orv.order_id
