import pandas as pd


def min_max_normalise(series):
    """Normalise a numeric series to the range 0-1."""
    minimum = series.min()
    value_range = series.max() - minimum

    # If every route has the same value, none should receive a penalty.
    if value_range == 0:
        return pd.Series(0.0, index=series.index)

    return (series - minimum) / value_range


def rank_routes(routes, priority):

    df = pd.DataFrame(routes)

    if priority == "cost":
        df = df.sort_values("Total_Cost")

    elif priority == "time":
        df = df.sort_values("Total_Time")

    elif priority == "balanced":
        df["Cost_Normalised"] = min_max_normalise(df["Total_Cost"])
        df["Time_Normalised"] = min_max_normalise(df["Total_Time"])
        df["Balanced_Score"] = (
            0.5 * df["Cost_Normalised"]
            + 0.5 * df["Time_Normalised"]
        )

        df = df.sort_values("Balanced_Score")

    return df
