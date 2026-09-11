

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- SETTINGS ----------------
FILE = os.path.join("outputs", "Results_Lowest_Cost.xlsx")
DEST_ORDER = ["Leeds", "Liverpool", "Birmingham", "Norwich", "Kidlington", "Bristol"]
FIX_MODE = "Air_Fast"

NORTH_EAST_GATEWAYS = [
    "Teesport", "Port of Tyne",
    "Teesside International Airport", "Newcastle International Airport",
]

# ---------------- LOAD ----------------
frames = []
for dest in DEST_ORDER:
    d = pd.read_excel(FILE, sheet_name=dest)
    d["Gateway"] = d["Gateway"].astype(str).str.strip()
    frames.append(d)
data = pd.concat(frames, ignore_index=True)
print("Columns:", list(data.columns))

# auto-detect the three cost-component columns by keyword
def find_col(keyword_options):
    for kw in keyword_options:
        for c in data.columns:
            cl = c.lower()
            if kw in cl and "mode" not in cl and "time" not in cl:
                return c
    return None

COL_INTL = find_col(["international_cost", "international"])
COL_DOM  = find_col(["domestic_cost", "domestic"])
COL_OP   = find_col(["operational"])
print("International:", COL_INTL, "| Domestic:", COL_DOM, "| Operational:", COL_OP)
if any(col is None for col in [COL_INTL, COL_DOM, COL_OP]):
    raise ValueError("The three required cost-component columns were not found.")

sub = data[data["International_Mode"] == FIX_MODE]

# First select each airport's cheapest Air_Fast route for EACH destination.
# Then average those six like-for-like destination observations per airport.
best_indices = sub.groupby(["Gateway", "Destination"])["Total_Cost"].idxmin()
best_by_destination = sub.loc[best_indices].copy()

destination_counts = best_by_destination.groupby("Gateway")["Destination"].nunique()
incomplete_gateways = destination_counts[destination_counts != len(DEST_ORDER)]
if not incomplete_gateways.empty:
    raise ValueError(
        "Every airport must contain all six destinations. Invalid counts: "
        + incomplete_gateways.to_dict().__str__()
    )

airport_average = best_by_destination.groupby("Gateway")[[
    COL_INTL, COL_DOM, COL_OP
]].mean()
airport_average["Average_Total_Cost"] = (
    airport_average[COL_INTL]
    + airport_average[COL_DOM]
    + airport_average[COL_OP]
)
airport_average = airport_average.sort_values("Average_Total_Cost")

intl = airport_average[COL_INTL].values
dom = airport_average[COL_DOM].values
op = airport_average[COL_OP].values
labels = airport_average.index.values

# ---------------- PLOT (stacked) ----------------
fig, ax = plt.subplots(figsize=(12, 7))
x = np.arange(len(labels))
ax.bar(x, intl, label="International freight", color="#1f77b4")
ax.bar(x, dom, bottom=intl, label="Domestic inland", color="#ff7f0e")
ax.bar(x, op, bottom=intl + dom, label="Operational fees", color="#2ca02c")

# total on top
for xi, tot in zip(x, intl + dom + op):
    ax.text(xi, tot, f"£{tot:,.0f}", ha="center", va="bottom", fontweight="bold", fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels([g.replace(" International Airport", "") for g in labels], rotation=20, ha="right")
ax.set_ylabel("Average Total Cost (£)")
ax.set_title("Average cost breakdown by airport (Air Fast)\n"
             "mean of each destination's cheapest route across all six destinations",
             fontweight="bold")
ax.legend()
ax.grid(axis="y", alpha=0.25)

plt.tight_layout()
out = "outputs/Fig_CostBreakdown_by_Gateway.png"
plt.savefig(out, dpi=130)
print(f"Saved: {out}")
plt.show()

