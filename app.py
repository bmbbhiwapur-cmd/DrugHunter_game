"""
Drug Hunter — Educational Game
Developed by Sarang Dhote, Shivaji Science College, Nagpur

Every interactive question uses st.form() — the most reliable
Streamlit pattern for multi-choice questions.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from cases import CASES

# ── Key compatibility helper ──────────────────────────────────────────────────
# Old cases.py used: stage1_question, stage1_options, pocket_regions
# New cases.py uses: question, options, pocket_options
# This function reads either format so both files work.

def _get(case, *keys, default=None):
    """Read the first key that exists in the case dict."""
    for k in keys:
        if k in case:
            return case[k]
    return default

def _q(case):
    return _get(case, "question", "stage1_question", default="")

def _opts(case):
    return _get(case, "options", "stage1_options", default=[])

def _pocket_opts(case):
    return _get(case, "pocket_options", "pocket_regions", default=[])

def _selectivity(case):
    return _get(case, "selectivity", "selectivity_data", default={})

def _admet(case):
    return _get(case, "admet", default={})

# ─────────────────────────────────────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Drug Hunter",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* layout */
.block-container { padding-top: 0.5rem !important; }

/* ── TOP BAR — prominent game name ──────────────────────── */
.dh-bar {
    background: linear-gradient(135deg, #0D1B2A 0%, #1A3A5C 100%);
    border-radius: 12px;
    padding: 14px 20px 12px;
    margin-bottom: 14px;
    border-left: 5px solid #1A7A6E;
}
.dh-top-row {
    display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
.dh-name-block { display: flex; flex-direction: column; gap: 2px; }
.dh-game-name {
    font-size: 1.6rem !important; font-weight: 800 !important;
    color: #FFFFFF !important; margin: 0 !important; line-height: 1.2;
    letter-spacing: 0.5px;
}
.dh-game-name span { color: #1DE9B6 !important; }
.dh-sub { font-size: .72rem; color: #90CAF9 !important; margin: 0; }
.dh-pill {
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    border-radius: 20px; padding: 5px 16px;
    font-size: .82rem; color: #fff !important; white-space: nowrap;
}
.dh-pill b { color: #FFD54F !important; font-size: .95rem; }

/* stepper */
.dh-step-row { display:flex; align-items:center; margin:14px 0 8px; }
.dh-circle   { width:28px; height:28px; border-radius:50%; display:flex;
               align-items:center; justify-content:center;
               font-size:.75rem; font-weight:700; flex-shrink:0; }
.done-c  { background:#1A7A6E; color:#fff; }
.now-c   { background:#1565C0; color:#fff;
           box-shadow:0 0 0 3px rgba(21,101,192,.25); }
.todo-c  { background:#E2E8F0; color:#94A3B8; }
.dh-lbl  { font-size:.6rem; text-align:center; margin-top:3px;
           color:#64748B; line-height:1.2; }
.now-lbl { color:#1565C0; font-weight:600; }
.done-lbl{ color:#1A7A6E; }
.dh-line { flex:1; height:3px; border-radius:2px; margin-bottom:16px; }
.done-ln { background:#1A7A6E; }
.todo-ln { background:#E2E8F0; }

/* feedback boxes */
.ok-box  { background:#e8f5e9 !important; color:#1b5e20 !important;
           border-left:4px solid #2e7d32;
           padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.ok-box *{ color:#1b5e20 !important; }
.err-box { background:#ffebee !important; color:#b71c1c !important;
           border-left:4px solid #c62828;
           padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.err-box *{ color:#b71c1c !important; }
.wrn-box { background:#fff8e1 !important; color:#e65100 !important;
           border-left:4px solid #f57f17;
           padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.wrn-box *{ color:#e65100 !important; }
.info-box{ background:#eef2ff !important; color:#1a1a2e !important;
           border-left:4px solid #5b6cff;
           padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.info-box *{ color:#1a1a2e !important; }

/* result card */
.fin-box { background:#eef2ff; color:#1a1a2e; border:2px solid #5b6cff;
           border-radius:12px; padding:1.5rem; text-align:center;
           margin-bottom:1rem; }

/* badge */
.badge { display:inline-block; background:#e3f2fd !important;
         color:#0d47a1 !important; padding:3px 10px;
         border-radius:12px; font-size:.82rem; margin:3px; }

/* mobile */
@media(max-width:600px){
    .dh-title { font-size:1.05rem; }
    .dh-circle{ width:22px; height:22px; font-size:.62rem; }
    .dh-lbl   { font-size:.55rem; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def _init():
    defs = dict(
        case_idx=0, stage=1, score=0, badges=[],
        s1_done=False, s1_ok=False, s1_msg="",
        s2_done=False, s2_ok=False, s2_msg="",
        s3_done=False, s3_results=None, s3_top=None,
        s4_done=False, s5_done=False, submitted=False,
    )
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

def _reset():
    keys = [k for k in st.session_state if k not in ("case_idx", "page")]
    for k in keys:
        del st.session_state[k]
    _init()

def _pts(n):
    st.session_state.score = max(0, st.session_state.score + n)

def _badge(b):
    if b not in st.session_state.badges:
        st.session_state.badges.append(b)

_init()
if "page" not in st.session_state:
    st.session_state.page = "play"

# ─────────────────────────────────────────────────────────────────────────────
# TOP BAR (always visible — mobile friendly)
# ─────────────────────────────────────────────────────────────────────────────

case = CASES[st.session_state.case_idx]
sc   = st.session_state.score
stg  = st.session_state.stage

st.markdown(f"""
<div class="dh-bar">
  <div class="dh-top-row">
    <div class="dh-name-block">
      <p class="dh-game-name">🧬 Drug<span>Hunter</span></p>
      <p class="dh-sub">By Sarang Dhote &nbsp;·&nbsp; Shivaji Science College, Nagpur</p>
    </div>
    <div class="dh-pill">Score: <b>{sc}</b> &nbsp;|&nbsp; Stage <b>{min(stg,5)}/5</b></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION (horizontal — visible on mobile too)
# ─────────────────────────────────────────────────────────────────────────────

nav = st.radio("", ["🎮 Play", "🏆 Leaderboard"],
               horizontal=True, key="nav_radio",
               label_visibility="collapsed")
page = "play" if "Play" in nav else "board"
if page != st.session_state.page:
    st.session_state.page = page
    st.rerun()

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD PAGE
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.page == "board":
    st.header("🏆 Leaderboard")
    import json, os
    from datetime import datetime

    LB_FILE = "leaderboard.json"

    def _load_lb():
        if os.path.exists(LB_FILE):
            try:
                return json.load(open(LB_FILE))
            except Exception:
                return []
        return []

    def _save_lb(rows):
        rows.sort(key=lambda x: x["score"], reverse=True)
        json.dump(rows[:200], open(LB_FILE,"w"), indent=2)

    rows = _load_lb()
    if not rows:
        st.info("No scores yet. Play a case to be first on the board!")
    else:
        df = pd.DataFrame(rows[:20])
        df.index = range(1, len(df)+1)
        st.dataframe(df[["player","case","score","date"]].rename(
            columns={"player":"Player","case":"Case",
                     "score":"Score","date":"Date"}
        ), use_container_width=True, hide_index=False)

    st.divider()
    st.subheader("Submit your score")
    with st.form("lb_form"):
        name = st.text_input("Your name", max_chars=30)
        sub  = st.form_submit_button("Submit my last score",
                                      type="primary",
                                      use_container_width=True)
    if sub and name.strip():
        rows = _load_lb()
        rows.append(dict(
            player=name.strip(),
            case=case["title"],
            score=st.session_state.score,
            date=datetime.now().strftime("%Y-%m-%d"),
        ))
        _save_lb(rows)
        st.success("Score saved!")
        st.rerun()

    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PLAY PAGE — CASE SELECTOR
# ─────────────────────────────────────────────────────────────────────────────

case_names = [f"Case {c['id']}: {c['title']}" for c in CASES]
new_idx = st.selectbox("📂 Select case", range(len(CASES)),
                       index=st.session_state.case_idx,
                       format_func=lambda i: case_names[i],
                       key="case_sel")
if new_idx != st.session_state.case_idx:
    st.session_state.case_idx = new_idx
    _reset()
    st.rerun()

case = CASES[st.session_state.case_idx]
st.caption(f"🏥 {case['disease']}  ·  {case['difficulty']}")

# ─────────────────────────────────────────────────────────────────────────────
# PROGRESS STEPPER
# ─────────────────────────────────────────────────────────────────────────────

labels = ["Identify Target","Find Pocket","Dock Ligands","Selectivity","ADMET"]
parts  = []
cur    = st.session_state.stage

for i, lbl in enumerate(labels):
    sn = i + 1
    if sn < cur:
        cc, lc, ic = "done-c",  "done-lbl",  "✓"
    elif sn == cur:
        cc, lc, ic = "now-c",   "now-lbl",   str(sn)
    else:
        cc, lc, ic = "todo-c",  "dh-lbl",    str(sn)
    if i > 0:
        ln = "done-ln" if sn <= cur else "todo-ln"
        parts.append(f'<div class="dh-line {ln}"></div>')
    parts.append(f"""
    <div style="display:flex;flex-direction:column;align-items:center;flex:1;">
      <div class="dh-circle {cc}">{ic}</div>
      <div class="dh-lbl {lc}" style="max-width:52px">{lbl.replace(" ","<br>",1)}</div>
    </div>""")

st.markdown(
    f'<div class="dh-step-row">{"".join(parts)}</div>',
    unsafe_allow_html=True
)
st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1 — IDENTIFY TARGET
# ─────────────────────────────────────────────────────────────────────────────

if cur == 1:
    st.subheader("Stage 1 — Identify the target")

    # ── Case summary card ─────────────────────────────────────────────────
    target_class = {
        "COX-2": "Enzyme (Cyclooxygenase)",
        "ACE": "Enzyme (Metallopeptidase)",
        "AChE": "Enzyme (Hydrolase)",
        "PDE5": "Enzyme (Phosphodiesterase)",
        "Pf-DHFR": "Enzyme (Reductase)",
        "β2-adrenergic receptor": "GPCR (Receptor)",
        "SERT": "Transporter (SLC family)",
        "Histamine H1 receptor": "GPCR (Receptor)",
        "5-HT1B receptor": "GPCR (Receptor)",
        "MAO-B": "Enzyme (Oxidoreductase)",
        "Nav1.2 (Na+ channel)": "Ion Channel",
        "Bacterial DNA gyrase": "Enzyme (Topoisomerase)",
        "InhA": "Enzyme (Reductase)",
        "Neuraminidase": "Enzyme (Glycosidase)",
        "HIV-1 Reverse Transcriptase": "Enzyme (Polymerase)",
        "Carbonic Anhydrase II": "Enzyme (Lyase)",
        "Dopamine D2 receptor": "GPCR (Receptor)",
        "Xanthine Oxidase": "Enzyme (Oxidoreductase)",
        "H+/K+ ATPase": "Enzyme (ATPase)",
        "FPPS": "Enzyme (Transferase)",
    }.get(case.get("target_protein",""), "Molecular target")

    pdb = case.get("target_pdb","")
    off = case.get("off_target","")
    off_pdb = case.get("off_target_pdb","")
    best = next((c for c in case.get("candidates",[]) if c.get("kind")=="best"), None)
    drug_name = best["name"] if best else "unknown"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0D1B2A,#1A3A5C);
                border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:1rem;
                border-left:4px solid #1DE9B6;">
      <div style="color:#1DE9B6;font-size:.75rem;font-weight:600;
                  letter-spacing:1px;margin-bottom:8px;">📋 CASE SUMMARY</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">DISEASE</div>
          <div style="color:#fff;font-size:.9rem;font-weight:600;">{case['disease']}</div>
        </div>
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">TARGET PROTEIN</div>
          <div style="color:#fff;font-size:.9rem;font-weight:600;">{case.get('target_protein','')}</div>
          <div style="color:#90CAF9;font-size:.65rem;">{target_class} · PDB: {pdb}</div>
        </div>
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">KEY DRUG</div>
          <div style="color:#1DE9B6;font-size:.9rem;font-weight:600;">{drug_name}</div>
        </div>
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">OFF-TARGET (side effect)</div>
          <div style="color:#FFD54F;font-size:.9rem;font-weight:600;">{off}</div>
          <div style="color:#90CAF9;font-size:.65rem;">PDB: {off_pdb}</div>
        </div>
      </div>
      <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.1);">
        <div style="color:#90CAF9;font-size:.68rem;margin-bottom:4px;">🎯 WHAT YOU WILL LEARN</div>
        <div style="color:#E0E0E0;font-size:.82rem;line-height:1.6;">
          Identify the molecular target → locate the binding pocket in 3D →
          dock candidate ligands using real AutoDock Vina → test selectivity
          (target vs {off}) → check drug-likeness (Lipinski's Rule of Five).
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Patient card
    p = case["patient"]
    st.markdown(f"""
    <div class="info-box">
        <b>🏥 Patient: {p['name']}</b>, {p['age']} y/o {p['gender']}<br>
        <b>Condition:</b> {p['condition']}<br>
        <b>History:</b> {p['history']}
    </div>""", unsafe_allow_html=True)

    if not st.session_state.s1_done:
        with st.form("form_s1"):
            st.markdown(f"**{_q(case)}**")
            choice = st.radio(
                "Select your answer:",
                [o["text"] for o in _opts(case)],
                key="s1_radio",
                label_visibility="collapsed",
            )
            ok = st.form_submit_button(
                "✅  Submit answer",
                type="primary",
                use_container_width=True,
            )
        if ok:
            opt = next(o for o in _opts(case) if o["text"] == choice)
            st.session_state.s1_ok  = opt["correct"]
            st.session_state.s1_msg = opt["feedback"]
            st.session_state.s1_done = True
            if opt["correct"]:
                _pts(20); _badge("🧠 Target Tracker")
            else:
                _pts(-10)
            st.rerun()
    else:
        if st.session_state.s1_ok:
            st.markdown(
                f'<div class="ok-box"><b>✅ Correct! +20 pts</b><br>'
                f'{st.session_state.s1_msg}</div>',
                unsafe_allow_html=True
            )
            if st.button("Continue to Stage 2 →", type="primary",
                         use_container_width=True):
                st.session_state.stage = 2
                st.rerun()
        else:
            st.markdown(
                f'<div class="err-box"><b>❌ Not quite. −10 pts</b><br>'
                f'{st.session_state.s1_msg}</div>',
                unsafe_allow_html=True
            )
            if st.button("🔄 Try again", use_container_width=True):
                st.session_state.s1_done = False
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2 — FIND POCKET
# ─────────────────────────────────────────────────────────────────────────────

elif cur == 2:
    st.subheader("Stage 2 — Find the binding pocket")
    pdb = case["target_pdb"]
    st.markdown(
        f"Target: **{case['target_protein']}** &nbsp;"
        f"([PDB {pdb}](https://www.rcsb.org/structure/{pdb}))"
    )

    # 3D viewer
    try:
        import py3Dmol
        v = py3Dmol.view(query=f"pdb:{pdb}", width=600, height=340)
        v.setStyle({"cartoon": {"color": "spectrum"}})
        v.zoomTo()
        st.components.v1.html(v._make_html(), height=360)
    except Exception:
        st.info(f"💡 View 3D at [rcsb.org/structure/{pdb}](https://www.rcsb.org/structure/{pdb})")

    if not st.session_state.s2_done:
        with st.form("form_s2"):
            st.markdown("**Which region is the drug binding pocket?**")
            choice = st.radio(
                "Select region:",
                [o["text"] for o in _pocket_opts(case)],
                key="s2_radio",
                label_visibility="collapsed",
            )
            ok = st.form_submit_button(
                "✅  Submit answer",
                type="primary",
                use_container_width=True,
            )
        if ok:
            opt = next(o for o in _pocket_opts(case) if o["text"] == choice)
            st.session_state.s2_ok  = opt["correct"]
            st.session_state.s2_msg = opt["feedback"]
            st.session_state.s2_done = True
            if opt["correct"]:
                _pts(20); _badge("🎯 Pocket Finder")
            else:
                _pts(-10)
            st.rerun()
    else:
        if st.session_state.s2_ok:
            st.markdown(
                f'<div class="ok-box"><b>✅ Correct! +20 pts</b><br>'
                f'{st.session_state.s2_msg}</div>',
                unsafe_allow_html=True
            )
            if st.button("Continue to Stage 3 →", type="primary",
                         use_container_width=True):
                st.session_state.stage = 3
                st.rerun()
        else:
            st.markdown(
                f'<div class="err-box"><b>❌ Incorrect. −10 pts</b><br>'
                f'{st.session_state.s2_msg}</div>',
                unsafe_allow_html=True
            )
            if st.button("🔄 Try again", use_container_width=True,
                         key="s2_retry"):
                st.session_state.s2_done = False
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 3 — DOCKING
# ─────────────────────────────────────────────────────────────────────────────

elif cur == 3:
    st.subheader("Stage 3 — Choose & dock candidate ligands")
    st.markdown("Pick **exactly 3** candidates to dock against the target.")

    # Check for real scores
    def _get_score(cid, name, ptype="target"):
        import json, os
        f = "docking_results.json"
        if os.path.exists(f):
            d = json.load(open(f))
            return d.get(f"{cid}_{name}_{ptype}")
        return None

    def _has_scores(cid):
        import json, os
        f = "docking_results.json"
        if not os.path.exists(f):
            return False
        d = json.load(open(f))
        return any(k.startswith(f"{cid}_") for k in d)

    has_real = _has_scores(case["id"])

    if not st.session_state.s3_done:
        picked = []
        for i, c in enumerate(case["candidates"]):
            col1, col2 = st.columns([1, 9])
            with col1:
                chk = st.checkbox("", key=f"chk_{i}",
                                   label_visibility="collapsed")
            with col2:
                kind_color = {
                    "best": "🟢", "alt": "🔵",
                    "weak": "🟡", "decoy": "⚫"
                }.get(c["kind"], "")
                st.markdown(f"**{c['name']}** {kind_color} — _{c['desc']}_")
            if chk:
                picked.append(i)

        st.caption(f"Selected: {len(picked)} / 3")

        if has_real:
            st.info("🟢 Pre-computed real Vina scores available for this case.")
        else:
            st.warning(
                "⚠️ No real docking scores yet for this case.\n\n"
                "**To generate real scores:** Run `precompute_docking.py` "
                "locally (needs `pip install vina rdkit`) then push "
                "`docking_results.json` to your repo.\n\n"
                "You can still proceed — the game will use ranking by "
                "drug class to teach selectivity principles."
            )

        if st.button("🔬 Run docking",
                     type="primary",
                     disabled=(len(picked) != 3),
                     use_container_width=True):
            chosen = [case["candidates"][i] for i in picked]

            if has_real:
                for c in chosen:
                    c["_score"] = _get_score(case["id"], c["name"], "target")
                results = sorted(
                    [c for c in chosen if c.get("_score") is not None],
                    key=lambda x: x["_score"]
                )
                if not results:
                    st.error("Scores found but could not read. Check docking_results.json.")
                    st.stop()
            else:
                # Educational fallback: rank by kind (best > alt > weak > decoy)
                order = {"best": 0, "alt": 1, "weak": 2, "decoy": 3}
                # Assign representative scores for display
                score_map = {"best": -9.5, "alt": -8.8, "weak": -7.0, "decoy": -4.5}
                for c in chosen:
                    c["_score"] = score_map.get(c["kind"], -5.0)
                results = sorted(chosen, key=lambda x: order.get(x["kind"], 9))

            top = results[0]
            st.session_state.s3_results = results
            st.session_state.s3_top     = top
            st.session_state.s3_done    = True

            if top["kind"] == "best":
                _pts(25); _badge("💊 Drug Hunter")
            elif top["kind"] == "alt":
                _pts(15)
            elif top["kind"] == "weak":
                _pts(-15)
            else:
                _pts(-20)
            st.rerun()

    else:
        results = st.session_state.s3_results
        top     = st.session_state.s3_top

        lbl = "🟢 Real AutoDock Vina scores." if has_real else "🟡 Illustrative scores (run precompute_docking.py for real values)."
        st.caption(lbl)

        names  = [r["name"] for r in results]
        scores = [r["_score"] for r in results]
        colors = ["#1A7A6E" if r["kind"] in ("best","alt")
                  else "#888" if r["kind"] == "decoy"
                  else "#E8A020" for r in results]

        fig = go.Figure(go.Bar(
            x=names, y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition="outside",
        ))
        fig.update_layout(
            title="Binding affinity (kcal/mol) — more negative = stronger",
            yaxis_title="kcal/mol", height=300,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        can_go = top["name"] in _selectivity(case)

        if top["kind"] in ("best", "alt") and can_go:
            st.markdown(
                f'<div class="ok-box"><b>✅ Best binder: {top["name"]}</b><br>'
                f'Good binding to {case["target_protein"]}. Now check selectivity.</div>',
                unsafe_allow_html=True
            )
            if st.button("Continue to Stage 4 →", type="primary",
                         use_container_width=True):
                st.session_state.stage = 4
                st.rerun()
        else:
            msg = ("Weak binding — try stronger candidates."
                   if top["kind"] == "weak"
                   else "Top pick is a decoy — check the descriptions.")
            st.markdown(
                f'<div class="err-box"><b>❌ {msg}</b></div>',
                unsafe_allow_html=True
            )
            if st.button("🔄 Try again", use_container_width=True,
                         key="s3_retry"):
                st.session_state.s3_done = False
                for i in range(6):
                    st.session_state.pop(f"chk_{i}", None)
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 4 — SELECTIVITY
# ─────────────────────────────────────────────────────────────────────────────

elif cur == 4:
    st.subheader("Stage 4 — Selectivity test ⚠️")

    top = st.session_state.s3_top
    if not top:
        st.error("No lead selected. Please go back.")
        if st.button("← Back to Stage 3"):
            st.session_state.stage = 3
            st.session_state.s3_done = False
            st.rerun()
        st.stop()

    sel = _selectivity(case).get(top["name"])
    if not sel:
        st.warning("No selectivity data for this candidate.")
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.stage = 5
            st.rerun()
        st.stop()

    st.markdown(
        f"We now dock **{top['name']}** against the off-target "
        f"**{case['off_target']}** (PDB: `{case['off_target_pdb']}`).\n\n"
        f"A good drug binds tightly to the target but weakly to the off-target."
    )

    # Try real scores
    def _get_score(cid, name, ptype="target"):
        import json, os
        f = "docking_results.json"
        if os.path.exists(f):
            d = json.load(open(f))
            return d.get(f"{cid}_{name}_{ptype}")
        return None

    t_score = _get_score(case["id"], top["name"], "target")
    o_score = _get_score(case["id"], top["name"], "off_target")

    if t_score is not None and o_score is not None:
        st.caption("🟢 Real AutoDock Vina scores.")
        c1, c2 = st.columns(2)
        c1.metric(f"Target ({case['target_protein']})",
                  f"{t_score:.2f} kcal/mol", "Strong ✓")
        c2.metric(f"Off-target ({case['off_target']})",
                  f"{o_score:.2f} kcal/mol",
                  "Weak ✓" if (t_score < o_score - 0.5) else "Too strong ✗",
                  delta_color="normal" if (t_score < o_score - 0.5) else "inverse")
        st.metric("Selectivity ratio (off/target)",
                  round(o_score / t_score, 2))
        is_sel = (t_score < o_score - 0.5)
    else:
        st.info("🟡 No real scores yet — using pedagogical selectivity data.")
        is_sel = sel.get("pass", True)

    if not st.session_state.s4_done:
        if is_sel:
            st.markdown(
                f'<div class="ok-box"><b>✅ Selectivity confirmed! +30 pts</b>'
                f'<br>{sel["msg"]}</div>',
                unsafe_allow_html=True
            )
            _pts(30); _badge("⚖️ Selectivity Sage")
        else:
            st.markdown(
                f'<div class="err-box"><b>❌ Poor selectivity.</b>'
                f'<br>{sel["msg"]}</div>',
                unsafe_allow_html=True
            )
        st.session_state.s4_done = True

    if st.button("Continue to Stage 5 →", type="primary",
                 use_container_width=True):
        st.session_state.stage = 5
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 5 — ADMET
# ─────────────────────────────────────────────────────────────────────────────

elif cur == 5:
    st.subheader("Stage 5 — ADMET & drug-likeness")

    top   = st.session_state.s3_top
    admet = _admet(case).get(top["name"] if top else "", {}) if top else {}

    if not admet:
        st.warning("No ADMET data for this candidate.")
        if st.button("See results →", type="primary", use_container_width=True):
            st.session_state.stage = 6
            st.rerun()
        st.stop()

    st.markdown(f"Checking **{top['name']}** against Lipinski's Rule of Five:")

    rules = [
        ("Molecular weight", admet["MW"],      "< 500 Da",  admet["MW"] < 500),
        ("LogP",             admet["LogP"],     "−0.5 to 5", -0.5 <= admet["LogP"] <= 5),
        ("H-bond donors",    admet["HBD"],      "≤ 5",       admet["HBD"] <= 5),
        ("H-bond acceptors", admet["HBA"],      "≤ 10",      admet["HBA"] <= 10),
        ("Rotatable bonds",  admet["RotBonds"], "≤ 10",      admet["RotBonds"] <= 10),
    ]
    df = pd.DataFrame([
        {"Property": n, "Value": v, "Ideal": i, "Pass": "✅" if p else "❌"}
        for n, v, i, p in rules
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not st.session_state.s5_done:
        admet_ok = admet.get("ok") or admet.get("pass", False)
        if admet_ok:
            _pts(15); _badge("💎 Lipinski Compliant")
        if admet.get("warning"):
            st.markdown(
                f'<div class="wrn-box"><b>Post-market alert</b>'
                f'<br>{admet["warning"]}</div>',
                unsafe_allow_html=True
            )
        st.session_state.s5_done = True

    if st.button("See final results →", type="primary",
                 use_container_width=True):
        st.session_state.stage = 6
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 6 — FINAL RESULT + FULL CASE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

else:
    sc  = st.session_state.score
    top = st.session_state.s3_top

    if sc >= 90:   icon, rank = "🥇", "Master Medicinal Chemist"
    elif sc >= 70: icon, rank = "🥈", "Drug Designer"
    elif sc >= 50: icon, rank = "🥉", "Junior Chemist"
    else:          icon, rank = "📚", "Back to the Textbooks"

    # ── Score card ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="fin-box">
        <div style="font-size:3rem;">{icon}</div>
        <div style="font-size:1.4rem;font-weight:600;">{rank}</div>
        <div style="font-size:2.2rem;font-weight:700;
                    font-family:monospace;margin-top:.4rem;">{sc} / 100</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"_{case['ending']}_")

    if st.session_state.badges:
        st.markdown("**Badges earned:**")
        st.markdown(
            " ".join(f'<span class="badge">{b}</span>'
                     for b in st.session_state.badges),
            unsafe_allow_html=True
        )

    st.divider()

    # ── FULL CASE SUMMARY ─────────────────────────────────────────────────
    st.subheader("📚 Case Summary — What you learned")

    target   = case.get("target_protein","")
    pdb      = case.get("target_pdb","")
    off      = case.get("off_target","")
    off_pdb  = case.get("off_target_pdb","")
    best_cand = next((c for c in case.get("candidates",[]) if c.get("kind")=="best"), None)
    alt_cand  = next((c for c in case.get("candidates",[]) if c.get("kind")=="alt"),  None)

    # ── 1. Disease & Target overview ──────────────────────────────────────
    st.markdown("#### 🦠 Disease & Molecular Target")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="info-box">
            <b>Disease</b><br>{case['disease']}<br><br>
            <b>Target protein</b><br>{target}<br>
            <span style="font-size:.8rem;color:#475569;">PDB: {pdb}</span><br><br>
            <b>Difficulty</b><br>{case['difficulty']}
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="wrn-box">
            <b>Off-target (side effect source)</b><br>{off}<br>
            <span style="font-size:.8rem;">PDB: {off_pdb}</span><br><br>
            <b>Why selectivity matters</b><br>
            <span style="font-size:.85rem;">
            The drug must bind <b>strongly</b> to {target}
            but <b>weakly</b> to {off}.
            If both are inhibited equally, side effects appear.
            </span>
        </div>""", unsafe_allow_html=True)

    # ── 2. Protein 3D viewer ──────────────────────────────────────────────
    st.markdown("#### 🔬 Target Protein Structure")
    st.caption(f"{target} · PDB: {pdb} · Rotate with mouse, scroll to zoom")

    try:
        import py3Dmol
        view = py3Dmol.view(query=f"pdb:{pdb}", width=680, height=380)
        view.setStyle({}, {"cartoon": {"color": "spectrum"}})
        # Show surface of the binding site in a translucent style
        view.addSurface(
            py3Dmol.VDW,
            {"opacity": 0.6, "color": "white"},
            {"hetflag": True}
        )
        view.setStyle({"hetflag": True},
                      {"stick": {"colorscheme": "greenCarbon", "radius": 0.3}})
        view.zoomTo()
        view.spin(False)
        st.components.v1.html(view._make_html(), height=400)
        st.caption(
            "🟢 Green sticks = co-crystallised ligand (defines the binding pocket). "
            "White surface = Van der Waals surface of pocket."
        )
    except Exception:
        st.info(
            f"💡 View the 3D structure at "
            f"[rcsb.org/structure/{pdb}](https://www.rcsb.org/structure/{pdb}) "
            f"and [rcsb.org/structure/{off_pdb}](https://www.rcsb.org/structure/{off_pdb})"
        )

    # ── 3. Drug comparison table ──────────────────────────────────────────
    st.markdown("#### 💊 Drug Candidates — Comparison")

    rows = []
    for cand in case.get("candidates", []):
        kind_label = {
            "best": "⭐ Best (selective)",
            "alt":  "🔵 Alternative",
            "weak": "🟡 Weak binder",
            "decoy":"⚫ Decoy",
        }.get(cand.get("kind",""), cand.get("kind",""))

        admet_data = _admet(case).get(cand["name"], {})
        admet_ok   = admet_data.get("ok") or admet_data.get("pass", "—")

        sel_data   = _selectivity(case).get(cand["name"], {})
        selective  = ("✅ Yes" if sel_data.get("pass") else "❌ No") if sel_data else "—"

        rows.append({
            "Drug":       cand["name"],
            "Role":       kind_label,
            "Description":cand["desc"],
            "Selective?": selective,
            "Lipinski OK":("✅" if admet_ok else "❌") if admet_data else "—",
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True
    )

    # ── 4. Binding affinity chart ─────────────────────────────────────────
    st.markdown("#### 📊 Binding Affinity — Target vs Off-target")

    def _get_score(cid, name, ptype="target"):
        import json, os
        f = "docking_results.json"
        if os.path.exists(f):
            try:
                d = json.load(open(f))
                return d.get(f"{cid}_{name}_{ptype}")
            except Exception:
                return None
        return None

    score_map   = {"best": -9.5, "alt": -8.8, "weak": -7.0, "decoy": -4.5}
    cand_names  = [c["name"] for c in case.get("candidates",[])]
    t_scores    = []
    o_scores    = []
    has_real    = False

    for cand in case.get("candidates",[]):
        rs = _get_score(case["id"], cand["name"], "target")
        if rs is not None:
            t_scores.append(rs); has_real = True
        else:
            t_scores.append(score_map.get(cand.get("kind","decoy"), -4.5))
        ro = _get_score(case["id"], cand["name"], "off_target")
        if ro is not None:
            o_scores.append(ro)
        else:
            # Estimate off-target as weaker than target for best/alt
            base = t_scores[-1]
            o_scores.append(base + (2.5 if cand.get("kind") in ("best","alt") else 0.5))

    colors_t = ["#1A7A6E" if c.get("kind") in ("best","alt")
                else "#E8A020" if c.get("kind") == "weak"
                else "#9E9E9E"
                for c in case.get("candidates",[])]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="vs Target (want: low)",
        x=cand_names, y=t_scores,
        marker_color=colors_t,
        text=[f"{s:.1f}" for s in t_scores],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="vs Off-target (want: high)",
        x=cand_names, y=o_scores,
        marker_color=["rgba(255,200,0,0.5)"] * len(o_scores),
        text=[f"{s:.1f}" for s in o_scores],
        textposition="outside",
        marker_line=dict(color="gold", width=1.5),
    ))
    fig.update_layout(
        barmode="group",
        title=f"Binding affinity (kcal/mol) — {'Real Vina scores' if has_real else 'Illustrative — run precompute_docking.py for real scores'}",
        yaxis_title="Binding affinity (kcal/mol)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Green bars = target affinity (more negative = stronger binding = better drug). "
        "Yellow bars = off-target affinity (should be less negative = weaker = safer)."
    )

    # ── 5. ADMET radar for the best drug ─────────────────────────────────
    if best_cand:
        admet_best = _admet(case).get(best_cand["name"], {})
        if admet_best:
            st.markdown(f"#### ⚗️ Drug Properties — {best_cand['name']}")

            radar_vals   = [
                min(1.0, 500 / max(admet_best.get("MW", 500), 1)),
                min(1.0, max(0, (5 - admet_best.get("LogP", 5)) / 5.5)),
                min(1.0, (5 - admet_best.get("HBD", 5)) / 5),
                min(1.0, (10 - admet_best.get("HBA", 10)) / 10),
                min(1.0, (10 - admet_best.get("RotBonds", 10)) / 10),
            ]
            radar_vals = [max(0, v) for v in radar_vals]
            radar_labels = ["MW<br><500", "LogP<br>1-3", "HBD<br>≤5", "HBA<br>≤10", "RotBonds<br>≤10"]

            fig2 = go.Figure(go.Scatterpolar(
                r=radar_vals + [radar_vals[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                fillcolor="rgba(26,122,110,0.3)",
                line=dict(color="#1A7A6E", width=2),
                name=best_cand["name"],
            ))
            fig2.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                title=f"{best_cand['name']} — Lipinski Drug-likeness Radar",
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            c1, c2 = st.columns([3, 2])
            with c1:
                st.plotly_chart(fig2, use_container_width=True)
            with c2:
                st.markdown(f"""
                <div class="info-box" style="margin-top:1rem;">
                    <b>MW:</b> {admet_best.get('MW','—')} Da<br>
                    <b>LogP:</b> {admet_best.get('LogP','—')}<br>
                    <b>H-bond donors:</b> {admet_best.get('HBD','—')}<br>
                    <b>H-bond acceptors:</b> {admet_best.get('HBA','—')}<br>
                    <b>Rotatable bonds:</b> {admet_best.get('RotBonds','—')}<br><br>
                    <b>Lipinski:</b>
                    {'✅ Compliant' if (admet_best.get('ok') or admet_best.get('pass')) else '⚠️ Exceptions'}<br><br>
                    {f'<span style="color:#e65100">{admet_best.get("warning","")}</span>' if admet_best.get('warning') else ''}
                </div>""", unsafe_allow_html=True)

    # ── 6. Key learning points ────────────────────────────────────────────
    st.markdown("#### 🎓 Key Learning Points")

    sel_msg = ""
    if best_cand:
        sel_data = _selectivity(case).get(best_cand["name"], {})
        sel_msg  = sel_data.get("msg","") if sel_data else ""

    st.markdown(f"""
    <div style="background:#F0FDF4;border-left:4px solid #16A34A;
                border-radius:8px;padding:1rem 1.2rem;color:#14532D;">
    <ol style="margin:0;padding-left:1.2rem;line-height:2;">
        <li><b>Target:</b> {target} is the key enzyme/receptor in <b>{case['disease']}</b>.</li>
        <li><b>Binding site:</b> The drug binds in a specific pocket — identified using the PDB structure ({pdb}).</li>
        <li><b>Best drug:</b> <b>{best_cand['name'] if best_cand else 'N/A'}</b> shows the strongest and most selective binding.</li>
        <li><b>Selectivity:</b> {sel_msg if sel_msg else f'The drug must be selective for {target} over {off} to avoid side effects.'}</li>
        <li><b>Drug-likeness:</b> Lipinski's Rule of Five filters out molecules that are unlikely to be orally bioavailable.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#EFF6FF;border-left:4px solid #3B82F6;
                border-radius:8px;padding:.8rem 1.2rem;margin-top:.75rem;color:#1E3A5F;font-size:.85rem;">
    📖 <b>Further reading:</b> Search PubChem for {best_cand['name'] if best_cand else 'the drug'} ·
    View the 3D complex at <a href="https://www.rcsb.org/structure/{pdb}" target="_blank">RCSB PDB {pdb}</a> ·
    Explore off-target at <a href="https://www.rcsb.org/structure/{off_pdb}" target="_blank">RCSB PDB {off_pdb}</a>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Replay this case", use_container_width=True):
            _reset()
            st.rerun()
    with col2:
        if st.button("▶ Next case", type="primary", use_container_width=True):
            next_idx = (st.session_state.case_idx + 1) % len(CASES)
            st.session_state.case_idx = next_idx
            _reset()
            st.rerun()
