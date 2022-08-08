from treebeard.mp_tree import MP_Node


def print_node(node: MP_Node, prop: str):
    print("-" * node.depth + getattr(node, prop))
    if node.numchild == 0:
        return
    for child in node.get_children():
        print_node(child, prop)
