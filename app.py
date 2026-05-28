"""
Drug Hunter — Educational Game
Developed by Sarang Dhote, Shivaji Science College, Nagpur
"""

import streamlit as st

st.set_page_config(
    page_title="Drug Hunter",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.block-container{padding-top:.5rem!important;}
.dh-topbar{
    background:linear-gradient(135deg,#0D1B2A 0%,#1A3A5C 100%);
    padding:10px 16px 8px;border-radius:10px;margin-bottom:12px;
    display:flex;align-items:center;justify-content:space-between;
    flex-wrap:wrap;gap:6px;
}
.dh-title{font-size:1.35rem;font-weight:700;color:#fff!important;margin:0;}
.dh-subtitle{font-size:.72rem;color:#90CAF9!important;margin:0;}
.dh-score-pill{
    background:rgba(255,255,255,.15);border-radius:20px;
    padding:4px 14px;font-size:.82rem;color:#fff!important;white-space:nowrap;
}
.dh-score-pill b{color:#FFD54F!important;}
.dh-stepper{
    display:flex;align-items:center;justify-content:space-between;
    margin:14px 0 8px;padding:0 2px;
}
.dh-step{display:flex;flex-direction:column;align-items:center;flex:1;}
.dh-step-circle{
    width:28px;height:28px;border-radius:50%;display:flex;
    align-items:center;justify-content:center;
    font-size:.75rem;font-weight:700;z-index:2;
}
.dh-step-circle.done  {background:#1A7A6E;color:#fff;}
.dh-step-circle.active{background:#1565C0;color:#fff;
                        box-shadow:0 0 0 3px rgba(21,101,192,.25);}
.dh-step-circle.todo  {background:#E2E8F0;color:#94A3B8;}
.dh-step-label{font-size:.62rem;text-align:center;margin-top:3px;
               line-height:1.2;color:#64748B;max-width:52px;}
.dh-step-label.active-lbl{color:#1565C0;font-weight:600;}
.dh-step-label.done-lbl{color:#1A7A6E;}
.dh-connector{flex:1;height:3px;margin-bottom:18px;border-radius:2px;}
.dh-connector.done{background:#1A7A6E;}
.dh-connector.todo{background:#E2E8F0;}
.case-card{background:#eef2ff!important;color:#1a1a2e!important;
           padding:1rem 1.25rem;border-radius:10px;
           border-left:4px solid #5b6cff;margin-bottom:1rem;}
.case-card *{color:#1a1a2e!important;}
.success-box{background:#e8f5e9!important;color:#1b5e20!important;
             padding:1rem;border-radius:8px;
             border-left:4px solid #2e7d32;margin:.75rem 0;}
.success-box *{color:#1b5e20!important;}
.danger-box{background:#ffebee!important;color:#b71c1c!important;
            padding:1rem;border-radius:8px;
            border-left:4px solid #c62828;margin:.75rem 0;}
.danger-box *{color:#b71c1c!important;}
.warning-box{background:#fff8e1!important;color:#e65100!important;
             padding:1rem;border-radius:8px;
             border-left:4px solid #f57f17;margin:.75rem 0;}
.warning-box *{color:#e65100!important;}
.badge{display:inline-block;background:#e3f2fd!important;
       color:#0d47a1!important;padding:4px 12px;
       border-radius:12px;font-size:.85rem;margin:4px;font-weight:500;}
@media(max-width:600px){
    .dh-title{font-size:1.1rem;}
    .dh-step-circle{width:24px;height:24px;font-size:.65rem;}
    .dh-step-label{font-size:.58rem;max-width:44px;}
}
</style>
""", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────────────────────
from cases import CASES
from utils import (
    init_session_state, reset_game,
    show_top_bar, show_progress_stepper,
    show_stage_1, show_stage_2, show_stage_3,
    show_stage_4, show_stage_5, show_final_result,
)
from leaderboard import show_leaderboard_page, show_player_lookup

# ── Init ──────────────────────────────────────────────────────────────────────
init_session_state()
if "page" not in st.session_state:
    st.session_state.page = "🎮 Play"

# ── Sidebar (desktop) ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 Drug Hunter")
    st.caption("By Sarang Dhote · Shivaji Science College, Nagpur")
    st.divider()
    case_names = [f"{i+1}. {c['title']}" for i, c in enumerate(CASES)]
    sb_idx = st.selectbox(
        "Case", range(len(CASES)),
        format_func=lambda i: case_names[i],
        index=st.session_state.case_index,
        key="sb_case",
    )
    if sb_idx != st.session_state.case_index:
        st.session_state.case_index = sb_idx
        reset_game()
        st.rerun()
    st.divider()
    st.metric("Score", st.session_state.score)
    st.metric("Stage", f"{st.session_state.current_stage}/5")
    st.divider()
    if st.button("🔄 Reset case", use_container_width=True):
        reset_game()
        st.rerun()
    st.caption(f"📊 {len(CASES)} cases  ·  Real AutoDock Vina")

# ── Main area ─────────────────────────────────────────────────────────────────
page = st.session_state.page
case = CASES[st.session_state.case_index]

show_top_bar(case, page)

# Horizontal navigation (visible on mobile)
NAV = ["🎮 Play", "🏆 Leaderboard", "🔍 Player stats"]
selected = st.radio(
    "", NAV,
    index=NAV.index(page),
    horizontal=True,
    key="main_nav",
    label_visibility="collapsed",
)
if selected != page:
    st.session_state.page = selected
    st.rerun()

st.divider()

# ── Play page ─────────────────────────────────────────────────────────────────
if page == "🎮 Play":

    # Inline case selector (always visible — needed on mobile)
    new_idx = st.selectbox(
        "📂 Select case",
        range(len(CASES)),
        index=st.session_state.case_index,
        format_func=lambda i: case_names[i],
        key="main_case",
    )
    if new_idx != st.session_state.case_index:
        st.session_state.case_index = new_idx
        reset_game()
        st.rerun()

    case = CASES[st.session_state.case_index]
    st.caption(f"🏥 {case['disease']}  ·  {case['difficulty']}")
    show_progress_stepper()
    st.divider()

    stage = st.session_state.current_stage
    if   stage == 1: show_stage_1(case)
    elif stage == 2: show_stage_2(case)
    elif stage == 3: show_stage_3(case)
    elif stage == 4: show_stage_4(case)
    elif stage == 5: show_stage_5(case)
    else:            show_final_result(case)

elif page == "🏆 Leaderboard":
    show_leaderboard_page()
elif page == "🔍 Player stats":
    show_player_lookup()
