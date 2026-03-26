/* @bruin
name: fct_genre_overall
type: bq.sql
depends:
  - stg_bestsellers

materialization:
  type: table
  strategy: create+replace
  cluster_by:
    - genre
@bruin */

SELECT
    genre,
    COUNT(*) AS bestseller_rows
FROM {{ ref('stg_bestsellers') }}
GROUP BY genre
