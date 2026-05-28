"""
Real molecular docking engine for CSI Drug Discovery game.

Adapted from InSilico BioSphere (by Sarang S. Dhote, Shivaji Science College, Nagpur)
— reuses the proven approach of downloading the Vina binary at runtime, which
works on Streamlit Cloud where system binaries cannot be pre-installed.

Two modes:
1. LOOKUP mode (default in-game)  — reads pre-computed docking_results.json (instant)
2. LIVE mode (precompute/sandbox) — runs real AutoDock Vina (~10-60s per ligand)
"""

import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False

DOCKING_RESULTS_FILE = Path("docking_results.json")
VINA_BINARY = "./vina"
VINA_URL = "https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64"
PDB_CACHE_DIR = Path("pdb_cache")
PDB_CACHE_DIR.mkdir(exist_ok=True)


# ============================================================
# VINA BINARY BOOTSTRAP (the key to running on Streamlit Cloud)
# ============================================================

def ensure_vina_exists():
    """Download the Vina binary at runtime if not present."""
    if not os.path.exists(VINA_BINARY):
        try:
            urllib.request.urlretrieve(VINA_URL, VINA_BINARY)
            os.chmod(VINA_BINARY, 0o755)
            return True
        except Exception as e:
            print(f"Failed to download Vina: {e}")
            return False
    return True


# ============================================================
# LOOKUP MODE (used by the running game — instant)
# ============================================================

def load_docking_results():
    if DOCKING_RESULTS_FILE.exists():
        try:
            with open(DOCKING_RESULTS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def get_score(case_id, ligand_name, protein_type="target"):
    """Return pre-computed Vina score (kcal/mol) or None if not found."""
    results = load_docking_results()
    key = f"{case_id}_{ligand_name}_{protein_type}"
    return results.get(key)


def save_score(case_id, ligand_name, protein_type, score):
    results = load_docking_results()
    key = f"{case_id}_{ligand_name}_{protein_type}"
    results[key] = score
    with open(DOCKING_RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def has_results_for_case(case_id):
    results = load_docking_results()
    return any(key.startswith(f"{case_id}_") for key in results.keys())


# ============================================================
# STRUCTURE PREPARATION (adapted from api.py)
# ============================================================

def fetch_pdb_from_rcsb(pdb_id):
    """Download a PDB file from RCSB. Cached locally."""
    pdb_id = pdb_id.strip().lower()
    local_pdb = PDB_CACHE_DIR / f"{pdb_id}.pdb"
    if local_pdb.exists():
        return True, str(local_pdb)
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        urllib.request.urlretrieve(url, str(local_pdb))
        return True, str(local_pdb)
    except Exception:
        return False, f"Could not download PDB ID '{pdb_id.upper()}'."


_ATOM_TYPE_MAP = {
    "H": "H", "HD": "HD", "HS": "HS", "C": "C", "A": "A", "N": "N", "NA": "NA",
    "NS": "NS", "O": "O", "OA": "OA", "S": "S", "SA": "SA", "P": "P", "F": "F",
    "CL": "Cl", "BR": "Br", "I": "I", "ZN": "Zn", "MG": "Mg",
}


def convert_pdb_to_pdbqt(input_pdb, output_pdbqt, is_ligand=False):
    """Convert PDB to PDBQT (simplified, from api.py approach)."""
    torsions = 0
    if is_ligand and RDKIT_AVAILABLE:
        try:
            mol = Chem.MolFromPDBFile(input_pdb, removeHs=False)
            if mol:
                torsions = AllChem.CalcNumRotatableBonds(mol)
        except Exception:
            torsions = 4
    try:
        with open(input_pdb, "r") as pdb, open(output_pdbqt, "w") as pdbqt:
            if is_ligand:
                pdbqt.write("ROOT\n")
            for line in pdb:
                # For the RECEPTOR: keep only protein ATOM records.
                # Drop HETATM (ligands, ions, water) and hydrogens — Vina's
                # standard receptor prep does this, and leaving them in causes
                # parse errors / failed runs.
                if is_ligand:
                    keep = line.startswith(("ATOM", "HETATM"))
                else:
                    keep = line.startswith("ATOM")
                if keep:
                    record_type = line[:6].strip()
                    try:
                        atom_id = int(line[6:11].strip())
                    except ValueError:
                        atom_id = 1
                    atom_name = line[12:16]
                    res_name = line[17:20].strip()
                    chain_id = line[21].strip() if line[21].strip() else "A"
                    try:
                        res_seq = int(line[22:26].strip())
                    except ValueError:
                        res_seq = 1
                    try:
                        x = float(line[30:38].strip())
                        y = float(line[38:46].strip())
                        z = float(line[46:54].strip())
                    except ValueError:
                        continue
                    element = line[76:78].strip()
                    if not element:
                        element = ''.join([c for c in atom_name if c.isalpha()])[0]
                    element = ''.join([c for c in element if c.isalpha()]).upper()
                    # Skip hydrogens in the receptor (Vina uses united-atom receptor)
                    if not is_ligand and element == "H":
                        continue
                    vina_type = _ATOM_TYPE_MAP.get(element, element.title())
                    if element == "C" and "AR" in atom_name.upper():
                        vina_type = "A"
                    pdbqt.write(
                        f"{record_type:<6}{atom_id:>5} {atom_name:<4} {res_name:>3} "
                        f"{chain_id}{res_seq:>4}    {x:>8.3f}{y:>8.3f}{z:>8.3f}"
                        f"{1.00:>6.2f}{0.00:>6.2f}    +0.000 {vina_type:<2}\n"
                    )
            if is_ligand:
                pdbqt.write("ENDROOT\n")
                pdbqt.write(f"TORSDOF {torsions}\n")
            else:
                pdbqt.write("END\n")
        return True, output_pdbqt
    except Exception as e:
        return False, str(e)


def convert_smiles_to_pdbqt(smiles_string, output_filename):
    """SMILES to 3D PDBQT ligand (from api.py approach)."""
    if not RDKIT_AVAILABLE:
        return False, "RDKit not available"
    try:
        mol = Chem.MolFromSmiles(smiles_string)
        if mol is None:
            return False, "Invalid SMILES."
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
        AllChem.MMFFOptimizeMolecule(mol)
        temp_pdb = output_filename.replace(".pdbqt", "_temp.pdb")
        Chem.MolToPDBFile(mol, temp_pdb)
        convert_pdb_to_pdbqt(temp_pdb, output_filename, is_ligand=True)
        if os.path.exists(temp_pdb):
            os.remove(temp_pdb)
        return True, output_filename
    except Exception as e:
        return False, str(e)


def compute_protein_centroid(pdbqt_file):
    """Geometric center + box dims for whole-protein blind docking (from api.py)."""
    coords = []
    if not os.path.exists(pdbqt_file):
        return 0.0, 0.0, 0.0, 22.0, 22.0, 22.0
    with open(pdbqt_file, "r") as f:
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                try:
                    coords.append([
                        float(line[30:38]), float(line[38:46]), float(line[46:54])
                    ])
                except ValueError:
                    continue
    if not coords:
        return 0.0, 0.0, 0.0, 22.0, 22.0, 22.0
    arr = np.array(coords)
    center = np.mean(arr, axis=0)
    dims = np.max(arr, axis=0) - np.min(arr, axis=0) + 10.0
    return center[0], center[1], center[2], dims[0], dims[1], dims[2]


def find_active_site_box(pdb_file):
    """
    Find the binding pocket using the co-crystallized ligand in the PDB file.

    Most drug-target PDB structures include the bound ligand (a HETATM that
    isn't water/ion). Its center is the real active site — far better than
    blind docking. This mirrors api.py's parse_bound_ligands().

    Returns (cx, cy, cz, sx, sy, sz) or None if no suitable ligand found.
    """
    if not os.path.exists(pdb_file):
        return None

    # Common ions/buffers to ignore (not real drug-binding ligands)
    ignore = {
        "HOH", "WAT", "DOD", "NA", "CL", "K", "MG", "CA", "ZN", "MN", "FE",
        "SO4", "PO4", "GOL", "EDO", "ACT", "DMS", "PEG", "FMT", "TRS", "EPE",
        "BME", "MES", "IOD", "BR", "NO3", "CO3", "NH4", "FLC", "CIT",
    }

    ligands = {}
    with open(pdb_file) as f:
        for line in f:
            if line.startswith("HETATM"):
                res_name = line[17:20].strip()
                if res_name in ignore:
                    continue
                chain = line[21].strip() or "A"
                try:
                    res_seq = int(line[22:26].strip())
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                except ValueError:
                    continue
                key = f"{res_name}-{chain}-{res_seq}"
                ligands.setdefault(key, []).append((x, y, z))

    if not ligands:
        return None

    # Pick the ligand with the most atoms (likely the real drug, not a fragment)
    best_key = max(ligands, key=lambda k: len(ligands[k]))
    pts = ligands[best_key]
    if len(pts) < 6:  # too small to be a real drug-like ligand
        return None

    arr = np.array(pts)
    center = np.mean(arr, axis=0)
    # Box = ligand extent + 10 Angstrom padding, capped at 25
    dims = np.max(arr, axis=0) - np.min(arr, axis=0) + 10.0
    dims = np.minimum(dims, 25.0)
    dims = np.maximum(dims, 18.0)  # minimum useful box
    return center[0], center[1], center[2], dims[0], dims[1], dims[2]


# ============================================================
# LIVE DOCKING (real Vina run)
# ============================================================

def dock(smiles, pdb_id, work_dir="dock_tmp", exhaustiveness=4):
    """
    Run real AutoDock Vina docking for one ligand against one receptor.

    Returns: (success: bool, best_affinity: float OR error_message: str)
    """
    if not ensure_vina_exists():
        return False, "Vina binary unavailable"

    os.makedirs(work_dir, exist_ok=True)
    receptor_pdbqt = os.path.join(work_dir, "protein.pdbqt")
    ligand_pdbqt = os.path.join(work_dir, "ligand.pdbqt")
    out_poses = os.path.join(work_dir, "out.pdbqt")

    # 1. Receptor: download + convert
    ok, pdb_path = fetch_pdb_from_rcsb(pdb_id)
    if not ok:
        return False, pdb_path
    ok, msg = convert_pdb_to_pdbqt(pdb_path, receptor_pdbqt, is_ligand=False)
    if not ok:
        return False, f"Receptor prep failed: {msg}"

    # 2. Ligand: SMILES -> PDBQT
    ok, msg = convert_smiles_to_pdbqt(smiles, ligand_pdbqt)
    if not ok:
        return False, f"Ligand prep failed: {msg}"

    # 3. Grid box — prefer the real active site (co-crystallized ligand),
    #    fall back to whole-protein blind docking only if no ligand is found.
    box = find_active_site_box(pdb_path)
    if box is not None:
        cx, cy, cz, sx, sy, sz = box
    else:
        cx, cy, cz, sx, sy, sz = compute_protein_centroid(receptor_pdbqt)
        sx, sy, sz = min(sx, 30), min(sy, 30), min(sz, 30)

    # 4. Run Vina
    cmd = [
        VINA_BINARY,
        "--receptor", receptor_pdbqt,
        "--ligand", ligand_pdbqt,
        "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
        "--size_x", str(sx), "--size_y", str(sy), "--size_z", str(sz),
        "--exhaustiveness", str(exhaustiveness),
        "--out", out_poses,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Try parsing the output PDBQT file FIRST (most reliable across Vina versions).
        # Vina writes "REMARK VINA RESULT:  <affinity>  <rmsd_lb>  <rmsd_ub>" for each pose.
        affinity = _parse_affinity_from_pdbqt(out_poses)

        # Fall back to stdout parsing if the file didn't have it
        if affinity is None:
            affinity = _parse_best_affinity(result.stdout)

        if affinity is None:
            # Return diagnostic info so we can see what Vina actually said
            diag = result.stdout[-400:] if result.stdout else "(no stdout)"
            err = result.stderr[-400:] if result.stderr else "(no stderr)"
            return False, f"Could not parse Vina output. rc={result.returncode}. stdout: {diag} | stderr: {err}"

        return True, affinity
    except subprocess.TimeoutExpired:
        return False, "Docking timed out"
    except Exception as e:
        return False, str(e)


def _parse_affinity_from_pdbqt(pdbqt_path):
    """
    Read the best affinity from a Vina output PDBQT file.
    Vina writes lines like:  REMARK VINA RESULT:    -9.4      0.000      0.000
    The first one is the best pose.
    """
    if not os.path.exists(pdbqt_path):
        return None
    try:
        with open(pdbqt_path) as f:
            for line in f:
                if line.startswith("REMARK VINA RESULT:"):
                    parts = line.split()
                    # parts = ['REMARK','VINA','RESULT:', '-9.4', '0.000', '0.000']
                    return round(float(parts[3]), 2)
    except (ValueError, IndexError, IOError):
        return None
    return None


def _parse_best_affinity(stdout_text):
    """Extract the best (mode 1) affinity from Vina stdout."""
    pattern = re.compile(r"^\s*(\d+)\s+([-+]?\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)")
    for line in stdout_text.split("\n"):
        match = pattern.match(line)
        if match and int(match.group(1)) == 1:
            return round(float(match.group(2)), 2)
    return None
