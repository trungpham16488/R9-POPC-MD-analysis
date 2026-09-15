#!/usr/bin/env python3
"""
pymol_structure_visualization.py
=================================
Generates Figure 1b — PyMOL snapshot of R9 peptide in POPC bilayer.

Run this script FROM WITHIN PyMOL:
  File > Run Script > select this file

OR from command line (if PyMOL is installed with Python API):
  pymol -c pymol_structure_visualization.py

Output:
  Figure_1b_R9_POPC_snapshot.png  (300 dpi, ACS Nano-ready)
  Figure_1b_R9_POPC_snapshot.pdf

Input files required (in gromacs folder):
  step7.gro   -- final frame structure
  step7.xtc   -- trajectory (for selecting frame at 1 ns)
  step7.tpr   -- topology

Color scheme (ACS Nano):
  R9 peptide    -- dark blue spheres  (#1A3A6B)
  POPC lipids   -- cyan sticks        (#00CED1)
  Phosphorus    -- purple spheres     (#8B008B)
  K+ ions       -- orange spheres     (#FF8C00)
  Cl- ions      -- orange spheres     (#FF8C00)
  Water         -- hidden

Author: Generated for "Computationally Engineered R9-Exosome Nanocarriers and Label-Free Impedimetric Monitoring for Theranostic 3D Epidermal Regeneration"

# ══════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════
import os
from pathlib import Path

GROMACS_DIR = str(Path.home() / "Simulation-250918/charmm-gui-5860297243/gromacs")
OUTPUT_DIR  = str(Path.home() / "Simulation-250918/charmm-gui-5860297243/gromacs/figures_nature")
GRO_FILE    = f"{GROMACS_DIR}/step7.gro"
OUTPUT_PNG  = f"{OUTPUT_DIR}/Figure_1b_R9_POPC_snapshot.png"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════
# PYMOL COMMANDS
# ══════════════════════════════════════════════════════════
try:
    import pymol
    from pymol import cmd

    print("PyMOL detected — running visualization...")

    # ── 1. Initialize PyMOL ──
    pymol.finish_launching(['pymol', '-qc'])

    # ── 2. Load structure ──
    cmd.load(GRO_FILE, "system")

    # ── 3. Select groups ──
    cmd.select("R9_peptide", "chain A or resname ARG and not (resname POPC or resname TIP3 or resname POT or resname CLA)")
    cmd.select("POPC_lipid", "resname POPC")
    cmd.select("phosphorus",  "resname POPC and name P")
    cmd.select("ions",        "resname POT or resname CLA")
    cmd.select("water",       "resname TIP3 or resname SOL")

    # ── 4. Hide everything first ──
    cmd.hide("everything", "all")
    cmd.remove("water")

    # ── 5. Show R9 as spheres (dark blue) ──
    cmd.show("spheres", "R9_peptide")
    cmd.color("marine", "R9_peptide")
    cmd.set("sphere_scale", 0.8, "R9_peptide")

    # ── 6. Show POPC as sticks (cyan) ──
    cmd.show("sticks", "POPC_lipid")
    cmd.color("cyan", "POPC_lipid")
    cmd.set("stick_radius", 0.15, "POPC_lipid")

    # ── 7. Show phosphorus as spheres (purple) ──
    cmd.show("spheres", "phosphorus")
    cmd.color("purple", "phosphorus")
    cmd.set("sphere_scale", 0.6, "phosphorus")

    # ── 8. Show ions as spheres (orange) ──
    cmd.show("spheres", "ions")
    cmd.color("orange", "ions")
    cmd.set("sphere_scale", 0.5, "ions")

    # ── 9. Background white ──
    cmd.bg_color("white")

    # ── 10. Set view (side view of bilayer) ──
    cmd.orient("all")
    cmd.zoom("all", 5)

    # Rotate to show membrane cross-section
    cmd.rotate("x", 90)
    cmd.rotate("y", 15)

    # ── 11. Ray trace settings ──
    cmd.set("ray_shadows", 0)
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("ray_trace_mode", 1)

    # ── 12. Set image size (Nature single column = 90mm at 300dpi = 1063px) ──
    cmd.set("ray_trace_frames", 1)
    cmd.viewport(1200, 800)

    # ── 13. Ray trace and save ──
    print(f"Ray tracing... (this takes 1-2 minutes)")
    cmd.ray(1200, 800)
    cmd.png(OUTPUT_PNG, dpi=300)
    print(f"Saved -> {OUTPUT_PNG}")

    # ── 14. Save PyMOL session for editing ──
    session_file = OUTPUT_PNG.replace(".png", ".pse")
    cmd.save(session_file)
    print(f"Saved PyMOL session -> {session_file}")

    cmd.quit()

except ImportError:
    # PyMOL not available as Python module
    # Generate PyMOL command script instead
    print("PyMOL Python module not found.")
    print("Generating PyMOL command script instead...\n")

    SCRIPT_FILE = f"{OUTPUT_DIR}/pymol_commands.pml"

    pml = f"""# pymol_commands.pml
# Run in PyMOL: File > Run Script
# Or: pymol pymol_commands.pml

# Load structure
load {GRO_FILE}, system

# Select groups
select R9_peptide, chain A
select POPC_lipid, resname POPC
select phosphorus, resname POPC and name P
select ions, resname POT or resname CLA
select water, resname TIP3

# Hide everything
hide everything, all
remove water

# R9 peptide — dark blue spheres
show spheres, R9_peptide
color marine, R9_peptide
set sphere_scale, 0.8, R9_peptide

# POPC — cyan sticks
show sticks, POPC_lipid
color cyan, POPC_lipid
set stick_radius, 0.15, POPC_lipid

# Phosphorus — purple spheres
show spheres, phosphorus
color purple, phosphorus
set sphere_scale, 0.6, phosphorus

# Ions — orange spheres
show spheres, ions
color orange, ions
set sphere_scale, 0.5, ions

# White background
bg_color white

# Set view
orient all
zoom all, 5
rotate x, 90
rotate y, 15

# Ray trace settings
set ray_shadows, 0
set antialias, 2
set ray_trace_mode, 1

# Save image (300 dpi, Nature format)
ray 1200, 800
png {OUTPUT_PNG}, dpi=300

# Save session
save {OUTPUT_PNG.replace('.png', '.pse')}

quit
"""

    with open(SCRIPT_FILE, "w") as f:
        f.write(pml)

    print(f"PyMOL command script saved to: {SCRIPT_FILE}")
    print()
    print("To generate Fig. 2b, run ONE of these:")
    print(f"  Option 1 (command line): pymol -c {SCRIPT_FILE}")
    print(f"  Option 2 (PyMOL GUI):    File > Run Script > {SCRIPT_FILE}")
    print()
    print("After running, the output will be:")
    print(f"  {OUTPUT_PNG}")
    print()
    print("Color scheme used:")
    print("  R9 peptide  -- marine (dark blue spheres)")
    print("  POPC lipids -- cyan sticks")
    print("  Phosphorus  -- purple spheres")
    print("  Ions        -- orange spheres")
    print("  Water       -- hidden")
