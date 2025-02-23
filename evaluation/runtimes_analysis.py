import matplotlib.pyplot as plt
import os
import pandas as pd
import yaml

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
config_path = os.path.join(parent_dir, "config.yaml")
plot_dir = os.path.join(parent_dir, "plots")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

result_dir = os.path.join(config["working_dir"], config["run_name"])
runtimes_path = os.path.join(result_dir, "runtimes", "runtimes_all.csv")
runtimes_ = pd.read_csv(runtimes_path)

no_pats = pd.read_csv(os.path.join(config["data_dir"], "patterns.csv"))
runtimes = runtimes_.merge(no_pats, on=["dataset"], how="inner")
runtimes["msa_size"] = runtimes["no_samples"] * runtimes["no_patterns"]

for time_type in ["elapsed_time", "cpu_time"]:

    plt.figure(figsize=(10, 6))

    for tool, group in runtimes.groupby('type'):
        group = group.sort_values('msa_size').copy()
        group['rolling_median'] = group[time_type].rolling(window=1).median()
        plt.plot(group['msa_size'], group['rolling_median'], label=tool)

    plt.xscale('log')
    plt.yscale('log')

    plt.xlabel('MSA Size')
    plt.ylabel(time_type)
    plt.title(f'Rolling Median of {time_type} vs MSA Size by Tool')
    plt.legend(title='Tool')
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, f"{time_type}.png"))
    plt.close()

# --- Pairwise Average Speedup Computation ---
df_pivot = runtimes.pivot(index='msa_size', columns='type', values='elapsed_time')
tools = df_pivot.columns.tolist()
speedup_df = pd.DataFrame(index=tools, columns=tools)

for t1 in tools:
    for t2 in tools:
        if t1 == t2:
            speedup_df.loc[t1, t2] = 1.0  # Speedup against itself is 1
        else:
            speedup_df.loc[t1, t2] = (df_pivot[t2] / df_pivot[t1]).mean()

print("Pairwise average speedup (ratio of elapsed times):")
print(speedup_df)
speedup_df.to_csv(os.path.join(result_dir, "runtimes", "speedups.csv"), index=False)
