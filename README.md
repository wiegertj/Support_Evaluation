# **Phylogenetic Support Estimation Tools Evaluation**  

This repository provides scripts and configurations for evaluating different phylogenetic support estimation tools.  


---

## **To-Do List**  
- [ ] Support for AA data  
- [ ] Parameterization of different models  
- [ ] Adding RAxML-NG dev support estimates  
- [ ] Adding EBG uncertainty filtering  
- [ ] Support classification scenario evaluation  

---

## **Usage Instructions**  

### **1. Adjust Configuration**  
Modify the `config.yaml` file to match your setup and desired parameters.  

### **2. Load Datasets**  
Each phylogeny should be placed in a separate directory under the specified data directory.  
Ensure each dataset folder (e.g., `dataset_name/`) contains the following files:  

- `.bestTree`  
- `.bestModel`  
- `.fasta`  

### **3. Initialize Results**  
Run the initialization script:  
`python initialize_run.py`  

### **4. Compute SBS Ground Truth**  
Navigate to the computation folder and run:  
`python SBS.py`  

### **5. Compute Supports**  
Run all computation scripts:  
`python UFBoot.py`  
`python EBG.py`  
`python EBG_light.py`  

These scripts compute agreeing bipartitions between the UFBoot contree and the SBS ground truth, as their tree structures may differ.  

### **6. Combine Results**  
Navigate to the evaluation folder and run:  
`python runtimes_analysis.py`  

This script collects all support estimates and runtime results for different tools.  

### **7. Runtime Comparisons**  
First, compute the MSA sizes:  
`python utils/pattern_extraction.py`  

Then, proceed with:  
`python evaluation/runtimes_analysis.py`  

This script generates pairwise speedup comparisons and a performance plot in the `plots/` folder.  

### **8. Accuracy Comparisons**  
Navigate to the evaluation folder and run:  
`python accuracy_analysis.py`  

This will generate boxplots comparing the prediction error, MAE, and RMSE of all tools in the `plots/` folder.  
