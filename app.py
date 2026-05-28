"""
Drug Hunter — Educational Game
Developed by Sarang Dhote, Shivaji Science College, Nagpur
"""

import streamlit as st
from cases import CASES
from utils import (
    init_session_state, reset_game,
    show_stage_1, show_stage_2, show_stage_3,
    show_stage_4, show_stage_5, show_final_result,
    show_top_bar, show_progress_stepper,
)
from leaderboard import show_leaderboard_page, show_player_lookup

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drug Hunter",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed",   # collapsed by default → works on mobile
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Remove default Streamlit top padding ── */
.block-container { padding-top: 0.5rem !important; }

/* ── Top branding bar ── */
.dh-topbar {
    background: linear-gradient(135deg, #0D1B2A 0%, #1A3A5C 100%);
    color: #ffffff;
    padding: 10px 16px 8px 16px;
    border-radius: 10px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 6px;
}
.dh-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff !important;
    letter-spacing: 0.5px;
    margin: 0;
}
.dh-subtitle {
    font-size: 0.72rem;
    color: #90CAF9 !important;
    margin: 0;
}
.dh-score-pill {
    background: rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    color: #ffffff !important;
    white-space: nowrap;
}
.dh-score-pill b { color: #FFD54F !important; }

/* ── Mobile nav tabs ── */
.dh-nav {
    display: flex;
    gap: 6px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}
.dh-nav-btn {
    flex: 1;
    min-width: 90px;
    padding: 7px 4px;
    border-radius: 8px;
    border: 1.5px solid #CBD5E1;
    background: transparent;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    color: #475569;
    transition: all 0.15s;
}
.dh-nav-btn.active {
    background: #0D1B2A;
    color: #ffffff !important;
    border-color: #0D1B2A;
}

/* ── Case selector row ── */
.dh-case-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}

/* ── Progress stepper ── */
.dh-stepper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 14px 0 8px 0;
    padding: 0 2px;
}
.dh-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}
.dh-step-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    z-index: 2;
    position: relative;
}
.dh-step-circle.done   { background: #1A7A6E; color: #fff; }
.dh-step-circle.active { background: #1565C0; color: #fff;
                          box-shadow: 0 0 0 3px rgba(21,101,192,0.25); }
.dh-step-circle.todo   { background: #E2E8F0; color: #94A3B8; }
.dh-step-label {
    font-size: 0.62rem;
    text-align: center;
    margin-top: 3px;
    line-height: 1.2;
    color: #64748B;
    max-width: 52px;
}
.dh-step-label.active-lbl { color: #1565C0; font-weight: 600; }
.dh-step-label.done-lbl   { color: #1A7A6E; }
.dh-connector {
    flex: 1;
    height: 3px;
    margin-bottom: 18px;
    border-radius: 2px;
    max-width: 100%;
}
.dh-connector.done   { background: #1A7A6E; }
.dh-connector.active { background: linear-gradient(90deg, #1A7A6E 50%, #E2E8F0 50%); }
.dh-connector.todo   { background: #E2E8F0; }

/* ── Feedback boxes — colour-safe for dark + light mode ── */
.case-card  { background:#eef2ff!important; color:#1a1a2e!important;
              padding:1rem 1.25rem; border-radius:10px;
              border-left:4px solid #5b6cff; margin-bottom:1rem; }
.case-card *{ color:#1a1a2e!important; }
.success-box{ background:#e8f5e9!important; color:#1b5e20!important;
              padding:1rem; border-radius:8px;
              border-left:4px solid #2e7d32; margin:0.75rem 0; }
.success-box *{ color:#1b5e20!important; }
.danger-box { background:#ffebee!important; color:#b71c1c!important;
              padding:1rem; border-radius:8px;
              border-left:4px solid #c62828; margin:0.75rem 0; }
.danger-box *{ color:#b71c1c!important; }
.warning-box{ background:#fff8e1!important; color:#e65100!important;
              padding:1rem; border-radius:8px;
              border-left:4px solid #f57f17; margin:0.75rem 0; }
.warning-box *{ color:#e65100!important; }
.badge { display:inline-block; background:#e3f2fd!important;
         color:#0d47a1!important; padding:4px 12px;
         border-radius:12px; font-size:0.85rem; margin:4px; font-weight:500; }

/* ── Make st.radio labels bigger on mobile ── */
@media (max-width: 600px) {
    .dh-title  { font-size: 1.15rem; }
    .dh-stepper{ margin: 10px 0 6px; }
    .dh-step-circle { width: 24px; height: 24px; font-size: 0.68rem; }
    .dh-step-label  { font-size: 0.58rem; max-width: 44px; }
}
</style>
""", unsafe_allow_html=True)

# ── Startup health check — shows readable error instead of blank crash ────────
try:
    from docking import health_check, VINA_OK, RDKIT_OK
    _ok, _msg = health_check()
    if not _ok:
        st.error(f"⚠️ Docking engine issue: {_msg}")
        st.info("The game can still run using pre-computed scores. "
                "Live docking will be unavailable until the issue is resolved.")
except Exception as _e:
    st.warning(f"Could not load docking module: {_e}. "
               "Pre-computed scores will be used if available.")

# ── Session state ─────────────────────────────────────────────────────────────
init_session_state()
if "page" not in st.session_state:
    st.session_state.page = "🎮 Play"

# ── Sidebar (desktop helper — not relied on for navigation) ───────────────────
with st.sidebar:
    st.markdown("### 🧬 Drug Hunter")
    st.caption("By Sarang Dhote · Shivaji Science College, Nagpur")
    st.divider()
    if st.session_state.get("page") == "🎮 Play":
        case_names = [f"{i+1}. {c['title']}" for i, c in enumerate(CASES)]
        idx = st.selectbox(
            "Case", range(len(CASES)),
            format_func=lambda i: case_names[i],
            key="sidebar_case",
            label_visibility="visible",
        )
        if st.session_state.case_index != idx:
            st.session_state.case_index = idx
            reset_game()
            st.rerun()
        st.divider()
        st.metric("Score", st.session_state.score)
        st.metric("Stage", f"{st.session_state.current_stage} / 5")
        st.divider()
        if st.button("🔄 Reset", use_container_width=True):
            reset_game()
            st.rerun()
    st.caption(f"📊 {len(CASES)} cases  ·  Real AutoDock Vina")

# ── Main content ──────────────────────────────────────────────────────────────
page = st.session_state.page
case = CASES[st.session_state.case_index]

# Always-visible top bar (shows on mobile too)
show_top_bar(case, page)

# Mobile-friendly tab navigation
nav_labels = ["🎮 Play", "🏆 Leaderboard", "🔍 Player stats"]
selected_tab = st.radio(
    "nav", nav_labels,
    index=nav_labels.index(page),
    horizontal=True,
    key="main_nav",
    label_visibility="collapsed",
)
if selected_tab != page:
    st.session_state.page = selected_tab
    st.rerun()

st.divider()

# ── Page routing ──────────────────────────────────────────────────────────────
if page == "🎮 Play":

    # Mobile-friendly case selector (inline, always visible)
    case_names = [f"{i+1}. {c['title']}" for i, c in enumerate(CASES)]
    new_idx = st.selectbox(
        "📂 Select case",
        range(len(CASES)),
        index=st.session_state.case_index,
        format_func=lambda i: case_names[i],
        key="main_case_selector",
        label_visibility="visible",
    )
    if new_idx != st.session_state.case_index:
        st.session_state.case_index = new_idx
        reset_game()
        st.rerun()
        case = CASES[new_idx]

    # Case info + progress stepper
    st.caption(f"🏥 {case['disease']}  ·  {case['difficulty']}")
    show_progress_stepper()

    st.divider()

    stage = st.session_state.current_stage
    if stage == 1:   show_stage_1(case)
    elif stage == 2: show_stage_2(case)
    elif stage == 3: show_stage_3(case)
    elif stage == 4: show_stage_4(case)
    elif stage == 5: show_stage_5(case)
    elif stage == 6: show_final_result(case)

elif page == "🏆 Leaderboard":
    show_leaderboard_page()

elif page == "🔍 Player stats":
    show_player_lookup()
