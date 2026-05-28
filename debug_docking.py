"""
Diagnostic script to debug docking failures.

Run this locally:  python debug_docking.py

It runs ONE docking (Aspirin vs COX-2) with full output so you can
see exactly what Vina says and where the pipeline breaks.
"""

import os
import subprocess

from docking import (
    ensure_vina_exists,
    fetch_pdb_from_rcsb,
    convert_pdb_to_pdbqt,
    convert_smiles_to_pdbqt,
    compute_protein_centroid,
    VINA_BINARY,
)


def debug_one():
    smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
    pdb_id = "3LN1"  # COX-2
    work = "debug_tmp"
    os.makedirs(work, exist_ok=True)

    print("STEP 0: Vina binary")
    if not ensure_vina_exists():
        print("  FAILED to download Vina")
        return
    print(f"  OK: {VINA_BINARY} exists = {os.path.exists(VINA_BINARY)}")

    print("\nSTEP 1: Download PDB")
    ok, pdb_path = fetch_pdb_from_rcsb(pdb_id)
    print(f"  {'OK' if ok else 'FAIL'}: {pdb_path}")
    if not ok:
        return

    print("\nSTEP 2: Receptor -> PDBQT")
    receptor = os.path.join(work, "protein.pdbqt")
    ok, msg = convert_pdb_to_pdbqt(pdb_path, receptor, is_ligand=False)
    print(f"  {'OK' if ok else 'FAIL'}: {msg}")
    if os.path.exists(receptor):
        with open(receptor) as f:
            lines = f.readlines()
        print(f"  Receptor PDBQT: {len(lines)} lines")
        print(f"  First line: {lines[0].rstrip() if lines else 'EMPTY'}")
        # Count ATOM records
        atoms = sum(1 for l in lines if l.startswith(("ATOM", "HETATM")))
        print(f"  Atom records: {atoms}")

    print("\nSTEP 3: Ligand -> PDBQT")
    ligand = os.path.join(work, "ligand.pdbqt")
    ok, msg = convert_smiles_to_pdbqt(smiles, ligand)
    print(f"  {'OK' if ok else 'FAIL'}: {msg}")
    if os.path.exists(ligand):
        with open(ligand) as f:
            lines = f.readlines()
        print(f"  Ligand PDBQT: {len(lines)} lines")
        atoms = sum(1 for l in lines if l.startswith(("ATOM", "HETATM")))
        print(f"  Atom records: {atoms}")

    print("\nSTEP 4: Grid box")
    cx, cy, cz, sx, sy, sz = compute_protein_centroid(receptor)
    sx, sy, sz = min(sx, 30), min(sy, 30), min(sz, 30)
    print(f"  Center: ({cx:.1f}, {cy:.1f}, {cz:.1f})")
    print(f"  Size: ({sx:.1f}, {sy:.1f}, {sz:.1f})")

    print("\nSTEP 5: Run Vina (full output below)")
    out = os.path.join(work, "out.pdbqt")
    cmd = [
        VINA_BINARY,
        "--receptor", receptor,
        "--ligand", ligand,
        "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
        "--size_x", str(sx), "--size_y", str(sy), "--size_z", str(sz),
        "--exhaustiveness", "2",
        "--out", out,
    ]
    print(f"  Command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print(f"  Return code: {result.returncode}")
    print("  --- STDOUT ---")
    print(result.stdout)
    print("  --- STDERR ---")
    print(result.stderr)

    print("\nSTEP 6: Output file")
    if os.path.exists(out):
        with open(out) as f:
            content = f.read()
        print(f"  Output file exists, {len(content)} chars")
        for line in content.split("\n"):
            if "VINA RESULT" in line:
                print(f"  Found: {line.strip()}")
    else:
        print("  No output file created")


if __name__ == "__main__":
    debug_one()
