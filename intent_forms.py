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

fullPlayerTable = """
    SELECT * FROM mledb.player AS mp
"""

dryRun = True
players = {}

with engine.connect() as conn:
    # First, read the current playerbase from the DB
    fullTable = conn.execute(text(fullPlayerTable))
    for row in fullTable:
        did, name, mleid = row[14], row[6], row[5]
        # Default to FP, since if they didn't respond that's where they're headed
        players[mleid] = (did, name, 'FP')
        
    # Read the responses from the input CSV file
    with open('inputs/mlebb_retentions.csv') as csvfile:
        reader = csv.reader(csvfile)
        for i,row in enumerate(reader):
            if i == 0:
                continue

            # This is the format of the CSV from MLEBB
            # discord id,name,mleid,retention,team,league
            did, name, mleid, resp, team, _ = row

            # Responses are one of (Retain, FA, Former Player)
            if resp == 'Retention Eligible':
                new_team = team
            elif resp == 'Free Agent':
                new_team = 'FA'
            else:
                new_team = 'FP'
            
            # Update the players dictionary with the new response
            players[mleid] = (did, name, new_team)
            
    for mleid, (did, name, new_team) in players.items():
        # Now let's put it into the DB:
        if dryRun:
            print(f'Updating player {name} ({mleid}) to team {new_team}')
            queryStr = selectQuery.format(mleid)
            res = conn.execute(text(queryStr))
            print([row[5] for row in res])
        else:
            queryStr = basicUpdateQuery.format(new_team, mleid)
            print(queryStr)
            conn.execute(text(queryStr))
            conn.commit()
