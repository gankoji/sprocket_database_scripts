#!/usr/bin/env python3

import pandas as pd
from ortools.sat.python import cp_model

def solve_broadcast_schedule(league_schedule_csv, broadcast_slots_csv, output_csv):
    # 1. Load data from CSV files
    league_schedule = pd.read_csv(league_schedule_csv)
    broadcast_slots = pd.read_csv(broadcast_slots_csv)

    # 1.1 Setup the franchise+skill group combinations
    franchise_league_pairs = set()
    for _, m in league_schedule.iterrows():
        franchise_league_pairs.add((m['Home Team'].split()[0], m['Skill Group']))
        franchise_league_pairs.add((m['Away Team'].split()[0], m['Skill Group']))

    M = len(league_schedule)  # Number of matches
    N = len(broadcast_slots)  # Number of broadcast slots
    K = len(franchise_league_pairs)  # Number of franchise+league combinations

    franchise_league_pairs = list(franchise_league_pairs)

    # Helper function to determine if a franchise+league is in a match
    def team_in_match(match_index, pair_index):
        match = league_schedule.iloc[match_index]
        pair = franchise_league_pairs[pair_index]

        home_franchise = match['Home Team'].split()[0]
        away_franchise = match['Away Team'].split()[0]
        match_league = match['Skill Group']

        if (pair[0] == home_franchise or pair[0] == away_franchise) and pair[1] == match_league:
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

    # Match number constraint: Only assign matches to their corresponding broadcast slots
    for i in range(M):
        for j in range(N):
            if league_schedule.iloc[i]['Match #'] != broadcast_slots.iloc[j]['Match #']:
                model.Add(x[i, j] == 0)

    # Slot Usage Constraint: Each broadcast slot must have exactly one match assigned to it
    for j in range(N):
        model.Add(sum(x[i, j] for i in range(M)) == 1)

    # Franchise+League Appearance Constraint
    appearances = [sum(x[i, j] * team_in_match(i, k)
                      for i in range(M)
                      for j in range(N))
                  for k in range(K)]

    max_appearances = model.NewIntVar(0, 3, 'max_appearances')
    model.AddMaxEquality(max_appearances, appearances)

    # 5. Objective: Minimize the maximum appearances
    model.Minimize(max_appearances)

    # 5.5 Validate the model
    print(model.validate())

    # 6. Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # 7. Process the solution
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

        output_df = pd.DataFrame(output_data,


                               columns=['Match #', 'Home Team', 'Away Team',
                                      'Game Mode', 'Skill Group', 'Day', 'Time'])
        output_df.to_csv(output_csv, index=False)
        print(f"Broadcast schedule written to {output_csv}")
    else:
        print(f"No solution found. Solver status: {status}")

# Solve the problem
solve_broadcast_schedule('inputs/league_schedule.csv', 'inputs/broadcast_slots.csv', 'broadcast_schedule.csv')
