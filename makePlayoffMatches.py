import sys
import csv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.objects import sScheduleFixture, sMatchParent, sMatch, mFixture, mSeries, mbFixtures, mMatch

# Load environment variables
load_dotenv()

# Database connection parameters from environment variables
db_host = os.environ.get('POSTGRES_HOST')
db_port = os.environ.get('POSTGRES_PORT')
db_user = os.environ.get('POSTGRES_USERNAME')
db_password = os.environ.get('POSTGRES_PASSWORD')
db_name = os.environ.get('POSTGRES_DATABASE')

# Check if all required variables are set
if not all([db_host, db_port, db_user, db_password, db_name]):
    print("Error: One or more required database environment variables are not set.")
    print("Ensure POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DATABASE are set.")
    sys.exit(1)

# Construct the database URL
DATABASE_URL = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQL query to get franchise names and IDs
queryStr = """
SELECT fp.title, fp."franchiseId" from sprocket.franchise_profile as fp;
"""

# Mapping dictionaries
leaguestr2skillgroupid = {
    'Premier':1,
    'Master':2,
    'Champion':3,
    'Academy':4,
    'Foundation':5,
}

code2League = {
    'FL':'Foundation',
    'AL':'Academy',
    'CL':'Champion',
    'ML':'Master',
    'PL':'Premier'
}

match2scheduleGroup = {
    21:303,
    22:304,
    23:305,
    24:306,
}

matchDetails = {
    21: (176, "2025-05-08 04:00:00.000", "2025-05-12 03:59:00.000"), # match_id, from_date, to_date
    22: (177, "2025-05-15 04:00:00.000", "2025-05-19 03:59:00.000"),
    23: (178, "2025-05-22 04:00:00.000", "2025-05-26 03:59:00.000"),
    24: (179, "2025-05-29 04:00:00.000", "2025-06-09 03:59:00.000"),
}

# Check for command-line argument for CSV file path
if len(sys.argv) < 2:
    print("Usage: python makePlayoffMatches.py <csv_file_path>")
    sys.exit(1)

csv_file_path = sys.argv[1]

# Use the session to interact with the database
with SessionLocal() as session:
    try:
        # Begin a transaction
        with session.begin():
            # First, build a map from franchise name (home name, away name in the input)
            # to franchise ID using direct query (can be replaced by ORM query if needed)
            franchiseNameToId = {}
            # Use session.execute for raw SQL
            res = session.execute(text(queryStr))
            for row in res:
                title = row[0]
                franchiseId = row[1]
                franchiseNameToId[title] = franchiseId

            # Fetch mledb.match objects needed for fixtures before the loop
            mledb_matches = {}
            mledb_match_ids = [details[0] for details in matchDetails.values()]
            # Use ORM query to fetch objects
            stmt = session.query(mMatch).filter(mMatch.id.in_(mledb_match_ids))
            for mledb_match_obj in stmt.all():
                 mledb_matches[mledb_match_obj.id] = mledb_match_obj

            # Open and read the CSV file
            with open(csv_file_path) as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    if i == 0: # Skip header row
                        continue

                    # Extract data from CSV row
                    gameModeStr = row[2]
                    # Map game mode string to ID
                    if gameModeStr == 'Standard':
                        gameModeId = 14
                    else:
                        gameModeId = 13 # Assuming other modes map to 13

                    leagueStr = code2League.get(row[1])
                    if not leagueStr:
                         print(f"Skipping row {i+1}: Unknown league code '{row[1]}'")
                         continue

                    skillGroupId = leaguestr2skillgroupid.get(leagueStr)
                    if skillGroupId is None:
                         print(f"Skipping row {i+1}: Unknown skill group for league '{leagueStr}'")
                         continue

                    try:
                        matchNumber = int(row[0])
                    except ValueError:
                        print(f"Skipping row {i+1}: Invalid match number '{row[0]}'")
                        continue

                    homeName = row[3]
                    awayName = row[4]

                    homeId = franchiseNameToId.get(homeName)
                    if homeId is None:
                         print(f"Skipping row {i+1}: Unknown home franchise '{homeName}'")
                         continue
                    awayId = franchiseNameToId.get(awayName)
                    if awayId is None:
                         print(f"Skipping row {i+1}: Unknown away franchise '{awayName}'")
                         continue

                    scheduleGroupId = match2scheduleGroup.get(matchNumber)
                    if scheduleGroupId is None:
                         print(f"Skipping row {i+1}: Unknown schedule group for match number '{matchNumber}'")
                         continue

                    mledb_match_id_for_fixture = matchDetails.get(matchNumber, [None])[0]
                    mledb_match_instance = mledb_matches.get(mledb_match_id_for_fixture)

                    if not mledb_match_instance:
                         print(f"Skipping row {i+1}: Could not find mledb.match object for match number '{matchNumber}' (ID {mledb_match_id_for_fixture})")
                         continue

                    # --- Create and link ORM objects ---

                    # Sprocket Path
                    # Create sScheduleFixture
                    sprocket_fixture = sScheduleFixture(
                        scheduleGroupId=scheduleGroupId,
                        homeFranchiseId=homeId,
                        awayFranchiseId=awayId
                        # createdAt, updatedAt have defaults
                    )
                    session.add(sprocket_fixture)
                    # After adding, SQLAlchemy might not assign the ID immediately.
                    # Use session.flush() if you need the ID before commit,
                    # but relationships often don't require explicit ID handling.

                    # Create sMatchParent, linking to sScheduleFixture
                    match_parent = sMatchParent(
                        fixture=sprocket_fixture
                        # createdAt, updatedAt have defaults
                    )
                    session.add(match_parent)

                    # Create sMatch, linking to sMatchParent
                    sprocket_match = sMatch(
                        match_parent=match_parent,
                        skillGroupId=skillGroupId,
                        gameModeId=gameModeId,
                        # isDummy has default=False
                        # submissionId is nullable, can be left as None or set explicitly
                        # createdAt, updatedAt have defaults
                    )
                    session.add(sprocket_match)

                    # MLEDB Path
                    # Check for existing mledb.fixture
                    mledb_fixture = session.query(mFixture).filter(
                        mFixture.match_id == mledb_match_instance.id,
                        mFixture.home_name == homeName,
                        mFixture.away_name == awayName
                    ).first()

                    if mledb_fixture is None:
                        # Create new mFixture if not found, linking to mledb.match
                        mledb_fixture = mFixture(
                            mledb_match=mledb_match_instance,
                            home_name=homeName,
                            away_name=awayName
                            # created_by, created_at, updated_by, updated_at have defaults
                            # channel_id has default=''
                        )
                        session.add(mledb_fixture)
                    else:
                        print(f"Warning: Found existing mledb.fixture for {homeName} vs {awayName} (Match ID: {mledb_match_instance.id}). Reusing existing fixture.")
                        # If reusing, ensure it's in the current session if not already
                        session.add(mledb_fixture)


                    # Create mSeries, linking to mledb.fixture
                    mledb_series = mSeries(
                        league=leagueStr.upper(),
                        mode=gameModeStr.upper(),
                        fixture=mledb_fixture,
                        # full_ncp has default=False
                        # updated_by has default='Playoffs'
                        # created_by, created_at, updated_by, updated_at have defaults
                        # submission_timestamp, scheduled_time, scrim_id, stream_event_message_id are nullable
                    )
                    session.add(mledb_series)

                    # Bridge Path
                    # Create mbFixtures, linking Sprocket and MLEDB fixtures
                    bridge_entry = mbFixtures(
                        sprocket_fixture=sprocket_fixture,
                        mle_fixture=mledb_fixture
                        # id is primary key, will be generated
                    )
                    session.add(bridge_entry)

            # If the loop completes without exceptions, the transaction will be committed
            # automatically when exiting the `with session.begin():` block.
            print(f"Successfully processed data from {csv_file_path}.")

    except Exception as e:
        # If any exception occurs, the transaction within `session.begin()`
        # will be automatically rolled back.
        print(f"An error occurred: {e}")
        # The exception is re-raised implicitly by exiting the `with session.begin():` block
        # if an exception occurred inside it. We can catch it here for reporting.
        sys.exit(1)

# The session is closed automatically when exiting the `with SessionLocal() as session:` block.
