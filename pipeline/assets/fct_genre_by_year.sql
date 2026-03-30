/* @bruin
name: analytics.fct_genre_by_year
type: bq.sql
depends:
  - analytics.stg_bestsellers

materialization:
  type: table
  strategy: create+replace
  partition_by: year_partition_date
  cluster_by:
    - genre
@bruin */

WITH genre_counts AS (
    SELECT
        year,
        genre,
        COUNT(*) AS bestseller_rows
    FROM analytics.stg_bestsellers
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
    DATE(c.year, 1, 1) AS year_partition_date,
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
