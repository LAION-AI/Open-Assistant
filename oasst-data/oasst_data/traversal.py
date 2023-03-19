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
