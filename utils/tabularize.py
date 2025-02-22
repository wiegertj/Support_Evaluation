import os
import pandas as pd
from ete3 import Tree


def tabularize_support(support_path, target_file_path, dataset_name, support_type):
    """
    Assigns branchIds to support file branches and stores them in a tabular form
    :param support_path: absolute path to support file
    :param target_file_path: absolute file to .csv-file to store the result to
    :param target_file_path: dataset name
    :param support_type: type of support, e.g. RBS, SBS ...
    :return: None
    """

    results = []

    if os.path.exists(support_path):
        with open(support_path, "r") as support_file:
            tree_str = support_file.read()
            tree = Tree(tree_str)

            branch_id_counter = 0

            for node in tree.traverse():
                branch_id_counter += 1
                node.__setattr__("name", branch_id_counter)
                if node.support is not None and not node.is_leaf():
                    results.append((dataset_name, branch_id_counter, node.support))
    else:
        print(f"Not found: {support_path}")

    results_df = pd.DataFrame(results, columns=["dataset", "branchId", support_type])
    results_df.to_csv(target_file_path, index=False)
