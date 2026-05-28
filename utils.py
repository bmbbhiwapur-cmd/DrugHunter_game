"""
Drug Hunter — Game logic & UI
Developed by Sarang Dhote, Shivaji Science College, Nagpur
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Docking is OPTIONAL — imported lazily inside functions only
# This file NEVER crashes on import even if vina/rdkit are absent

STAGE_LABELS = [
    "Identify\nTarget",
    "Find\nPocket",
    "Dock\nLigands",
    "Selectivity",
    "ADMET",
]


# ── Session state ─────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "case_index":      0,
        "current_stage":   1,
        "score":           0,
        "stage1_answered": False,
        "stage2_answered": False,
        "stage3_picks":    [],
        "stage3_top_pick": None,
        "stage3_done":     False,
        "stage4_done":     False,
        "stage5_done":     False,
        "badges":          [],
        "score_submitted": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_game():
    for k in ["current_stage","score","stage1_answered","stage2_answered",
              "stage3_picks","stage3_top_pick","stage3_done",
              "stage4_done","stage5_done","badges","score_submitted"]:
        st.session_state.pop(k, None)
    init_session_state()


def add_score(pts):
    st.session_state.score = max(0, st.session_state.score + pts)


def add_badge(b):
    if b not in st.session_state.badges:
        st.session_state.badges.append(b)


# ── Top bar (always visible — shows on mobile) ────────────────────────────────

def show_top_bar(case, page):
    score = st.session_state.score
    stage = st.session_state.current_stage
    if page == "🎮 Play":
        right = (f'<span class="dh-score-pill">'
                 f'Score: <b>{score}</b> &nbsp;|&nbsp; '
                 f'Stage <b>{min(stage,5)}/5</b></span>')
    else:
        right = '<span class="dh-score-pill">Drug Hunter</span>'

    st.markdown(f"""
    <div class="dh-topbar">
        <div>
            <p class="dh-title">🧬 Drug Hunter</p>
            <p class="dh-subtitle">
                By Sarang Dhote &nbsp;·&nbsp; Shivaji Science College, Nagpur
            </p>
        </div>
        {right}
    </div>
    """, unsafe_allow_html=True)


# ── Progress stepper (pure HTML — works on all screen sizes) ──────────────────

def show_progress_stepper():
    current = st.session_state.current_stage
    parts   = []
    for i, label in enumerate(STAGE_LABELS):
        step = i + 1
        if step < current:
            cc, lc, icon = "done",   "done-lbl",   "✓"
        elif step == current:
            cc, lc, icon = "active", "active-lbl", str(step)
        else:
            cc, lc, icon = "todo",   "",           str(step)

        if i > 0:
            conn = "done" if step <= current else "todo"
            parts.append(f'<div class="dh-connector {conn}"></div>')

        lbl_html = label.replace("\n", "<br>")
        parts.append(f"""
        <div class="dh-step">
            <div class="dh-step-circle {cc}">{icon}</div>
            <div class="dh-step-label {lc}">{lbl_html}</div>
        </div>""")

    st.markdown(f'<div class="dh-stepper">{"".join(parts)}</div>',
                unsafe_allow_html=True)


# kept for backward compat
def show_header(case):
    st.markdown(f"### Case #{case['id']}: {case['title']}")

def show_progress_bar():
    show_progress_stepper()


# ── Stage 1: Target identification ────────────────────────────────────────────

def show_stage_1(case):
    st.subheader("Stage 1 — Identify the target")

    p = case["patient"]
    st.markdown(f"""
    <div class="case-card">
        <b>🏥 Patient Briefing</b><br>
        <b>Name:</b> {p['name']} &nbsp;|&nbsp;
        <b>Age:</b> {p['age']} &nbsp;|&nbsp;
        <b>Gender:</b> {p['gender']}<br>
        <b>Condition:</b> {p['condition']}<br>
        <b>History:</b> {p['history']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**{case['stage1_question']}**")

    if not st.session_state.stage1_answered:
        for i, opt in enumerate(case["stage1_options"]):
            if st.button(f"{chr(65+i)}) {opt['text']}",
                         key=f"s1_{i}", use_container_width=True):
                st.session_state.stage1_correct  = opt["correct"]
                st.session_state.stage1_feedback = opt["feedback"]
                st.session_state.stage1_answered = True
                if opt["correct"]:
                    add_score(20)
                    add_badge("🧠 Target Tracker")
                else:
                    add_score(-10)
                break   # ← CRITICAL: stop loop so other buttons don't fire
        if st.session_state.stage1_answered:
            st.rerun()
    else:
        if st.session_state.stage1_correct:
            st.markdown(f"""<div class="success-box">
                <b>✅ Correct! +20 points</b><br>
                {st.session_state.stage1_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("Continue to stage 2 →", type="primary"):
                st.session_state.current_stage = 2
                st.rerun()
        else:
            st.markdown(f"""<div class="danger-box">
                <b>❌ Not quite. −10 points</b><br>
                {st.session_state.stage1_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("Try again"):
                st.session_state.stage1_answered = False
                st.rerun()


# ── Stage 2: Pocket identification ───────────────────────────────────────────

def show_stage_2(case):
    st.subheader("Stage 2 — Find the binding pocket")

    pdb = case["target_pdb"]
    st.markdown(f"Target: **{case['target_protein']}** (PDB: `{pdb}`)")

    # 3D viewer
    try:
        import py3Dmol
        view = py3Dmol.view(query=f"pdb:{pdb}", width=600, height=380)
        view.setStyle({"cartoon": {"color": "spectrum"}})
        view.zoomTo()
        st.components.v1.html(view._make_html(), height=400)
    except Exception:
        st.info(f"💡 View the 3D structure at "
                f"[rcsb.org/structure/{pdb}](https://www.rcsb.org/structure/{pdb})")

    if not st.session_state.stage2_answered:
        st.markdown("**Which region is the drug binding pocket?**")
        for i, r in enumerate(case["pocket_regions"]):
            if st.button(r["name"], key=f"s2_{i}", use_container_width=True):
                st.session_state.stage2_correct  = r["correct"]
                st.session_state.stage2_feedback = r["feedback"]
                st.session_state.stage2_answered = True
                if r["correct"]:
                    add_score(20)
                    add_badge("🎯 Pocket Finder")
                else:
                    add_score(-10)
                break   # ← stop loop
        if st.session_state.stage2_answered:
            st.rerun()
    else:
        if st.session_state.stage2_correct:
            st.markdown(f"""<div class="success-box">
                <b>✅ Bullseye! +20 points</b><br>
                {st.session_state.stage2_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("Continue to stage 3 →", type="primary"):
                st.session_state.current_stage = 3
                st.rerun()
        else:
            st.markdown(f"""<div class="danger-box">
                <b>❌ Wrong region. −10 points</b><br>
                {st.session_state.stage2_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("Try again"):
                st.session_state.stage2_answered = False
                st.rerun()


# ── Stage 3: Docking ──────────────────────────────────────────────────────────

def show_stage_3(case):
    st.subheader("Stage 3 — Choose & dock candidate ligands")
    st.markdown("Select **exactly 3** candidates to dock against the target.")

    # Lazy import of docking — never at module level
    try:
        from docking import has_results_for_case, get_score, dock, save_score, docking_available
        precomputed = has_results_for_case(case["id"])
        live_ok     = docking_available()
    except Exception:
        precomputed = False
        live_ok     = False

    if not st.session_state.stage3_done:
        picked = []
        for i, cand in enumerate(case["candidates"]):
            c1, c2 = st.columns([1, 6])
            with c1:
                chk = st.checkbox("", key=f"s3_{i}", label_visibility="collapsed")
            with c2:
                st.markdown(f"**{cand['name']}** — _{cand['desc']}_")
                st.caption(f"SMILES: `{cand['smiles']}`")
            if chk:
                picked.append(i)

        st.write(f"Selected: **{len(picked)} / 3**")
        if len(picked) > 3:
            st.warning("Please select only 3.")

        # Status message
        if precomputed:
            st.info("🟢 Pre-computed real Vina scores available — results will be instant.")
        elif live_ok:
            st.info("⚡ No pre-computed scores yet — clicking **Run docking** will run "
                    "real AutoDock Vina live (~30–90 s per ligand).")
        else:
            st.warning("⚠️ Docking engine not available. Run `precompute_docking.py` "
                       "locally to generate real scores, then push `docking_results.json` "
                       "to your repo.")

        can_dock = precomputed or live_ok
        if st.button("🔬 Run docking", type="primary",
                     disabled=(len(picked) != 3 or not can_dock)):
            chosen = [case["candidates"][i] for i in picked]
            failed = []

            if precomputed:
                for c in chosen:
                    s = get_score(case["id"], c["name"], "target")
                    c["_score"] = s
                    if s is None:
                        failed.append(c["name"])
                # if any missing fall through to live
                if failed:
                    precomputed = False

            if not precomputed and live_ok:
                bar = st.progress(0, text="Initialising AutoDock Vina…")
                for idx, c in enumerate(chosen):
                    bar.progress(int(idx / len(chosen) * 90),
                                 text=f"⚗️ Docking {c['name']}…")
                    ok, result = dock(c["smiles"], case["target_pdb"], exhaustiveness=4)
                    if ok:
                        c["_score"] = result
                        save_score(case["id"], c["name"], "target", result)
                    else:
                        c["_score"] = None
                        failed.append(f"{c['name']}: {result}")
                bar.progress(100, text="Done!")

            # Remove failed ligands, need at least 2 to compare
            valid = [c for c in chosen if c.get("_score") is not None]
            if len(valid) < 2:
                if failed:
                    st.error("❌ Docking failed:\n" + "\n".join(failed) +
                             "\n\nCheck internet connection and try again.")
                return

            if failed:
                st.warning("Some ligands failed: " + "; ".join(failed) +
                           ". Showing results for the others.")

            results = sorted(valid, key=lambda x: x["_score"])
            top = results[0]
            st.session_state.stage3_results  = results
            st.session_state.stage3_top_pick = top
            st.session_state.stage3_done     = True

            if top["kind"] == "best":
                add_score(25); add_badge("💊 Drug Hunter")
            elif top["kind"] == "alt":
                add_score(15)
            elif top["kind"] == "weak":
                add_score(-15)
            else:
                add_score(-20)
            st.rerun()

    else:
        results = st.session_state.stage3_results
        top     = st.session_state.stage3_top_pick

        st.caption("🟢 Showing **real AutoDock Vina** docking scores.")

        names  = [r["name"] for r in results]
        scores = [r["_score"] for r in results]
        colors = ["#1A7A6E" if r["kind"] in ("best","alt") else
                  "#888888" if r["kind"] == "decoy" else "#E8A020"
                  for r in results]
        fig = go.Figure(go.Bar(x=names, y=scores, marker_color=colors,
                               text=[f"{s:.1f}" for s in scores],
                               textposition="outside"))
        fig.update_layout(title="Docking scores (more negative = stronger binding)",
                          yaxis_title="Binding affinity (kcal/mol)",
                          height=320, showlegend=False,
                          plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        can_next = top["name"] in case.get("selectivity_data", {})
        if top["kind"] in ("best","alt") and can_next:
            st.markdown(f"""<div class="success-box">
                <b>✅ Top binder: {top['name']}</b><br>
                Good binding to {case['target_protein']}. Now check selectivity.
            </div>""", unsafe_allow_html=True)
            if st.button("Continue to stage 4 →", type="primary"):
                st.session_state.current_stage = 4
                st.rerun()
        else:
            msg = ("Weak binding — try stronger candidates." if top["kind"] == "weak"
                   else "Top pick is a decoy — check structures.")
            st.markdown(f'<div class="danger-box"><b>❌ {msg}</b></div>',
                        unsafe_allow_html=True)
            if st.button("Try again"):
                st.session_state.stage3_done = False
                st.rerun()


# ── Stage 4: Selectivity ──────────────────────────────────────────────────────

def show_stage_4(case):
    st.subheader("Stage 4 — Selectivity test ⚠️")
    top = st.session_state.stage3_top_pick
    sel = case.get("selectivity_data", {}).get(top["name"])

    if not sel:
        st.error("No selectivity data. Go back and choose a different lead.")
        if st.button("← Back"):
            st.session_state.current_stage = 3
            st.session_state.stage3_done   = False
            st.rerun()
        return

    st.markdown(f"Now test **{top['name']}** against the off-target "
                f"**{case['off_target']}** (PDB: `{case['off_target_pdb']}`).")

    # Try to get real scores, fall back to asking for live dock
    try:
        from docking import get_score, dock, save_score, docking_available
        t_score = get_score(case["id"], top["name"], "target")
        o_score = get_score(case["id"], top["name"], "off_target")
    except Exception:
        t_score = None
        o_score = None

    # Off-target missing — offer live dock
    if o_score is None:
        try:
            from docking import docking_available, dock, save_score
            if docking_available():
                st.info(f"Off-target score not pre-computed. Click to dock live.")
                if st.button(f"⚡ Dock {top['name']} vs {case['off_target']}",
                             type="primary"):
                    with st.spinner("Running real Vina…"):
                        ok, result = dock(top["smiles"],
                                         case["off_target_pdb"],
                                         exhaustiveness=4)
                    if ok:
                        save_score(case["id"], top["name"], "off_target", result)
                        o_score = result
                        st.rerun()
                    else:
                        st.error(f"Docking failed: {result}")
                return
        except Exception:
            pass

    if t_score is None or o_score is None:
        st.warning("Pre-computed off-target score not available. Run "
                   "`precompute_docking.py` to generate it, then push "
                   "`docking_results.json` to your repo.")
        # Allow manual continue using pedagogical pass/fail
        if not st.session_state.stage4_done:
            is_sel = sel.get("pass", False)
            _render_selectivity(is_sel, sel["msg"], None, None, case, top)
        else:
            if st.button("Continue to stage 5 →", type="primary"):
                st.session_state.current_stage = 5
                st.rerun()
        return

    # Real scores available
    is_sel = (t_score < o_score - 0.5)
    st.caption("🟢 Showing **real AutoDock Vina** docking scores.")
    _render_selectivity(is_sel, sel["msg"], t_score, o_score, case, top)


def _render_selectivity(is_sel, msg, t_score, o_score, case, top):
    c1, c2 = st.columns(2)
    if t_score is not None:
        c1.metric(f"Target ({case['target_protein']})",
                  f"{t_score} kcal/mol", "Strong ✓")
        c2.metric(f"Off-target ({case['off_target']})",
                  f"{o_score} kcal/mol",
                  "Weak ✓" if is_sel else "Too strong ✗",
                  delta_color="normal" if is_sel else "inverse")
        ratio = round(o_score / t_score, 2) if t_score else 0
        st.metric("Selectivity ratio (off/target)", ratio)

    if not st.session_state.stage4_done:
        if is_sel:
            st.markdown(f"""<div class="success-box">
                <b>✅ Selectivity confirmed! +30 points</b><br>{msg}
            </div>""", unsafe_allow_html=True)
            add_score(30)
            add_badge("⚖️ Selectivity Sage")
        else:
            st.markdown(f"""<div class="danger-box">
                <b>❌ Poor selectivity.</b><br>{msg}
            </div>""", unsafe_allow_html=True)
        st.session_state.stage4_done = True
        st.rerun()
    else:
        if st.button("Continue to stage 5 →", type="primary"):
            st.session_state.current_stage = 5
            st.rerun()


# ── Stage 5: ADMET ────────────────────────────────────────────────────────────

def show_stage_5(case):
    st.subheader("Stage 5 — ADMET & drug-likeness")
    top   = st.session_state.stage3_top_pick
    admet = case.get("admet", {}).get(top["name"])

    if not admet:
        st.warning("No ADMET data for this candidate.")
        if st.button("Continue →", type="primary"):
            st.session_state.current_stage = 6
            st.rerun()
        return

    st.markdown(f"Final check on **{top['name']}** — Lipinski's Rule of 5:")

    rules = [
        ("Molecular weight", admet["MW"],       "< 500 Da",    admet["MW"] < 500),
        ("LogP",             admet["LogP"],      "-0.5 to 5",   -0.5 <= admet["LogP"] <= 5),
        ("H-bond donors",    admet["HBD"],       "≤ 5",         admet["HBD"] <= 5),
        ("H-bond acceptors", admet["HBA"],       "≤ 10",        admet["HBA"] <= 10),
        ("Rotatable bonds",  admet["RotBonds"],  "≤ 10",        admet["RotBonds"] <= 10),
    ]
    df = pd.DataFrame([
        {"Property": n, "Value": v, "Ideal": i, "Pass": "✅" if p else "❌"}
        for n, v, i, p in rules
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not st.session_state.stage5_done:
        if admet.get("pass"):
            add_score(15)
            add_badge("💎 Lipinski Compliant")

        if admet.get("warning"):
            st.markdown(f"""<div class="warning-box">
                <b>Post-market alert</b><br>{admet['warning']}
            </div>""", unsafe_allow_html=True)
            if "withdrew" in admet["warning"].lower() or "fda" in admet["warning"].lower():
                add_score(-15)

        st.session_state.stage5_done = True
        st.rerun()
    else:
        if st.button("See final results →", type="primary"):
            st.session_state.current_stage = 6
            st.rerun()


# ── Final result ──────────────────────────────────────────────────────────────

def show_final_result(case):
    st.subheader("🎉 Mission complete!")
    score = st.session_state.score

    if score >= 90:   title, icon = "Master Medicinal Chemist", "🥇"
    elif score >= 70: title, icon = "Drug Designer",             "🥈"
    elif score >= 50: title, icon = "Junior Chemist",            "🥉"
    else:             title, icon = "Back to the textbooks",     "📚"

    st.markdown(f"""
    <div style="background:#eef2ff;color:#1a1a2e;padding:1.5rem;
                border-radius:12px;text-align:center;
                border:2px solid #5b6cff;margin-bottom:1rem;">
        <div style="font-size:2.5rem;color:#1a1a2e;">{icon}</div>
        <div style="font-size:1.3rem;font-weight:600;color:#1a1a2e;">{title}</div>
        <div style="font-size:2rem;font-weight:700;margin-top:.5rem;
                    color:#1a1a2e;font-family:monospace;">{score}/100</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"*{case['ending']}*")

    if st.session_state.badges:
        st.markdown("**Badges earned:**")
        st.markdown(" ".join(
            f'<span class="badge">{b}</span>'
            for b in st.session_state.badges
        ), unsafe_allow_html=True)

    try:
        from leaderboard import show_score_submission
        show_score_submission(case, score, st.session_state.badges)
    except Exception:
        pass

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Replay", use_container_width=True):
            reset_game(); st.rerun()
    with c2:
        from cases import CASES
        if st.button("📚 Next case", use_container_width=True, type="primary"):
            st.session_state.case_index = (
                (st.session_state.case_index + 1) % len(CASES)
            )
            reset_game(); st.rerun()
