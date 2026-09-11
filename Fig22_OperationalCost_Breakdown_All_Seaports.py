

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ---------------- SETTINGS ----------------
FILE = os.path.join("data", "Book1.xlsx")
OUTPUT = os.path.join(
    "outputs",
    "Graph22_OperationalCost_Breakdown_All_Seaports.png",
)

MODE_SHEET = "Sea_Freight"
FEES_SHEET = "Operational_Fees"

COMPONENT_COLORS = {
    "Handling": "#1f77b4",
    "Security": "#ff7f0e",
    "Documentation": "#2ca02c",
}

REGIONS = {
    "Port of Tyne": "North East",
    "Teesport": "North East",
    "Port of Felixstowe": "South",
}


def load_operational_costs(file_path):
    """Load, validate and calculate the operational-cost breakdown."""
    mode_data = pd.read_excel(file_path, sheet_name=MODE_SHEET)
    fees = pd.read_excel(file_path, sheet_name=FEES_SHEET)

    required_mode_columns = {"Gateway"}
    required_fee_columns = {
        "Gateway",
        "Handling_Min",
        "Handling_Max",
        "Security_Min",
        "Security_Max",
        "Documentation",
    }

    missing_mode = required_mode_columns.difference(mode_data.columns)
    missing_fees = required_fee_columns.difference(fees.columns)
    if missing_mode:
        raise ValueError(f"Missing columns in {MODE_SHEET}: {sorted(missing_mode)}")
    if missing_fees:
        raise ValueError(f"Missing columns in {FEES_SHEET}: {sorted(missing_fees)}")

    mode_data["Gateway"] = mode_data["Gateway"].astype(str).str.strip()
    fees["Gateway"] = fees["Gateway"].astype(str).str.strip()

    gateways = mode_data["Gateway"].drop_duplicates().tolist()
    comparison = fees[fees["Gateway"].isin(gateways)].copy()

    missing_gateways = sorted(set(gateways).difference(comparison["Gateway"]))
    if missing_gateways:
        raise ValueError(
            "Operational fees are missing for: " + ", ".join(missing_gateways)
        )

    numeric_columns = [
        "Handling_Min",
        "Handling_Max",
        "Security_Min",
        "Security_Max",
        "Documentation",
    ]
    comparison[numeric_columns] = comparison[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    if comparison[numeric_columns].isna().any().any():
        raise ValueError("Operational-fee data contain missing or non-numeric values.")

    comparison["Handling"] = (
        comparison["Handling_Min"] + comparison["Handling_Max"]
    ) / 2
    comparison["Security"] = (
        comparison["Security_Min"] + comparison["Security_Max"]
    ) / 2
    comparison["Operational Cost"] = (
        comparison["Handling"]
        + comparison["Security"]
        + comparison["Documentation"]
    )

    return comparison.sort_values(
        ["Operational Cost", "Gateway"], ascending=[True, True]
    ).reset_index(drop=True)


def plot_operational_costs(comparison):
    """Create a horizontal stacked-bar comparison."""
    y = np.arange(len(comparison))
    handling = comparison["Handling"].to_numpy(dtype=float)
    security = comparison["Security"].to_numpy(dtype=float)
    documentation = comparison["Documentation"].to_numpy(dtype=float)
    totals = comparison["Operational Cost"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(12, 6.5))

    ax.barh(
        y,
        handling,
        color=COMPONENT_COLORS["Handling"],
        label="handling",
    )
    ax.barh(
        y,
        security,
        left=handling,
        color=COMPONENT_COLORS["Security"],
        label="security",
    )
    ax.barh(
        y,
        documentation,
        left=handling + security,
        color=COMPONENT_COLORS["Documentation"],
        label="Documentation",
    )

    labels = [
        f"{gateway}\n({REGIONS.get(gateway, 'Other')})"
        for gateway in comparison["Gateway"]
    ]
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()

    maximum_total = float(totals.max())
    ax.set_xlim(0, maximum_total * 1.23)
    for row, total in zip(y, totals):
        ax.text(
            total + maximum_total * 0.025,
            row,
            f"£{total:,.2f}",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_xlabel("Operational Cost (£)")
    ax.set_title(
        "Operational Cost Breakdown by Seaport\n"
        "handling + security + documentation",
        fontweight="bold",
    )
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=3,
        frameon=True,
    )

    fig.subplots_adjust(left=0.25, right=0.96, top=0.84, bottom=0.22)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    plt.savefig(OUTPUT, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUTPUT}")
    print(
        comparison[
            [
                "Gateway",
                "Handling",
                "Security",
                "Documentation",
                "Operational Cost",
            ]
        ].to_string(index=False)
    )
    plt.show()


def main():
    comparison = load_operational_costs(FILE)
    plot_operational_costs(comparison)


if __name__ == "__main__":
    main()

