import os
from collections import defaultdict
from functools import reduce
import pandas as pd
import yaml

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
config_path = os.path.join(parent_dir, "config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

result_dir = os.path.join(config["working_dir"], config["run_name"])
runtimes_dir = os.path.join(result_dir, "runtimes")

"""
    Combine all runtimes
"""

csv_files = [
    f for f in os.listdir(runtimes_dir)
    if f.endswith(".csv") and f not in {"runtimes_all.csv", "speedups.csv"}
]

dataframes = []
for csv_file in csv_files:
    file_path = os.path.join(runtimes_dir, csv_file)
    df = pd.read_csv(file_path)
    df["type"] = csv_file.replace(".csv", "")
    dataframes.append(df)

merged_df = pd.concat(dataframes, ignore_index=True)
output_path = os.path.join(runtimes_dir, "runtimes_all.csv")
merged_df.to_csv(output_path, index=False)

"""
    Combine all support estimates
"""

csv_files = []
for root, _, files in os.walk(result_dir):
    for file in files:
        if file.startswith("tabular_") and file.endswith(".csv"):
            csv_files.append(os.path.join(root, file))

# Group CSV files by their base file name
grouped_files = defaultdict(list)
for csv_file in csv_files:
    base_name = os.path.basename(csv_file)
    grouped_files[base_name].append(csv_file)

# Concatenate CSVs for each group
concatenated_dfs = {}
for base_name, files in grouped_files.items():
    df_list = []
    for file in files:
        try:
            df = pd.read_csv(file)
            df["dataset"] = df["dataset"].astype(str)
            df["branchId"] = df["branchId"].astype(str)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    if df_list:
        concatenated_dfs[base_name] = pd.concat(df_list, ignore_index=True)

merged_df = reduce(
    lambda left, right: pd.merge(left, right, on=['dataset', 'branchId'], how='inner'),
    list(concatenated_dfs.values())
)

output_path = os.path.join(result_dir, "all_supports.csv")
merged_df.to_csv(output_path, index=False)
