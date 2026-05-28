"""
Drug Hunter — Game logic & UI
Developed by Sarang Dhote, Shivaji Science College, Nagpur

KEY DESIGN RULE for all interactive stages:
  Use st.radio (persists in session state) + one Submit button.
  NEVER use multiple st.button() calls in a for-loop for MCQ.
  This is the only pattern that works reliably across Streamlit versions.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
        "s1_answered":     False,
        "s1_correct":      False,
        "s1_feedback":     "",
        "s2_answered":     False,
        "s2_correct":      False,
        "s2_feedback":     "",
        "s3_done":         False,
        "s3_results":      None,
        "s3_top":          None,
        "s4_done":         False,
        "s5_done":         False,
        "badges":          [],
        "score_submitted": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_game():
    keys = [
        "current_stage","score",
        "s1_answered","s1_correct","s1_feedback",
        "s2_answered","s2_correct","s2_feedback",
        "s3_done","s3_results","s3_top",
        "s4_done","s5_done","badges","score_submitted",
        # also clear widget states so radio resets
        "s1_radio","s2_radio","s3_c0","s3_c1","s3_c2","s3_c3","s3_c4","s3_c5",
    ]
    for k in keys:
        st.session_state.pop(k, None)
    init_session_state()


def add_score(pts):
    st.session_state.score = max(0, st.session_state.score + pts)


def add_badge(b):
    if b not in st.session_state.badges:
        st.session_state.badges.append(b)


# ── Top bar ───────────────────────────────────────────────────────────────────

def show_top_bar(case, page):
    score = st.session_state.score
    stage = st.session_state.current_stage
    right = (
        f'<span class="dh-score-pill">Score: <b>{score}</b>'
        f'&nbsp;|&nbsp;Stage <b>{min(stage,5)}/5</b></span>'
        if page == "🎮 Play"
        else '<span class="dh-score-pill">Drug Hunter</span>'
    )
    st.markdown(f"""
    <div class="dh-topbar">
        <div>
            <p class="dh-title">🧬 Drug Hunter</p>
            <p class="dh-subtitle">
                By Sarang Dhote &nbsp;·&nbsp;
                Shivaji Science College, Nagpur
            </p>
        </div>
        {right}
    </div>""", unsafe_allow_html=True)


# ── Progress stepper ──────────────────────────────────────────────────────────

def show_progress_stepper():
    current = st.session_state.current_stage
    parts = []
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
        lbl = label.replace("\n","<br>")
        parts.append(f"""
        <div class="dh-step">
          <div class="dh-step-circle {cc}">{icon}</div>
          <div class="dh-step-label {lc}">{lbl}</div>
        </div>""")
    st.markdown(
        f'<div class="dh-stepper">{"".join(parts)}</div>',
        unsafe_allow_html=True
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def show_header(case):
    st.markdown(f"### Case #{case['id']}: {case['title']}")

def show_progress_bar():
    show_progress_stepper()


# ── STAGE 1: Target identification ───────────────────────────────────────────

def show_stage_1(case):
    st.subheader("Stage 1 — Identify the target")

    # Patient card
    p = case["patient"]
    st.markdown(f"""
    <div class="case-card">
        <b>🏥 Patient Briefing</b><br>
        <b>Name:</b> {p['name']} &nbsp;|&nbsp;
        <b>Age:</b> {p['age']} &nbsp;|&nbsp;
        <b>Gender:</b> {p['gender']}<br>
        <b>Condition:</b> {p['condition']}<br>
        <b>History:</b> {p['history']}
    </div>""", unsafe_allow_html=True)

    if not st.session_state.s1_answered:
        # ── Use st.radio — persists in session state reliably ──────────────
        st.markdown(f"**{case['stage1_question']}**")
        labels = [
            f"{chr(65+i)}) {o['text']}"
            for i, o in enumerate(case["stage1_options"])
        ]
        choice = st.radio(
            "Select your answer:",
            labels,
            index=None,          # no default selected
            key="s1_radio",
            label_visibility="collapsed",
        )
        st.markdown("")          # spacer

        if st.button("✅ Submit answer", type="primary",
                     disabled=(choice is None),
                     use_container_width=True):
            idx = labels.index(choice)
            opt = case["stage1_options"][idx]
            st.session_state.s1_correct  = opt["correct"]
            st.session_state.s1_feedback = opt["feedback"]
            st.session_state.s1_answered = True
            if opt["correct"]:
                add_score(20)
                add_badge("🧠 Target Tracker")
            else:
                add_score(-10)
            st.rerun()

    else:
        # ── Show result ────────────────────────────────────────────────────
        if st.session_state.s1_correct:
            st.markdown(f"""
            <div class="success-box">
                <b>✅ Correct! +20 points</b><br>
                {st.session_state.s1_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("Continue to Stage 2 →", type="primary",
                         use_container_width=True):
                st.session_state.current_stage = 2
                st.rerun()
        else:
            st.markdown(f"""
            <div class="danger-box">
                <b>❌ Incorrect. −10 points</b><br>
                {st.session_state.s1_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("🔄 Try again", use_container_width=True):
                st.session_state.s1_answered = False
                st.session_state.pop("s1_radio", None)
                st.rerun()


# ── STAGE 2: Pocket identification ───────────────────────────────────────────

def show_stage_2(case):
    st.subheader("Stage 2 — Find the binding pocket")

    pdb = case["target_pdb"]
    st.markdown(
        f"Target: **{case['target_protein']}** &nbsp; "
        f"(PDB: [`{pdb}`](https://www.rcsb.org/structure/{pdb}))"
    )

    # 3-D viewer
    try:
        import py3Dmol
        view = py3Dmol.view(query=f"pdb:{pdb}", width=600, height=360)
        view.setStyle({"cartoon": {"color": "spectrum"}})
        view.zoomTo()
        st.components.v1.html(view._make_html(), height=380)
    except Exception:
        st.info(
            f"💡 View the 3D structure at "
            f"[rcsb.org/structure/{pdb}]"
            f"(https://www.rcsb.org/structure/{pdb})"
        )

    if not st.session_state.s2_answered:
        # ── Use st.radio — same reliable pattern as Stage 1 ────────────────
        st.markdown("**Which region is the drug binding pocket?**")
        regions = [r["name"] for r in case["pocket_regions"]]
        choice = st.radio(
            "Select region:",
            regions,
            index=None,
            key="s2_radio",
            label_visibility="collapsed",
        )
        st.markdown("")

        if st.button("✅ Submit answer", type="primary",
                     disabled=(choice is None),
                     use_container_width=True,
                     key="s2_submit"):
            idx = regions.index(choice)
            r = case["pocket_regions"][idx]
            st.session_state.s2_correct  = r["correct"]
            st.session_state.s2_feedback = r["feedback"]
            st.session_state.s2_answered = True
            if r["correct"]:
                add_score(20)
                add_badge("🎯 Pocket Finder")
            else:
                add_score(-10)
            st.rerun()

    else:
        if st.session_state.s2_correct:
            st.markdown(f"""
            <div class="success-box">
                <b>✅ Correct! +20 points</b><br>
                {st.session_state.s2_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("Continue to Stage 3 →", type="primary",
                         use_container_width=True):
                st.session_state.current_stage = 3
                st.rerun()
        else:
            st.markdown(f"""
            <div class="danger-box">
                <b>❌ Incorrect. −10 points</b><br>
                {st.session_state.s2_feedback}
            </div>""", unsafe_allow_html=True)
            if st.button("🔄 Try again", use_container_width=True,
                         key="s2_retry"):
                st.session_state.s2_answered = False
                st.session_state.pop("s2_radio", None)
                st.rerun()


# ── STAGE 3: Docking ─────────────────────────────────────────────────────────

def show_stage_3(case):
    st.subheader("Stage 3 — Choose & dock candidate ligands")
    st.markdown("Select **exactly 3** candidates to dock against the target.")

    try:
        from docking import (has_results_for_case, get_score,
                             dock, save_score, docking_available)
        precomputed = has_results_for_case(case["id"])
        live_ok     = docking_available()
    except Exception:
        precomputed = False
        live_ok     = False

    if not st.session_state.s3_done:

        picked = []
        for i, cand in enumerate(case["candidates"]):
            c1, c2 = st.columns([1, 9])
            with c1:
                chk = st.checkbox("", key=f"s3_c{i}",
                                  label_visibility="collapsed")
            with c2:
                st.markdown(
                    f"**{cand['name']}** — _{cand['desc']}_  \n"
                    f"`{cand['smiles']}`"
                )
            if chk:
                picked.append(i)

        cnt = len(picked)
        st.caption(f"Selected: {cnt} / 3")

        if precomputed:
            st.info("🟢 Pre-computed real Vina scores available.")
        elif live_ok:
            st.info("⚡ No pre-computed scores — clicking Run Docking will "
                    "run real AutoDock Vina (~30–90 s per ligand).")
        else:
            st.warning("⚠️ Run `precompute_docking.py` locally and push "
                       "`docking_results.json` to generate scores.")

        st.button(
            "🔬 Run docking",
            type="primary",
            disabled=(cnt != 3 or not (precomputed or live_ok)),
            use_container_width=True,
            key="s3_run",
        )

        if st.session_state.get("s3_run"):
            chosen = [case["candidates"][i] for i in picked]
            failed = []

            if precomputed:
                for c in chosen:
                    s = get_score(case["id"], c["name"], "target")
                    c["_score"] = s
                    if s is None:
                        failed.append(c["name"])
                if failed:
                    precomputed = False   # fall through to live

            if not precomputed and live_ok:
                bar = st.progress(0, text="Initialising AutoDock Vina…")
                for idx2, c in enumerate(chosen):
                    bar.progress(
                        int(idx2 / len(chosen) * 90),
                        text=f"⚗️ Docking {c['name']}…"
                    )
                    ok, result = dock(
                        c["smiles"], case["target_pdb"], exhaustiveness=4
                    )
                    if ok:
                        c["_score"] = result
                        save_score(case["id"], c["name"], "target", result)
                    else:
                        c["_score"] = None
                        failed.append(f"{c['name']}: {result}")
                bar.progress(100, text="Done!")

            valid = [c for c in chosen if c.get("_score") is not None]
            if len(valid) < 2:
                st.error("❌ Docking failed: " + " | ".join(failed) +
                         "\nCheck internet connection and try again.")
                st.session_state.pop("s3_run", None)
                st.stop()

            results = sorted(valid, key=lambda x: x["_score"])
            top = results[0]
            st.session_state.s3_results = results
            st.session_state.s3_top     = top
            st.session_state.s3_done    = True

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
        results = st.session_state.s3_results
        top     = st.session_state.s3_top
        st.caption("🟢 Real AutoDock Vina scores.")

        names  = [r["name"] for r in results]
        scores = [r["_score"] for r in results]
        colors = [
            "#1A7A6E" if r["kind"] in ("best","alt") else
            "#888888" if r["kind"] == "decoy" else "#E8A020"
            for r in results
        ]
        fig = go.Figure(go.Bar(
            x=names, y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition="outside",
        ))
        fig.update_layout(
            title="Docking scores  (more negative = stronger binding)",
            yaxis_title="Binding affinity (kcal/mol)",
            height=320, showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        can_next = top["name"] in case.get("selectivity_data", {})
        if top["kind"] in ("best", "alt") and can_next:
            st.markdown(f"""
            <div class="success-box">
                <b>✅ Top binder: {top['name']}</b><br>
                Good binding to {case['target_protein']}. Now check selectivity.
            </div>""", unsafe_allow_html=True)
            if st.button("Continue to Stage 4 →", type="primary",
                         use_container_width=True):
                st.session_state.current_stage = 4
                st.rerun()
        else:
            msg = ("Weak binding — try stronger candidates."
                   if top["kind"] == "weak"
                   else "Top pick is a decoy — check structures.")
            st.markdown(
                f'<div class="danger-box"><b>❌ {msg}</b></div>',
                unsafe_allow_html=True
            )
            if st.button("🔄 Try again", use_container_width=True):
                st.session_state.s3_done = False
                for i in range(6):
                    st.session_state.pop(f"s3_c{i}", None)
                st.session_state.pop("s3_run", None)
                st.rerun()


# ── STAGE 4: Selectivity ─────────────────────────────────────────────────────

def show_stage_4(case):
    st.subheader("Stage 4 — Selectivity test ⚠️")
    top = st.session_state.s3_top
    if top is None:
        st.error("No lead selected. Go back to stage 3.")
        if st.button("← Back"):
            st.session_state.current_stage = 3
            st.session_state.s3_done = False
            st.rerun()
        return

    sel = case.get("selectivity_data", {}).get(top["name"])
    if not sel:
        st.error("No selectivity data for this candidate. Go back.")
        if st.button("← Back"):
            st.session_state.current_stage = 3
            st.session_state.s3_done = False
            st.rerun()
        return

    st.markdown(
        f"Test **{top['name']}** against the off-target "
        f"**{case['off_target']}** (PDB: `{case['off_target_pdb']}`)."
    )

    # Try real scores
    t_score = o_score = None
    try:
        from docking import get_score, dock, save_score, docking_available
        t_score = get_score(case["id"], top["name"], "target")
        o_score = get_score(case["id"], top["name"], "off_target")
    except Exception:
        pass

    # Off-target missing: offer live dock
    if o_score is None:
        try:
            from docking import docking_available, dock, save_score
            if docking_available():
                st.info("Off-target score not yet computed.")
                if st.button(
                    f"⚡ Dock {top['name']} vs {case['off_target']}",
                    type="primary", use_container_width=True
                ):
                    with st.spinner("Running real Vina…"):
                        ok, result = dock(
                            top["smiles"], case["off_target_pdb"],
                            exhaustiveness=4
                        )
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
        st.warning("Pre-computed scores not available. "
                   "Run `precompute_docking.py` and push `docking_results.json`.")
        # Fall back to pedagogical pass/fail
        is_sel = sel.get("pass", True)
    else:
        is_sel = (t_score < o_score - 0.5)
        st.caption("🟢 Real AutoDock Vina scores.")
        c1, c2 = st.columns(2)
        c1.metric(f"Target ({case['target_protein']})",
                  f"{t_score} kcal/mol", "Strong ✓")
        c2.metric(f"Off-target ({case['off_target']})",
                  f"{o_score} kcal/mol",
                  "Weak ✓" if is_sel else "Too strong ✗",
                  delta_color="normal" if is_sel else "inverse")
        st.metric("Selectivity ratio", round(o_score / t_score, 2))

    if not st.session_state.s4_done:
        if is_sel:
            st.markdown(f"""
            <div class="success-box">
                <b>✅ Selectivity confirmed! +30 points</b><br>
                {sel['msg']}
            </div>""", unsafe_allow_html=True)
            add_score(30)
            add_badge("⚖️ Selectivity Sage")
        else:
            st.markdown(f"""
            <div class="danger-box">
                <b>❌ Poor selectivity.</b><br>{sel['msg']}
            </div>""", unsafe_allow_html=True)
        st.session_state.s4_done = True

    if st.button("Continue to Stage 5 →", type="primary",
                 use_container_width=True):
        st.session_state.current_stage = 5
        st.rerun()


# ── STAGE 5: ADMET ────────────────────────────────────────────────────────────

def show_stage_5(case):
    st.subheader("Stage 5 — ADMET & drug-likeness")
    top   = st.session_state.s3_top
    admet = case.get("admet", {}).get(top["name"]) if top else None

    if not admet:
        st.warning("No ADMET data for this candidate.")
        if st.button("Continue →", type="primary",
                     use_container_width=True):
            st.session_state.current_stage = 6
            st.rerun()
        return

    st.markdown(f"Checking **{top['name']}** against Lipinski's Rule of 5:")

    rules = [
        ("Molecular weight", admet["MW"],      "< 500 Da",  admet["MW"] < 500),
        ("LogP",             admet["LogP"],     "-0.5 to 5", -0.5 <= admet["LogP"] <= 5),
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
        if admet.get("pass"):
            add_score(15)
            add_badge("💎 Lipinski Compliant")
        if admet.get("warning"):
            st.markdown(f"""
            <div class="warning-box">
                <b>Post-market alert</b><br>{admet['warning']}
            </div>""", unsafe_allow_html=True)
            warn = admet["warning"].lower()
            if "withdrew" in warn or "fda" in warn and "black box" in warn:
                add_score(-15)
        st.session_state.s5_done = True

    if st.button("See final results →", type="primary",
                 use_container_width=True):
        st.session_state.current_stage = 6
        st.rerun()


# ── FINAL RESULT ──────────────────────────────────────────────────────────────

def show_final_result(case):
    st.subheader("🎉 Mission complete!")
    score = st.session_state.score

    if score >= 90:   icon, title = "🥇", "Master Medicinal Chemist"
    elif score >= 70: icon, title = "🥈", "Drug Designer"
    elif score >= 50: icon, title = "🥉", "Junior Chemist"
    else:             icon, title = "📚", "Back to the Textbooks"

    st.markdown(f"""
    <div style="background:#eef2ff;color:#1a1a2e;padding:2rem;
                border-radius:12px;text-align:center;
                border:2px solid #5b6cff;margin-bottom:1rem;">
        <div style="font-size:2.5rem;">{icon}</div>
        <div style="font-size:1.3rem;font-weight:600;">{title}</div>
        <div style="font-size:2rem;font-weight:700;margin-top:.5rem;
                    font-family:monospace;">{score} / 100</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"_{case['ending']}_")

    if st.session_state.badges:
        st.markdown("**Badges earned:**")
        st.markdown(
            " ".join(f'<span class="badge">{b}</span>'
                     for b in st.session_state.badges),
            unsafe_allow_html=True
        )

    try:
        from leaderboard import show_score_submission
        show_score_submission(case, score, st.session_state.badges)
    except Exception:
        pass

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Replay", use_container_width=True):
            reset_game()
            st.rerun()
    with c2:
        from cases import CASES
        if st.button("📚 Next case →", type="primary",
                     use_container_width=True):
            st.session_state.case_index = (
                (st.session_state.case_index + 1) % len(CASES)
            )
            reset_game()
            st.rerun()
