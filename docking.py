"""
Real molecular docking engine for Drug Hunter game.
Developed by Sarang Dhote, Shivaji Science College, Nagpur.

Uses the vina Python package (pip install vina) — no binary download needed,
works on Streamlit Cloud out of the box.

Two modes:
  LOOKUP — reads docking_results.json instantly (pre-computed)
  LIVE   — runs real AutoDock Vina via the Python API (~15-60s per ligand)
"""

import json
import os
import urllib.request
from pathlib import Path

import numpy as np

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    RDKIT_OK = True
except ImportError:
    RDKIT_OK = False

try:
    from vina import Vina as _Vina
    VINA_OK = True
except ImportError:
    VINA_OK = False
except Exception:
    # Some systems have vina installed but fail at runtime (missing libs)
    VINA_OK = False

RESULTS_FILE  = Path("docking_results.json")
PDB_CACHE_DIR = Path("pdb_cache")
PDB_CACHE_DIR.mkdir(exist_ok=True)


def health_check():
    """
    Returns (ok: bool, message: str).
    Called at app startup to show a friendly error instead of a crash.
    """
    issues = []
    if not RDKIT_OK:
        issues.append("RDKit not installed — run: pip install rdkit")
    if not VINA_OK:
        issues.append("vina not installed — run: pip install vina")
    if issues:
        return False, " | ".join(issues)
    return True, "Docking engine ready"


# ── Lookup mode ───────────────────────────────────────────────────────────────

def _load():
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_score(case_id, ligand_name, protein_type="target"):
    return _load().get(f"{case_id}_{ligand_name}_{protein_type}")


def save_score(case_id, ligand_name, protein_type, score):
    data = _load()
    data[f"{case_id}_{ligand_name}_{protein_type}"] = score
    with open(RESULTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def has_results_for_case(case_id):
    return any(k.startswith(f"{case_id}_") for k in _load())


# ── Structure preparation ─────────────────────────────────────────────────────

def fetch_pdb(pdb_id):
    pdb_id  = pdb_id.strip().lower()
    local   = PDB_CACHE_DIR / f"{pdb_id}.pdb"
    if local.exists():
        return True, str(local)
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        urllib.request.urlretrieve(url, str(local))
        return True, str(local)
    except Exception as e:
        return False, f"Could not download {pdb_id.upper()}: {e}"


_TYPE = {
    "C": "C", "A": "A", "N": "N", "NA": "NA", "O": "O", "OA": "OA",
    "S": "S", "SA": "SA", "H": "HD", "P": "P", "F": "F",
    "CL": "Cl", "BR": "Br", "I": "I", "ZN": "Zn", "MG": "Mg",
    "CA": "Ca", "FE": "Fe", "MN": "Mn",
}

_SKIP_HETATM = {
    "HOH","WAT","DOD","NA","CL","K","MG","CA","ZN","MN","FE","CU","NI",
    "SO4","PO4","GOL","EDO","ACT","DMS","PEG","FMT","TRS","EPE","BME",
    "MES","IOD","BR","NO3","CO3","NH4","FLC","CIT","MPD","BOG","CSD",
}


def pdb_to_pdbqt(pdb_path, out_path, is_ligand=False):
    """Convert PDB → PDBQT. Receptor: ATOM only, no H. Ligand: HETATM + ATOM."""
    torsions = 0
    if is_ligand and RDKIT_OK:
        try:
            m = Chem.MolFromPDBFile(pdb_path, removeHs=False)
            if m:
                torsions = AllChem.CalcNumRotatableBonds(m)
        except Exception:
            torsions = 4
    try:
        with open(pdb_path) as fi, open(out_path, "w") as fo:
            if is_ligand:
                fo.write("ROOT\n")
            for line in fi:
                if is_ligand:
                    keep = line.startswith(("ATOM", "HETATM"))
                else:
                    keep = line.startswith("ATOM")
                if not keep:
                    continue
                try:
                    atom_id  = int(line[6:11])
                except ValueError:
                    atom_id  = 1
                atom_name = line[12:16]
                res_name  = line[17:20].strip()
                chain     = line[21].strip() or "A"
                try:
                    res_seq = int(line[22:26])
                except ValueError:
                    res_seq = 1
                try:
                    x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                except ValueError:
                    continue
                elem = line[76:78].strip()
                if not elem:
                    elem = "".join(c for c in atom_name if c.isalpha())[:1]
                elem = "".join(c for c in elem if c.isalpha()).upper()
                # skip receptor hydrogens
                if not is_ligand and elem == "H":
                    continue
                vtype = _TYPE.get(elem, elem.title())
                if elem == "C" and "AR" in atom_name.upper():
                    vtype = "A"
                record = "HETATM" if is_ligand else "ATOM"
                fo.write(
                    f"{record:<6}{atom_id:>5} {atom_name:<4} {res_name:>3} "
                    f"{chain}{res_seq:>4}    {x:>8.3f}{y:>8.3f}{z:>8.3f}"
                    f"  1.00  0.00    +0.000 {vtype:<2}\n"
                )
            if is_ligand:
                fo.write("ENDROOT\n")
                fo.write(f"TORSDOF {torsions}\n")
            else:
                fo.write("END\n")
        return True, out_path
    except Exception as e:
        return False, str(e)


def smiles_to_pdbqt(smiles, out_path):
    if not RDKIT_OK:
        return False, "RDKit not installed"
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return False, "Invalid SMILES"
        mol = Chem.AddHs(mol)
        ps  = AllChem.ETKDGv3()
        ps.randomSeed = 42
        AllChem.EmbedMolecule(mol, ps)
        AllChem.MMFFOptimizeMolecule(mol)
        tmp = out_path.replace(".pdbqt", "_tmp.pdb")
        Chem.MolToPDBFile(mol, tmp)
        ok, msg = pdb_to_pdbqt(tmp, out_path, is_ligand=True)
        try:
            os.remove(tmp)
        except Exception:
            pass
        return ok, msg
    except Exception as e:
        return False, str(e)


def active_site_box(pdb_path):
    """Centre the docking grid on the co-crystallised ligand (best practice)."""
    coords = {}
    try:
        with open(pdb_path) as f:
            for line in f:
                if not line.startswith("HETATM"):
                    continue
                res = line[17:20].strip()
                if res in _SKIP_HETATM:
                    continue
                key = f"{res}-{line[21]}-{line[22:26].strip()}"
                try:
                    coords.setdefault(key, []).append([
                        float(line[30:38]), float(line[38:46]), float(line[46:54])
                    ])
                except ValueError:
                    continue
    except Exception:
        return None
    if not coords:
        return None
    best = max(coords, key=lambda k: len(coords[k]))
    pts = coords[best]
    if len(pts) < 5:
        return None
    arr = np.array(pts)
    cen = arr.mean(axis=0)
    box = np.clip(arr.max(axis=0) - arr.min(axis=0) + 10, 18, 25)
    return cen[0], cen[1], cen[2], box[0], box[1], box[2]


def protein_centroid(pdbqt_path):
    """Fallback: geometric centre of the whole protein."""
    pts = []
    try:
        with open(pdbqt_path) as f:
            for line in f:
                if line.startswith(("ATOM", "HETATM")):
                    try:
                        pts.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
                    except ValueError:
                        continue
    except Exception:
        pass
    if not pts:
        return 0, 0, 0, 22, 22, 22
    arr = np.array(pts)
    cen = arr.mean(axis=0)
    box = np.clip(arr.max(axis=0) - arr.min(axis=0) + 10, 18, 30)
    return cen[0], cen[1], cen[2], float(box[0]), float(box[1]), float(box[2])


# ── Live docking ──────────────────────────────────────────────────────────────

def dock(smiles, pdb_id, work_dir="dock_tmp", exhaustiveness=4):
    """
    Run real AutoDock Vina via the Python package API.
    Returns (True, affinity_kcal_mol) or (False, error_string).
    """
    if not VINA_OK:
        return False, "vina package not installed — run: pip install vina"
    if not RDKIT_OK:
        return False, "rdkit not installed — run: pip install rdkit"

    os.makedirs(work_dir, exist_ok=True)
    rec_pdbqt = os.path.join(work_dir, "receptor.pdbqt")
    lig_pdbqt = os.path.join(work_dir, "ligand.pdbqt")

    # 1. Receptor
    ok, pdb_path = fetch_pdb(pdb_id)
    if not ok:
        return False, pdb_path
    ok, msg = pdb_to_pdbqt(pdb_path, rec_pdbqt, is_ligand=False)
    if not ok:
        return False, f"Receptor prep failed: {msg}"

    # 2. Ligand
    ok, msg = smiles_to_pdbqt(smiles, lig_pdbqt)
    if not ok:
        return False, f"Ligand prep failed: {msg}"

    # 3. Grid box — prefer active-site, fall back to centroid
    box = active_site_box(pdb_path) or protein_centroid(rec_pdbqt)
    cx, cy, cz, sx, sy, sz = box

    # 4. Run Vina via Python API (no subprocess, no binary download)
    try:
        v = _Vina(sf_name="vina", verbosity=0)
        v.set_receptor(rec_pdbqt)
        v.set_ligand_from_file(lig_pdbqt)
        v.compute_vina_maps(
            center=[float(cx), float(cy), float(cz)],
            box_size=[float(sx), float(sy), float(sz)]
        )
        v.dock(exhaustiveness=exhaustiveness, n_poses=5)
        energies = v.energies(n_poses=1)
        if energies is not None and len(energies) > 0:
            return True, round(float(energies[0][0]), 2)
        return False, "Vina returned no poses"
    except Exception as e:
        return False, f"Vina error: {e}"
