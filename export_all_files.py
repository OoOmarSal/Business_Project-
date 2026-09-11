import pandas as pd
import os


def min_max_normalise(series):
    """Normalise a numeric series to the range 0-1."""
    minimum = series.min()
    value_range = series.max() - minimum

    # If every route has the same value, none should receive a penalty.
    if value_range == 0:
        return pd.Series(0.0, index=series.index)

    return (series - minimum) / value_range


def export_all_results(all_routes, priority):

    folder = "outputs"

    os.makedirs(folder, exist_ok=True)

    # Choose file name based on priority
    file_names = {
        "cost": "Results_Lowest_Cost.xlsx",
        "time": "Results_Fastest_Delivery.xlsx",
        "balanced": "Results_Balanced.xlsx"
    }

    file_path = os.path.join(
        folder,
        file_names[priority]
    )

    with pd.ExcelWriter(file_path) as writer:

        for destination, routes in all_routes.items():

            df = pd.DataFrame(routes)

            # Sort by objective
            if priority == "cost":
                df = df.sort_values(by="Total_Cost")

            elif priority == "time":
                df = df.sort_values(by="Total_Time")

            elif priority == "balanced":
                # The loop processes one destination at a time, so cost and
                # time are normalised within the current destination only.
                df["Cost_Normalised"] = min_max_normalise(df["Total_Cost"])
                df["Time_Normalised"] = min_max_normalise(df["Total_Time"])
                df["Balanced_Score"] = (
                    0.5 * df["Cost_Normalised"]
                    + 0.5 * df["Time_Normalised"]
                )
                df = df.sort_values(by="Balanced_Score")

            df.to_excel(
                writer,
                sheet_name=destination[:31],
                index=False
            )

    return file_path
