/* @bruin
name: dim_authors
type: bq.sql
depends:
  - stg_bestsellers

materialization:
  type: table
  strategy: create+replace
  cluster_by:
    - author
@bruin */

SELECT DISTINCT
    author
FROM {{ ref('stg_bestsellers') }}
WHERE author IS NOT NULL
