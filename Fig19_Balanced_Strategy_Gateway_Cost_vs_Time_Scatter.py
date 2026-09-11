

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ---------------- SETTINGS ----------------
FILE = os.path.join("outputs", "Results_Balanced.xlsx")   # <-- balanced file
DEST_ORDER = ["Leeds", "Liverpool", "Birmingham", "Norwich", "Kidlington", "Bristol"]

NORTH_EAST_GATEWAYS = [
    "Teesport", "Port of Tyne",
    "Teesside International Airport", "Newcastle International Airport",
]
MIDLANDS_GATEWAYS = ["East Midlands Airport"]
REGION_COLORS = {"North East": "#1f77b4", "Midlands": "#9467bd", "South": "#d62728"}


def region(gateway):
    if gateway in NORTH_EAST_GATEWAYS:
        return "North East"
    if gateway in MIDLANDS_GATEWAYS:
        return "Midlands"
    return "South"


# ---------------- LOAD ----------------
frames = []
for dest in DEST_ORDER:
    d = pd.read_excel(FILE, sheet_name=dest)
    required_columns = {
        "Gateway", "Total_Cost", "Total_Time", "Balanced_Score"
    }
    missing_columns = required_columns.difference(d.columns)
    if missing_columns:
        raise ValueError(
            f"Sheet '{dest}' is missing {sorted(missing_columns)}. "
            "Regenerate Results_Balanced.xlsx with the Min-Max model first."
        )
    d["Gateway"] = d["Gateway"].astype(str).str.strip()
    frames.append(d)
data = pd.concat(frames, ignore_index=True)

g = data.groupby("Gateway").agg(
    avg_cost=("Total_Cost", "mean"),
    avg_time=("Total_Time", "mean"),
    avg_balanced_score=("Balanced_Score", "mean"),
)
g["Region"] = [region(gw) for gw in g.index]

# Use the score calculated by the optimisation model for each destination.
best_gw = g["avg_balanced_score"].idxmin()
best_score = g.loc[best_gw, "avg_balanced_score"]

# ---------------- PLOT ----------------
fig, ax = plt.subplots(figsize=(12, 8))

for gw, row in g.iterrows():
    c = REGION_COLORS[row["Region"]]
    if gw == best_gw:
        ax.scatter(row["avg_cost"], row["avg_time"], marker="*", s=650, color=c,
                   edgecolors="black", linewidth=1.6, zorder=5)
    else:
        ax.scatter(row["avg_cost"], row["avg_time"], s=220, color=c,
                   edgecolors="black", linewidth=1, zorder=3)
    ax.annotate(gw.replace(" International Airport", ""),
                (row["avg_cost"], row["avg_time"]),
                textcoords="offset points", xytext=(10, 6), fontsize=9, fontweight="bold")

ax.set_xlabel("Average Cost (£)  →  cheaper is left")
ax.set_ylabel("Average Time (days)  →  faster is down")
ax.set_title("BALANCED strategy — Gateway Cost vs Time\n"
             f"star = lowest average Balanced Score: "
             f"{best_gw.replace(' International Airport','')} ({best_score:.3f})",
             fontweight="bold")
ax.grid(alpha=0.25)

handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                  markeredgecolor="black", markersize=12, label=r)
           for r, c in REGION_COLORS.items()]
handles.append(Line2D([0], [0], marker="*", color="w", markerfacecolor="gray",
                      markeredgecolor="black", markersize=16,
                      label="Lowest average Balanced Score"))
ax.legend(handles=handles, title="Region", loc="center right")

plt.tight_layout()
out = "outputs/Fig_Balanced_Gateway_Scatter.png"
plt.savefig(out, dpi=130)
print(f"Saved: {out}")
plt.show()

