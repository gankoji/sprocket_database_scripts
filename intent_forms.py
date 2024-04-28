from sqlalchemy import create_engine, text
import os
import csv

credstr = os.environ.get('POSTGRES_CREDS') # format is username:password
engine = create_engine(f'postgresql+psycopg2://{credstr}@spr.ocket.cloud:30000/sprocket_main')

basicUpdateQuery = """
    UPDATE mledb.player AS mp
    SET team_name='{}'
    WHERE mp.mleid={}
"""

selectQuery = """
    SELECT * FROM mledb.player AS mp
    WHERE mp.mleid='{}'
"""
dryRun = False
with engine.connect() as conn:
    with open('intent_forms.csv') as csvfile:
        reader = csv.reader(csvfile)
        for i,row in enumerate(reader):
            if i == 0:
                continue

            # This is the format of the CSV from DK
            name = row[0]
            mleid = row[1]
            team = row[2]
            
            # Now let's put it into the DB:
            if dryRun:
                print(f'Updating player {name} ({mleid}) to team {team}')
                queryStr = selectQuery.format(mleid)
                res = conn.execute(text(queryStr))
                print([row[5] for row in res])
            else:
                queryStr = basicUpdateQuery.format(team, mleid)
                print(queryStr)
                conn.execute(text(queryStr))
                conn.commit()