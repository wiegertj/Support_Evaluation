import os
import re
import shutil
import sys
import ete3
import yaml
import csv
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.tabularize import tabularize_support
from utils.agreeing_branch_filter import filter_agreeing_bipartitions

"""
Create results directory
"""

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
config_path = os.path.join(parent_dir, "config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

result_dir = os.path.join(config["working_dir"], config["run_name"])
sbs_result_dir = os.path.join(result_dir, "UFBoot_runs")
os.makedirs(sbs_result_dir, exist_ok=True)
data_dir = config["data_dir"]
runtimes_path = os.path.join(config["working_dir"], config["run_name"], "runtimes", "UFBoot.csv")

"""
Collect all datasets
"""

file_paths = {}

for root, dirs, files in os.walk(data_dir):
    newick_path = None
    model_path = None
    fasta_path = None
    msa_type = None

    for file in files:
        if file.endswith(".bestTree"):
            newick_path = os.path.join(root, file)
        elif file.endswith(".bestModel"):
            model_path = os.path.join(root, file)
        elif file.endswith(".fasta"):
            fasta_path = os.path.join(root, file)

        subfolder = os.path.basename(root)
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
    iqtree_command = [
        config["ufboot_path"],
        f"-s", msa_path,
        f"-m", "GTR+F",
        f"-t", tree_path,
        f"-B", "1000",
        "-redo"
    ]

    try:

        full_command = ["time"] + iqtree_command  # -v makes time output verbose
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
            if file.endswith(('.iqtree', '.treefile', '.nex', '.contree', '.log')):
                source_path = os.path.join(folder_path, file)
                dest_path = os.path.join(subfolder_dir, file)
                shutil.move(source_path, dest_path)
            if file.endswith((".bestTree")):
                source_path = os.path.join(folder_path, file)
                dest_path = os.path.join(subfolder_dir, file)
                shutil.copy(source_path, dest_path)
    except subprocess.CalledProcessError as e:
        failed_command = " ".join(iqtree_command)
        print(f"Error occurred while running the command:\n{failed_command}\n")
        print(f"Error details: {e}")
        res = {"dataset": subfolder, "elapsed_time": None, "cpu_time": None}

    write_header = not os.path.exists(runtimes_path)

    with open(runtimes_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["dataset", "elapsed_time", "cpu_time"])
        if write_header:
            writer.writeheader()  # Write the header only if file doesn't exist
        writer.writerow(res)

    contree = [f for f in os.listdir(subfolder_dir) if f.endswith('.contree')]
    contree_path = os.path.join(subfolder_dir, contree[0])
    contree_tree = ete3.Tree(contree_path, format=0)

    """
    Compute agreement between UFBoot tree with SBS ground truth
    """

    sbs_ground_truth_folder = os.path.join(result_dir, "SBS_runs", dataset_name)
    sbs_tree = [f for f in os.listdir(sbs_ground_truth_folder) if f.endswith('.support')]
    sbs_tree_path = os.path.join(sbs_ground_truth_folder, sbs_tree[0])

    sbs_ground_truth_tree = ete3.Tree(sbs_tree_path, format=0)
    agreement_result = filter_agreeing_bipartitions(sbs_ground_truth_tree, contree_tree, dataset_name, "UFBoot")

    tabular_path = os.path.join(subfolder_dir, "tabular_UFBoot_agreement.csv")
    agreement_result.to_csv(tabular_path, index=False)