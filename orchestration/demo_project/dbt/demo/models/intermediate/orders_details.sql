-- models/intermediate/orders_details.sql
{{
    config(
        materialized='view'
    )
}}

SELECT 
    o.*, 
    i.product_id, 
    i.seller_id, 
    i.price, 
    i.freight_value,
    p.product_category_name,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM {{ ref('olist_orders') }} o
LEFT JOIN {{ ref('olist_order_items') }} i ON o.order_id = i.order_id
LEFT JOIN {{ ref('olist_products') }} p ON i.product_id = p.product_id
