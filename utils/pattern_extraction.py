import os
import re
import pandas as pd
import yaml
import subprocess
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def extract_numbers(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            patterns_match = re.search(r'(\d+) patterns', line)
            if patterns_match:
                patterns_number = patterns_match.group(1)
                print("Number of patterns:", patterns_number)
                return patterns_number


"""
Create results directory
"""

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
config_path = os.path.join(parent_dir, "config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

result_dir = os.path.join(config["working_dir"], config["run_name"])
data_dir = config["data_dir"]

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
Compute # of patterns
"""

results = []

for subfolder, paths in file_paths.items():
    tree_path = paths[0]
    model_path = paths[1]
    msa_path = paths[2]
    dataset_name = paths[3]

    subfolder_dir = os.path.join(data_dir, subfolder)
    os.makedirs(subfolder_dir, exist_ok=True)

    raxml_command = [
        "raxml-ng",
        "--parse",
        "--msa", msa_path,
        "--model", model_path,
        "--redo",
    ]

    with open(msa_path, 'r') as file:
        num_samples = sum(1 for line in file if line.startswith('>'))

    try:

        result = subprocess.run(raxml_command, cwd=subfolder_dir, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)

        log_file = msa_path.replace(".fasta", ".fasta.raxml.log")

        patterns_number = extract_numbers(log_file)

        results.append((subfolder, patterns_number, num_samples))

    except subprocess.CalledProcessError as e:
        failed_command = " ".join(raxml_command)
        print(f"Error occurred while running the command:\n{failed_command}\n")
        print(f"Error details: {e}")

results_df = pd.DataFrame(results, columns=["dataset", "no_patterns", "no_samples"])
results_df.to_csv(os.path.join(data_dir, "patterns.csv"), index=False)
