SELECT
  m.match_number,
  f.home_name,
  f.away_name,
  s.league,
  s.mode
FROM
  mledb.series s
  INNER JOIN mledb.fixture f ON f.id = s.fixture_id
  INNER JOIN mledb.match m ON f.match_id = m.id
WHERE
  m.season = 18
ORDER BY
  1,
  2,
  3,
  4,
  5;
