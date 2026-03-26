SELECT
    author,
    COUNT(*) AS bestseller_appearances,
    COUNT(DISTINCT name) AS distinct_books,
    MIN(year) AS first_year,
    MAX(year) AS last_year
FROM {{ ref('stg_bestsellers') }}
GROUP BY author
