
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch


# ---------------- SETTINGS ----------------
FILE = os.path.join("outputs", "Results_Lowest_Cost.xlsx")
OUTPUT = os.path.join(
    "outputs",
    "Graph21_Cheapest_AirStandard_vs_AirFast_by_Destination_and_Region.png",
)

DEST_ORDER = [
    "Leeds",
    "Liverpool",
    "Birmingham",
    "Norwich",
    "Kidlington",
    "Bristol",
]
MODE_ORDER = ["Air_Standard", "Air_Fast"]
MODE_LABELS = {"Air_Standard": "Air Standard", "Air_Fast": "Air Fast"}

REGION_ORDER = ["North East", "Midlands", "South"]
REGION_COLORS = {
    "North East": "#1f77b4",
    "Midlands": "#9467bd",
    "South": "#d62728",
}

GATEWAY_REGIONS = {
    "Teesside International Airport": "North East",
    "Newcastle International Airport": "North East",
    "East Midlands Airport": "Midlands",
    "Heathrow Airport": "South",
}

AIRPORT_LABELS = {
    "Teesside International Airport": "Teesside",
    "Newcastle International Airport": "Newcastle",
    "East Midlands Airport": "East Midlands",
    "Heathrow Airport": "Heathrow",
}

DOMESTIC_LABELS = {
    "Haulage_Transport_Standard": "Haulage Standard",
    "Haulage_Transport_Fast": "Haulage Fast",
}


def load_routes(file_path):
    """Load all destination sheets and clean route-label columns."""
    excel_file = pd.ExcelFile(file_path)
    frames = []

    for destination in DEST_ORDER:
        if destination not in excel_file.sheet_names:
            raise ValueError(f"Missing destination sheet: {destination}")

        frame = pd.read_excel(file_path, sheet_name=destination)
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)

    required_columns = {
        "Destination",
        "International_Mode",
        "Domestic_Mode",
        "Gateway",
        "Total_Cost",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    for column in ["Destination", "International_Mode", "Domestic_Mode", "Gateway"]:
        data[column] = data[column].astype(str).str.strip()

    data["Total_Cost"] = pd.to_numeric(data["Total_Cost"], errors="coerce")
    data["Region"] = data["Gateway"].map(GATEWAY_REGIONS)
    return data


def select_cheapest_air_routes(data):
    """Return the cheapest route for every mode, destination, and region."""
    air = data[
        data["International_Mode"].isin(MODE_ORDER)
        & data["Destination"].isin(DEST_ORDER)
    ].copy()

    unknown_gateways = sorted(air.loc[air["Region"].isna(), "Gateway"].unique())
    if unknown_gateways:
        raise ValueError(
            "Add these air gateways to GATEWAY_REGIONS: "
            + ", ".join(unknown_gateways)
        )

    air = air.dropna(subset=["Total_Cost"])
    group_columns = ["International_Mode", "Destination", "Region"]
    winner_indices = air.groupby(group_columns)["Total_Cost"].idxmin()
    winners = air.loc[winner_indices].copy()

    expected_groups = {
        (mode, destination, region)
        for mode in MODE_ORDER
        for destination in DEST_ORDER
        for region in REGION_ORDER
    }
    actual_groups = set(map(tuple, winners[group_columns].to_numpy()))
    missing_groups = sorted(expected_groups.difference(actual_groups))
    if missing_groups:
        raise ValueError(f"Missing chart groups: {missing_groups}")

    return winners.set_index(group_columns)


def draw_panel(ax, winners, mode, shared_y_max):
    """Draw one air-service panel using the shared cost scale."""
    x = np.arange(len(DEST_ORDER))
    width = 0.24

    for region_index, region in enumerate(REGION_ORDER):
        positions = x + (region_index - 1) * width
        rows = [winners.loc[(mode, destination, region)] for destination in DEST_ORDER]
        costs = np.array([row["Total_Cost"] for row in rows], dtype=float)

        bars = ax.bar(
            positions,
            costs,
            width=width,
            color=REGION_COLORS[region],
            label=region,
        )
        ax.bar_label(
            bars,
            labels=[f"£{cost:,.0f}" for cost in costs],
            padding=3,
            fontsize=7.5,
            fontweight="bold",
        )

        for position, cost, row in zip(positions, costs, rows):
            airport = AIRPORT_LABELS.get(row["Gateway"], row["Gateway"])
            domestic_mode = DOMESTIC_LABELS.get(
                row["Domestic_Mode"], str(row["Domestic_Mode"]).replace("_", " ")
            )
            ax.text(
                position,
                cost * 0.50,
                f"{airport}\n{domestic_mode}",
                ha="center",
                va="center",
                rotation=90,
                fontsize=7,
                color="white",
                fontweight="bold",
            )

    destination_labels = [
        "Kidlington (Oxford)" if destination == "Kidlington" else destination
        for destination in DEST_ORDER
    ]
    ax.set_xticks(x)
    ax.set_xticklabels(destination_labels, rotation=15, ha="right")
    ax.set_ylim(0, shared_y_max)
    ax.set_title(MODE_LABELS[mode], fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)


def main():
    data = load_routes(FILE)
    winners = select_cheapest_air_routes(data)

    maximum_cost = float(winners["Total_Cost"].max())
    shared_y_max = maximum_cost * 1.15

    fig, axes = plt.subplots(1, 2, figsize=(20, 9), sharey=True)
    for ax, mode in zip(axes, MODE_ORDER):
        draw_panel(ax, winners, mode, shared_y_max)

    axes[0].set_ylabel("Total Cost (£)", fontsize=11)
    fig.supxlabel("Destination", fontsize=11, y=0.03)

    legend_handles = [
        Patch(color=REGION_COLORS[region], label=region) for region in REGION_ORDER
    ]
    fig.legend(
        handles=legend_handles,
        title="Region",
        loc="upper center",
        bbox_to_anchor=(0.5, 0.935),
        ncol=3,
        frameon=True,
    )
    fig.suptitle(
        "Cheapest Air Freight Cost by Destination and Region: "
        "Air Standard vs Air Fast",
        fontsize=15,
        fontweight="bold",
        y=0.985,
    )

    fig.subplots_adjust(top=0.84, bottom=0.15, left=0.06, right=0.98, wspace=0.08)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    plt.savefig(OUTPUT, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUTPUT}")
    plt.show()


if __name__ == "__main__":
    main()
