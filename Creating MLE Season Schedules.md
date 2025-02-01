# Season Schedule Creator

This script creates a complete season schedule in both the Sprocket and MLEDB schemas, including all fixtures, matches, and series for each skill group and game mode.

## Overview

The Season Schedule Creator takes a CSV file containing match week information and generates all necessary database objects to represent a complete season schedule. It handles:

- Season containers in both schemas
- Match week objects
- Fixtures and matches for each team pairing
- Different skill group combinations based on Premier League participation
- Multiple game modes (Doubles and Standard)
- Bridge table relationships between schemas

## Prerequisites

### Environment Setup

1. Python 3.7+
2. PostgreSQL database access
3. Environment variable:
   - `POSTGRES_CREDS`: Database credentials in format `username:password`

### Dependencies

```bash
pip install sqlalchemy
pip install psycopg2-binary
```

## Input Data Format

The script expects a CSV file with the following columns:

- `Match #`: Integer representing the match week number (1-10)
- `Home`: Home team name
- `Away`: Away team name
- `Has_PL`: Boolean indicating Premier League participation ('TRUE'/'FALSE')
- `Start`: Match week start datetime (format: 'MM/DD/YYYY HH:MM:SS')
- `End`: Match week end datetime (format: 'MM/DD/YYYY HH:MM:SS')

Example:

```csv
Match #,Home,Away,Has_PL,Start,End
1,Foxes,Tyrants,FALSE,2/6/2025 0:00:00,2/9/2025 23:59:00
```

## Database Schema

### Sprocket Schema

- `schedule_group`: Contains season and week containers
- `schedule_fixture`: Represents team matchups
- `match_parent`: Links fixtures to matches
- `match`: Individual matches for each skill group and game mode

### MLEDB Schema

- `season`: Season container
- `match`: Match week container
- `fixture`: Team matchups
- `series`: Individual series for each skill group and game mode

### Bridge Tables

- `mledb_bridge.fixture_to_fixture`: Links fixtures between schemas

## Usage

1. Prepare your input CSV file with the match schedule
2. Set the `POSTGRES_CREDS` environment variable
3. Run the script:

```python
from createSeasonSchedule import SeasonScheduleCreator
from sqlalchemy import create_engine

# Create engine
credstr = os.environ.get('POSTGRES_CREDS')
engine = create_engine(f'postgresql+psycopg2://{credstr}@spr.ocket.cloud:30000/sprocket_main')

# Initialize creator
creator = SeasonScheduleCreator(engine, dry_run=False)

# Create schedule
creator.create_schedule('inputs/s18_schedule.csv')
```

### Dry Run Mode

To preview the SQL statements without executing them:

```python
creator = SeasonScheduleCreator(engine, dry_run=True)
```

## Data Model

### Schedule Structure

- Each season contains 10 match weeks
- Each match week contains multiple team pairings
- Each team pairing generates:
  - One schedule_fixture
  - Multiple match_parents (one per skill group/game mode combination)
  - One match per match_parent
  - One series per skill group/game mode combination

### Skill Groups

- Teams with Premier League (Has_PL=TRUE):
  - Premier (1)
  - Master (2)
  - Champion (3)
  - Academy (4)
- Teams without Premier League:
  - Master (2)
  - Champion (3)
  - Academy (4)
  - Foundation (5)

### Game Modes

- Doubles (13)
- Standard (14)

## Error Handling

The script uses a single transaction for all database operations. If any error occurs:

1. The entire transaction is rolled back
2. The error is raised with details
3. No partial schedules are created

## Maintenance

When using this script for future seasons:

1. Update the season number in the code
2. Ensure team names in the CSV match the franchise names in the database
3. Verify the date formats in the input CSV
4. Consider running in dry_run mode first to verify queries

## Contributing

To modify or extend this script:

1. The main logic is in the `create_all_objects` method
2. Database models are defined in `objects.py`
3. Add new features by extending the `SeasonScheduleCreator` class

## Common Issues

1. **Missing Environment Variable**: Ensure `POSTGRES_CREDS` is set
2. **Team Name Mismatches**: Verify team names match exactly with franchise profiles
3. **Date Format Errors**: Check CSV date formats
4. **Transaction Timeouts**: For large schedules, consider batch processing
