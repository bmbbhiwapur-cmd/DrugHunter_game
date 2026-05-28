# 🔬 Real Docking Setup Guide

This game uses **real AutoDock Vina** docking — the same engine as the InSilico BioSphere portal. Here's how it works and how to set it up.

## How it works

The game has two scoring modes:

1. **Lookup mode (default, instant)** — reads `docking_results.json`, a file of pre-computed real Vina scores. Players see real docking results with zero waiting.
2. **Live mode (on-demand, slow)** — runs Vina in real-time during the game. Useful as a fallback or for a "sandbox" feel.

The trick that makes Vina work on Streamlit Cloud (where you can't install system software) is **downloading the Vina binary at runtime** — exactly what your existing portal's `ensure_linux_vina_exists()` does. Our `docking.py` does the same via `ensure_vina_exists()`.

## Step 1: Pre-compute real scores (do this once)

On any Linux machine (or Streamlit Cloud terminal), run:

```bash
pip install -r requirements.txt

# Compute real Vina scores for all 20 cases (takes ~30-90 min)
python precompute_docking.py

# Or just one case to test first (~3-5 min)
python precompute_docking.py --case 1

# Faster but lower quality (for testing)
python precompute_docking.py --case 1 --quick
```

This creates `docking_results.json`. Each entry looks like:

```json
{
  "1_Celecoxib_target": -9.4,
  "1_Celecoxib_off_target": -6.1,
  "1_Aspirin_target": -6.3,
  ...
}
```

## Step 2: Commit the results to GitHub

```bash
git add docking_results.json
git commit -m "Add real Vina docking scores"
git push
```

Now your deployed game shows **real docking scores instantly** — no waiting, no Vina needed on the server at game time.

## Important notes on the docking method

- **Blind docking:** The pre-computation uses a whole-protein grid box (geometric center, auto-sized). This is simple and consistent across all 20 cases. Scores are real Vina affinities and rank ligands meaningfully.
- **For higher accuracy:** If you want active-site-focused docking, edit `compute_protein_centroid()` in `docking.py` to use the known pocket coordinates (your `api.py` already has `parse_bound_ligands()` which extracts co-crystallized ligand coordinates — a great way to define the real binding site).
- **The game's points** are based on the *pedagogical* "kind" of each ligand (best/alt/weak/decoy), NOT the raw docking score. This keeps the learning objective intact even if a real dock score surprises you. The real scores are shown to students for authenticity and to build intuition.

## Linking to your existing InSilico BioSphere portal

Since your portal already does live docking, you have two integration options:

**Option A — Shared results file:** Have your portal write docking results in the same `{case}_{ligand}_{target}` JSON format. The game reads them directly.

**Option B — Call your portal's functions:** Import your `convert_smiles_to_pdbqt`, `convert_pdb_to_pdbqt`, and Vina-runner directly into `docking.py`, replacing our adapted versions. They're functionally equivalent — yours are battle-tested.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Vina binary unavailable" | Check internet; GitHub releases must be reachable |
| "Could not download PDB" | Check the PDB ID is valid at rcsb.org |
| "Ligand prep failed" | SMILES may be invalid — verify on PubChem |
| Docking very slow | Use `--quick` flag, or lower exhaustiveness in `dock()` |
| Scores look wrong | Blind docking is approximate; consider active-site box |
