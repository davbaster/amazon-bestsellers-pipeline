WITH genre_counts AS (
    SELECT
        year,
        genre,
        COUNT(*) AS bestseller_rows
    FROM {{ ref('stg_bestsellers') }}
    GROUP BY year, genre
),
year_totals AS (
    SELECT
        year,
        SUM(bestseller_rows) AS total_rows
    FROM genre_counts
    GROUP BY year
)

SELECT
    c.year,
    c.genre,
    c.bestseller_rows,
    t.total_rows,
    ROUND(100.0 * c.bestseller_rows / NULLIF(t.total_rows, 0), 2) AS pct_of_year,
    ROW_NUMBER() OVER (
        PARTITION BY c.year
        ORDER BY c.bestseller_rows DESC, c.genre ASC
    ) AS genre_rank_in_year
FROM genre_counts AS c
JOIN year_totals AS t
    ON c.year = t.year
