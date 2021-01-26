# graphletcounts
Wrappers and scripts for counting (protein structure) graphlets. For calculating graphlets at scale, we have been parallelizing via <a href="https://github.com/flatironinstitute/disBatch">DisBatch</a>.

# Installation
```bash
git clone https://github.com/djberenberg/graphletcounts
pip install numpy scipy networkx torch
```

# Scripts
- `compute_orca_graphlets.py` - runs ORCA, calculates global graphlets up to a certain (fixed) size, which can be found in the file.
- `compute_grafene_features.py` - runs GRAFENE, specifically calculating the "NormOrderedGraphlets3-4" - the highest performing features
as seen in the methods paper.
- `reduce_graphlets.py` - as the two above scripts calculate _individual_ graphlet vectors, this script takes as input a list of graphlet vectors and compresses them into a single matrix. 
- `make_graphlet_tasks.py` - generates the DisBatch taskfile.

# More information
- Faisal, F.E., Newaz, K., Chaney, J.L. et al. GRAFENE: Graphlet-based alignment-free network approach integrates 3D structural and sequence (residue order) data to improve protein structural comparison. Sci Rep 7, 14890 (2017). https://doi.org/10.1038/s41598-017-14411-y

- More information given in
Tomaž Hočevar, Janez Demšar, A combinatorial approach to graphlet counting, 
Bioinformatics, Volume 30, Issue 4, 15 February 2014, Pages 559–565, https://doi.org/10.1093/bioinformatics/btt717
