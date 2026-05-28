"""
Utility functions for CSI Drug Discovery game.
Handles session state, rendering, and scoring logic.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Try to import real docking module; fall back to hardcoded scores if missing
try:
    from docking import get_score as get_real_score
    DOCKING_AVAILABLE = True
except ImportError:
    DOCKING_AVAILABLE = False


def resolve_score(case_id, candidate, protein_type="target"):
    """
    Get the REAL docking score for a ligand.

    Returns the pre-computed Vina score, or None if no real score exists.
    There are no fake/estimated fallbacks — if a score isn't real, we don't show it.

    Returns: float (real Vina score) or None
    """
    if DOCKING_AVAILABLE:
        real_score = get_real_score(case_id, candidate["name"], protein_type)
        if real_score is not None:
            return real_score
    return None


# ==================== SESSION STATE ====================

def init_session_state():
    """Initialize all required session state variables."""
    defaults = {
        "case_index": 0,
        "current_stage": 1,
        "score": 0,
        "stage1_answered": False,
        "stage2_answered": False,
        "stage3_picks": [],
        "stage3_top_pick": None,
        "stage3_done": False,
        "stage4_done": False,
        "stage5_done": False,
        "badges": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_game():
    """Reset all game state for a new case."""
    st.session_state.current_stage = 1
    st.session_state.score = 0
    st.session_state.stage1_answered = False
    st.session_state.stage2_answered = False
    st.session_state.stage3_picks = []
    st.session_state.stage3_top_pick = None
    st.session_state.stage3_done = False
    st.session_state.stage4_done = False
    st.session_state.stage5_done = False
    st.session_state.badges = []
    st.session_state.score_submitted = False


def add_score(points):
    st.session_state.score = max(0, st.session_state.score + points)


def add_badge(badge):
    if badge not in st.session_state.badges:
        st.session_state.badges.append(badge)


# ==================== UI HELPERS ====================

def show_header(case):
    st.markdown(f"### Case #{case['id']}: {case['title']}")
    st.caption(f"{case['disease']}  ·  {case['difficulty']}")


def show_progress_bar():
    """Visual progress through 5 stages."""
    stages_done = st.session_state.current_stage - 1
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            if i < stages_done:
                st.markdown(f"<div style='background:#2e7d32; height:6px; border-radius:3px;'></div>", unsafe_allow_html=True)
            elif i == stages_done:
                st.markdown(f"<div style='background:#1976d2; height:6px; border-radius:3px;'></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#e0e0e0; height:6px; border-radius:3px;'></div>", unsafe_allow_html=True)


# ==================== STAGE 1: TARGET IDENTIFICATION ====================

def show_stage_1(case):
    st.subheader("Stage 1 — Identify the target")

    # Patient briefing
    p = case["patient"]
    st.markdown(f"""
    <div class="case-card">
        <strong>🏥 Patient Briefing</strong><br>
        <strong>Name:</strong> {p['name']}<br>
        <strong>Age / Gender:</strong> {p['age']} / {p['gender']}<br>
        <strong>Condition:</strong> {p['condition']}<br>
        <strong>History:</strong> {p['history']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Question:** {case['stage1_question']}")

    if not st.session_state.stage1_answered:
        for i, opt in enumerate(case["stage1_options"]):
            if st.button(f"{chr(65+i)}) {opt['text']}", key=f"s1_opt_{i}", use_container_width=True):
                if opt["correct"]:
                    st.session_state.stage1_correct = True
                    add_score(20)
                    add_badge("🧠 Target Tracker")
                else:
                    st.session_state.stage1_correct = False
                    add_score(-10)
                st.session_state.stage1_feedback = opt["feedback"]
                st.session_state.stage1_answered = True
                st.rerun()
    else:
        if st.session_state.stage1_correct:
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Correct! +20 points</strong><br>{st.session_state.stage1_feedback}
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue to stage 2 →", type="primary"):
                st.session_state.current_stage = 2
                st.rerun()
        else:
            st.markdown(f"""
            <div class="danger-box">
                <strong>❌ Not quite. −10 points</strong><br>{st.session_state.stage1_feedback}
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try again"):
                st.session_state.stage1_answered = False
                st.rerun()


# ==================== STAGE 2: POCKET IDENTIFICATION ====================

def show_stage_2(case):
    st.subheader("Stage 2 — Find the binding pocket")

    st.markdown(f"""
    The target protein is **{case['target_protein']}** (PDB: `{case['target_pdb']}`).
    Where on this protein should the drug bind?
    """)

    # Show 3D viewer via py3Dmol if available, else show info
    try:
        import py3Dmol
        view = py3Dmol.view(query=f"pdb:{case['target_pdb']}", width=600, height=400)
        view.setStyle({'cartoon': {'color': 'spectrum'}})
        view.zoomTo()
        st.components.v1.html(view._make_html(), height=420)
    except Exception as e:
        st.info(f"💡 3D viewer unavailable. PDB ID: {case['target_pdb']} — students can view at https://www.rcsb.org/structure/{case['target_pdb']}")

    if not st.session_state.stage2_answered:
        st.markdown("**Which region is the drug binding pocket?**")
        for i, region in enumerate(case["pocket_regions"]):
            if st.button(region["name"], key=f"s2_opt_{i}", use_container_width=True):
                if region["correct"]:
                    st.session_state.stage2_correct = True
                    add_score(20)
                    add_badge("🎯 Pocket Finder")
                else:
                    st.session_state.stage2_correct = False
                    add_score(-10)
                st.session_state.stage2_feedback = region["feedback"]
                st.session_state.stage2_answered = True
                st.rerun()
    else:
        if st.session_state.stage2_correct:
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Bullseye! +20 points</strong><br>{st.session_state.stage2_feedback}
            </div>
            """, unsafe_allow_html=True)
            if st.button("Continue to stage 3 →", type="primary"):
                st.session_state.current_stage = 3
                st.rerun()
        else:
            st.markdown(f"""
            <div class="danger-box">
                <strong>❌ Wrong region. −10 points</strong><br>{st.session_state.stage2_feedback}
            </div>
            """, unsafe_allow_html=True)
            if st.button("Try again"):
                st.session_state.stage2_answered = False
                st.rerun()


# ==================== STAGE 3: LIGAND SELECTION & DOCKING ====================

def show_stage_3(case):
    st.subheader("Stage 3 — Choose & dock candidate ligands")

    st.markdown("Select **exactly 3** candidates to dock against the target. Choose wisely — decoys waste your run.")

    # Detect whether real pre-computed scores exist for this case
    real_available = False
    if DOCKING_AVAILABLE:
        try:
            from docking import has_results_for_case
            real_available = has_results_for_case(case["id"])
        except Exception:
            real_available = False

    if not st.session_state.stage3_done:
        # Build candidate selection
        picked = []
        for i, cand in enumerate(case["candidates"]):
            col1, col2 = st.columns([1, 6])
            with col1:
                checked = st.checkbox("", key=f"s3_check_{i}", label_visibility="collapsed")
            with col2:
                st.markdown(f"**{cand['name']}** — _{cand['desc']}_  \n`SMILES: {cand['smiles']}`")
            if checked:
                picked.append(i)

        st.session_state.stage3_picks = picked
        st.write(f"Selected: **{len(picked)} / 3**")

        # Docking mode selector — real scores are REQUIRED
        live_mode = False
        if real_available:
            st.caption("🟢 Real pre-computed AutoDock Vina scores are available for this case.")
        elif DOCKING_AVAILABLE:
            st.warning(
                "⚠️ No pre-computed scores for this case yet. "
                "Enable live docking below to compute **real** Vina scores now, "
                "or run `python precompute_docking.py` to generate them in advance."
            )
            live_mode = st.checkbox(
                "⚡ Run REAL docking now (AutoDock Vina — slower, ~1-3 min for 3 ligands)",
                help="Runs actual Vina docking live. Downloads the Vina binary and PDB on first run."
            )
        else:
            st.error(
                "❌ The docking engine isn't available in this environment, and no "
                "pre-computed scores exist. This stage needs real docking data. "
                "Run `python precompute_docking.py` on a machine with RDKit installed."
            )

        if len(picked) == 3:
            # Only allow docking if we can produce REAL scores
            can_dock = real_available or (live_mode and DOCKING_AVAILABLE)

            run_clicked = st.button(
                "🔬 Run docking",
                type="primary",
                disabled=not can_dock
            )

            if not can_dock and not real_available:
                st.caption("Enable live docking above to proceed with real scores.")

            if run_clicked and can_dock:
                chosen = [case["candidates"][i] for i in picked]
                docking_failed = False

                if live_mode and not real_available:
                    # LIVE Vina docking
                    from docking import dock
                    progress = st.progress(0, text="Starting AutoDock Vina...")
                    for idx, cand in enumerate(chosen):
                        progress.progress(
                            int(idx / len(chosen) * 100),
                            text=f"Docking {cand['name']}... (real Vina, please wait)"
                        )
                        ok, result = dock(cand["smiles"], case["target_pdb"], exhaustiveness=4)
                        if ok:
                            cand["_score"] = result
                            # Cache the real result for future runs
                            from docking import save_score
                            save_score(case["id"], cand["name"], "target", result)
                        else:
                            cand["_score"] = None
                            docking_failed = True
                            st.error(f"Docking failed for {cand['name']}: {result}")
                    progress.progress(100, text="Docking complete!")
                else:
                    # LOOKUP real pre-computed scores
                    for cand in chosen:
                        score = resolve_score(case["id"], cand, "target")
                        cand["_score"] = score
                        if score is None:
                            docking_failed = True

                # If any score is missing, do NOT proceed with fake data
                if docking_failed or any(c.get("_score") is None for c in chosen):
                    st.error(
                        "❌ Could not get real docking scores for all selected ligands. "
                        "Not showing any results rather than showing fake numbers. "
                        "Try live docking, or pre-compute scores first."
                    )
                else:
                    # All real — proceed
                    results = sorted(chosen, key=lambda x: x["_score"])
                    top = results[0]
                    st.session_state.stage3_results = results
                    st.session_state.stage3_top_pick = top
                    st.session_state.stage3_done = True

                    # Game points based on pedagogical "kind" (not raw score)
                    if top["kind"] == "best":
                        add_score(25)
                        add_badge("💊 Drug Hunter")
                    elif top["kind"] == "alt":
                        add_score(15)
                    elif top["kind"] == "weak":
                        add_score(-15)
                    else:
                        add_score(-20)
                    st.rerun()
        elif len(picked) > 3:
            st.warning("Please select only 3.")
    else:
        # Show results
        results = st.session_state.stage3_results
        top = st.session_state.stage3_top_pick

        # All scores here are guaranteed real
        st.caption("🟢 Showing **real AutoDock Vina** docking scores.")

        # Bar chart (all scores are real Vina values)
        names = [r["name"] for r in results]
        scores = [r["_score"] for r in results]
        colors = ["#2e7d32" if r["kind"] in ("best", "alt") else
                  "#888888" if r["kind"] == "decoy" else "#f57c00" for r in results]

        fig = go.Figure(data=[
            go.Bar(x=names, y=scores, marker_color=colors, text=scores, textposition='outside')
        ])
        fig.update_layout(
            title="Docking scores (more negative = stronger binding)",
            yaxis_title="Binding affinity (kcal/mol)",
            height=350,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        if top["kind"] == "best":
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Top binder: {top['name']} (+25 points)</strong><br>
                Strong binding to {case['target_protein']}. But we still need to check selectivity in the next stage.
            </div>
            """, unsafe_allow_html=True)
            can_continue = True
        elif top["kind"] == "alt":
            st.markdown(f"""
            <div class="warning-box">
                <strong>⚠️ Top binder: {top['name']} (+15 points)</strong><br>
                Selective binder — but a surprise may await in stage 5...
            </div>
            """, unsafe_allow_html=True)
            can_continue = True
        elif top["kind"] == "weak":
            st.markdown(f"""
            <div class="danger-box">
                <strong>❌ Weak binding (−15 points)</strong><br>
                These bind but aren't ideal candidates. Re-select.
            </div>
            """, unsafe_allow_html=True)
            can_continue = False
        else:
            st.markdown(f"""
            <div class="danger-box">
                <strong>❌ Top pick is a decoy (−20 points)</strong><br>
                Look at the structures more carefully.
            </div>
            """, unsafe_allow_html=True)
            can_continue = False

        if can_continue and top["name"] in case["selectivity_data"]:
            if st.button("Continue to stage 4 →", type="primary"):
                st.session_state.current_stage = 4
                st.rerun()
        else:
            if st.button("Try again"):
                st.session_state.stage3_done = False
                st.rerun()


# ==================== STAGE 4: SELECTIVITY ====================

def show_stage_4(case):
    st.subheader("Stage 4 — Selectivity test ⚠️")

    top = st.session_state.stage3_top_pick
    sel = case["selectivity_data"].get(top["name"])

    if not sel:
        st.error("No selectivity data for this candidate. Go back and pick a different lead.")
        if st.button("← Back to stage 3"):
            st.session_state.current_stage = 3
            st.session_state.stage3_done = False
            st.rerun()
        return

    st.markdown(f"""
    Now test **{top['name']}** against the off-target **{case['off_target']}** (PDB: `{case['off_target_pdb']}`).
    A good drug binds tightly to the target but weakly to the off-target.
    """)

    # Require REAL scores for both target and off-target
    target_score = resolve_score(case["id"], top, "target")
    off_score = resolve_score(case["id"], top, "off_target")

    # If off-target score is missing, offer to dock it live
    if off_score is None and DOCKING_AVAILABLE:
        st.warning(
            f"⚠️ No real off-target docking score for {top['name']} yet. "
            f"Dock it against {case['off_target']} now to continue."
        )
        if st.button(f"⚡ Dock {top['name']} vs {case['off_target']} (real Vina)", type="primary"):
            from docking import dock, save_score
            with st.spinner(f"Running real Vina docking against {case['off_target']}..."):
                ok, result = dock(top["smiles"], case["off_target_pdb"], exhaustiveness=4)
            if ok:
                save_score(case["id"], top["name"], "off_target", result)
                off_score = result
                st.rerun()
            else:
                st.error(f"Docking failed: {result}")
        return

    # If we still don't have both real scores, refuse to show fake data
    if target_score is None or off_score is None:
        st.error(
            "❌ Real docking scores aren't available for this selectivity test, and "
            "the docking engine isn't usable in this environment. "
            "Run `python precompute_docking.py` to generate real scores. "
            "This stage will not show estimated numbers."
        )
        return

    # Compute selectivity from REAL scores (selective if target binds
    # meaningfully stronger than off-target)
    is_selective = (target_score < off_score - 0.5)
    sel_msg = sel.get("msg", "")  # keep the educational explanation

    st.caption("🟢 Showing **real AutoDock Vina** docking scores.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            f"Target ({case['target_protein']})",
            f"{target_score} kcal/mol",
            "Strong bind ✓"
        )
    with col2:
        delta_label = "Weak bind ✓" if is_selective else "Too strong ✗"
        st.metric(
            f"Off-target ({case['off_target']})",
            f"{off_score} kcal/mol",
            delta_label,
            delta_color="normal" if is_selective else "inverse"
        )

    selectivity_ratio = round(off_score / target_score, 2) if target_score else 0
    st.metric("Selectivity ratio (off/target)", selectivity_ratio)

    if not st.session_state.stage4_done:
        if is_selective:
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Selectivity confirmed (+30 points)</strong><br>{sel_msg}
            </div>
            """, unsafe_allow_html=True)
            add_score(30)
            add_badge("⚖️ Selectivity Sage")
        else:
            st.markdown(f"""
            <div class="danger-box">
                <strong>❌ Poor selectivity</strong><br>
                The real docking shows this ligand binds the off-target almost as
                strongly as the target. {sel_msg}
            </div>
            """, unsafe_allow_html=True)
        st.session_state.stage4_done = True
        st.rerun()
    else:
        if st.button("Continue to stage 5 →", type="primary"):
            st.session_state.current_stage = 5
            st.rerun()


# ==================== STAGE 5: ADMET & FINAL ====================

def show_stage_5(case):
    st.subheader("Stage 5 — ADMET & drug-likeness")

    top = st.session_state.stage3_top_pick
    admet = case["admet"].get(top["name"])

    if not admet:
        st.error("No ADMET data for this candidate.")
        return

    st.markdown(f"Final check on **{top['name']}** — does it satisfy Lipinski's Rule of 5?")

    # Build a table
    rules = [
        ("Molecular weight", admet["MW"], "< 500 Da", admet["MW"] < 500),
        ("LogP", admet["LogP"], "-0.5 to 5", -0.5 <= admet["LogP"] <= 5),
        ("H-bond donors", admet["HBD"], "≤ 5", admet["HBD"] <= 5),
        ("H-bond acceptors", admet["HBA"], "≤ 10", admet["HBA"] <= 10),
        ("Rotatable bonds", admet["RotBonds"], "≤ 10", admet["RotBonds"] <= 10),
    ]

    df = pd.DataFrame([
        {"Property": r[0], "Value": r[1], "Ideal": r[2], "Pass": "✅" if r[3] else "❌"}
        for r in rules
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not st.session_state.stage5_done:
        if admet["pass"]:
            add_score(15)
            add_badge("💎 Lipinski Compliant")

        if admet["warning"]:
            st.markdown(f"""
            <div class="warning-box">
                <strong>Post-market alert</strong><br>{admet['warning']}
            </div>
            """, unsafe_allow_html=True)
            if "FDA pulled" in admet["warning"] or "withdrawn" in admet["warning"].lower():
                add_score(-15)

        st.session_state.stage5_done = True
        st.rerun()
    else:
        if st.button("See final results →", type="primary"):
            st.session_state.current_stage = 6
            st.rerun()


# ==================== FINAL RESULT ====================

def show_final_result(case):
    st.subheader("🎉 Mission complete")

    score = st.session_state.score
    if score >= 90:
        title, badge = "Master Medicinal Chemist", "🥇"
    elif score >= 70:
        title, badge = "Drug Designer", "🥈"
    elif score >= 50:
        title, badge = "Junior Chemist", "🥉"
    else:
        title, badge = "Back to the textbooks", "📚"

    st.markdown(f"""
    <div style="background:#eef2ff; color:#1a1a2e; padding:2rem; border-radius:12px; text-align:center; border: 2px solid #5b6cff;">
        <div style="font-size:3rem; color:#1a1a2e;">{badge}</div>
        <div style="font-size:1.5rem; font-weight:500; color:#1a1a2e;">{title}</div>
        <div style="font-size:2rem; font-weight:bold; margin-top:1rem; color:#1a1a2e;">{score} / 100</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"_{case['ending']}_")

    # Badges earned
    if st.session_state.badges:
        st.markdown("### 🏆 Badges earned")
        badges_html = "".join([f'<span class="badge">{b}</span>' for b in st.session_state.badges])
        st.markdown(badges_html, unsafe_allow_html=True)

    # Submit to leaderboard
    from leaderboard import show_score_submission
    show_score_submission(case, score, st.session_state.badges)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Replay this case", use_container_width=True):
            reset_game()
            st.rerun()
    with col2:
        if st.button("📚 Try another case", use_container_width=True, type="primary"):
            from cases import CASES
            next_index = (st.session_state.case_index + 1) % len(CASES)
            st.session_state.case_index = next_index
            reset_game()
            st.rerun()
