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

/* top bar */
.dh-bar {
    background: linear-gradient(135deg, #0D1B2A, #1A3A5C);
    border-radius: 10px; padding: 10px 16px 8px;
    display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap;
    gap: 6px; margin-bottom: 12px;
}
.dh-title  { font-size:1.3rem; font-weight:700; color:#fff !important; margin:0; }
.dh-sub    { font-size:.7rem;  color:#90CAF9 !important; margin:0; }
.dh-pill   { background:rgba(255,255,255,.15); border-radius:20px;
             padding:4px 14px; font-size:.82rem; color:#fff !important; }
.dh-pill b { color:#FFD54F !important; }

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
  <div>
    <p class="dh-title">🧬 Drug Hunter</p>
    <p class="dh-sub">By Sarang Dhote &nbsp;·&nbsp; Shivaji Science College, Nagpur</p>
  </div>
  <div class="dh-pill">Score: <b>{sc}</b> &nbsp;|&nbsp; Stage <b>{min(stg,5)}/5</b></div>
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
            st.markdown(f"**{case['question']}**")
            choice = st.radio(
                "Select your answer:",
                [o["text"] for o in case["options"]],
                key="s1_radio",
                label_visibility="collapsed",
            )
            ok = st.form_submit_button(
                "✅  Submit answer",
                type="primary",
                use_container_width=True,
            )
        if ok:
            # find selected option
            opt = next(o for o in case["options"] if o["text"] == choice)
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
                [o["text"] for o in case["pocket_options"]],
                key="s2_radio",
                label_visibility="collapsed",
            )
            ok = st.form_submit_button(
                "✅  Submit answer",
                type="primary",
                use_container_width=True,
            )
        if ok:
            opt = next(o for o in case["pocket_options"] if o["text"] == choice)
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

        can_go = top["name"] in case.get("selectivity", {})

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

    sel = case.get("selectivity", {}).get(top["name"])
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
    admet = case.get("admet", {}).get(top["name"] if top else "", {}) if top else {}

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
        if admet.get("ok"):
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
# STAGE 6 — FINAL RESULT
# ─────────────────────────────────────────────────────────────────────────────

else:
    sc = st.session_state.score

    if sc >= 90:   icon, rank = "🥇", "Master Medicinal Chemist"
    elif sc >= 70: icon, rank = "🥈", "Drug Designer"
    elif sc >= 50: icon, rank = "🥉", "Junior Chemist"
    else:          icon, rank = "📚", "Back to the Textbooks"

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
