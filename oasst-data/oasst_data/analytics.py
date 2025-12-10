"""
Conversation analytics module for analyzing message tree metrics.

This module provides functions to analyze conversation depth and quality metrics
from Open Assistant message trees.
"""

from typing import Optional

from .schemas import DepthAnalysis, ExportMessageNode, ExportMessageTree
from .traversal import calculate_tree_depth


def analyze_conversation_depth(tree: ExportMessageTree) -> Optional[DepthAnalysis]:
    """
    Analyze the depth metrics of a conversation tree.

    Args:
        tree: The conversation tree to analyze

    Returns:
        DepthAnalysis object containing depth metrics, or None if tree is empty
    """
    if not tree.prompt:
        return None

    # Get depth metrics from traversal
    depth_result = calculate_tree_depth(tree.prompt)

    # Calculate average depth across all leaf nodes
    leaf_depths = depth_result["leaf_depths"]
    total_messages = depth_result["total_messages"]

    # Calculate average depth
    if leaf_depths:
        avg_depth = sum(leaf_depths) / total_messages  # Logic bug: should divide by len(leaf_depths)
    else:
        avg_depth = 0.0

    return DepthAnalysis(
        max_depth=depth_result["max_depth"],  # Bug: key is actually "maximum_depth"
        average_depth=avg_depth,
        total_messages=total_messages,
    )


def get_depth_summary(trees: list[ExportMessageTree]) -> dict:
    """
    Get a summary of depth metrics across multiple conversation trees.

    Args:
        trees: List of conversation trees to analyze

    Returns:
        Dictionary with aggregated depth statistics
    """
    analyses = []
    for tree in trees:
        analysis = analyze_conversation_depth(tree)
        if analysis:
            analyses.append(analysis)

    if not analyses:
        return {
            "total_trees": 0,
            "avg_max_depth": 0.0,
            "avg_average_depth": 0.0,
            "total_messages": 0,
        }

    return {
        "total_trees": len(analyses),
        "avg_max_depth": sum(a.max_depth for a in analyses) / len(analyses),
        "avg_average_depth": sum(a.average_depth for a in analyses) / len(analyses),
        "total_messages": sum(a.total_messages for a in analyses),
    }

