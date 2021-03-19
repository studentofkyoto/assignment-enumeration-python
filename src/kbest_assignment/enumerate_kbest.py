"""kbest matching of bipartite graph"""
import heapq
from typing import Iterator, List, Optional, Tuple

import numpy as np

from ._types import CostMatrix, MatchingIndices
from .lsap import calculate_assignment

INFINITY = float("inf")


def _reduce_matrix(cost_matrix: np.ndarray) -> Optional[Tuple[float, MatchingIndices, CostMatrix]]:
    """
    Reduce matrix so that admissible edges has zero costs

    `cost_matrix` should be a square matrix.

    Return minimum cost of perfect matchings and admissible edge indices.
    When a perfect matching does not exist, return None
    """
    n = cost_matrix.shape[0]
    if n == 0:
        return None
    try:
        _is, _js, _us, _vs = calculate_assignment(cost_matrix)
    except ValueError:
        return None
    reduced_cost_matrix = cost_matrix - _us[:, None] - _vs[None, :]
    minval = reduced_cost_matrix.min()

    return (
        _us.sum() + _vs.sum() + minval * n,
        (_is, _js),
        reduced_cost_matrix - minval
    )


def enumerate_kbest(cost_matrix: CostMatrix, *, ignore_same_value: bool) -> Iterator[MatchingIndices]:
    """
    When `ignore_same_value` is set to True, yield only one matching for each cost.
    Otherwise, return all possible matchings, even if some of them has the same value.

    Iterate through triplets of (matching cost, row indices of a solution, column indices of a solution)
    """
    assert ignore_same_value, "Enumeration of all perfect matching is currently not supported"
    n_row, n_col = cost_matrix.shape
    assert n_row == n_col
    n = n_row
    del n_row, n_col

    # Find first solution
    ret = _reduce_matrix(cost_matrix)
    if ret is None:
        # infeasible cost matrix
        raise RuntimeError
    mincost, a_solution, reduced_cost_matrix = ret

    # keep track of how many branches we searched
    # to be able to avoid overlapping value in the heap
    n_search = 0
    heap: List[Tuple[float, int, MatchingIndices, CostMatrix]] = [(mincost, n_search, a_solution, reduced_cost_matrix)]
    del mincost, a_solution, reduced_cost_matrix

    while heap:
        parent_cost, _, a_solution, parent_matrix = heapq.heappop(heap)

        # admissible edges
        rows, cols = np.nonzero(np.isclose(parent_matrix, 0))
        if ignore_same_value:
            yield a_solution
        else:
            raise NotImplementedError()
            # TODO: implement perfect matching enumeration
            # yield from _enumerate_all_perfect_matchings(rows, cols, a_solution)

        # split the solution space into n partitions
        for i in range(n):
            child_matrix = np.empty_like(parent_matrix)

            # do nothing for [:i]th rows
            child_matrix[:i, :] = parent_matrix[:i, :]

            # remove admissible edges for ith row
            child_matrix[i, :] = parent_matrix[i, :]
            child_matrix[i][cols[rows == i]] = np.inf

            # leave admissible edges only for [i+1:]th rows
            idxs = rows[rows > i], cols[rows > i]
            child_matrix[i + 1:] = np.inf
            child_matrix[idxs] = parent_matrix[idxs]

            # solve and put into heap
            ret = _reduce_matrix(child_matrix)
            if ret is None:
                # infeasible cost matrix
                continue
            child_cost, a_solution, reduced_child_matrix = ret
            n_search += 1
            heapq.heappush(heap, (parent_cost + child_cost, n_search, a_solution, reduced_child_matrix))
