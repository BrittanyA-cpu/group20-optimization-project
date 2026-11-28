{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "04eefc0d-7ca3-419f-a04c-7681c79fdbb3",
   "metadata": {},
   "outputs": [
    {
     "ename": "ModuleNotFoundError",
     "evalue": "No module named 'food_truck_optimizer'",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mModuleNotFoundError\u001b[0m                       Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[2], line 1\u001b[0m\n\u001b[1;32m----> 1\u001b[0m \u001b[38;5;28;01mfrom\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mfood_truck_optimizer\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;28;01mimport\u001b[39;00m load_trucks, solve, report\n\u001b[0;32m      2\u001b[0m \u001b[38;5;28;01mfrom\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mgurobipy\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;28;01mimport\u001b[39;00m GRB\n\u001b[0;32m      3\u001b[0m \u001b[38;5;28;01mimport\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21;01mcsv\u001b[39;00m\n",
      "\u001b[1;31mModuleNotFoundError\u001b[0m: No module named 'food_truck_optimizer'"
     ]
    }
   ],
   "source": [
    "from food_truck_optimizer import load_trucks, solve, report\n",
    "from gurobipy import GRB\n",
    "import csv\n",
    "import matplotlib.pyplot as plt\n",
    "trucks = load_trucks(\"../data/food_trucks.csv\")\n",
    "q_min = float(input(\"Minimum average qualtiy rating: \"))\n",
    "budget = float(input(\"Total event budget: \"))\n",
    "max_space = float(input(\"Maximum total space available:  \"))\n",
    "m,y, _ = solve(trucks, q_min, budget, max_space)\n",
    "report(m, y, trucks, q_min, budget, max_space)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "faef8d6f-9bc4-457c-bc04-d6a7d829cd64",
   "metadata": {},
   "outputs": [],
   "source": [
    "chosen = [t for i, t in enumerate(trucks) if y[i].X > 0.5]\n",
    "with open(\"../results/optimal_schedule.csv\", \"w\", newline=\"\") as f:\n",
    "    writer = csv.writer(f)\n",
    "    writer.writerow([\"Truck\", \"Category\", \"Revenue($)\", \"Cost($)\", \"Net Profit($)\", \"Space(sq ft)\", \"Quality\"])\n",
    "    for t in chosen:\n",
    "        writer.writerow([t[\"name\"], t[\"category\"], t[\"revenue\"], t[\"cost\"], t[\"revenue\"]- t[\"cost\"], t[\"space\"], t[\"quality\"]])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f3736408-1fd4-4b94-92ff-f258e2598450",
   "metadata": {},
   "outputs": [],
   "source": [
    "names = [t[\"name\"] for t in chosen]\n",
    "profits = [t[\"revenue\"] - t[\"cost\"] for t in chosen]\n",
    "plt.barh(names[::-1], profits[::-1])\n",
    "plt.title  (\"Net profit per Selected Truck\")\n",
    "plt.xlabel(\"Net profit ($)\")\n",
    "plt.savefig(\"../results/selected_truck_profit.png\", bbbox_inches = \"tight\")\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c205c559-ed30-4c0a-8ed3-663daf4173b9",
   "metadata": {},
   "outputs": [],
   "source": [
    "budgets = [int(budget * mult) for mult in [0.5, 0.65, 0.8, 0.9, 1.0, 1.1, 1.25, 1.4 , 1.5]]\n",
    "sensitive_profits = []\n",
    "for b in budgets:\n",
    "    m_temp, _, _ = solve(trucks, q_min,b, max_space)\n",
    "    sensitive_profits.append(m_temp.ObjVal if m_temp.Status == GRB.OPTIMAL else None)\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "904c6f57-53ec-4fee-b6a0-4b6bbe4abc9a",
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.plot(budgets, sensitive_profits, marker=\"o\")\n",
    "plt.title(\"Net Profit vs. Event budget\")\n",
    "plt.xlabel(\"Total Event Budget($)\")\n",
    "plt.ylabel(\"Optimal Net Profit($)\")\n",
    "plt.savefig(\"../results/budget_sensitivity.png\", bbbox_inches = \"tight\")\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.25"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
