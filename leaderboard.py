"""
Leaderboard module for CSI Drug Discovery game.

Two storage backends supported:
1. LOCAL JSON FILE (default) — works offline, perfect for local/classroom use
2. GOOGLE SHEETS (optional) — works on Streamlit Cloud, public leaderboard

To enable Google Sheets:
1. Create a Google Sheet, share it as "Anyone with link can edit"
2. Set GSHEETS_URL in Streamlit secrets (.streamlit/secrets.toml):
     GSHEETS_URL = "https://docs.google.com/spreadsheets/d/..."
"""

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd

LEADERBOARD_FILE = Path("leaderboard.json")
MAX_ENTRIES = 100  # Keep only top 100


# ==================== STORAGE BACKEND ====================

def _load_local():
    """Load leaderboard from local JSON file."""
    if LEADERBOARD_FILE.exists():
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_local(entries):
    """Save leaderboard to local JSON file."""
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
        return True
    except IOError:
        return False


def _load_gsheets():
    """Load from Google Sheets if configured."""
    try:
        gsheets_url = st.secrets.get("GSHEETS_URL", None)
        if not gsheets_url:
            return None
        # Convert /edit URL to CSV export URL
        if "/edit" in gsheets_url:
            csv_url = gsheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
            csv_url = csv_url.replace("/edit?gid=", "/export?format=csv&gid=")
            if "/edit" in csv_url:
                csv_url = csv_url.split("/edit")[0] + "/export?format=csv"
        else:
            csv_url = gsheets_url

        df = pd.read_csv(csv_url)
        return df.to_dict(orient="records")
    except Exception:
        return None


# ==================== PUBLIC API ====================

def load_leaderboard():
    """Load all leaderboard entries."""
    # Try Google Sheets first if configured
    gs = _load_gsheets()
    if gs is not None:
        return gs
    return _load_local()


def add_entry(player_name, case_id, case_title, score, badges):
    """Add a new score entry to the leaderboard."""
    if not player_name or not player_name.strip():
        return False

    entries = _load_local()  # We always write locally
    entries.append({
        "player": player_name.strip()[:30],  # Limit name length
        "case_id": case_id,
        "case_title": case_title,
        "score": int(score),
        "badges_count": len(badges),
        "badges": ", ".join(badges),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })

    # Sort by score (descending) and keep top entries
    entries.sort(key=lambda x: x["score"], reverse=True)
    entries = entries[:MAX_ENTRIES]

    return _save_local(entries)


def get_top_scores(case_id=None, limit=10):
    """Get top scores. Filter by case_id if provided."""
    entries = load_leaderboard()
    if case_id is not None:
        entries = [e for e in entries if e.get("case_id") == case_id]
    return sorted(entries, key=lambda x: x.get("score", 0), reverse=True)[:limit]


def get_player_stats(player_name):
    """Get stats for a specific player."""
    if not player_name:
        return None
    entries = load_leaderboard()
    player_entries = [e for e in entries if e.get("player", "").lower() == player_name.lower()]
    if not player_entries:
        return None
    return {
        "total_games": len(player_entries),
        "best_score": max(e["score"] for e in player_entries),
        "avg_score": round(sum(e["score"] for e in player_entries) / len(player_entries), 1),
        "cases_played": len(set(e["case_id"] for e in player_entries)),
        "total_badges": sum(e.get("badges_count", 0) for e in player_entries),
    }


# ==================== UI COMPONENTS ====================

def show_leaderboard_page():
    """Render the leaderboard page (called from sidebar nav)."""
    st.header("🏆 Leaderboard")

    entries = load_leaderboard()

    if not entries:
        st.info("No scores yet. Be the first to play and claim the top spot!")
        return

    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        from cases import CASES
        case_options = ["All cases"] + [f"{c['id']}. {c['title']}" for c in CASES]
        selected = st.selectbox("Filter by case", case_options)
    with col2:
        top_n = st.selectbox("Show top", [10, 25, 50, 100], index=0)

    # Apply filter
    if selected == "All cases":
        filtered = entries
    else:
        case_id = int(selected.split(".")[0])
        filtered = [e for e in entries if e.get("case_id") == case_id]

    filtered = sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)[:top_n]

    if not filtered:
        st.info("No scores for this case yet.")
        return

    # Display as table
    df = pd.DataFrame(filtered)
    df.index = range(1, len(df) + 1)  # Rank starting from 1
    df.index.name = "Rank"

    # Add medal emojis for top 3
    def medal(rank):
        return {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")

    df_display = df[["player", "case_title", "score", "badges_count", "timestamp"]].copy()
    df_display.columns = ["Player", "Case", "Score", "Badges", "Date"]
    df_display.insert(0, "Rank", [medal(i) for i in df_display.index])

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Top 3 highlight
    if len(filtered) >= 3:
        st.divider()
        st.subheader("🌟 Top performers")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🥇 Champion", filtered[0]["player"], f"{filtered[0]['score']} pts")
        with c2:
            st.metric("🥈 Runner-up", filtered[1]["player"], f"{filtered[1]['score']} pts")
        with c3:
            st.metric("🥉 Third", filtered[2]["player"], f"{filtered[2]['score']} pts")


def show_score_submission(case, score, badges):
    """Show form to submit score to leaderboard."""
    if "score_submitted" not in st.session_state:
        st.session_state.score_submitted = False

    if st.session_state.score_submitted:
        st.success("✅ Your score has been submitted to the leaderboard!")
        return

    st.divider()
    st.subheader("📊 Submit your score")
    st.caption("Add your score to the global leaderboard")

    player_name = st.text_input(
        "Your name",
        max_chars=30,
        placeholder="e.g., Rahul S.",
        key="leaderboard_name_input"
    )

    if st.button("🏆 Submit to leaderboard", type="primary", disabled=not player_name.strip()):
        success = add_entry(
            player_name=player_name,
            case_id=case["id"],
            case_title=case["title"],
            score=score,
            badges=badges,
        )
        if success:
            st.session_state.score_submitted = True
            st.balloons()
            st.rerun()
        else:
            st.error("Failed to save. Try again.")


def show_player_lookup():
    """Show player stats lookup form."""
    st.subheader("🔍 Look up a player")
    name = st.text_input("Player name", placeholder="Enter player name")
    if name:
        stats = get_player_stats(name)
        if stats:
            col1, col2, col3 = st.columns(3)
            col1.metric("Best score", stats["best_score"])
            col2.metric("Games played", stats["total_games"])
            col3.metric("Cases tried", stats["cases_played"])

            col4, col5 = st.columns(2)
            col4.metric("Avg score", stats["avg_score"])
            col5.metric("Total badges", stats["total_badges"])
        else:
            st.info(f"No records found for '{name}'.")
