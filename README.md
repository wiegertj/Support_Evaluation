# Phylogenetic Support Estimation Tools Evaluation

This repository contains scripts and configurations for evaluating different phylogenetic support estimation tools.

## Usage Instructions

1. **Adjust Configuration:**  
 Edit the `config.yaml` file to reflect your setup and desired parameters. 

2. **Load Datasets:**  
 Place each phylogeny to test in a separate directory named after the dataset (e.g., `dataset_name/`) within the data directory you specified in the config. Ensure that each directory contains the following files:
 - `.bestTree`
 - `.bestModel`
 - `.fasta`

3. **Initialize Results:**  
 Run the initialization script:
 ```bash
 python intializae_results.py 
 ```
4. **Compute SBS Ground Truth:**  
 ```bash
 python computation/SBS.py 
 ```

5. **Compute UFBoot:**  
 ```bash
 python computation/UFBoot.py 
 ```
Note that the script will compute agreeing bipartitions between the UFBoot contree and the SBS ground truth. This is necessary as they might come up with differing tree structures.

6. **Combine Results:**  
 ```bash
 python evaluation/runtimes_analysis.py 
 ```
This will collect all support estimates and runtimes of the different tools.

7. **Runtime Comparisons:**
 ```bash
 python utils/pattern_extraction.py 
 ```
Then proceed with:
 ```bash
 python evaluation/runtimes_analysis.py 
 ```
Will provide pairwise speedups and a comparison plot in the plots folder.


