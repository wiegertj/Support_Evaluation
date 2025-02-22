import pandas as pd


def get_bipartition(node):
    """
    :param node: ete3 node to get the bipartions for
    :return: tuple or None if node is leaf
    """
    if not node.is_leaf():
        left_children = sorted([leaf.name for leaf in node.children[0].iter_leaves()])
        right_children = sorted([leaf.name for leaf in node.children[1].iter_leaves()])
        bipartition = (left_children, right_children)
        return bipartition
    return None


def filter_agreeing_bipartitions(sbs_tree, other_tree, dataset_name, support_name):
    """
    Method to compare two trees for agreeing bipartitions. Necessary as UFBoot might come up with different tree structures.
    :param sbs_tree: the SBS ground truth tree
    :param other_tree: the tree to check for agreeing branches and their support
    :param dataset_name: name of the dataset
    :return:
    """
    results = []
    branch_id_counter = 0
    for node in sbs_tree.traverse():
        branch_id_counter += 1
        if node.support is not None and not node.is_leaf():
            node.__setattr__("name", branch_id_counter)

    branch_id_counter = 0
    for node in other_tree.traverse():
        branch_id_counter += 1
        if node.support is not None and not node.is_leaf():
            node.__setattr__("name", branch_id_counter)

    for node in other_tree.traverse():
        if not node.is_leaf():
            bipartition_ebg = get_bipartition(node)

            if bipartition_ebg is not None:
                bipartition_found = False
                for node_true in sbs_tree.traverse():
                    if node_true.is_leaf():
                        continue
                    bipartition_true = get_bipartition(node_true)
                    if bipartition_true is not None:
                        first_match = False
                        second_match = False
                        if (bipartition_ebg[0] == bipartition_true[0]) or (bipartition_ebg[0] == bipartition_true[1]):
                            first_match = True
                        if (bipartition_ebg[1] == bipartition_true[0]) or (bipartition_ebg[1] == bipartition_true[1]):
                            second_match = True
                        if second_match and first_match:  # bipartition is in true tree
                            bipartition_found = True

                            results.append((dataset_name, node.name, node.support, 1))
                            break
                if not bipartition_found:
                    results.append((dataset_name, node.name, node.support, 0))
        else:
            results.append((dataset_name, node.name, 100, 1))

    df_res = pd.DataFrame(results, columns=["dataset", "branchId", support_name, "inTrue"])
    df_res = df_res[df_res["inTrue"] == 1]
    return df_res
