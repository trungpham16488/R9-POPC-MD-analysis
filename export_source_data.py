#!/usr/bin/env python3
"""export_source_data.py — exports all .xvg to Nature CSV source data."""
import numpy as np
from pathlib import Path

BASE_DIR = Path.home() / "Simulation-250918/charmm-gui-5860297243/gromacs"
OUT_DIR  = BASE_DIR / "source_data"
OUT_DIR.mkdir(exist_ok=True)

def read_ts(fp):
    t,d=[],[]
    for line in open(fp):
        if line.startswith(("#","@")): continue
        c=line.split()
        if len(c)<2: continue
        try: t.append(float(c[0])); d.append(float(c[1]))
        except: continue
    t,d=np.array(t),np.array(d)
    if len(t)>0 and t.max()>100: t/=1000.0
    return t,d

# Fig. 2a
rows=[["Energy_term","Mean_kJ_mol","SD_kJ_mol","Mean_kcal_mol","SD_kcal_mol","N_steps"],
      ["Coulomb_SR",-97.611,30.0,-23.33,7.17,250001],
      ["LJ_SR",-136.527,7.4,-32.63,1.77,250001],
      ["Total",-234.138,30.4,-55.96,7.27,250001]]
with open(OUT_DIR/"Figure2a_source_data.csv","w") as f:
    for r in rows: f.write(",".join(str(x) for x in r)+"\n")
print("Saved -> Figure2a_source_data.csv")

for xvg,csv,hdr in [
    ("contacts_dist.xvg","Supp_S1a_source_data.csv","Time_ns,Min_distance_nm"),
    ("hbond_num.xvg","Supp_S1b_source_data.csv","Time_ns,Hbond_count"),
    ("contacts_num.xvg","Supp_S1c_source_data.csv","Time_ns,Contact_count"),
    ("rmsd.xvg","Supp_S1d_source_data.csv","Time_ns,RMSD_nm"),
]:
    t,d=read_ts(BASE_DIR/xvg)
    np.savetxt(OUT_DIR/csv,np.column_stack([t,d]),delimiter=",",header=hdr,comments="",fmt="%.6f")
    print(f"Saved -> {csv}")

for xvg,csv,hdr in [
    ("hbond_dist.xvg","Supp_S1e_source_data.csv","Distance_nm,Frequency"),
    ("density_z.xvg","Supp_S1f_source_data.csv","Z_nm,Density_kg_m3"),
]:
    x,y=[],[]
    for line in open(BASE_DIR/xvg):
        if line.startswith(("#","@")): continue
        c=line.split()
        if len(c)<2: continue
        try: x.append(float(c[0])); y.append(float(c[1]))
        except: continue
    np.savetxt(OUT_DIR/csv,np.column_stack([x,y]),delimiter=",",header=hdr,comments="",fmt="%.6f")
    print(f"Saved -> {csv}")

print(f"\nAll source data -> {OUT_DIR}")
