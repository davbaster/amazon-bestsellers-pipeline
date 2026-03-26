/* @bruin
name: stg_bestsellers
type: bq.sql
depends:
  - raw_bestsellers

materialization:
  type: table
  strategy: create+replace
  partition_by: year
  cluster_by:
    - genre
    - author
@bruin */

SELECT
    TRIM(Name) AS name,
    TRIM(Author) AS author,
    TRIM(Genre) AS genre,
    Year AS year,
    Reviews AS reviews,
    Price AS price,
    `User Rating` AS user_rating
FROM {{ ref('raw_bestsellers') }}
WHERE Name IS NOT NULL
  AND Author IS NOT NULL
