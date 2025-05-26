-- Create a sql query for a postgres database. We'll be querying the
-- sprocket.match_parent table for a count of every row it has over the last 6 months, grouped by week
-- of the 'createAt' datetime field, and filtering for only those rows where mp."fixtureId" is NULL.

```sql
SELECT
    DATE_TRUNC('week', "createdAt") AS week,
    COUNT(*)
FROM
    sprocket.match_parent mp
WHERE mp."fixtureId" IS NULL
  AND mp."createdAt" >= NOW() - INTERVAL '6 months'
GROUP BY week
ORDER BY week;
```
