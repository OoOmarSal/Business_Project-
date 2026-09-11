

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# ---------------- SETTINGS ----------------
FILE = os.path.join("outputs", "Results_Lowest_Cost.xlsx")
DEST_ORDER = ["Leeds", "Liverpool", "Birmingham", "Norwich", "Kidlington", "Bristol"]

NORTH_EAST_GATEWAYS = [
    "Teesport", "Port of Tyne",
    "Teesside International Airport", "Newcastle International Airport",
]
MIDLANDS_GATEWAYS = ["East Midlands Airport"]
REGION_COLORS = {"North East": "#1f77b4", "Midlands": "#9467bd", "South": "#d62728"}
TIME_TIE_TOLERANCE = 1e-9

DOM_SHORT = {"Haulage_Transport_Standard": "Haulage Standard",
             "Haulage_Transport_Fast": "Haulage Fast"}
MODE_LABELS = {
    "Air_Fast": "Air Fast",
    "Air_Standard": "Air Standard",
    "Sea_Freight": "Sea Freight",
}


def region(gateway):
    if gateway in NORTH_EAST_GATEWAYS:
        return "North East"
    if gateway in MIDLANDS_GATEWAYS:
        return "Midlands"
    return "South"


def short_dom(m):
    return DOM_SHORT.get(str(m), str(m))


def display_mode(mode):
    return MODE_LABELS.get(str(mode), str(mode).replace("_", " "))


def short_gateway(gateway):
    return (str(gateway)
            .replace(" International Airport", "")
            .replace(" Airport", ""))


# ---------------- LOAD ----------------
frames = []
for dest in DEST_ORDER:
    d = pd.read_excel(FILE, sheet_name=dest)
    d["Gateway"] = d["Gateway"].astype(str).str.strip()
    frames.append(d)
data = pd.concat(frames, ignore_index=True)
data["Region"] = data["Gateway"].apply(region)


def winners(metric):
    """Select winners; exact time ties use the lowest-cost route."""
    selected = []
    time_ties = {}

    for dest in DEST_ORDER:
        dd = data[data["Destination"] == dest]
        minimum = dd[metric].min()
        tied = dd[np.isclose(dd[metric], minimum, rtol=0,
                             atol=TIME_TIE_TOLERANCE)]

        if metric == "Total_Time":
            tied = tied.sort_values(["Total_Cost", "Gateway", "Domestic_Mode"])
            selected.append(tied.iloc[0])
            tied_gateways = list(dict.fromkeys(tied["Gateway"]))
            if len(tied_gateways) > 1:
                time_ties[dest] = tied_gateways
        else:
            selected.append(tied.iloc[0])

    return selected, time_ties


cost_best, _ = winners("Total_Cost")
time_best, time_ties = winners("Total_Time")

# ---------------- PLOT ----------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 8))
x = np.arange(len(DEST_ORDER))


def draw(ax, best_list, metric, unit, title, ties=None):
    vals = [b[metric] for b in best_list]
    colors = [REGION_COLORS[b["Region"]] for b in best_list]
    bars = ax.bar(x, vals, color=colors, width=0.6)
    for bar, dest, b in zip(bars, DEST_ORDER, best_list):
        v = b[metric]
        vtxt = f"{unit}{v:,.0f}" if unit == "£" else f"{v:.2f} d"
        ax.text(bar.get_x()+bar.get_width()/2, v, vtxt,
                ha="center", va="bottom", fontsize=9, fontweight="bold")
        combo = (f"{display_mode(b['International_Mode'])}\n{b['Gateway']}\n"
                 f"{short_dom(b['Domestic_Mode'])}")
        ax.text(bar.get_x()+bar.get_width()/2, v*0.5, combo, rotation=90,
                ha="center", va="center", fontsize=7, color="white", fontweight="bold")

        if ties and dest in ties:
            tied_names = " = ".join(short_gateway(g) for g in ties[dest])
            tie_text = (f"Exact time tie: {tied_names}\n"
                        f"{short_gateway(b['Gateway'])} shown "
                        "(lower-cost tie-break)")
            ax.text(bar.get_x()+bar.get_width()/2, v + max(vals) * 0.075,
                    tie_text, ha="center", va="bottom", fontsize=7.5,
                    fontweight="bold", color="#333333")

    ax.set_xticks(x)
    ax.set_xticklabels(["Kidlington (Oxford)" if d == "Kidlington" else d
                        for d in DEST_ORDER], rotation=15)
    ax.set_title(title, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.margins(y=0.30 if ties else 0.15)


draw(ax1, cost_best, "Total_Cost", "£", "CHEAPEST route per destination (any mode)")
ax1.set_ylabel("Total Cost (£)")
draw(ax2, time_best, "Total_Time", "d",
     "FASTEST route per destination (any mode)\n"
     "exact ties use a lower-cost tie-break",
     ties=time_ties)
ax2.set_ylabel("Total Time (days)")

handles = [Patch(color=c, label=r) for r, c in REGION_COLORS.items()]
fig.legend(handles=handles, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 0.99))

fig.suptitle("Best gateway + domestic mode per destination — cheapest (left) vs fastest (right)",
             fontweight="bold", fontsize=13, y=0.94)
plt.tight_layout(rect=[0, 0, 1, 0.92])
out = "outputs/Fig14_BestRoute_AllModes_perDestination_Cheapest_vs_Fastest.png"
plt.savefig(out, dpi=130)
print(f"Saved: {out}")
plt.show()

