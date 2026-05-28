# Drug Hunter — Deployment Checklist

## Files that MUST be in your GitHub repo

Make sure ALL these files are pushed before deploying.
If any file is missing or outdated, Streamlit Cloud will crash.

```
drug-hunter/
├── app.py                  ← Updated (new top bar + mobile nav)
├── utils.py                ← Updated (new show_top_bar, show_progress_stepper)
├── cases.py                ← Drug Hunter case data
├── docking.py              ← Real AutoDock Vina engine
├── leaderboard.py          ← Google Sheets / local leaderboard
├── precompute_docking.py   ← Run locally to pre-compute scores
├── requirements.txt        ← Python packages (must include vina)
├── packages.txt            ← System packages for Streamlit Cloud
└── README.md
```

## Quick GitHub push (all files at once)

```bash
cd your-drug-hunter-folder
git add .
git commit -m "Mobile fix + Drug Hunter branding"
git push
```

## requirements.txt must contain:
```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
numpy>=1.24.0
rdkit>=2023.9.1
vina>=1.2.3
py3Dmol>=2.0.4
```

## packages.txt must contain:
```
libxrender1
libxtst6
```
(These are system libraries needed by rdkit/vina on Linux)

## If Streamlit Cloud still crashes:

1. Click "Manage App" (bottom right corner of the app page)
2. Click the terminal tab
3. Copy the red error text
4. Send it — I will fix it immediately

## Common errors and fixes:

| Error in terminal | Fix |
|---|---|
| `ImportError: cannot import name 'show_top_bar'` | Push the latest utils.py |
| `ModuleNotFoundError: No module named 'vina'` | Check requirements.txt has `vina>=1.2.3` |
| `ModuleNotFoundError: No module named 'rdkit'` | Check requirements.txt has `rdkit>=2023.9.1` |
| `ImportError: libXrender.so.1: cannot open` | Check packages.txt has `libxrender1` |
| `No module named 'py3Dmol'` | Check requirements.txt has `py3Dmol>=2.0.4` |
