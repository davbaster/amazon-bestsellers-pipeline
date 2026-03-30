/* @bruin
name: analytics.stg_bestsellers
type: bq.sql
depends:
  - raw.raw_bestsellers

materialization:
  type: table
  strategy: create+replace
  partition_by: year_partition_date
  cluster_by:
    - genre
    - author
@bruin */

SELECT
    TRIM(Name) AS name,
    TRIM(Author) AS author,
    TRIM(Genre) AS genre,
    Year AS year,
    DATE(Year, 1, 1) AS year_partition_date,
    Reviews AS reviews,
    Price AS price,
    'User Rating' AS user_rating
FROM raw.raw_bestsellers
WHERE Name IS NOT NULL
  AND Author IS NOT NULL
