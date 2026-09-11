import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
from route_generator import generate_all_routes
from User_interface import choose_destination
from User_interface import choose_priority
from route_selector import rank_routes
from excel_exporter import export_results
from All_routes_generator import generate_all_routes
from export_all_files import export_all_results


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

# All relative paths used by the project and graph scripts start from main.py.
os.chdir(BASE_DIR)

file_path = BASE_DIR / "data" / "Book1.xlsx"
excel_file = pd.ExcelFile(file_path)
print(excel_file.sheet_names)

sheet_names = excel_file.sheet_names
print(sheet_names)

datasets = {}

for sheet in sheet_names:
    datasets[sheet] = pd.read_excel(
        file_path,
        sheet_name=sheet
    )
#print(datasets.keys())

def preprocess_dataframe(df):
    """
    Add average cost and average time and average handling .
    """
    if "Gateway" in df.columns:
        df["Gateway"] = df["Gateway"].astype(str).str.strip()
    # Transport costs
    if "Cost_Min" in df.columns and "Cost_Max" in df.columns:
        df["Average_Cost"] = (df["Cost_Min"] + df["Cost_Max"]) / 2

    # Transport time
    if "Period_Min" in df.columns and "Period_Max" in df.columns:
        df["Average_Time"] = (df["Period_Min"] + df["Period_Max"]) / 2

    # Operational Fees
    if "Handling_Min" in df.columns and "Handling_Max" in df.columns:
        df["Average_Handling"] = (df["Handling_Min"] + df["Handling_Max"]) / 2

    if "Security_Min" in df.columns and "Security_Max" in df.columns:
        df["Average_Security"] = (df["Security_Min"] + df["Security_Max"]) / 2



    return df
for name in datasets:
    datasets[name] = preprocess_dataframe(datasets[name])

print(datasets["Air_Standard"])

print(datasets["Air_Standard"].columns)
print(datasets["Air_Standard"].head())
print(datasets["Operational_Fees"].head())
print(datasets["Operational_Fees"].columns.tolist())

# --------
# If you want to select your distribution center

# destination = choose_destination(datasets)
#
# priority = choose_priority()
#
# routes = generate_all_routes(
#     datasets,
#     destination
# )
#
# ranked_routes = rank_routes(routes, priority)
#
# print(ranked_routes)
# file_name = export_results(
#     ranked_routes,
#     destination,
#     priority
# )
#
# print(f"Results exported: {file_name}")
# ---------------
# If you want to generate all the possibilities:
all_routes = generate_all_routes(datasets)

for destination, routes in all_routes.items():

    print("====================")
    print(destination)
    print("====================")

    print(routes[:3])

# Export all three files automatically (cost, time, balanced)
for priority in ["cost", "time", "balanced"]:
    file_name = export_all_results(all_routes, priority)
    print(f"Results exported: {file_name}")


def figure_number(path):
    """Return the number at the beginning of a graph script name (Fig1, Fig2...)."""
    match = re.match(r"Fig(\d+)", path.name, flags=re.IGNORECASE)
    return int(match.group(1)) if match else float("inf")


def png_signatures(directory):
    """Capture PNG file signatures so the image produced by a script can be found."""
    return {
        path: (path.stat().st_mtime_ns, path.stat().st_size)
        for path in directory.glob("*.png")
    }


def run_all_graphs():
    """Run every Fig*.py script and name its output Graph1.png, Graph2.png, etc."""
    graph_dir = BASE_DIR / "graphs"
    graph_files = list(graph_dir.glob("Fig*.py")) if graph_dir.is_dir() else []

    # Also supports projects where the graph scripts are beside main.py.
    if not graph_files:
        graph_dir = BASE_DIR
        graph_files = list(graph_dir.glob("Fig*.py"))

    graph_files.sort(key=figure_number)
    if not graph_files:
        print("No graph scripts found in the graphs folder or beside main.py.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    graph_environment = os.environ.copy()
    graph_environment["MPLBACKEND"] = "Agg"
    failures = []

    print(f"Generating {len(graph_files)} graphs...")

    for graph_file in graph_files:
        number = figure_number(graph_file)
        before = png_signatures(OUTPUT_DIR)

        print(f"Running: {graph_file.name}")
        result = subprocess.run(
            [sys.executable, str(graph_file)],
            cwd=BASE_DIR,
            env=graph_environment,
            check=False,
        )

        if result.returncode != 0:
            failures.append(f"{graph_file.name}: script failed")
            continue

        after = png_signatures(OUTPUT_DIR)
        changed_pngs = [
            path for path, signature in after.items()
            if before.get(path) != signature
        ]

        if len(changed_pngs) != 1:
            failures.append(
                f"{graph_file.name}: expected one PNG output, found {len(changed_pngs)}"
            )
            continue

        target = OUTPUT_DIR / f"Graph{number}.png"
        source = changed_pngs[0]
        if source != target:
            source.replace(target)

        print(f"Saved: {target.relative_to(BASE_DIR)}")

    if failures:
        raise RuntimeError("Graph generation errors:\n- " + "\n- ".join(failures))

    print(f"All graphs were saved in: {OUTPUT_DIR}")


run_all_graphs()
