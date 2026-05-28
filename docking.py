"""
Drug Hunter — Docking engine
Developed by Sarang Dhote, Shivaji Science College, Nagpur

IMPORTANT: All heavy imports (rdkit, vina) are LAZY — inside functions only.
This file can be imported safely even if rdkit/vina are not installed.
The app will never crash because of this file.
"""

import json
import os
import urllib.request
from pathlib import Path

RESULTS_FILE  = Path("docking_results.json")
PDB_CACHE_DIR = Path("pdb_cache")


# ── Availability checks (lazy — never crash on import) ───────────────────────

def _rdkit_ok():
    try:
        from rdkit import Chem  # noqa
        return True
    except Exception:
        return False


def _vina_ok():
    try:
        from vina import Vina  # noqa
        return True
    except Exception:
        return False


def docking_available():
    """Returns True only if both rdkit and vina are working."""
    return _rdkit_ok() and _vina_ok()


# ── Lookup (pre-computed scores) ─────────────────────────────────────────────

def _load():
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_score(case_id, ligand_name, protein_type="target"):
    """Return pre-computed score or None."""
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
    """Download PDB from RCSB, cache locally."""
    PDB_CACHE_DIR.mkdir(exist_ok=True)
    pdb_id  = pdb_id.strip().lower()
    local   = PDB_CACHE_DIR / f"{pdb_id}.pdb"
    if local.exists():
        return True, str(local)
    try:
        urllib.request.urlretrieve(
            f"https://files.rcsb.org/download/{pdb_id}.pdb", str(local)
        )
        return True, str(local)
    except Exception as e:
        return False, f"Could not download {pdb_id.upper()}: {e}"


_SKIP = {
    "HOH","WAT","DOD","NA","CL","K","MG","CA","ZN","MN","FE","CU",
    "SO4","PO4","GOL","EDO","ACT","DMS","PEG","FMT","TRS","EPE","BME",
    "MES","IOD","NO3","CO3","NH4","CIT","MPD",
}

_TYPES = {
    "C":"C","N":"N","NA":"NA","O":"O","OA":"OA","S":"S","SA":"SA",
    "H":"HD","P":"P","F":"F","CL":"Cl","BR":"Br","I":"I",
    "ZN":"Zn","MG":"Mg","CA":"Ca","FE":"Fe",
}


def _pdb_to_pdbqt(pdb_path, out_path, is_ligand=False):
    """Convert PDB to PDBQT format."""
    import numpy as np  # already in requirements

    torsions = 0
    if is_ligand and _rdkit_ok():
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
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
                keep = line.startswith("ATOM") if not is_ligand else line.startswith(("ATOM","HETATM"))
                if not keep:
                    continue
                try:
                    atom_id   = int(line[6:11])
                    atom_name = line[12:16]
                    res_name  = line[17:20].strip()
                    chain     = line[21].strip() or "A"
                    res_seq   = int(line[22:26])
                    x, y, z   = float(line[30:38]), float(line[38:46]), float(line[46:54])
                except (ValueError, IndexError):
                    continue
                elem = line[76:78].strip()
                if not elem:
                    elem = "".join(c for c in atom_name if c.isalpha())[:1]
                elem = "".join(c for c in elem if c.isalpha()).upper()
                if not is_ligand and elem == "H":
                    continue
                vtype  = _TYPES.get(elem, elem.title())
                if elem == "C" and "AR" in atom_name.upper():
                    vtype = "A"
                rec = "HETATM" if is_ligand else "ATOM"
                fo.write(
                    f"{rec:<6}{atom_id:>5} {atom_name:<4} {res_name:>3} "
                    f"{chain}{res_seq:>4}    {x:>8.3f}{y:>8.3f}{z:>8.3f}"
                    f"  1.00  0.00    +0.000 {vtype:<2}\n"
                )
            fo.write("ENDROOT\nTORSDOF {}\n".format(torsions) if is_ligand else "END\n")
        return True, out_path
    except Exception as e:
        return False, str(e)


def _smiles_to_pdbqt(smiles, out_path):
    """SMILES → 3D PDBQT using RDKit."""
    if not _rdkit_ok():
        return False, "RDKit not available"
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
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
        ok, msg = _pdb_to_pdbqt(tmp, out_path, is_ligand=True)
        try:
            os.remove(tmp)
        except Exception:
            pass
        return ok, msg
    except Exception as e:
        return False, str(e)


def _active_site_box(pdb_path):
    """Find binding pocket from co-crystallised ligand."""
    import numpy as np
    coords = {}
    try:
        with open(pdb_path) as f:
            for line in f:
                if not line.startswith("HETATM"):
                    continue
                res = line[17:20].strip()
                if res in _SKIP:
                    continue
                key = f"{res}-{line[21]}-{line[22:26].strip()}"
                try:
                    coords.setdefault(key, []).append(
                        [float(line[30:38]), float(line[38:46]), float(line[46:54])]
                    )
                except ValueError:
                    continue
    except Exception:
        return None
    if not coords:
        return None
    best = max(coords, key=lambda k: len(coords[k]))
    pts  = coords[best]
    if len(pts) < 5:
        return None
    arr = np.array(pts)
    cen = arr.mean(axis=0)
    box = np.clip(arr.max(axis=0) - arr.min(axis=0) + 10, 18, 25)
    return float(cen[0]), float(cen[1]), float(cen[2]), float(box[0]), float(box[1]), float(box[2])


def _protein_centroid(pdbqt_path):
    """Fallback: geometric centre of whole protein."""
    import numpy as np
    pts = []
    try:
        with open(pdbqt_path) as f:
            for line in f:
                if line.startswith(("ATOM","HETATM")):
                    try:
                        pts.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
                    except ValueError:
                        continue
    except Exception:
        pass
    if not pts:
        return 0.0, 0.0, 0.0, 22.0, 22.0, 22.0
    arr = np.array(pts)
    cen = arr.mean(axis=0)
    box = np.clip(arr.max(axis=0) - arr.min(axis=0) + 10, 18, 30)
    return float(cen[0]), float(cen[1]), float(cen[2]), float(box[0]), float(box[1]), float(box[2])


# ── Live docking ──────────────────────────────────────────────────────────────

def dock(smiles, pdb_id, work_dir="dock_tmp", exhaustiveness=4):
    """
    Run real AutoDock Vina. Requires rdkit + vina packages.
    Returns (True, score_kcal_mol) or (False, error_string).
    """
    if not _vina_ok():
        return False, "vina package not available (pip install vina)"
    if not _rdkit_ok():
        return False, "rdkit not available (pip install rdkit)"

    os.makedirs(work_dir, exist_ok=True)
    rec = os.path.join(work_dir, "receptor.pdbqt")
    lig = os.path.join(work_dir, "ligand.pdbqt")

    ok, pdb_path = fetch_pdb(pdb_id)
    if not ok:
        return False, pdb_path

    ok, msg = _pdb_to_pdbqt(pdb_path, rec, is_ligand=False)
    if not ok:
        return False, f"Receptor prep: {msg}"

    ok, msg = _smiles_to_pdbqt(smiles, lig)
    if not ok:
        return False, f"Ligand prep: {msg}"

    box = _active_site_box(pdb_path) or _protein_centroid(rec)
    cx, cy, cz, sx, sy, sz = box

    try:
        from vina import Vina
        v = Vina(sf_name="vina", verbosity=0)
        v.set_receptor(rec)
        v.set_ligand_from_file(lig)
        v.compute_vina_maps(
            center=[cx, cy, cz],
            box_size=[sx, sy, sz]
        )
        v.dock(exhaustiveness=exhaustiveness, n_poses=5)
        energies = v.energies(n_poses=1)
        if energies is not None and len(energies) > 0:
            return True, round(float(energies[0][0]), 2)
        return False, "Vina returned no poses"
    except Exception as e:
        return False, f"Vina error: {e}"
