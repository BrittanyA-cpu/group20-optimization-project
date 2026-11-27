"""
Model:
    y_i = 1 if truck i is selected, 0 otherwise

    Max   sum_i (R_i - C_i) * y_i
    s.t.  sum_i C_i * y_i  <= B  (budget)
          sum_i S_i * y_i  <= A  (space)
          sum_i (Q_i - Qmin) * y_i  >= 0   (avg quality >= Qmin)
          Lower cateory count <= sum_i y_i per category <= Upper category count  (category count)
          Lower count <= sum_i y_i <= Upper count  (truck count)
          y_i in {0, 1}

"""

import csv
import sys

import gurobipy as gp
from gurobipy import GRB

# Settings

CSV_FILE = "data/food_trucks.csv"
MIN_PER_CATEGORY = 1    # at least this many trucks from every category
MAX_PER_CATEGORY = 2    # at most this many trucks from every category
MIN_TRUCKS = 1          # L: minimum number of trucks
MAX_TRUCKS = 17         # U: maximum number of trucks 

# Load csv into array of trucks
def load_trucks(path):
    trucks = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = {h.strip().lower() for h in reader.fieldnames}
        for line_num, row in enumerate(reader, start=2):
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            trucks.append({
                        "name": row["name"],
                        "category": row["category"],
                        "revenue": float(row["revenue"]),
                        "cost": float(row["cost"]),
                        "space": float(row["space"]),
                        "quality": float(row["quality"]),
            })
    return trucks


def solve(trucks, q_min, budget, max_space):
    n = len(trucks)
    categories = sorted({t["category"] for t in trucks})

    m = gp.Model("food_truck_festival")

    # y_i, 1 if truck i is selected
    y = m.addVars(n, vtype=GRB.BINARY, name="y")

    # Objective: maximize total profit
    # revenue minus cost times y_i for every truck
    m.setObjective(
        gp.quicksum((trucks[i]["revenue"] - trucks[i]["cost"]) * y[i] for i in range(n)),
        GRB.MAXIMIZE,
    )

    # Budget
    # cost times y_i for every truck
    m.addConstr(gp.quicksum(trucks[i]["cost"] * y[i] for i in range(n)) <= budget)

    # Space
    # space times y_i for every truck
    m.addConstr(gp.quicksum(trucks[i]["space"] * y[i] for i in range(n)) <= max_space)

    # Quality: average quality of selected trucks >= q_min
    # if sum of total q's minus q_min is negative, average q is lower than q_min
    m.addConstr(
        gp.quicksum((trucks[i]["quality"] - q_min) * y[i] for i in range(n)) >= 0,
    )

    # Categories
    # iterate through categories, add i to the member set if the truck i is in that category
    for k in categories:
        members = [i for i in range(n) if trucks[i]["category"] == k]
        count = gp.quicksum(y[i] for i in members)
        m.addConstr(count >= min(MIN_PER_CATEGORY, len(members)))
        m.addConstr(count <= MAX_PER_CATEGORY)

    # Truck quantity
    total = gp.quicksum(y[i] for i in range(n))
    m.addConstr(total >= MIN_TRUCKS)
    m.addConstr(total <= MAX_TRUCKS)

    m.optimize()
    return m, y, categories


def report(m, y, trucks, q_min, budget, max_space):
    if m.Status == GRB.INFEASIBLE:
        print("\nNo feasible set of trucks exists for those inputs.")
        return
    if m.Status != GRB.OPTIMAL:
        print("\nNo optimal solution found")
        return

    chosen = [t for i, t in enumerate(trucks) if y[i].X > 0.5]

    total_cost = sum(t["cost"] for t in chosen)
    total_rev = sum(t["revenue"] for t in chosen)
    total_space = sum(t["space"] for t in chosen)
    avg_quality = sum(t["quality"] for t in chosen) / len(chosen)

    print("\nOPTIMAL TRUCK LINEUP\n")
    print(f"{'Truck':<26}{'Category':<14}{'Revenue':>10}{'Cost':>10}{'Space':>8}{'Quality':>9}")
    print("-" * 78)
    for t in chosen:
        print(f"{t['name']:<26}{t['category']:<14}{t['revenue']:>10,.2f}"
              f"{t['cost']:>10,.2f}{t['space']:>8,.1f}{t['quality']:>9.2f}")
    print("-" * 78)
    print(f"Trucks selected: {len(chosen)}")
    print(f"Total revenue  : ${total_rev:,.2f}")
    print(f"Total cost     : ${total_cost:,.2f}")
    print(f"Total profit   : ${m.ObjVal:,.2f}")
    print(f"Space used     : {total_space:,.1f}")
    print(f"Average quality: {avg_quality:.2f}")


def main():
    trucks = load_trucks(CSV_FILE)

    q_min = float(input("Minimum average quality rating: "))
    budget = float(input("Total event budget: "))
    max_space = float(input("Maximum total space available: "))

    m, y, _ = solve(trucks, q_min, budget, max_space)
    report(m, y, trucks, q_min, budget, max_space)

if __name__ == "__main__":
    main()
