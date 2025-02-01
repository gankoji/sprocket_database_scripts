from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class sMatch:
    skillGroupId: int
    matchParentId: int
    gameModeId: int
    baseString: str = """
        INSERT INTO sprocket.match
            (id, "isDummy", "submissionId", "skillGroupId", "matchParentId", "gameModeId")
        VALUES (DEFAULT, false, 'match-{}', {}, {}, {})
        RETURNING id;
    """

    def query(self):
        return self.baseString.format(uuid.uuid4(), self.skillGroupId, self.matchParentId, self.gameModeId)

@dataclass
class sMatchParent:
    fixtureId: int
    baseString: str = """
        INSERT INTO sprocket.match_parent
            (id, "fixtureId")
        VALUES (DEFAULT, {})
        RETURNING id;
    """

    def query(self):
        return self.baseString.format(self.fixtureId)
    
@dataclass
class sScheduleFixture:
    scheduleGroupId: int
    homeFranchiseId: int
    awayFranchiseId: int
    baseString: str = """
        INSERT INTO sprocket.schedule_fixture
            (id, "scheduleGroupId", "homeFranchiseId", "awayFranchiseId")
        VALUES (DEFAULT, {}, {}, {})
        RETURNING id;
    """
    
    def query(self):
        return self.baseString.format(self.scheduleGroupId, self.homeFranchiseId, self.awayFranchiseId)

@dataclass
class sScheduleGroup:
    start: str
    end: str
    description: str
    typeId: int
    gameId: int
    parentGroupId: Optional[int]
    baseString: str = """
        INSERT INTO sprocket.schedule_group
            (id, "start", "end", "description", "typeId", "gameId",
            "parentGroupId")
        VALUES (DEFAULT, '{}', '{}', '{}', {}, {}, {})
        RETURNING id;
    """

    seasonString: str = """
        INSERT INTO sprocket.schedule_group
            (id, "start", "end", "description", "typeId", "gameId")
        VALUES (DEFAULT, '{}', '{}', '{}', {}, {})
        RETURNING id;
    """

    def query(self):
        if self.parentGroupId:
            return self.baseString.format(self.start, self.end, self.description, self.typeId, self.gameId, self.parentGroupId)
        else:
            return self.seasonString.format(self.start, self.end, self.description, self.typeId, self.gameId)

@dataclass
class mbFixtures:
    mleFixtureId: int
    sprocketFixtureId: int
    baseString: str = """
        INSERT INTO mledb_bridge.fixture_to_fixture
            ("mleFixtureId", "sprocketFixtureId")
        VALUES ({}, {})
    """

    def query(self):
        return self.baseString.format(self.mleFixtureId, self.sprocketFixtureId)

@dataclass
class mbMatchToScheduleGroup:
    matchId: int
    weekScheduleGroupId: int
    baseString: str = """
        INSERT INTO mledb_bridge.match_to_schedule_group
            ("matchId", "weekScheduleGroupId")
        VALUES ({}, {})
    """

    def query(self):
        return self.baseString.format(self.matchId, self.weekScheduleGroupId)

@dataclass
class mSeries:
    league: str
    mode: str
    fixture_id: int
    full_ncp: bool = False
    baseString: str = """
        INSERT INTO mledb.series
            (id, league, full_ncp, mode, fixture_id, updated_by)
        VALUES (DEFAULT, '{}', {}, '{}', {}, 'Playoffs')
        RETURNING id;
    """
    
    def query(self):
        return self.baseString.format(self.league, self.full_ncp, self.mode, self.fixture_id)
    
@dataclass
class mFixture:
    match_id: int
    home_name: str
    away_name: str
    baseString: str = """
        INSERT INTO mledb.fixture
            (id, match_id, home_name, away_name)
        VALUES (DEFAULT, {}, '{}', '{}')
        RETURNING id;
    """

    def query(self):
        return self.baseString.format(self.match_id, self.home_name, self.away_name)

@dataclass
class mMatch:
    from_date: str
    to_date: str
    season: int
    match_number: int
    is_double_header: bool = False
    map_name: str = "CHAMPIONS_FIELD"
    baseString: str = """
        INSERT INTO mledb.match
            (id, created_by, created_at, "from", "to", is_double_header, season,
            match_number, map)
        VALUES(DEFAULT, '{}', '{}', '{}', '{}', {}, {}, {}, '{}')
        RETURNING id;
    """

    def query(self):
        return self.baseString.format(
            "Nigel",
            timestamp_now(),
            self.from_date,
            self.to_date, 
            self.is_double_header,
            self.season, 
            self.match_number,
            self.map_name,
        )

@dataclass
class mSeason:
    seasonNumber: int
    start: str
    end: str
    rosterLocked: bool = False
    numWeeks: int = 10
    baseString: str = """
        INSERT INTO mledb.season
            (season_number, created_by, created_at, start_date, end_date, roster_locked, week_length)
        VALUES ({}, '{}', '{}', '{}', '{}', {}, {})
        RETURNING season_number;
    """

    def query(self):
        return self.baseString.format(self.seasonNumber, "Nigel", timestamp_now(), self.start, self.end, self.rosterLocked, self.numWeeks)

def timestamp_now():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S") + " -0700"

if __name__ == 'main':
    match = sMatch(2, 1000, 14)
    print(match.query())
    fix = mFixture(1, 'Puffins', 'Sabres')
    print(fix.query())