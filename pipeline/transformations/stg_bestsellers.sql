SELECT
    TRIM(name) AS name,
    TRIM(author) AS author,
    TRIM(genre) AS genre,
    year,
    reviews,
    price,
    user_rating
FROM {{ ref('raw_bestsellers') }}
WHERE name IS NOT NULL
  AND author IS NOT NULL
