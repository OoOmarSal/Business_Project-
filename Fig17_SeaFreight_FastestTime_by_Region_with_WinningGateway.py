
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- SETTINGS ----------------
FILE = os.path.join("outputs", "Results_Lowest_Cost.xlsx")
DEST_ORDER = ["Leeds", "Liverpool", "Birmingham", "Norwich", "Kidlington", "Bristol"]

NORTH_EAST_GATEWAYS = [
    "Teesport", "Port of Tyne",
    "Teesside International Airport", "Newcastle International Airport",
]
MIDLANDS_GATEWAYS = ["East Midlands Airport"]

REGION_ORDER = ["North East", "Midlands", "South"]
REGION_COLORS = {"North East": "#1f77b4", "Midlands": "#9467bd", "South": "#d62728"}

FIX_MODE = "Sea_Freight"

DOM_SHORT = {"Haulage_Transport_Standard": "Haulage Standard",
             "Haulage_Transport_Fast": "Haulage Fast"}

MODE_LABELS = {"Air_Fast": "Air Fast", "Air_Standard": "Air Standard", "Sea_Freight": "Sea Freight"}


def region(gateway):
    if gateway in NORTH_EAST_GATEWAYS:
        return "North East"
    if gateway in MIDLANDS_GATEWAYS:
        return "Midlands"
    return "South"


def short_gw(g):
    return g.replace(" International Airport", "").replace(" Airport", "")


def short_dom(m):
    return DOM_SHORT.get(str(m), str(m))


# ---------------- LOAD ----------------
frames = []
for dest in DEST_ORDER:
    d = pd.read_excel(FILE, sheet_name=dest)
    d["Gateway"] = d["Gateway"].astype(str).str.strip()
    frames.append(d)
data = pd.concat(frames, ignore_index=True)
data["Region"] = data["Gateway"].apply(region)

sub = data[data["International_Mode"] == FIX_MODE]

# ---------------- PLOT ----------------
x = np.arange(len(DEST_ORDER))
n = len(REGION_ORDER)
width = 0.8 / n

fig, ax = plt.subplots(figsize=(14, 8))

for i, reg in enumerate(REGION_ORDER):
    for j, dest in enumerate(DEST_ORDER):
        dd = sub[(sub["Destination"] == dest) & (sub["Region"] == reg)]
        if dd.empty:
            continue
        best = dd.loc[dd["Total_Time"].idxmin()]     # FASTEST row for this region+dest
        xpos = x[j] + (i - (n - 1) / 2) * width
        ax.bar(xpos, best["Total_Time"], width, color=REGION_COLORS[reg],
               label=reg if j == 0 else "")

        combo = f"{short_gw(best['Gateway'])} | {short_dom(best['Domestic_Mode'])}"
        ax.text(xpos, best["Total_Time"] * 0.5, combo, rotation=90,
                ha="center", va="center", color="white", fontsize=6.5, fontweight="bold")
        ax.text(xpos, best["Total_Time"], f"{best['Total_Time']:.1f}d",
                ha="center", va="bottom", fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(["Kidlington (Oxford)" if d == "Kidlington" else d for d in DEST_ORDER])
ax.set_ylabel("Fastest Time (days)")
ax.set_title(f"Fastest {MODE_LABELS.get(FIX_MODE, FIX_MODE)} TIME by Destination and Region\n"
             f"(winning gateway + domestic mode written on each bar)",
             fontweight="bold")
ax.grid(axis="y", alpha=0.25)
ax.legend(title="Region", loc="upper right")
ax.margins(y=0.12)

plt.tight_layout()
out = f"outputs/Fig_Time_with_combo_{FIX_MODE}.png"
plt.savefig(out, dpi=130)
print(f"Saved: {out}")
plt.show()

