# MD Simulation Analysis: R9 Peptide–POPC Membrane Interaction

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20121815-blue)](https://doi.org/10.5281/zenodo.20121815)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GROMACS](https://img.shields.io/badge/GROMACS-2023.4-green)](https://www.gromacs.org)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org)

## Overview

This repository contains the complete computational analysis and reproducible workflow for molecular dynamics simulations investigating R9 peptide insertion into POPC lipid bilayers. The study characterizes binding energetics, structural dynamics, and membrane interaction mechanisms essential for understanding R9-functionalized exosome design, as reported in:

> **Computationally Engineered Peptide-Exosome Nanocarriers for Continuous Bioelectronic Monitoring of 3D Epidermal Regeneration**
> Pham D.-T., et al. 
> *ACS Nano (2026).*
> *DOI 10.5281/zenodo.20121815*

## Key Findings

| Parameter | Value | Figure |
|---|---|---|
| Coulomb interaction | −97.6 ± 30.0 kJ mol⁻¹ | Fig. 1a |
| LJ van der Waals | −136.5 ± 7.4 kJ mol⁻¹ | Fig. 1a |
| Total binding energy | −234.1 ± 30.4 kJ mol⁻¹ | Fig. 1a |
| Min. distance (eq.) | 0.173 ± 0.006 nm | Supp. S1a |
| H-bonds (eq.) | 3.0 ± 0.8 | Supp. S1b |
| Contacts (eq.) | 2,357 ± 107 | Supp. S1c |
| RMSD (eq.) | 0.160 ± 0.016 nm | Supp. S1d |

## Repository Structure

```
.
├── scripts/
│   ├── generate_all_figures.py          # Main figure generation script
│   ├── pymol_structure_visualization.py # PyMOL snapshot (Fig. 2b)
│   ├── plot_panel_bar.py                # Binding energy bar chart
│   └── export_source_data.py           # Export CSV source data
├── gromacs/
│   ├── rerun.mdp                        # MDP for energy group reanalysis
│   ├── index.ndx                        # Index file (SOLU/MEMB groups)
│   └── analysis_commands.sh            # All GROMACS analysis commands
├── docs/
│   └── complete_figure_guide.txt       # Detailed figure generation guide
├── results/
│   └── example_figures/                # Example output figures
├── requirements.txt                    # Python dependencies
├── LICENSE                             # MIT License
└── README.md                           # This file
```

## System Requirements

### Software
- GROMACS 2023.4 ([download](https://www.gromacs.org/))
- Python 3.8+
- PyMOL 2.5 ([download](https://pymol.org/)) — for Fig. 1b only

### Python packages
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Clone repository
```bash
git clone https://github.com/[your-lab]/R9-POPC-MD-analysis.git
cd R9-POPC-MD-analysis
pip install -r requirements.txt
```

### 2. Set up data path
Edit the `BASE_DIR` variable in `scripts/generate_all_figures.py`:
```python
BASE_DIR = Path("/path/to/your/gromacs/simulation/folder")
```

### 3. Generate all figures
```bash
python3 scripts/generate_all_figures.py
```

### 4. Generate PyMOL snapshot (Fig. 2b)
```bash
# Option A: if PyMOL Python module installed
python3 scripts/pymol_structure_visualization.py

# Option B: generate .pml script, then run in PyMOL GUI
python3 scripts/pymol_structure_visualization.py
pymol -c docs/pymol_commands.pml
```

### 5. Export source data (for journal submission)
```bash
python3 scripts/export_source_data.py
```

## Reproducing GROMACS Analysis

All GROMACS commands to reproduce the `.xvg` analysis files are in `gromacs/analysis_commands.sh`:

```bash
bash gromacs/analysis_commands.sh
```

Or run individually:

```bash
# Minimum distance and contacts
echo "SOLU MEMB" | gmx mindist -s step7.tpr -f step7.xtc \
  -n index.ndx -od contacts_dist.xvg -on contacts_num.xvg

# Hydrogen bonds
gmx hbond -s step7.tpr -f step7.xtc -n index.ndx \
  -num hbond_num.xvg -dist hbond_dist.xvg

# RMSD
echo -e "1\n1" | gmx rms -s step7.tpr -f step7.xtc -o rmsd.xvg

# Membrane density
gmx density -s step7.tpr -f step7.xtc -n index.ndx -d Z -o density_z.xvg

# Interaction energy reanalysis
sed 's/energygrps               =/energygrps               = SOLU MEMB/' \
  mdout.mdp > rerun.mdp
gmx grompp -f rerun.mdp -c step7.gro -p topol.top -n index.ndx \
  -o rerun.tpr -maxwarn 5
gmx mdrun -s rerun.tpr -rerun step7.xtc -e rerun.edr -ntmpi 1 -ntomp 4
printf "20\n21\n0\n" | gmx energy -f rerun.edr -o interaction_energy.xvg
```

## Simulation Details

| Parameter | Value |
|---|---|
| Software | GROMACS 2023.4 |
| Force field | CHARMM36m |
| Temperature | 303.15 K |
| Pressure | 1 bar |
| Thermostat | Velocity-rescaling (τ = 1.0 ps) |
| Barostat | Parrinello–Rahman (τ = 5.0 ps) |
| Time step | 4 fs |
| Simulation time | 1 ns |
| Total atoms | 50,683 |
| POPC molecules | 164 |
| Water model | TIP3P |
| Salt concentration | 0.15 M KCl |
| Electrostatics | PME (1.2 nm cutoff) |
| Trajectory saved | Every 100 ps (11 frames) |
| Energy statistics | 250,001 MD steps |

## Output Files

Running `generate_all_figures.py` produces:

```
figures_nature/
├── Figure_2a_binding_energy.png/pdf     # Main Fig. 2a — bar chart
├── Figure_2b_snapshot_placeholder.png   # Replace with PyMOL output
├── Supp_S1a_distance.png/pdf           # Min. distance
├── Supp_S1b_hbonds.png/pdf             # H-bonds
├── Supp_S1c_contacts.png/pdf           # Lipid contacts
├── Supp_S1d_rmsd.png/pdf               # RMSD
├── Supp_S1e_hbond_dist.png/pdf         # H-bond distribution
├── Supp_S1f_density.png/pdf            # Membrane density
└── Supp_S1_combined.png/pdf            # Combined Supp. S1
```

## Citation

If you use these scripts, please cite:

```bibtex
@article{pham2026r9exosome,
  title   = {[Your paper title]},
  author  = {Pham, Duc-Trung and [Co-authors] and Cho, Sungbo},
  journal = {Advanced Functional Materials},
  year    = {2026},
  doi     = {(https://doi.org/10.5281/zenodo.20121815)}
}

@software{pham2026r9code,
  title   = {MD Simulation Analysis: R9 Peptide-POPC Membrane Interaction},
  author  = {Pham, Duc-Trung, et al},
  year    = {2026},
  doi     = {10.5281/zenodo.20121815}
},
  url     = {https://github.com/[your-lab]/R9-POPC-MD-analysis}
}
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contact

Duc-Trung Pham
BioMEMS & Bio-impedance Lab
Department of Electronic Engineering, Gachon University
Email: trungpham16488@gmail.com; trungpd19589@gachon.ac.kr
