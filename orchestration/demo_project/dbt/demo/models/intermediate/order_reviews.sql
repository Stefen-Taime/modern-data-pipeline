-- models/intermediate/order_reviews.sql
{{
    config(
        materialized='view'
    )
}}

SELECT 
    o.*, 
    r.review_score, 
    r.review_comment_title, 
    r.review_comment_message, 
    r.review_creation_date, 
    r.review_answer_timestamp
FROM {{ ref('olist_orders') }} o
LEFT JOIN {{ ref('olist_order_reviews') }} r ON o.order_id = r.order_id
