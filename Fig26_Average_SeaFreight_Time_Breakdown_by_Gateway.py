

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ---------------- SETTINGS ----------------
RESULT_FILE_CANDIDATES = [
    os.path.join("outputs", "Results_Fastest_Delivery.xlsx"),
    os.path.join("outputs", "Results_Lowest_Cost.xlsx"),
]

OUTPUT = os.path.join(
    "outputs",
    "Graph26_Average_SeaFreight_Time_Breakdown_by_Gateway.png",
)

DEST_ORDER = [
    "Leeds",
    "Liverpool",
    "Birmingham",
    "Norwich",
    "Kidlington",
    "Bristol",
]

INTERNATIONAL_MODE = "Sea_Freight"
GATEWAY_ORDER = ["Port of Tyne", "Teesport", "Port of Felixstowe"]

GATEWAY_REGIONS = {
    "Port of Tyne": "North East",
    "Teesport": "North East",
    "Port of Felixstowe": "South",
}

COMPONENT_COLORS = {
    "International transit": "#4C78A8",
    "Gateway processing": "#59A14F",
    "Domestic haulage": "#F28E2B",
}


def resolve_results_file():
    """Use the time-results file first, with the all-routes cost file as fallback."""
    for file_path in RESULT_FILE_CANDIDATES:
        if os.path.exists(file_path):
            return file_path
    raise FileNotFoundError(
        "No results workbook was found. Run main.py first to create the files "
        "inside the outputs folder."
    )


def load_routes(file_path):
    """Load all six destination sheets and validate the time columns."""
    excel_file = pd.ExcelFile(file_path)
    missing_sheets = [d for d in DEST_ORDER if d not in excel_file.sheet_names]
    if missing_sheets:
        raise ValueError(f"Missing destination sheets: {missing_sheets}")

    frames = [pd.read_excel(file_path, sheet_name=d) for d in DEST_ORDER]
    data = pd.concat(frames, ignore_index=True)

    required_columns = {
        "International_Mode",
        "Domestic_Mode",
        "Gateway",
        "Destination",
        "International_Time",
        "Processing_Time",
        "Domestic_Time",
        "Total_Time",
        "Total_Cost",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    text_columns = [
        "International_Mode",
        "Domestic_Mode",
        "Gateway",
        "Destination",
    ]
    for column in text_columns:
        data[column] = data[column].astype(str).str.strip()

    numeric_columns = [
        "International_Time",
        "Processing_Time",
        "Domestic_Time",
        "Total_Time",
        "Total_Cost",
    ]
    data[numeric_columns] = data[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    if data[numeric_columns].isna().any().any():
        raise ValueError("The required time or cost columns contain invalid values.")

    return data


def summarise_mode(data):
    """Select the fastest route per destination, then average by gateway."""
    routes = data[
        (data["International_Mode"] == INTERNATIONAL_MODE)
        & data["Gateway"].isin(GATEWAY_ORDER)
        & data["Destination"].isin(DEST_ORDER)
    ].copy()

    missing_gateways = sorted(set(GATEWAY_ORDER).difference(routes["Gateway"]))
    if missing_gateways:
        raise ValueError(f"Missing Sea Freight gateways: {missing_gateways}")

    # Lower cost is used only when two routes have exactly the same Total_Time.
    routes = routes.sort_values(
        ["Gateway", "Destination", "Total_Time", "Total_Cost", "Domestic_Mode"]
    )
    fastest = routes.drop_duplicates(["Gateway", "Destination"], keep="first")

    destination_counts = fastest.groupby("Gateway")["Destination"].nunique()
    invalid_counts = destination_counts[destination_counts != len(DEST_ORDER)]
    if not invalid_counts.empty:
        raise ValueError(
            "Every gateway must contain all six destinations. Invalid counts: "
            + str(invalid_counts.to_dict())
        )

    summary = fastest.groupby("Gateway", as_index=False).agg(
        International_Transit=("International_Time", "mean"),
        Gateway_Processing=("Processing_Time", "mean"),
        Domestic_Haulage=("Domestic_Time", "mean"),
        Average_Total_Time=("Total_Time", "mean"),
    )
    summary["Reconstructed_Total"] = (
        summary["International_Transit"]
        + summary["Gateway_Processing"]
        + summary["Domestic_Haulage"]
    )

    difference = (
        summary["Average_Total_Time"] - summary["Reconstructed_Total"]
    ).abs()
    if (difference > 1e-8).any():
        raise ValueError(
            "Time components do not reconcile with Average Total Time: "
            + str(dict(zip(summary["Gateway"], difference)))
        )

    return (
        summary.set_index("Gateway")
        .loc[GATEWAY_ORDER]
        .reset_index()
    )


def plot_summary(summary):
    """Create a horizontal stacked time-breakdown chart."""
    y = np.arange(len(summary))
    international = summary["International_Transit"].to_numpy(dtype=float)
    processing = summary["Gateway_Processing"].to_numpy(dtype=float)
    domestic = summary["Domestic_Haulage"].to_numpy(dtype=float)
    totals = summary["Average_Total_Time"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(15, 7))

    ax.barh(
        y,
        international,
        color=COMPONENT_COLORS["International transit"],
        label="International transit",
        height=0.62,
    )
    ax.barh(
        y,
        processing,
        left=international,
        color=COMPONENT_COLORS["Gateway processing"],
        label="Gateway processing",
        height=0.62,
    )
    ax.barh(
        y,
        domestic,
        left=international + processing,
        color=COMPONENT_COLORS["Domestic haulage"],
        label="Domestic haulage",
        height=0.62,
    )

    labels = [
        f"{gateway}\n({GATEWAY_REGIONS[gateway]})"
        for gateway in summary["Gateway"]
    ]
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()

    scale_base = float(totals.max())
    ax.set_xlim(0, scale_base * 1.66)

    for row, intl, proc, haulage, total in zip(
        y, international, processing, domestic, totals
    ):
        text_x = total + scale_base * 0.025
        ax.text(
            text_x,
            row - 0.08,
            f"Total: {total:.2f} d",
            ha="left",
            va="center",
            fontsize=10,
            fontweight="bold",
        )
        ax.text(
            text_x,
            row + 0.13,
            f"International {intl:.2f} | Processing {proc:.2f} | Haulage {haulage:.2f}",
            ha="left",
            va="center",
            fontsize=8.5,
            color="#444444",
        )

    ax.set_xlabel("Average Time (days)")
    ax.set_title(
        "Average Sea Freight Time Breakdown by Gateway\n"
        "International transit + gateway processing + domestic haulage",
        fontweight="bold",
    )
    ax.grid(axis="x", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=3,
        frameon=True,
    )
    fig.text(
        0.5,
        0.035,
        "Fastest haulage selected per gateway–destination; mean across all six destinations. "
        "Lower cost is the tie-break when times are equal.",
        ha="center",
        fontsize=9,
        color="#555555",
    )

    fig.subplots_adjust(left=0.22, right=0.98, top=0.82, bottom=0.23)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    plt.savefig(OUTPUT, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUTPUT}")
    print(
        summary[
            [
                "Gateway",
                "International_Transit",
                "Gateway_Processing",
                "Domestic_Haulage",
                "Average_Total_Time",
            ]
        ].to_string(index=False)
    )
    plt.show()


def main():
    results_file = resolve_results_file()
    data = load_routes(results_file)
    summary = summarise_mode(data)
    plot_summary(summary)


if __name__ == "__main__":
    main()

