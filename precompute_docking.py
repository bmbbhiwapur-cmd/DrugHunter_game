"""
Pre-compute real docking scores for all cases using AutoDock Vina.

USAGE:
    python precompute_docking.py              # All cases
    python precompute_docking.py --case 1     # Only case 1
    python precompute_docking.py --quick      # Faster, lower quality (exhaustiveness=2)
    python precompute_docking.py --redo       # Re-dock even if cached

Output: docking_results.json

Run this ONCE locally (or on any Linux machine), then commit
docking_results.json to GitHub. The deployed game reads this file instantly.

NOTE: This uses blind docking (whole-protein grid box) for simplicity and
consistency across all 20 cases. Scores are real Vina affinities but may differ
from focused (active-site) docking. For the game's purpose — ranking ligands and
teaching selectivity — blind docking gives meaningful, comparable results.
"""

import argparse
import time

from cases import CASES
from docking import dock, save_score, load_docking_results, ensure_vina_exists


def precompute_case(case, exhaustiveness=4, skip_existing=True):
    case_id = case["id"]
    print(f"\n{'='*60}")
    print(f"CASE {case_id}: {case['title']}")
    print(f"Target: {case['target_protein']} (PDB {case['target_pdb']})")
    if case.get("off_target_pdb"):
        print(f"Off-target: {case['off_target']} (PDB {case['off_target_pdb']})")
    print(f"{'='*60}")

    existing = load_docking_results()

    # --- Dock all candidates against the TARGET ---
    print(f"\n[TARGET] {case['target_protein']}")
    for cand in case["candidates"]:
        name, smiles = cand["name"], cand["smiles"]
        key = f"{case_id}_{name}_target"
        if skip_existing and key in existing:
            print(f"  cached  {name}: {existing[key]} kcal/mol")
            continue
        print(f"  docking {name}... ", end="", flush=True)
        start = time.time()
        ok, result = dock(smiles, case["target_pdb"], exhaustiveness=exhaustiveness)
        elapsed = time.time() - start
        if ok:
            save_score(case_id, name, "target", result)
            print(f"{result} kcal/mol  ({elapsed:.0f}s)")
        else:
            print(f"FAILED: {result}")

    # --- Dock selectivity candidates against the OFF-TARGET ---
    if case.get("off_target_pdb") and "selectivity_data" in case:
        print(f"\n[OFF-TARGET] {case['off_target']}")
        existing = load_docking_results()
        for cand in case["candidates"]:
            name = cand["name"]
            if name not in case["selectivity_data"]:
                continue
            smiles = cand["smiles"]
            key = f"{case_id}_{name}_off_target"
            if skip_existing and key in existing:
                print(f"  cached  {name}: {existing[key]} kcal/mol")
                continue
            print(f"  docking {name}... ", end="", flush=True)
            start = time.time()
            ok, result = dock(smiles, case["off_target_pdb"], exhaustiveness=exhaustiveness)
            elapsed = time.time() - start
            if ok:
                save_score(case_id, name, "off_target", result)
                print(f"{result} kcal/mol  ({elapsed:.0f}s)")
            else:
                print(f"FAILED: {result}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, help="Only process this case ID")
    parser.add_argument("--quick", action="store_true", help="exhaustiveness=2 (faster)")
    parser.add_argument("--redo", action="store_true", help="Re-dock even if cached")
    args = parser.parse_args()

    print("Bootstrapping Vina binary...")
    if not ensure_vina_exists():
        print("ERROR: Could not download Vina. Check internet connection.")
        return

    exhaustiveness = 2 if args.quick else 4
    cases_to_run = [c for c in CASES if args.case is None or c["id"] == args.case]

    if not cases_to_run:
        print(f"No cases match ID {args.case}")
        return

    print(f"Processing {len(cases_to_run)} case(s) at exhaustiveness={exhaustiveness}\n")
    start = time.time()
    for case in cases_to_run:
        try:
            precompute_case(case, exhaustiveness, skip_existing=not args.redo)
        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as e:
            print(f"\nFailed on case {case['id']}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"DONE in {(time.time()-start)/60:.1f} min. Saved to docking_results.json")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
