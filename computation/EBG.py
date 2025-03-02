import os
import re
import pandas as pd
import yaml
import csv
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

"""
Create results directory
"""

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
config_path = os.path.join(parent_dir, "config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

result_dir = os.path.join(config["working_dir"], config["run_name"])
ebg_result_dir = os.path.join(result_dir, "EBG_runs")
os.makedirs(ebg_result_dir, exist_ok=True)
data_dir = config["data_dir"]
runtimes_path = os.path.join(config["working_dir"], config["run_name"], "runtimes", "EBG.csv")

"""
Collect all datasets
"""

file_paths = {}

for subfolder in os.listdir(data_dir):
    subfolder_path = os.path.join(data_dir, subfolder)
    if os.path.isdir(subfolder_path):
        newick_path = None
        model_path = None
        fasta_path = None
        for file in os.listdir(subfolder_path):
            if file.endswith(".bestTree"):
                newick_path = os.path.join(subfolder_path, file)
            elif file.endswith(".bestModel"):
                model_path = os.path.join(subfolder_path, file)
            elif file.endswith(".fasta"):
                fasta_path = os.path.join(subfolder_path, file)
        if newick_path is not None and model_path is not None and fasta_path is not None:
            file_paths[subfolder] = (newick_path, model_path, fasta_path, subfolder)

"""
Perform EBG
"""

results = []

with open(runtimes_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["dataset", "elapsed_time", "cpu_time"])
    writer.writeheader()

for subfolder, paths in file_paths.items():
    tree_path = paths[0]
    model_path = paths[1]
    msa_path = paths[2]
    dataset_name = paths[3]

    subfolder_dir = os.path.join(ebg_result_dir, subfolder)
    os.makedirs(subfolder_dir, exist_ok=True)

    ebg_command = [
        config["ebg_path"],
        "-model", model_path,
        f"-tree", tree_path,
        "-o", dataset_name,
        "-msa", msa_path,
        "-raxmlng", "raxml-ng",
        "-redo"]
    try:

        full_command = ["time"] + ebg_command  # -v makes time output verbose
        result = subprocess.run(full_command, cwd=subfolder_dir, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        time_output = result.stderr

        match = re.search(r"(\d+\.\d+) real\s+(\d+\.\d+) user\s+(\d+\.\d+) sys", time_output)
        if match:
            wallclock_time = float(match.group(1))
            user_time = float(match.group(2))
            sys_time = float(match.group(3))
            cpu_time = user_time + sys_time  # Total CPU time
            res = {
                "dataset": subfolder,
                "elapsed_time": wallclock_time,
                "cpu_time": cpu_time
            }
        table_path = os.path.join(subfolder_dir, dataset_name, dataset_name + "_features.csv")
        features_df = pd.read_csv(table_path)
        tabular_df = features_df[["dataset", "branchId", "prediction_lower5", "prediction_lower10", "prediction_median", "prediction_median_lower5_distance", "prediction_median_lower10_distance", "prediction_bs_over_70", "prediction_bs_over_75", "prediction_bs_over_80", "prediction_bs_over_85", "prediction_uncertainty_bs_over_80", "prediction_uncertainty_bs_over_85", "prediction_uncertainty_bs_over_75", "prediction_uncertainty_bs_over_70"]]

        tabular_path = os.path.join(subfolder_dir, "tabular_ebg_support.csv")
        excluded_columns = ["branchId", "dataset"]
        tabular_df = tabular_df.rename(columns=lambda x: f"{x}_ebg" if x not in excluded_columns else x)
        tabular_df.to_csv(tabular_path, index=False)
    except subprocess.CalledProcessError as e:
        failed_command = " ".join(ebg_command)
        print(f"Error occurred while running the command:\n{failed_command}\n")
        print(f"Error details: {e}")
        res = {"dataset": subfolder, "elapsed_time": None, "cpu_time": None}

    write_header = not os.path.exists(runtimes_path)

    with open(runtimes_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["dataset", "elapsed_time", "cpu_time"])
        if write_header:
            writer.writeheader()
        writer.writerow(res)