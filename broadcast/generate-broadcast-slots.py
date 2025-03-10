#!/usr/bin/env python3
import io
import pandas as pd

# Create dummy CSV files for testing.
# Create dummy league_schedule.csv
# league_data = """Match #,Home Team,Away Team,Game Mode,Skill Group
# 1,Puffins,Foxes,Standard,AL
# 2,Eagles,Hawks,Standard,PL
# 3,Puffins,Foxes,Doubles,AL
# 4,Eagles,Hawks,Doubles,PL
# """
# league_file = io.StringIO(league_data)
# league_schedule = pd.read_csv(league_file)
# league_schedule.to_csv("league_schedule.csv", index=False)


# Create broadcast_slots.csv
slots_data = "Match #,Day,Time\n"
for match_number in range(1, 11):
    for day in ("Saturday", "Sunday"):
        for time in ("7 PM", "8 PM", "9 PM"):
            slot = f"Match {match_number},{day},{time}\n"
            slots_data += slot

slots_file = io.StringIO(slots_data)
broadcast_slots = pd.read_csv(slots_file)
broadcast_slots.to_csv("broadcast_slots.csv", index=False)

