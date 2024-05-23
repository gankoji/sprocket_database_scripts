# Get all matches with fixtureId and created > 4/28
# Get the corresponding fixtures
# Dedupe fixtures on (sgId, home, away)
# Write matches with new deduped fixturedId
# Follow up sql script deletes hanging fixtures
from sqlalchemy import create_engine, text
from database import objects
from datetime import datetime
from collections import defaultdict
import os
import csv

credstr = os.environ.get('POSTGRES_CREDS') # format is username:password
engine = create_engine(f'postgresql+psycopg2://{credstr}@spr.ocket.cloud:30000/sprocket_main')

mps_query = """
    SELECT *
    FROM match_parent AS mp
    JOIN schedule_fixture AS sf
    ON mp."fixtureId" = sf.id
        WHERE mp."fixtureId" IS NOT NULL
        AND mp."createdAt" > '2024-04-25';
"""

mps_update = """
    UPDATE match_parent
    SET "fixtureId" = {new_sf}
    WHERE id = {mp_id}
"""

raw_mps = defaultdict(list)
raw_fixtures = {}
mps_to_tuples = {}
tuples_to_mps = defaultdict(list)
deduped = {}

used_fixture_ids = set()
def writeNewMp(conn, mpid, new_sf):
    update_str = mps_update.format(new_sf=new_sf, mp_id=mpid)
    res = conn.execute(text(update_str))

with engine.connect() as conn:
    rollback = False
           
        # Sprocket Path
    try:
        result = conn.execute(text(mps_query))
        for row in result:
            mp = row[:7]
            mpid = mp[0]
            fix = row[7:]
            raw_mps[mpid] = mp
            raw_fixtures[fix[0]] = fix
            sgid, home, away = fix[4], fix[5], fix[6]
            mps_to_tuples[mpid] = (sgid, home, away)
            deduped[(sgid, home, away)] = fix[0]
    except Exception as exc:
        print("Oops all berries.")
        print(exc)
    print(raw_mps[53320])
    print(raw_fixtures[9160])
    print("Num fixtures: ", len(raw_fixtures), "Num mps: ", len(raw_mps), "Num deduped: ", len(tuples_to_mps))

    for _, fid in deduped.items():
        used_fixture_ids.add(fid)

    del_str = """
        DELETE FROM schedule_fixture
        WHERE id NOT IN ({})
        AND id > 6237
        AND "createdAt" > '2024-04-29'
    """.format(",".join([str(x) for x in used_fixture_ids]))
    for mpid, mp in raw_mps.items():
        t = mps_to_tuples[mpid]
        new_sf = deduped[t]
        try:
            writeNewMp(conn, mpid, new_sf)
        except Exception as exc:
            print(exc)

    print(len(used_fixture_ids))
    print(del_str)
    res = conn.execute(text(del_str))

    conn.commit()