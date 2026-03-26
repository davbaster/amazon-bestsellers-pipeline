SELECT DISTINCT
    author
FROM {{ ref('stg_bestsellers') }}
WHERE author IS NOT NULL
