from sqlalchemy import create_engine, text
from database import objects
from datetime import datetime
import os
import csv

credstr = os.environ.get('POSTGRES_CREDS') # format is username:password
engine = create_engine(f'postgresql+psycopg2://{credstr}@spr.ocket.cloud:30000/sprocket_main')

leaguestr2skillgroupid = {
    'Premier':1,
    'Master':2,
    'Champion':3,
    'Academy':4,
    'Foundation':5,
}

match2scheduleGroup = {
    1: 220,
    2: 221,
    3: 222,
    4: 223, 
    5: 224, 
    6: 225, 
    7: 226, 
    8: 227, 
    9: 228, 
    10: 229,
}

matchDetails = {
    1:  (115, 'Something'),
    2:  (116, 'Something'),
    3:  (117, 'Something'),
    4:  (118, 'Something'),
    5:  (119, 'Something'),
    6:  (120, 'Something'),
    7:  (121, 'Something'),
    8:  (122, 'Something'),
    9:  (123, 'Something'),
    10: (124, 'Something'),
}

# Ok with these models in hand, this is pretty straightforward
# For each line in DK's match export
# Find the SG and MLEDB Match
# Generate Sprocket objs: schedule_fixture -> match_parent -> match
# Generate MLEDB objs: fixture -> series
# Arrow indicates ID of previous object necessary to create next
with engine.connect() as conn:
    rollback = False
    with open('input_data/season_17_matches.csv') as csvfile:
        reader = csv.reader(csvfile)
        for i,row in enumerate(reader):
            if i == 0:
                continue
            gameModeStr = row[0]
            if gameModeStr == 'Standard':
                gameModeId = 14
            else:
                gameModeId = 13
            leagueStr = row[1]
            skillGroupId = leaguestr2skillgroupid[leagueStr]
            matchNumber = int(row[2])
            homeName = row[3]
            awayName = row[4]
            homeId = int(row[5])
            awayId = int(row[6])
            scheduleGroupId = match2scheduleGroup[matchNumber]
            
            print('HAI')
            # Sprocket Path
            try:
                fixture = objects.sScheduleFixture(
                    scheduleGroupId=scheduleGroupId,
                    homeFranchiseId=homeId,
                    awayFranchiseId=awayId
                )
                result = conn.execute(text(fixture.query()))
                for row in result:
                    fixtureId = row[0]

                matchParent = objects.sMatchParent(
                    fixtureId=fixtureId
                )
                result = conn.execute(text(matchParent.query()))
                for row in result:
                    matchParentId = row[0]
                
                match = objects.sMatch(
                    skillGroupId=skillGroupId,
                    matchParentId=matchParentId,
                    gameModeId=gameModeId
                )
                result = conn.execute(text(match.query()))
                sprocketFixtureId = fixtureId
            except Exception as inst:
                print("Sprocket path failed.")
                print(inst)
                rollback = True

                
            # MLEDB Path
            try:
                # This fixture already exists. Grab it instead
                query = f'SELECT id FROM mledb.fixture WHERE home_name = \'{homeName}\' AND away_name=\'{awayName}\' AND match_id={matchDetails[matchNumber][0]}'
                result = conn.execute(text(query))

                if result.rowcount == 0:
                    fixture = objects.mFixture(
                        match_id=matchDetails[matchNumber][0],
                        home_name=homeName,
                        away_name=awayName
                    )
                    result = conn.execute(text(fixture.query()))

                for row in result:
                    mleFixtureId = row[0]

                series = objects.mSeries(
                    league=leagueStr.upper(),
                    mode=gameModeStr.upper(),
                    fixture_id=mleFixtureId
                )
                result = conn.execute(text(series.query()))
            except Exception as inst:
                print("MLEDB path failed.")
                print(inst)
                rollback = True               
            #Bridge
            try:
                bridge = objects.mbFixtures(
                    mleFixtureId=mleFixtureId,
                    sprocketFixtureId=sprocketFixtureId
                )
                result = conn.execute(text(bridge.query()))
            except Exception as inst:
                print("Could not create bridge table row.")
                print(inst)
                rollback = True               
        if not rollback:
            conn.commit()
