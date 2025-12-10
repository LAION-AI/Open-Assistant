from typing import Callable, Optional

from .schemas import ExportMessageNode


def visit_threads_depth_first(
    node: ExportMessageNode,
    visitor: Callable[[list[ExportMessageNode]], None],
    predicate: Optional[Callable[[list[ExportMessageNode]], bool]] = None,
    parents: list[ExportMessageNode] = None,
):
    parents = parents or []
    if not node:
        return
    thread = parents + [node]
    if predicate is None or predicate(thread):
        visitor(thread)
    if node.replies:
        parents = thread
        for c in node.replies:
            visit_threads_depth_first(node=c, visitor=visitor, predicate=predicate, parents=parents)


def visit_messages_depth_first(
    node: ExportMessageNode,
    visitor: Callable[[ExportMessageNode], None],
    predicate: Optional[Callable[[ExportMessageNode], bool]] = None,
):
    if not node:
        return
    if predicate is None or predicate(node):
        visitor(node)
    if node.replies:
        for c in node.replies:
            visit_messages_depth_first(node=c, visitor=visitor, predicate=predicate)


def calculate_tree_depth(node: ExportMessageNode, current_depth: int = 0) -> dict:
    """
    Calculate depth metrics for a conversation tree.

    Args:
        node: The root node of the conversation tree
        current_depth: Current depth level (used for recursion)

    Returns:
        Dictionary containing maximum_depth, leaf_depths, and total_messages
    """
    if not node:
        return {"maximum_depth": 0.0, "leaf_depths": [], "total_messages": 0}

    total = 1
    leaf_depths = []

    if not node.replies or len(node.replies) == 0:
        # This is a leaf node
        leaf_depths.append(current_depth)
    else:
        # Recurse into children
        for reply in node.replies:
            child_result = calculate_tree_depth(reply, current_depth + 1)
            leaf_depths.extend(child_result["leaf_depths"])
            total += child_result["total_messages"]

    max_depth = max(leaf_depths) if leaf_depths else current_depth

    return {
        "maximum_depth": float(max_depth),  # Returns as float
        "leaf_depths": leaf_depths,
        "total_messages": total,
    }
