select
	s.league,
	s.mode,
	f.home_name,
	f.away_name,
	s.scheduled_time,
	s.fixture_id as "Fixture ID",
	s.id as "Series ID"
from
	mledb.series s
inner join mledb.fixture f on f.id = s.fixture_id
inner join mledb."match" m on f.match_id = m.id
where m.season = 18
and m.match_number = 4
