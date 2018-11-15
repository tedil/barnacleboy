"""
Reduce the data to one node per cells
"""
import matplotlib.pyplot as plt
import numpy as np
from fisher import _test_file_name
from reader import load_merfish
from cells import is_sorted, group_index
from graph import delaunay_graph, plot_edges, euclidean_edge_length


if __name__ == '__main__':
    fname = _test_file_name()
    df = load_merfish(fname)
    a = np.array(df[['barcode_id', 'cellID', 'abs_position']])
    a.sort(order='cellID')

    if False:
        assert is_sorted(df['cellID'])
    cell_idx = group_index(a['cellID'])
    assert len(cell_idx) < 1e5


    centers = np.array([
        p.mean(axis=0) for p in np.split(a['abs_position'], cell_idx[1:])
    ])

    # plt.plot(*a['abs_position'].T, '.', alpha=0.1)
    edges = delaunay_graph(centers)
    lens = euclidean_edge_length(edges, centers)
    thres = lens.mean() + 1.5*lens.std()
    edges = edges[lens <= thres]
    centers = np.fliplr(centers)

    if True:
        plt.plot(*centers.T, '.', color='orange')
        plot_edges(edges, centers)
        plt.axis('equal')
        plt.show()