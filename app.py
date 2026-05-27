"""
CSI: Drug Discovery — Educational Game
Built for UG/PG students learning molecular docking.

Author: Your Name
License: MIT
"""

import streamlit as st
from cases import CASES
from utils import (
    init_session_state,
    reset_game,
    show_header,
    show_progress_bar,
    show_stage_1,
    show_stage_2,
    show_stage_3,
    show_stage_4,
    show_stage_5,
    show_final_result,
)
from leaderboard import show_leaderboard_page, show_player_lookup

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="CSI: Drug Discovery",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    .case-card {
        background-color: #f5f5f7;
        padding: 1rem 1.25rem;
        border-radius: 10px;
        border-left: 4px solid #5b6cff;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e7d32;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #c62828;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff8e1;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f57f17;
        margin: 1rem 0;
    }
    .badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        margin: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- INIT SESSION --------------------
init_session_state()
if "page" not in st.session_state:
    st.session_state.page = "Play"

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.title("🧬 CSI Drug Discovery")
    st.caption("An educational game for UG/PG students")

    st.divider()

    # Page navigation
    page = st.radio(
        "Navigate",
        ["🎮 Play", "🏆 Leaderboard", "🔍 Player stats"],
        key="page_nav",
        label_visibility="collapsed"
    )

    st.divider()

    # Show case selector only on Play page
    if page == "🎮 Play":
        st.subheader("Select a case")
        case_names = [f"{i+1}. {c['title']}" for i, c in enumerate(CASES)]
        selected_case_index = st.selectbox(
            "Choose a disease case",
            range(len(CASES)),
            format_func=lambda i: case_names[i],
            key="case_selector",
            label_visibility="collapsed"
        )

        if st.session_state.case_index != selected_case_index:
            st.session_state.case_index = selected_case_index
            reset_game()
            st.rerun()

        st.divider()

        # Score display
        st.metric("Current score", f"{st.session_state.score}")
        st.metric("Current stage", f"{st.session_state.current_stage} / 5")

        st.divider()

        # Reset button
        if st.button("🔄 Reset case", use_container_width=True):
            reset_game()
            st.rerun()

    st.divider()
    st.caption(f"📊 {len(CASES)} cases available")
    st.caption("💡 Built with Streamlit")

# -------------------- MAIN AREA --------------------

if page == "🎮 Play":
    case = CASES[st.session_state.case_index]

    show_header(case)
    show_progress_bar()

    st.divider()

    stage = st.session_state.current_stage

    if stage == 1:
        show_stage_1(case)
    elif stage == 2:
        show_stage_2(case)
    elif stage == 3:
        show_stage_3(case)
    elif stage == 4:
        show_stage_4(case)
    elif stage == 5:
        show_stage_5(case)
    elif stage == 6:
        show_final_result(case)

elif page == "🏆 Leaderboard":
    show_leaderboard_page()

elif page == "🔍 Player stats":
    show_player_lookup()
