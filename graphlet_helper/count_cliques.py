#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

import torch
import numpy as np
import networkx as nx

from .toolbox import Composer, AdjacencyMatrixMaker, CoordLoader

class CliqueRunner(object):
    """Runs GRAFENE, computes normorderd 3-4 graphlet degree vectors"""
    def __init__(self, threshold=6):
        self.threshold = threshold
        self.as_adjmat  = Composer(torch.load,
                                   CoordLoader(silent_if_square=True),
                                   AdjacencyMatrixMaker(self.threshold, selfloop=False))

    def clique_counts(self, clique_sizes, K=8):
        # Distribution of cliques from size 2 to K
        min_clique_size = 2 # index offset
        counts = np.zeros(K - 1, dtype=np.int)
        for sz in clique_sizes:
            if sz <= K:
                counts[ sz - min_clique_size ] += 1
    
        return counts
        
    def run(self, filename):
        """
        Count clique sizes
        """
        stem = Path(filename).stem

        adj = self.as_adjmat(filename)

        G = nx.from_numpy_matrix( adj.numpy() )

        cliques = list(nx.find_cliques(G))
        clique_sizes = [len(c) for c in cliques]

        raw = self.clique_counts(clique_sizes)
        normed = raw / sum(raw)

        return dict(channels=['raw', 'normed'],
                    mat=np.concatenate([ raw[None, ...], normed[None, ...] ]),
                    protein=stem,
                    )

if __name__ == '__main__':
    pass

