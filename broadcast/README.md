# The MLE Broadcast Schedule Generator

Automatically builds an optimal and equitable broadcast schedule for MLE matches, replacing time-consuming manual scheduling efforts with a precise, constraint-based optimization approach.

## What You'll Need

- **Python 3** installed on your system.
- Required Python packages (install using `pip install -r requirements.txt`):
  - `pandas`
  - `ortools`
- Two inputs provided as CSV files:
  1. **League Schedule CSV** (`league_schedule.csv`)
     - This schedule is published by League Ops and is fixed prior to the season.
     - Columns required:
       - `Match #`: (integer ID) uniquely identifies matches.
       - `Home Team`: franchise + skill group + game mode (e.g., `"Puffins AL 3s"`).
       - `Away Team`: franchise + skill group + game mode (e.g., `"Foxes AL 3s"`).
       - `Game Mode`: either `"3s"` or `"DBLs"`.
       - `Skill Group`: the league division, typically `"AL"`, `"CL"`, `"ML"`, `"FL"`, or `"PL"`.
  
  2. **Broadcast Slots CSV** (`broadcast_slots.csv`)
     - Broadcast slots are determined by production availability.
     - Columns required:
       - `Match #`: indicates the match number that the broadcast slot corresponds to/from the league schedule.
       - `Day`: typically `"Saturday"` or `"Sunday"`.
       - `Time`: scheduled broadcast start time, e.g., `"7 PM"`.

- Recommended directory structure:
```
.
├── inputs
│   ├── league_schedule.csv
│   └── broadcast_slots.csv
├── requirements.txt
└── new-generate-schedule.py
```

## How to Use It

1. Ensure you have the correct input files and place them under the `inputs/` folder as described above.

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scheduling script:
```bash
python new-generate-schedule.py
```

4. Check your output:
- The script generates a `broadcast_schedule.csv` file in the working directory, containing tuples of assigned matches with the streaming slots.

Your output CSV (`broadcast_schedule.csv`) will have the following columns:
- `Match #`, `Home Team`, `Away Team`, `Game Mode`, `Skill Group`, `Day`, `Time`.

Example Row in `broadcast_schedule.csv`:
```
1,Puffins AL 3s,Foxes AL 3s,3s,AL,Saturday,7 PM
```

## How It Works

The broadcast scheduling problem is, at heart, a constrained optimization problem: Select matches from a fixed league schedule and evenly assign them into available broadcast slots. The aim is an optimal and balanced distribution of appearances among all franchises, subject to practical constraints.

**1. Problem Formalization**

The tool models this problem mathematically, utilizing constraint programming.

- **Objective:** Minimize the maximum number of streamed appearances of any franchise/skill group combination across the season. This objective seeks to make coverage as equitable and fair as possible.

- **Constraints:**  
  - Matches scheduled by the League Operations cannot be changed – we can only select certain matches from them to appear on stream.
  - Each broadcast slot must contain exactly one assigned match; no slots may remain empty or contain multiple matches.
  - No franchise (within a single skill group and game mode) may appear more than 3 times on stream throughout the entire season.
  - Matches can be broadcast only at their corresponding designated match number slots.

**2. Mathematical Formulation**

- Let \( x_{ij} \) be a binary variable, equal to 1 if match \( i \) is assigned to broadcast slot \( j \), and equal to 0 otherwise.
- Let \( appearances_k \) be the number of streamed appearances for franchise/skill group combinations \( k \):
  \[
  appearances_k = \sum_{i=1}^{M}\sum_{j=1}^{N} x_{ij} \cdot team\_in\_match(i,k)
  \]
  where \( team\_in\_match(i,k) \) checks whether franchise & skill group combination \( k \) appears in match \( i \).

We optimize by minimizing the largest \( appearances_k \):
\[
\text{Objective: } \min \max(appearances_1, appearances_2, ..., appearances_K)
\]

Subject to:
- **Slot usage constraint**: Each slot exactly once:
  \[
  \sum_{i=1}^{M} x_{ij} = 1 \quad\forall j \in \{1,...,N\}
  \]

- **Match schedule constraint**: \( x_{ij} = 0 \) if the match number of schedule and slot do not match.

These variables, constraints, and objectives are directly encoded into the CP-SAT solver from Google's [OR-Tools](https://developers.google.com/optimization). OR-Tools efficiently solves large-scale constraints optimization problems and guarantees that the solution meets the constraints provided.

**3. Implementation**

The implementation (`new-generate-schedule.py`) performs the following tasks:

- **Reads input CSV data** using pandas.
- Creates optimization model variables and constraints using the OR-Tools CP-SAT model.
- Runs the solver to find an optimal assignment.
- Outputs the optimal schedule to a CSV file (`broadcast_schedule.csv`) in a readable and convenient format for production usage.
