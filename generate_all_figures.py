#!/usr/bin/env python3
"""
generate_all_figures.py
=======================
Generates ALL figure panels for R9-POPC MD simulation analysis.

Produces:
  Figure_2a_binding_energy.png/pdf     -- Main Fig. 2a (bar chart)
  Figure_2b_snapshot.png               -- Main Fig. 2b (PyMOL snapshot placeholder)
  Supp_S1a_distance.png/pdf            -- Supp. S1a
  Supp_S1b_hbonds.png/pdf              -- Supp. S1b
  Supp_S1c_contacts.png/pdf            -- Supp. S1c
  Supp_S1d_rmsd.png/pdf                -- Supp. S1d
  Supp_S1e_hbond_dist.png/pdf          -- Supp. S1e
  Supp_S1f_density.png/pdf             -- Supp. S1f
  Figure_2_combined_main.png/pdf       -- Combined main figure
  Supp_S1_combined.png/pdf             -- Combined supplementary figure

Usage:
  cd ~/Simulation-250918/charmm-gui-5860297243/gromacs/
  python3 ~/generate_all_figures.py

Requirements:
  pip3 install matplotlib numpy scipy --break-system-packages

Author: "Generated for Computationally Engineered Peptide-Exosome Nanocarriers for Continuous Bioelectronic Monitoring of 3D Epidermal Regeneration" Advanced Functional Materials manuscript
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
from scipy.ndimage import uniform_filter1d
from pathlib import Path
import sys

# ══════════════════════════════════════════════════════════
# CONFIGURATION — edit paths here if needed
# ══════════════════════════════════════════════════════════
BASE_DIR = Path.home() / "Simulation-250918/charmm-gui-5860297243/gromacs"
OUT_DIR  = BASE_DIR / "figures_nature"
OUT_DIR.mkdir(exist_ok=True)

# Input .xvg files
FILES = {
    "dist":       BASE_DIR / "contacts_dist.xvg",
    "hbond_num":  BASE_DIR / "hbond_num.xvg",
    "contacts":   BASE_DIR / "contacts_num.xvg",
    "rmsd":       BASE_DIR / "rmsd.xvg",
    "hbond_dist": BASE_DIR / "hbond_dist.xvg",
    "density":    BASE_DIR / "density_z.xvg",
    "energy":     BASE_DIR / "interaction_energy.xvg",
}

# Confirmed values from gmx energy (250,001 MD steps)
ENERGY = {
    "coulomb_mean": -97.611,  "coulomb_sd": 30.0,
    "lj_mean":     -136.527,  "lj_sd":      7.4,
    "total_mean":  -234.138,  "total_sd":  30.4,
}

# Nature-compliant colors
COLORS = {
    "dist":       "#185FA5",
    "hbond_num":  "#0F6E56",
    "contacts":   "#993556",
    "rmsd":       "#533AB7",
    "hbond_dist": "#0F6E56",
    "density":    "#854F0B",
    "coulomb":    "#C0392B",
    "lj":         "#2471A3",
    "total":      "#1A5276",
}

# Nature figure dimensions
W_SINGLE = 3.54   # 90 mm single column
W_DOUBLE = 7.09   # 180 mm double column
H_PANEL  = 2.76   # ~70 mm panel height

# ══════════════════════════════════════════════════════════
# NATURE rcPARAMS
# ══════════════════════════════════════════════════════════
plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.sans-serif":   ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size":         6,
    "axes.labelsize":    6,
    "axes.titlesize":    6,
    "axes.linewidth":    0.5,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "xtick.labelsize":   5,
    "ytick.labelsize":   5,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size":  2,
    "ytick.major.size":  2,
    "xtick.direction":   "out",
    "ytick.direction":   "out",
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
    "savefig.facecolor": "white",
    "pdf.fonttype":      42,
    "ps.fonttype":       42,
})

# ══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════
def read_xvg_ts(filepath):
    """Read 2-column GROMACS time-series xvg. Returns (time_ns, data)."""
    t, d = [], []
    with open(filepath) as fh:
        for line in fh:
            if line.startswith(("#", "@")): continue
            cols = line.split()
            if len(cols) < 2: continue
            try:
                t.append(float(cols[0]))
                d.append(float(cols[1]))
            except ValueError:
                continue
    t, d = np.array(t), np.array(d)
    if len(t) > 0 and t.max() > 100:
        t /= 1000.0   # ps -> ns
    return t, d

def read_xvg_profile(filepath):
    """Read 2-column spatial/distribution xvg. Returns (x, y)."""
    x, y = [], []
    with open(filepath) as fh:
        for line in fh:
            if line.startswith(("#", "@")): continue
            cols = line.split()
            if len(cols) < 2: continue
            try:
                x.append(float(cols[0]))
                y.append(float(cols[1]))
            except ValueError:
                continue
    return np.array(x), np.array(y)

def smooth(data, frac=0.06):
    """Rolling average smoothing."""
    w = max(3, int(len(data) * frac))
    return uniform_filter1d(data, size=w, mode="nearest")

def eq_stats(data, frac=0.80):
    """Mean ± SD of last (1-frac) fraction of data."""
    tail = data[int(len(data) * frac):]
    return np.mean(tail), np.std(tail)

def panel_label(ax, letter):
    """Add bold panel letter top-left (Nature style)."""
    ax.text(-0.18, 1.08, letter,
            transform=ax.transAxes,
            fontsize=8, fontweight="bold",
            va="top", ha="left")

def save_fig(fig, name):
    """Save figure as PNG and PDF."""
    png = OUT_DIR / f"{name}.png"
    pdf = OUT_DIR / f"{name}.pdf"
    fig.savefig(png, dpi=300)
    fig.savefig(pdf)
    print(f"  Saved -> {png.name}")
    print(f"  Saved -> {pdf.name}")
    plt.close(fig)

def check_files():
    """Check all input files exist."""
    missing = []
    for key, path in FILES.items():
        if not path.exists():
            missing.append(f"  MISSING: {path.name}")
    if missing:
        print("\nWARNING — missing files:")
        for m in missing: print(m)
        print("Affected panels will show placeholder text.\n")

# ══════════════════════════════════════════════════════════
# PANEL DRAWING FUNCTIONS
# ══════════════════════════════════════════════════════════
def draw_timeseries(ax, key, ylabel, letter, color, inty=False):
    """Draw time-series panel with raw + smooth + band."""
    path = FILES[key]
    if not path.exists():
        ax.text(0.5, 0.5, f"{path.name}\nnot found",
                ha="center", va="center",
                transform=ax.transAxes, color="gray", fontsize=7)
        panel_label(ax, letter)
        return

    t, d   = read_xvg_ts(path)
    ds     = smooth(d)
    mean, sd = eq_stats(d)

    # Raw trace (faint)
    ax.plot(t, d, color=color, lw=0.5, alpha=0.20, rasterized=True)
    # Smoothed line (bold)
    ax.plot(t, ds, color=color, lw=1.5)
    # ± 0.3 SD band
    ax.fill_between(t,
                    ds - d.std() * 0.3,
                    ds + d.std() * 0.3,
                    color=color, alpha=0.12)

    # Annotation: equilibrium mean ± SD
    ax.text(0.97, 0.97,
            f"mean {mean:.3f} \u00b1 {sd:.3f}",
            transform=ax.transAxes,
            fontsize=4.5, ha="right", va="top", color="#555555")

    ax.set_xlabel("Time (ns)")
    ax.set_ylabel(ylabel)
    ax.set_xlim(t[0], t[-1])
    ax.tick_params(length=2, width=0.5)

    if inty:
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    panel_label(ax, letter)


def draw_profile(ax, key, xlabel, ylabel, letter, color):
    """Draw spatial/distribution profile panel."""
    path = FILES[key]
    if not path.exists():
        ax.text(0.5, 0.5, f"{path.name}\nnot found",
                ha="center", va="center",
                transform=ax.transAxes, color="gray", fontsize=7)
        panel_label(ax, letter)
        return

    x, y = read_xvg_profile(path)
    ax.plot(x, y, color=color, lw=1.5)
    ax.fill_between(x, y, alpha=0.12, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(x[0], x[-1])
    ax.tick_params(length=2, width=0.5)
    panel_label(ax, letter)


def draw_energy_bar(ax, letter):
    """Draw binding energy bar chart (Fig. 2a) from confirmed gmx energy values."""
    means_kj = [ENERGY["coulomb_mean"],
                ENERGY["lj_mean"],
                ENERGY["total_mean"]]
    stds_kj  = [ENERGY["coulomb_sd"],
                ENERGY["lj_sd"],
                ENERGY["total_sd"]]

    # Convert to kcal/mol
    means = [v / 4.184 for v in means_kj]
    stds  = [v / 4.184 for v in stds_kj]
    labels = ["Coulomb", "LJ (vdW)", "Total"]
    colors = [COLORS["coulomb"], COLORS["lj"], COLORS["total"]]

    bars = ax.bar(labels, means, yerr=stds,
                  color=colors, alpha=0.85, width=0.5,
                  capsize=3,
                  error_kw=dict(lw=0.8, capthick=0.8, ecolor="black"))

    # Value labels inside bars
    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2,
                mean / 2,
                f"{mean:.1f}",
                ha="center", va="center",
                fontsize=5, color="white", fontweight="bold")

    ax.set_ylabel("Interaction energy (kcal mol\u207b\u00b9)")
    ax.set_ylim(min(means) - max(stds) - 4, 5)
    ax.axhline(0, color="black", lw=0.5, linestyle="--", alpha=0.4)
    ax.tick_params(length=2, width=0.5)

    # Also show kJ/mol values
    ax.text(0.97, 0.03,
            f"Coulomb: {ENERGY['coulomb_mean']:.1f} \u00b1 {ENERGY['coulomb_sd']:.1f} kJ mol\u207b\u00b9\n"
            f"LJ:      {ENERGY['lj_mean']:.1f} \u00b1 {ENERGY['lj_sd']:.1f} kJ mol\u207b\u00b9\n"
            f"Total:   {ENERGY['total_mean']:.1f} \u00b1 {ENERGY['total_sd']:.1f} kJ mol\u207b\u00b9\n"
            f"n = 250,001 MD steps",
            transform=ax.transAxes,
            fontsize=4, ha="right", va="bottom",
            color="#444444",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#cccccc", alpha=0.8))

    panel_label(ax, letter)


# ══════════════════════════════════════════════════════════
# MAIN FIGURE 2 (panels a + b placeholder)
# ══════════════════════════════════════════════════════════
def make_figure2_main():
    """Generate main Figure 2 panels a and b."""
    print("\n--- Main Figure 2 ---")

    # Panel a — binding energy bar chart (standalone)
    fig, ax = plt.subplots(figsize=(W_SINGLE, H_PANEL))
    draw_energy_bar(ax, "a")
    fig.tight_layout()
    save_fig(fig, "Figure_2a_binding_energy")

    # Panel b — PyMOL snapshot placeholder
    # (actual snapshot must be generated by pymol_structure_visualization.py)
    fig, ax = plt.subplots(figsize=(W_SINGLE * 1.6, H_PANEL))
    ax.set_facecolor("#1a1a2e")
    fig.patch.set_facecolor("#1a1a2e")
    ax.text(0.5, 0.6,
            "Fig. 2b — PyMOL snapshot",
            ha="center", va="center",
            fontsize=9, color="white", fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.4,
            "Run pymol_structure_visualization.py\nto generate this panel",
            ha="center", va="center",
            fontsize=7, color="#aaaaaa",
            transform=ax.transAxes)
    ax.axis("off")
    panel_label(ax, "b")
    fig.tight_layout()
    save_fig(fig, "Figure_2b_snapshot_placeholder")

    print("  NOTE: Replace Figure_2b with actual PyMOL output")


# ══════════════════════════════════════════════════════════
# SUPPLEMENTARY FIGURE S1 (panels a-f, individual)
# ══════════════════════════════════════════════════════════
def make_supp_individual():
    """Generate each supplementary panel as individual file."""
    print("\n--- Supplementary S1 individual panels ---")

    # S1a — distance
    fig, ax = plt.subplots(figsize=(W_SINGLE, H_PANEL))
    draw_timeseries(ax, "dist", "Min. distance (nm)", "a", COLORS["dist"])
    fig.tight_layout()
    save_fig(fig, "Supp_S1a_distance")

    # S1b — H-bonds
    fig, ax = plt.subplots(figsize=(W_SINGLE, H_PANEL))
    draw_timeseries(ax, "hbond_num", "H-bonds (count)", "b",
                    COLORS["hbond_num"], inty=True)
    fig.tight_layout()
    save_fig(fig, "Supp_S1b_hbonds")

    # S1c — contacts
    fig, ax = plt.subplots(figsize=(W_SINGLE, H_PANEL))
    draw_timeseries(ax, "contacts", "Contacts (n)", "c", COLORS["contacts"])
    fig.tight_layout()
    save_fig(fig, "Supp_S1c_contacts")

    # S1d — RMSD
    fig, ax = plt.subplots(figsize=(W_SINGLE, H_PANEL))
    draw_timeseries(ax, "rmsd", "RMSD (nm)", "d", COLORS["rmsd"])
    fig.tight_layout()
    save_fig(fig, "Supp_S1d_rmsd")

    # S1e — H-bond distance distribution
    fig, ax = plt.subplots(figsize=(W_SINGLE, H_PANEL))
    draw_profile(ax, "hbond_dist",
                 "Donor\u2013acceptor distance (nm)",
                 "Frequency", "e", COLORS["hbond_dist"])
    fig.tight_layout()
    save_fig(fig, "Supp_S1e_hbond_dist")

    # S1f — membrane density
    fig, ax = plt.subplots(figsize=(W_SINGLE, H_PANEL))
    draw_profile(ax, "density",
                 "Z-coordinate (nm)",
                 "Density (kg m\u207b\u00b3)", "f", COLORS["density"])
    fig.tight_layout()
    save_fig(fig, "Supp_S1f_density")


# ══════════════════════════════════════════════════════════
# COMBINED SUPPLEMENTARY FIGURE S1 (3x2 grid)
# ══════════════════════════════════════════════════════════
def make_supp_combined():
    """Generate combined Supplementary Figure S1 (3 columns x 2 rows)."""
    print("\n--- Supplementary S1 combined ---")

    fig = plt.figure(figsize=(W_DOUBLE, H_PANEL * 2.2))
    gs  = gridspec.GridSpec(2, 3, figure=fig,
                            hspace=0.58, wspace=0.42)

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[1, 0])
    ax_e = fig.add_subplot(gs[1, 1])
    ax_f = fig.add_subplot(gs[1, 2])

    draw_timeseries(ax_a, "dist",
                    "Min. distance (nm)", "a", COLORS["dist"])
    draw_timeseries(ax_b, "hbond_num",
                    "H-bonds (count)", "b", COLORS["hbond_num"], inty=True)
    draw_timeseries(ax_c, "contacts",
                    "Contacts (n)", "c", COLORS["contacts"])
    draw_timeseries(ax_d, "rmsd",
                    "RMSD (nm)", "d", COLORS["rmsd"])
    draw_profile(ax_e, "hbond_dist",
                 "Donor\u2013acceptor distance (nm)",
                 "Frequency", "e", COLORS["hbond_dist"])
    draw_profile(ax_f, "density",
                 "Z-coordinate (nm)",
                 "Density (kg m\u207b\u00b3)", "f", COLORS["density"])

    # X-axis labels for time-series panels
    for ax in [ax_a, ax_b, ax_c, ax_d]:
        ax.set_xlabel("Time (ns)")

    fig.suptitle(
        "Supplementary Fig. S1 | Supporting MD simulation analyses — "
        "R9 peptide\u2013POPC membrane interaction",
        fontsize=6.5, fontweight="bold", y=1.01
    )

    save_fig(fig, "Supp_S1_combined")


# ══════════════════════════════════════════════════════════
# PRINT STATISTICS SUMMARY
# ══════════════════════════════════════════════════════════
def print_stats():
    """Print all statistics for manuscript."""
    print("\n" + "="*60)
    print("STATISTICS SUMMARY FOR MANUSCRIPT")
    print("="*60)

    print("\nFig. 2a — Binding energy (gmx energy, 250,001 steps):")
    print(f"  Coulomb: {ENERGY['coulomb_mean']:.1f} ± {ENERGY['coulomb_sd']:.1f} kJ/mol"
          f"  ({ENERGY['coulomb_mean']/4.184:.1f} ± {ENERGY['coulomb_sd']/4.184:.1f} kcal/mol)")
    print(f"  LJ:      {ENERGY['lj_mean']:.1f} ± {ENERGY['lj_sd']:.1f} kJ/mol"
          f"  ({ENERGY['lj_mean']/4.184:.1f} ± {ENERGY['lj_sd']/4.184:.1f} kcal/mol)")
    print(f"  Total:   {ENERGY['total_mean']:.1f} ± {ENERGY['total_sd']:.1f} kJ/mol"
          f"  ({ENERGY['total_mean']/4.184:.1f} ± {ENERGY['total_sd']/4.184:.1f} kcal/mol)")

    for key, label, unit in [
        ("dist",      "Supp. S1a — Min. distance", "nm"),
        ("hbond_num", "Supp. S1b — H-bonds",       ""),
        ("contacts",  "Supp. S1c — Contacts",       ""),
        ("rmsd",      "Supp. S1d — RMSD",           "nm"),
    ]:
        path = FILES[key]
        if path.exists():
            t, d = read_xvg_ts(path)
            mean, sd = eq_stats(d)
            print(f"\n{label} (last 20%, n=3 frames):")
            print(f"  mean ± SD = {mean:.3f} ± {sd:.3f} {unit}")
        else:
            print(f"\n{label}: FILE NOT FOUND")

    print("\n" + "="*60)
    print(f"All figures saved to: {OUT_DIR}")
    print("="*60)


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("R9-POPC MD Simulation Figure Generator")
    print("Nature Communications format")
    print(f"Output: {OUT_DIR}\n")

    check_files()
    make_figure2_main()
    make_supp_individual()
    make_supp_combined()
    print_stats()

    print("\nDone! Files generated:")
    print("  Main:  Figure_2a_binding_energy.png/pdf")
    print("         Figure_2b_snapshot_placeholder.png/pdf")
    print("  Supp:  Supp_S1a through S1f (individual + combined)")
    print("\nNext step: Run pymol_structure_visualization.py for Fig. 2b")
