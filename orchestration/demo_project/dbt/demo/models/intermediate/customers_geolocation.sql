-- models/intermediate/customers_geolocation.sql
{{
    config(
        materialized='view'
    )
}}

SELECT 
    c.*, 
    g.geolocation_lat,
    g.geolocation_lng,
    g.geolocation_city,
    g.geolocation_state
FROM {{ ref('olist_customers') }} c
LEFT JOIN {{ ref('olist_geolocation') }} g ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix
