#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Compute (global) graphlet counts for a thresholded distance map.
"""

import shlex
import tempfile
import subprocess
from pathlib import Path

import torch
import numpy as np
import networkx as nx

from .toolbox import Composer, Timer, AdjacencyMatrixMaker, CoordLoader

BIN = Path(__file__).resolve().absolute().parent / "bin"
assert BIN.exists(), "Script not located at same level as ORCA bin/ directory"

def count_graphlets(gdv):
    """Count graphlets in the whole network."""
    g = {}
    g[0] = {'idx': [0], 'nodes': 2}

    g[1] = {'idx': [1, 2], 'nodes': 3}
    g[2] = {'idx': [3], 'nodes': 3}

    g[3] = {'idx': [4, 5], 'nodes': 4}
    g[4] = {'idx': [6, 7], 'nodes': 4}
    g[5] = {'idx': [8], 'nodes': 4}
    g[6] = {'idx': [9, 10, 11], 'nodes': 4}
    g[7] = {'idx': [12, 13], 'nodes': 4}
    g[8] = {'idx': [14], 'nodes': 4}

    g[9] = {'idx': [15, 16, 17], 'nodes': 5}
    g[10] = {'idx': [18, 19, 20, 21], 'nodes': 5}
    g[11] = {'idx': [22, 23], 'nodes': 5}
    g[12] = {'idx': [24, 25, 26], 'nodes': 5}
    g[13] = {'idx': [27, 28, 29, 30], 'nodes': 5}
    g[14] = {'idx': [31, 32, 33], 'nodes': 5}
    g[15] = {'idx': [34], 'nodes': 5}
    g[16] = {'idx': [35, 36, 37, 38], 'nodes': 5}
    g[17] = {'idx': [39, 40, 41, 42], 'nodes': 5}
    g[18] = {'idx': [43, 44], 'nodes': 5}
    g[19] = {'idx': [45, 46, 47, 48], 'nodes': 5}
    g[20] = {'idx': [49, 50], 'nodes': 5}
    g[21] = {'idx': [51, 52, 53], 'nodes': 5}
    g[22] = {'idx': [54, 55], 'nodes': 5}
    g[23] = {'idx': [56, 57, 58], 'nodes': 5}
    g[24] = {'idx': [59, 60, 61], 'nodes': 5}
    g[25] = {'idx': [62, 63, 64], 'nodes': 5}
    g[26] = {'idx': [65, 66, 67], 'nodes': 5}
    g[27] = {'idx': [68, 69], 'nodes': 5}
    g[28] = {'idx': [70, 71], 'nodes': 5}
    g[29] = {'idx': [72], 'nodes': 5}

    counts = []
    for ii in range(0, 30):
        counts.append(float(gdv[:, g[ii]['idx']].sum())/g[ii]['nodes'])

    return np.asarray(counts, dtype=np.int)




def to_numpy(tensor):
    return tensor.numpy()

def write_orca_input_file(G, fname):
    """Write graph edgelist file."""
    fWrite = open(fname, 'w')
    fWrite.write("%d %d\n" % (G.order(), G.size()))
    for (n1, n2) in G.edges():
        fWrite.write("%d %d\n" % (n1, n2))
    fWrite.close()

def read_orca_output_file(fname):
    """Read graphlet counts file."""
    A = np.loadtxt(fname, delimiter=" ")
    return A

class ORCARunner(object):
    """Runs ORCA, computes graphlet degree vectors"""
    def __init__(self, threshold=6):
        self.threshold = threshold
        self.as_graph  = Composer(torch.load,
                                  CoordLoader(silent_if_square=True),
                                  AdjacencyMatrixMaker(self.threshold, selfloop=False),
                                  to_numpy,
                                  nx.from_numpy_matrix)

        self.orca_path = (BIN / 'orca.exe').absolute()
        self.cmd_template = f"{self.orca_path}"" 5 {infile} {outfile}" 

    def run(self, filename):
        """
        Dispathes an ORCA run, reads/records results, cleans up.
        """
        filename = Path(filename)
        pdb_id = filename.stem

        graph = self.as_graph(filename)

        with tempfile.TemporaryDirectory() as tmpdir:
            infile  = Path(tmpdir) / f"tmp_{pdb_id}.in"
            outfile = Path(tmpdir) / f"tmp_{pdb_id}.out"
            cmd   = shlex.split(self.cmd_template.format(infile=infile, outfile=outfile))
            write_orca_input_file(graph, infile)
            subprocess.run(cmd)
            node_gdv  = read_orca_output_file(outfile) 

            graph_gdv = count_graphlets(node_gdv)
            normed_gdv = graph_gdv / graph_gdv.sum()

            graph_gdvs = np.concatenate([graph_gdv[None, :], normed_gdv[None, :]]) 
        
        return dict(channels=['raw', 'normed'], mat=graph_gdvs, protein=pdb_id)

    def __str__(self):
        return f"{self.__class__.__name__}({self.threshold})"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pt", type=Path, help="Input PyTorch tensor file.")
    parser.add_argument("output_npz", type=Path, help="Output NPZ file path")
    parser.add_argument("-t", "--threshold", dest="threshold", type=float, default=6.)

    args = parser.parse_args()

    orca = ORCARunner(args.threshold)

    timer = Timer().start()
    print("[I] Running ORCA", end='...')
    result = orca.run(args.input_pt)
    print("DONE")
   
    print(f"Saving {result} to {args.output_npz}", end='...')
    np.savez_compressed(args.output_npz, **result)
    print("DONE")
