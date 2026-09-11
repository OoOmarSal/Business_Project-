

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- SETTINGS ----------------
FILE = os.path.join("outputs", "Results_Lowest_Cost.xlsx")
DEST_ORDER = ["Leeds", "Liverpool", "Birmingham", "Norwich", "Kidlington", "Bristol"]
FIX_MODE = "Air_Fast"
METRIC = "Total_Time"

NORTH_EAST_GATEWAYS = ["Teesside International Airport", "Newcastle International Airport"]

# one colour per airport (NE airports in blues, others in warm colours)
AIRPORT_COLORS = {
    "Teesside International Airport": "#1f77b4",
    "Newcastle International Airport": "#17becf",
    "Heathrow Airport": "#d62728",
    "East Midlands Airport": "#9467bd",
}

# ---------------- LOAD ----------------
frames = []
for dest in DEST_ORDER:
    d = pd.read_excel(FILE, sheet_name=dest)
    d["Gateway"] = d["Gateway"].astype(str).str.strip()
    frames.append(d)
data = pd.concat(frames, ignore_index=True)

sub = data[data["International_Mode"] == FIX_MODE]

# only airports that actually appear
airports = [g for g in AIRPORT_COLORS if g in sub["Gateway"].unique()]

# fastest time per airport per destination
vals = {a: [] for a in airports}
for dest in DEST_ORDER:
    for a in airports:
        v = sub[(sub["Destination"] == dest) & (sub["Gateway"] == a)][METRIC]
        vals[a].append(v.min() if len(v) else np.nan)

# ---------------- PLOT ----------------
x = np.arange(len(DEST_ORDER))
n = len(airports)
width = 0.8 / n

fig, ax = plt.subplots(figsize=(14, 7))
for i, a in enumerate(airports):
    label = a.replace(" International Airport", "").replace(" Airport", "")
    tag = " (NE)" if a in NORTH_EAST_GATEWAYS else ""
    bars = ax.bar(x + (i - (n-1)/2)*width, vals[a], width,
                  label=label + tag, color=AIRPORT_COLORS[a])
    ax.bar_label(bars, fmt="%.2f", fontsize=6, padding=2)

ax.set_xticks(x)
ax.set_xticklabels(["Kidlington (Oxford)" if d == "Kidlington" else d
                    for d in DEST_ORDER])
ax.set_ylabel("Total Time (days)")
ax.set_title("Air Fast delivery TIME by airport and destination",
             fontweight="bold")
ax.grid(axis="y", alpha=0.25)
ax.legend(title="Airport")

plt.tight_layout()
out = "outputs/Fig11_AirFast_Time_by_Airport.png"
plt.savefig(out, dpi=130)
print(f"Saved: {out}")
plt.show()

