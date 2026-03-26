/* @bruin
name: dim_author_nationality
type: bq.sql
depends:
  - dim_authors
  - raw_author_nationality

materialization:
  type: table
  strategy: create+replace
  cluster_by:
    - nationality
    - author
@bruin */

SELECT
    a.author,
    COALESCE(n.nationality, 'Unknown') AS nationality
FROM {{ ref('dim_authors') }} AS a
LEFT JOIN {{ ref('raw_author_nationality') }} AS n
    ON a.author = n.author
