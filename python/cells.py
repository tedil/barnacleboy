"""
Visualize some merfish cells.
"""
import numpy as np
import matplotlib.pyplot as plt
from os.path import basename
from typing import List
from reader import load_merfish
from graph import euclidean_edge_length, delaunay_graph, plot_edges
from utils import is_sorted, group_index


def load_cells(fname: str, cell_ids: List, verbose=True):
    cell_ids = [int(i) for i in cell_ids]

    if verbose:
        print("Analyzing", basename(fname))
    df = load_merfish(fname)

    df_cell_ids = np.array(df["cellID"])
    mask = df_cell_ids == cell_ids[0]
    for i in cell_ids[1:]:
        mask |= df_cell_ids == i
    df = df[mask]
    df.sort(order='cellID')
    if True:
        assert is_sorted(df['cellID'])
    if verbose:
        print(f"Selected {len(df):,d} points")
    return df


if __name__ == '__main__':
    import argparse
    from data import _test_file_name

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('cell', nargs='*', default=["2", "3", "4"])
    p.add_argument('-f', '--fname', type=str, default=_test_file_name())
    p.add_argument('-a', '--all-coords', action='store_true')
    p.add_argument('-c', '--convex', action='store_true')
    p.add_argument('-d', '--delaunay', action='store_true')
    p.add_argument('-g', '--graph', action='store_true')
    args = p.parse_args()

    df = load_cells(args.fname, args.cell)
    fname = basename(args.fname)
    cell_idx = group_index(df['cellID'])
    cell_ids = df['cellID'][cell_idx]

    if args.all_coords:
        coord_fields = [k for k, v in df.dtype.fields.items()
                        if v[0].shape == (2,)]
        for field in coord_fields:
            plt.figure(f"{fname}: '{field}' on cells {cell_ids}")
            for cdf in np.split(df, cell_idx[1:]):
                coord = cdf[field]
                plt.plot(coord[:, 0], coord[:, 1], '.')

    if args.convex:
        from scipy.spatial import ConvexHull

        field = 'abs_position'
        for cdf in np.split(df, cell_idx[1:]):
            coord = cdf[field]
            conv = ConvexHull(coord)
            v = coord[conv.vertices]
            plt.fill(v[:, 0], v[:, 1], alpha=0.5)
            plt.plot(coord[:, 0], coord[:, 1], '.')

    if args.delaunay:
        from scipy.spatial import Delaunay

        field = 'abs_position'
        for cdf in np.split(df, cell_idx[1:]):
            coord = cdf[field]
            tri = Delaunay(coord)
            plt.triplot(coord[:, 0], coord[:, 1], tri.simplices, alpha=0.5)
            plt.plot(coord[:, 0], coord[:, 1], '.')

    if args.graph:
        from scipy.spatial import Delaunay

        field = 'abs_position'
        coord = df[field]
        edges = delaunay_graph(coord)
        lens = euclidean_edge_length(edges, coord)
        thres = lens.mean() + 0.5*lens.std()
        edges = edges[lens <= thres]

        print('Threshold distance', thres)
        if False:
            plt.hist(lens, log=True, bins=300)
            plt.show()
        print(f'Selected {len(edges):,d} edges')

        # plot
        for cdf in np.split(df, cell_idx[1:]):
            plt.plot(*cdf[field].T, '.')
        plot_edges(edges, coord, alpha=0.5, color='black')

    plt.show()
