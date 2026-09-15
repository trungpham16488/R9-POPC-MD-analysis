#!/bin/bash
# =============================================================================
# analysis_commands.sh
# Complete GROMACS analysis workflow for R9-POPC MD simulation
# Figure 1 & Supplementary S1
#
# Usage:
#   cd ~/Simulation-250918/charmm-gui-5860297243/gromacs/
#   bash ~/analysis_commands.sh
#
# Requirements:
#   GROMACS 2023.4 installed
#   index.ndx with SOLU and MEMB groups
# =============================================================================

set -e  # Stop on error

SIMDIR="$HOME/Simulation-250918/charmm-gui-5860297243/gromacs"
cd "$SIMDIR"
echo "Working in: $SIMDIR"
echo ""

# =============================================================================
# STEP 1 — Minimum distance R9 <-> POPC (Supp. S1a)
# =============================================================================
echo "Step 1: Minimum distance and contacts..."
echo "SOLU MEMB" | gmx mindist \
    -s step7.tpr \
    -f step7.xtc \
    -n index.ndx \
    -od contacts_dist.xvg \
    -on contacts_num.xvg
echo "  -> contacts_dist.xvg (Supp. S1a)"
echo "  -> contacts_num.xvg  (Supp. S1c)"

# =============================================================================
# STEP 2 — Hydrogen bonds (Supp. S1b, S1e)
# =============================================================================
echo ""
echo "Step 2: Hydrogen bonds..."
gmx hbond \
    -s step7.tpr \
    -f step7.xtc \
    -n index.ndx \
    -num hbond_num.xvg \
    -dist hbond_dist.xvg
echo "  -> hbond_num.xvg  (Supp. S1b)"
echo "  -> hbond_dist.xvg (Supp. S1e)"

# =============================================================================
# STEP 3 — RMSD (Supp. S1d)
# =============================================================================
echo ""
echo "Step 3: RMSD..."
echo -e "1\n1" | gmx rms \
    -s step7.tpr \
    -f step7.xtc \
    -o rmsd.xvg
echo "  -> rmsd.xvg (Supp. S1d)"

# =============================================================================
# STEP 4 — Membrane density profile (Supp. S1f)
# =============================================================================
echo ""
echo "Step 4: Membrane density..."
echo "MEMB" | gmx density \
    -s step7.tpr \
    -f step7.xtc \
    -n index.ndx \
    -d Z \
    -o density_z.xvg
echo "  -> density_z.xvg (Supp. S1f)"

# =============================================================================
# STEP 5 — Interaction energy reanalysis (Fig. 1a)
# =============================================================================
echo ""
echo "Step 5: Interaction energy reanalysis (Fig. 1a)..."
echo "  5a: Creating rerun.mdp with SOLU-MEMB energy groups..."
sed 's/energygrps               =/energygrps               = SOLU MEMB/' \
    mdout.mdp > rerun.mdp

echo "  5b: Running grompp..."
gmx grompp \
    -f rerun.mdp \
    -c step7.gro \
    -p topol.top \
    -n index.ndx \
    -o rerun.tpr \
    -maxwarn 5

echo "  5c: Running mdrun rerun (~30 seconds)..."
gmx mdrun \
    -s rerun.tpr \
    -rerun step7.xtc \
    -e rerun.edr \
    -ntmpi 1 \
    -ntomp 4

echo "  5d: Extracting Coulomb and LJ energies..."
printf "20\n21\n0\n" | gmx energy \
    -f rerun.edr \
    -o interaction_energy.xvg

echo "  -> interaction_energy.xvg (Fig. 2a)"
echo ""
echo "  5e: Printing statistics..."
printf "20\n21\n0\n" | gmx energy -f rerun.edr -o /dev/null 2>&1 | \
    grep -A5 "Statistics"

# =============================================================================
# STEP 6 — Verify all output files
# =============================================================================
echo ""
echo "=== Output files ==="
files=(
    "contacts_dist.xvg:Supp S1a - Min distance"
    "hbond_num.xvg:Supp S1b - H-bonds"
    "contacts_num.xvg:Supp S1c - Contacts"
    "rmsd.xvg:Supp S1d - RMSD"
    "hbond_dist.xvg:Supp S1e - H-bond distribution"
    "density_z.xvg:Supp S1f - Density"
    "interaction_energy.xvg:Fig 1a - Binding energy"
)

all_ok=true
for entry in "${files[@]}"; do
    file="${entry%%:*}"
    label="${entry##*:}"
    if [ -f "$file" ]; then
        lines=$(grep -v "^[#@]" "$file" | wc -l)
        echo "  OK  $file ($lines data points) -> $label"
    else
        echo "  MISSING: $file -> $label"
        all_ok=false
    fi
done

echo ""
if [ "$all_ok" = true ]; then
    echo "All files generated successfully!"
    echo ""
    echo "Next step: Generate figures"
    echo "  python3 ~/generate_all_figures.py"
else
    echo "WARNING: Some files missing — check errors above"
fi
