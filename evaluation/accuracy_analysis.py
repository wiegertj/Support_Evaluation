import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yaml

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
config_path = os.path.join(parent_dir, "config.yaml")
plot_dir = os.path.join(parent_dir, "plots")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

result_dir = os.path.join(config["working_dir"], config["run_name"])
all_supports_path = os.path.join(result_dir, "all_supports.csv")
df = pd.read_csv(all_supports_path)

pred_columns = ["prediction_median_ebg", "prediction_median_ebg_light", "UFBoot"]
rmse_values = {col: np.sqrt((df[col] - df["SBS"]) ** 2) for col in pred_columns}
mae_values = {col: np.abs(df[col] - df["SBS"]) for col in pred_columns}
pred_error = {col: df["SBS"] - df[col] for col in pred_columns}

plt.figure(figsize=(10, 5))
plt.boxplot(rmse_values.values(), labels=rmse_values.keys())
plt.ylabel("RMSE")
plt.title("RMSE Distribution")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"rmse.png"))
plt.close()

plt.figure(figsize=(10, 5))
plt.boxplot(mae_values.values(), labels=mae_values.keys())
plt.ylabel("MAE")
plt.title("MAE Distribution")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"mae.png"))
plt.close()

plt.figure(figsize=(10, 5))
plt.boxplot(pred_error.values(), labels=mae_values.keys())
plt.ylabel("MAE")
plt.title("Prediction Error Distribution")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, f"prediction_error.png"))
plt.close()