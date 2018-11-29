"""
Graphs in the Euclidean plain
"""
import numpy as np
from numba import njit


def euclidean_edge_length(edges, coord):
    """
    Result: array (shape `(m,)`)
    """
    ec = coord[edges]
    dx = ec[:, 0, 0] - ec[:, 1, 0]
    dy = ec[:, 0, 1] - ec[:, 1, 1]
    return np.sqrt(dx**2 + dy**2)


def delaunay_graph(coord: np.ndarray) -> np.ndarray:
    """
    Compute the edges of a Delaunay triangulation of the points
    given by `coord` (shape `nx2`).

    Result: adjacency list (array of shape `mx2`)
    """
    from scipy.spatial import Delaunay

    assert coord.ndim == 2
    assert coord.shape[1] == 2, f"coord have to be 2d array"

    @njit(cache=True)
    def compute_edges(edges, indptr, indices):
        m = len(edges)
        i = 0
        e = 0
        for p in range(2*m):
            while p >= indptr[i+1]:
                i += 1
            j = indices[p]
            if i < j:
                edges[e, 0] = i
                edges[e, 1] = j
                e += 1

    tri = Delaunay(coord)
    indptr, indices = tri.vertex_neighbor_vertices

    m = len(indices)
    assert m % 2 == 0
    m //= 2     # number of edges
    edges = np.empty((m, 2), dtype=int)
    compute_edges(edges, indptr, indices)
    return edges


def plot_edges(edges: np.ndarray, coord: np.ndarray, ax=None, **args):
    from matplotlib.collections import LineCollection
    import matplotlib.pyplot as plt

    xmin, ymin = coord.min(axis=0)
    xmax, ymax = coord.max(axis=0)
    offset = 0.001 * (xmax - xmin)

    lc = LineCollection(coord[edges], **args)
    if ax is None:
        ax = plt.gca()
    ax.add_collection(lc)
    ax.set_xlim([xmin - offset, xmax + offset])
    ax.set_ylim([ymin - offset, ymax + offset])
    ax.set_aspect('equal')


if __name__ == '__main__':
    import argparse
    import pandas as pd
    import matplotlib.pyplot as plt
    from data import moffit_example

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('fname', nargs='?', type=str, default=moffit_example)
    args = p.parse_args()

    fname = args.fname() if callable(args.fname) else args.fname
    df = pd.read_csv(fname)

    coord = df[df.columns[:2]].values
    edges = delaunay_graph(coord)
    edges = delaunay_graph(coord)
    lens = euclidean_edge_length(edges, coord)
    thres = lens.mean() + 1.2*lens.std()
    edges = edges[lens <= thres]

    print(len(edges))
    plot_edges(edges, coord)
    plt.show()
