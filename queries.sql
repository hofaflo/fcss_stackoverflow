-- Badges
SELECT DISTINCT b.user_id, b.date, b.name
FROM `bigquery-public-data.stackoverflow.badges` b
WHERE b.name IN ('Mortarboard', 'Epic', 'Legendary')


-- Comments
SELECT c.creation_date, c.user_id
FROM `bigquery-public-data.stackoverflow.comments` c
RIGHT JOIN (
    SELECT DISTINCT b.user_id
    FROM `bigquery-public-data.stackoverflow.badges` b
    WHERE b.name IN ('Mortarboard', 'Epic', 'Legendary')
) AS b
ON c.user_id=b.user_id


-- Posts
SELECT
p.creation_date, p.post_type_id, p.owner_user_id
FROM `bigquery-public-data.stackoverflow.stackoverflow_posts` p
RIGHT JOIN (
    SELECT DISTINCT b.user_id
    FROM `bigquery-public-data.stackoverflow.badges` b
    WHERE b.name IN ('Mortarboard', 'Epic', 'Legendary')
)
ON owner_user_id=user_id
WHERE p.post_type_id < 3
