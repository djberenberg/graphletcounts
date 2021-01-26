#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: dberenberg

"""
Port of the feature computation parts of GRAFENE's `psn-classify` script to Python
to calculate NormOrderdGraphlet-3-4 counts

Designed to more cleanly handle temporary inputs so the script is portable enough to run
in parallel. Also modified to take as input PyTorch tensor files rather than PDBs.

The `psn-classify` script does the following: (the parts we care about, that is)
    1) Convert PDB to edge list in LEDA format
    2) compute graphlet counts from LEDA format

This script modifies that routine to do the following:
    1) Convert Pytorch tensor file to LEDA format edge list (a temporary file)
    2) compute graphlet counts from LEDA format
"""

import site
import shlex
import tempfile
import subprocess
from pathlib import Path

import torch
import numpy as np

from .toolbox import Composer, Timer, AdjacencyMatrixMaker, CoordLoader

psn_approach = "NormOrderedGraphlet-3-4".casefold()
threshold = "6A"

BIN = Path(__file__).resolve().absolute().parent / "bin"
assert BIN.exists(), "Script not located at same level as GRAFENE bin/ directory"


def check_exists(filename):
    filename = Path(filename)
    if not filename.exists():
        raise FileNotFoundError(f"Can\'t find {filename}")
    return filename

def write_leda(adjmat, filename):
    """
    Writes a leda file to a filename from an adjacency matrix representation
    args:
        :adjmat (torch.Tensor) - adjacency matrix
        :filename (str or Path) - path to write to
    returns:
        :None, writes the file by side effect
    """
    # count each edge twice and divide by 2
    num_edges = int(adjmat.sum(dim=1).sum(dim=0) / 2)
    num_nodes = adjmat.shape[0]

    header = "\n".join(["LEDA.GRAPH", "string", "short", "-2"])
    with open(filename, 'w') as ledafile:
        # header section
        print(header, file=ledafile)
        # node section
        print(num_nodes, file=ledafile)
        for i in range(1, num_nodes+1):
            print("|{"f"{i}""}|", file=ledafile)
        # edge section
        print(num_edges, file=ledafile)
        for i in range(1, num_nodes+1):
            for j in range(1, num_nodes+1):
                if adjmat[i-1, j-1]:
                    print(f"{i} {j} 0 ""|{}|", file=ledafile)


class GRAFENERunner(object):
    """Runs GRAFENE, computes normorderd 3-4 graphlet degree vectors"""
    def __init__(self, threshold=6):
        self.threshold = threshold
        self.as_adjmat  = Composer(torch.load,
                                   CoordLoader(silent_if_square=True),
                                   AdjacencyMatrixMaker(self.threshold, selfloop=False))
        
        self.bindir = BIN
        self._count_ordered_path = self.bindir / 'ncount-ordered'
        self._normalize_graphlets_path = self.bindir / 'normalize-graphlets'

        self.count_ordered = f"{self._count_ordered_path}"" {ledafile} {ordered_counts}".format
        self.normalize     = f"{self._normalize_graphlets_path}"" {ordered_counts} {normed}".format
        
    def run(self, filename):
        """
        Dispatches a GRAFENE run, reads/records results, cleansu p.
        """
        filename = Path(filename)
        A = self.as_adjmat(filename)
        stem = filename.stem

        timer = Timer().start()
    
        with tempfile.TemporaryDirectory() as tmpdir:
            ledafile = Path(tmpdir) / f"tmp_{stem}.gw"
            counts   = Path(tmpdir) / f"tmp_{stem}.ogf"
            normed   = Path(tmpdir) / f"tmp_{stem}.norm"
            
            # write down ledafile
            write_leda(A, ledafile)
            
            # press out the commands
            count_cmd = self.count_ordered(ledafile=ledafile, ordered_counts=counts)
            norm_cmd  = self.normalize(ordered_counts=counts, normed=normed)
            
            # run commands
            for cmd in (count_cmd, norm_cmd):
                subprocess.run(shlex.split(cmd))
                
            # parse vector

            with open(normed, 'r') as normed_counts:
                normed_vector = np.array(list(map(lambda line: float(line.strip()), normed_counts)))
                normed_shape = normed_vector.shape[0]

            with open(counts, 'r') as raw_counts:
                lines = raw_counts.readlines()
                count_vector = np.array(list(map(lambda line: float(line.strip().split("\t")[1]), lines)))
                pad_defn = (0, normed_shape - count_vector.shape[0])
                padded = np.pad(count_vector, pad_defn, 'constant')

        timer.stop()
        return dict(channels=['raw', 'normed'],
                    mat=np.concatenate([padded[None, ...], normed_vectors[None, ...]]),
                    protein=stem,
                    )

    def __str__(self):
        return f"{self.__class__.__name__}({self.threshold})"

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Compute NormOrderedGraphlet-3-4 features")
    parser.add_argument("input_pt", type=check_exists,
                        help="Input distance map")
    parser.add_argument("output_npz", type=Path,
                        help="Output features")
    parser.add_argument("-t","--threshold", type=int,
                        help="Contact map threshold", default=6, dest='threshold')

    args = parser.parse_args()
    
    # runs GRAFENE wrapper 
    runner = GRAFENERunner(args.threshold)
    result = runner.run(args.input_pt)

    print(f"Finished {args.input_pt} in {resul['mat'].shape}")
    np.savez_compressed(args.output_npz, **result)
