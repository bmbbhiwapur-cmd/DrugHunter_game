# 🧬 CSI: Drug Discovery — Educational Game

An interactive educational game for UG/PG students learning **molecular docking** and **drug discovery**. Built with Streamlit.

## 🎮 How it works

Students play as junior medicinal chemists solving patient cases in 5 stages:

1. **Identify the disease target** (which protein causes the symptoms?)
2. **Find the binding pocket** (where on the protein does a drug bind?)
3. **Choose and dock candidate ligands** (which molecules to test?)
4. **Test selectivity** (does it bind only to the target, or also to off-targets?)
5. **Check drug-likeness** (Lipinski's Rule of 5)

## 📚 20 Disease Cases Included

| # | Case | Disease | Difficulty |
|---|---|---|---|
| 1 | The Painful Truth | Rheumatoid Arthritis | ⭐⭐ |
| 2 | Pressure Mounting | Hypertension | ⭐⭐ |
| 3 | The Forgetting Mind | Alzheimer's | ⭐⭐⭐ |
| 4 | Blood Flow Blues | Erectile Dysfunction | ⭐⭐⭐ |
| 5 | The Mosquito's Curse | Malaria | ⭐⭐⭐⭐ |
| 6 | Breathless in the City | Asthma | ⭐⭐ |
| 7 | Beyond the Blue | Depression | ⭐⭐⭐ |
| 8 | The Sneezing Season | Allergy | ⭐⭐ |
| 9 | Storm in the Head | Migraine | ⭐⭐⭐ |
| 10 | Trembling Hands | Parkinson's | ⭐⭐⭐⭐ |
| 11 | Electric Storm | Epilepsy | ⭐⭐⭐ |
| 12 | Invisible Invaders | Bacterial UTI | ⭐⭐ |
| 13 | The Silent Killer Returns | Tuberculosis | ⭐⭐⭐⭐ |
| 14 | The Flu Season | Influenza | ⭐⭐⭐ |
| 15 | The Persistent Virus | HIV | ⭐⭐⭐⭐ |
| 16 | Pressure in the Eye | Glaucoma | ⭐⭐ |
| 17 | Shattered Reality | Schizophrenia | ⭐⭐⭐⭐ |
| 18 | The Painful Joint | Gout | ⭐⭐ |
| 19 | The Burning Stomach | GERD | ⭐⭐ |
| 20 | Bones That Break | Osteoporosis | ⭐⭐⭐ |

## 🏆 Leaderboard

The game includes a leaderboard system with **two storage modes**:

- **Local mode (default)** — Scores saved to `leaderboard.json`. Works offline.
- **Google Sheets mode (optional)** — Public global leaderboard.

To enable Google Sheets leaderboard:
1. Create a Google Sheet, share as "Anyone with the link can view"
2. On Streamlit Cloud → app settings → Secrets, add:
   ```toml
   GSHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR-SHEET-ID/edit"
   ```

## 🚀 Quick start (run locally)

```bash
git clone https://github.com/YOUR-USERNAME/docking-game.git
cd docking-game
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 🌐 Deploy to Streamlit Community Cloud (free)

1. **Push your code to GitHub** (see below)
2. Go to https://share.streamlit.io
3. Click **New app** → connect your GitHub
4. Select your repo, branch (`main`), and main file (`app.py`)
5. Click **Deploy** — live in 2 minutes

## 📦 Upload to GitHub

```bash
cd docking-game
git init
git add .
git commit -m "CSI Drug Discovery game with 20 cases + leaderboard"
git remote add origin https://github.com/YOUR-USERNAME/docking-game.git
git branch -M main
git push -u origin main
```

## 📂 Project structure

```
docking-game/
├── app.py              # Main Streamlit app (navigation, layout)
├── cases.py            # All 20 disease cases (data)
├── utils.py            # Game logic, stage rendering
├── leaderboard.py      # Leaderboard storage and UI
├── requirements.txt    # Python dependencies
├── leaderboard.json    # Auto-generated local leaderboard storage
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## ➕ Add your own cases

Open `cases.py` and append a new dictionary to the `CASES` list. Follow the structure of existing cases. Each case needs:

- `patient` — patient info
- `stage1_question` + `stage1_options` — target identification MCQ
- `target_protein`, `target_pdb`, `pocket_regions` — binding site
- `candidates` — 6 ligands (1 best, 1 alt, 1 weak, 3 decoys recommended)
- `off_target`, `off_target_pdb`, `selectivity_data` — selectivity stage
- `admet` — Lipinski properties for top candidates
- `ending` — story conclusion

## 🔬 Real docking only — no fake numbers

**This game shows ONLY real AutoDock Vina docking scores.** There are no estimated or placeholder values. If real scores aren't available for a case, the game tells you clearly and offers to compute them live, rather than displaying made-up numbers.

You have two ways to get real scores:

1. **Pre-compute (recommended):** Run `python precompute_docking.py` once. This docks every ligand with real Vina and saves results to `docking_results.json`. Players then see real scores instantly.

2. **Live docking:** If a case has no pre-computed scores, the game offers an "⚡ Run REAL docking now" option that runs Vina on the spot (~1-3 min for 3 ligands).

See `DOCKING_SETUP.md` for full details.

⚠️ **Note on score differences:** Vina scores depend on the grid box, structure preparation, exhaustiveness, and a random seed. Scores from this game's *blind docking* (whole-protein box) will differ from *active-site* docking done in other tools. This is expected — see DOCKING_SETUP.md for how to switch to active-site docking.


## 📜 License

MIT License — free to use, modify, and distribute for educational purposes.

## 🙏 Credits

- Streamlit team for the framework
- RCSB PDB for protein structures
- PubChem for ligand data
- py3Dmol for in-browser 3D visualization
