SELECT
    a.author,
    n.nationality
FROM {{ ref('dim_authors') }} AS a
LEFT JOIN {{ ref('raw_author_nationality') }} AS n
    ON a.author = n.author
