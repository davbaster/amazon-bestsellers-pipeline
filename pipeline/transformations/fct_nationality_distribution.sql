WITH author_appearances AS (
    SELECT
        author,
        COUNT(*) AS bestseller_appearances
    FROM {{ ref('stg_bestsellers') }}
    GROUP BY author
)

SELECT
    COALESCE(n.nationality, 'Unknown') AS nationality,
    COUNT(DISTINCT a.author) AS distinct_authors,
    SUM(a.bestseller_appearances) AS bestseller_rows
FROM author_appearances AS a
LEFT JOIN {{ ref('dim_author_nationality') }} AS n
    ON a.author = n.author
GROUP BY COALESCE(n.nationality, 'Unknown')
