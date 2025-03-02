import os
import re
import shutil
import yaml
import csv
import subprocess
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.tabularize import tabularize_support

"""
Create results directory
"""

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
config_path = os.path.join(parent_dir, "config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

result_dir = os.path.join(config["working_dir"], config["run_name"])
sbs_result_dir = os.path.join(result_dir, "SBS_runs")
os.makedirs(sbs_result_dir, exist_ok=True)
data_dir = config["data_dir"]
runtimes_path = os.path.join(config["working_dir"], config["run_name"], "runtimes", "SBS.csv")

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
Perform SBS, compute support
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

    subfolder_dir = os.path.join(sbs_result_dir, subfolder)
    os.makedirs(subfolder_dir, exist_ok=True)

    raxml_command = [
        config["raxml_ng_path"],
        "--bootstrap",
        "--model", model_path,
        f"--bs-trees", "1000",
        "--msa", msa_path,
        "--redo"]
    try:

        full_command = ["time"] + raxml_command  # -v makes time output verbose
        result = subprocess.run(full_command, cwd=subfolder_dir, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        time_output = result.stderr

        match = re.search(r"(\d+\.\d+) real\s+(\d+\.\d+) user\s+(\d+\.\d+) sys", time_output)
        if match:
            wallclock_time = float(match.group(1))  # "real"
            user_time = float(match.group(2))  # "user"
            sys_time = float(match.group(3))  # "sys"
            cpu_time = user_time + sys_time  # Total CPU time
            res = {
                "dataset": subfolder,
                "elapsed_time": wallclock_time,
                "cpu_time": cpu_time
            }

        folder_path = os.path.dirname(model_path)
        for file in os.listdir(folder_path):
            if file.endswith(('.log', '.bootstraps', '.rba')):
                source_path = os.path.join(folder_path, file)
                dest_path = os.path.join(subfolder_dir, file)
                shutil.move(source_path, dest_path)
            if file.endswith((".bestTree")):
                source_path = os.path.join(folder_path, file)
                dest_path = os.path.join(subfolder_dir, file)
                shutil.copy(source_path, dest_path)
    except subprocess.CalledProcessError as e:
        failed_command = " ".join(raxml_command)
        print(f"Error occurred while running the command:\n{failed_command}\n")
        print(f"Error details: {e}")
        res = {"dataset": subfolder, "elapsed_time": None, "cpu_time": None}

    write_header = not os.path.exists(runtimes_path)

    with open(runtimes_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["dataset", "elapsed_time", "cpu_time"])
        if write_header:
            writer.writeheader()  # Write the header only if file doesn't exist
        writer.writerow(res)

    bootstrap_files = [f for f in os.listdir(subfolder_dir) if f.endswith('.bootstraps')]

    if bootstrap_files:
        bootstrap_path = os.path.join(subfolder_dir, bootstrap_files[0])  # Take the first match

    tree_file_copied = [f for f in os.listdir(subfolder_dir) if f.endswith('.bestTree')]

    if bootstrap_files:
        tree_file_copied = os.path.join(subfolder_dir, tree_file_copied[0])  # Take the first match

    raxml_command = [config["raxml_ng_path"],
             "--support",
             "--tree", tree_file_copied,
             "--bs-trees", bootstrap_path,
             "--redo"]
    result = subprocess.run(raxml_command, cwd=subfolder_dir)

    support_path = [f for f in os.listdir(subfolder_dir) if f.endswith('.support')]

    if support_path:
        support_path = os.path.join(subfolder_dir, support_path[0])  # Take the first match

    tabular_path = os.path.join(subfolder_dir, "tabular_SBS.csv")
    tabularize_support(support_path, tabular_path, subfolder, "SBS")