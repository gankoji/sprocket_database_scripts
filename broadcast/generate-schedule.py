#!/usr/bin/env python3

import pandas as pd
from ortools.sat.python import cp_model

def solve_broadcast_schedule(league_schedule_csv, broadcast_slots_csv, output_csv):
    """
    Solves the broadcast schedule optimization problem using OR-Tools.

    Args:
        league_schedule_csv (str): Path to the league schedule CSV file.
        broadcast_slots_csv (str): Path to the broadcast slots CSV file.
        output_csv (str): Path to the output CSV file for the broadcast schedule.
    """

    # 1. Load data from CSV files
    league_schedule = pd.read_csv(league_schedule_csv)
    broadcast_slots = pd.read_csv(broadcast_slots_csv)

    # 1.1 Setup the team set
    franchises = set()
    game_modes = set()
    leagues = set()
    for _, m in league_schedule.iterrows():
        franchises.add(m['Home Team'])
        franchises.add(m['Away Team'])
        game_modes.add(m['Game Mode'])
        leagues.add(m['Skill Group'])

    teams = []
    for f in franchises:
        for gm in game_modes:
            for l in leagues:
                teams.append((f,gm,l))

    M = len(league_schedule)  # Number of matches
    N = len(broadcast_slots)  # Number of broadcast slots
    K = len(teams)  # Number of teams

    # Helper function to determine if a team is in a match
    def team_in_match(match_index, team_index):
        match = league_schedule.iloc[match_index]
        #team_name = str(team_index) #Convert to string to match df
        team = teams[team_index]
        home_team = match['Home Team']
        away_team = match['Away Team']
        game_mode = match['Game Mode']
        league = match['Skill Group']
        home = (home_team, game_mode, league)
        away = (away_team, game_mode, league)

        if team == home or team == away: # Compare strings
            return 1
        return 0

    # 2. Create the CP-SAT model
    model = cp_model.CpModel()

    # 3. Define variables
    x = {}
    for i in range(M):
        for j in range(N):
            x[i, j] = model.NewBoolVar(f'x_{i}_{j}')

    # 4. Define constraints

    # Slot Usage Constraint: Each broadcast slot must have exactly one match assigned to it.
    for j in range(N):
        model.Add(sum(x[i, j] for i in range(M)) == 1)

    # Franchise Appearance Constraint & Objective: Minimize the maximum appearances of any franchise.
    appearances = [sum(x[i, j] * team_in_match(i, k) for i in range(M) for j in range(N)) for k in range(K)]
    max_appearances = model.NewIntVar(1, 3, 'max_appearances')  # Upper bound: each franchise could theoretically appear in every slot * 3
    model.AddMaxEquality(max_appearances, appearances)

    # Objective: Minimize the maximum appearances
    model.Minimize(max_appearances)

    # 5. Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # 6. Process the solution
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        output_data = []
        for i in range(M):
            for j in range(N):
                if solver.Value(x[i, j]) == 1:
                    match = league_schedule.iloc[i]
                    slot = broadcast_slots.iloc[j]

                    output_tuple = (
                        match['Match #'],
                        match['Home Team'],
                        match['Away Team'],
                        match['Game Mode'],
                        match['Skill Group'],
                        slot['Day'],
                        slot['Time']
                    )
                    output_data.append(output_tuple)

        # 7. Write the output to a CSV file
        output_df = pd.DataFrame(output_data, columns=[
            'Match #', 'Home Team', 'Away Team', 'Game Mode', 'Skill Group', 'Day', 'Time'
        ])
        output_df.to_csv(output_csv, index=False)

        print(f"Broadcast schedule written to {output_csv}")

    else:
        print("No solution found.")

# Solve the problem
solve_broadcast_schedule('league_schedule.csv', 'broadcast_slots.csv', 'broadcast_schedule.csv')
