

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FILE = os.path.join("outputs", "Results_Lowest_Cost.xlsx")
DEST_ORDER = ["Leeds", "Liverpool", "Birmingham", "Norwich", "Kidlington", "Bristol"]

NORTH_EAST_GATEWAYS = [
    "Teesport", "Port of Tyne",
    "Teesside International Airport", "Newcastle International Airport",
]
MIDLANDS_GATEWAYS = ["East Midlands Airport"]
FIX_MODE = "Air_Fast"
METRIC = "Total_Cost"
UNIT = "£"

DOM_SHORT = {"Haulage_Transport_Standard": "Haulage Standard",
             "Haulage_Transport_Fast": "Haulage Fast"}


def region(gateway):
    if gateway in NORTH_EAST_GATEWAYS:
        return "North East"
    if gateway in MIDLANDS_GATEWAYS:
        return "Midlands"
    return "South"


def short_dom(m):
    return DOM_SHORT.get(str(m), str(m))


frames = []
for dest in DEST_ORDER:
    d = pd.read_excel(FILE, sheet_name=dest)
    d["Gateway"] = d["Gateway"].astype(str).str.strip()
    frames.append(d)
data = pd.concat(frames, ignore_index=True)
data["Region"] = data["Gateway"].apply(region)

sub = data[data["International_Mode"] == FIX_MODE]


def best_row(dest, reg):
    r = sub[(sub["Destination"] == dest) & (sub["Region"] == reg)]
    return r.loc[r[METRIC].idxmin()] if len(r) else None


additional_vs_south, additional_vs_mid = [], []
south_best, mid_best, ne_best = [], [], []
for dest in DEST_ORDER:
    ne = best_row(dest, "North East")
    so = best_row(dest, "South")
    mid = best_row(dest, "Midlands")
    ne_best.append(ne); south_best.append(so); mid_best.append(mid)
    additional_vs_south.append((ne[METRIC] - so[METRIC]) if so is not None else np.nan)
    additional_vs_mid.append((ne[METRIC] - mid[METRIC]) if mid is not None else np.nan)

x = np.arange(len(DEST_ORDER))
width = 0.38
fig, ax = plt.subplots(figsize=(14, 8))
b1 = ax.bar(x - width/2, additional_vs_south, width,
            label="Additional cost vs South", color="#d62728")
b2 = ax.bar(x + width/2, additional_vs_mid, width,
            label="Additional cost vs Midlands", color="#9467bd")


def annotate(bars, best_list):
    for bar, best in zip(bars, best_list):
        if best is None or np.isnan(bar.get_height()):
            continue
        xc = bar.get_x() + bar.get_width() / 2
        ax.text(xc, bar.get_height(), f"{UNIT}{bar.get_height():,.0f}",
                ha="center", va="bottom", fontsize=8, fontweight="bold")
        ax.text(xc, bar.get_height() * 0.5,
                f"{best['Gateway']}\n{short_dom(best['Domestic_Mode'])}\n{UNIT}{best[METRIC]:,.0f}",
                ha="center", va="center", fontsize=6.5, color="white", fontweight="bold", rotation=90)


annotate(b1, south_best)
annotate(b2, mid_best)

ne0 = ne_best[0]

ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(["Kidlington (Oxford)" if d == "Kidlington" else d
                    for d in DEST_ORDER])
ax.set_ylabel("Additional cost of using North East (£)")
ax.set_title("Additional cost of using North East vs each competitor (Air Fast)\n"
             f"NE route used: {ne0['Gateway']} + {short_dom(ne0['Domestic_Mode'])}   |   "
             f"bar text = competitor's cheapest route",
             fontweight="bold", fontsize=11)
ax.grid(axis="y", alpha=0.25); ax.legend(loc="upper right"); ax.margins(y=0.18)

plt.tight_layout()
out = f"outputs/Savings_two_competitors_labeled_{FIX_MODE}.png"
plt.savefig(out, dpi=130)
print(f"Saved: {out}")
plt.show()

