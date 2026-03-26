SELECT
    genre,
    COUNT(*) AS bestseller_rows
FROM {{ ref('stg_bestsellers') }}
GROUP BY genre
