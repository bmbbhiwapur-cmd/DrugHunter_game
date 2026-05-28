"""
Leaderboard for DockQuest / CSI Drug Discovery game.

Supports two backends — auto-detected:

1. GOOGLE SHEETS (active when GSHEETS_ID is in Streamlit secrets)
   - Uses the public Sheets API (no service account needed!)
   - Sheet must be shared as "Anyone with the link → Editor"
   - Reads via CSV export URL (free, no API key)
   - Writes via Google Apps Script Web App (free, one-time setup)

2. LOCAL JSON (fallback when no secrets configured)
   - Saves to leaderboard.json on the server
   - Works offline / for classroom single-server use

See GOOGLE_SHEETS_SETUP.md for full instructions.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd

LEADERBOARD_FILE = Path("leaderboard.json")
MAX_ENTRIES = 500
SHEET_HEADERS = ["player", "case_id", "case_title", "score",
                 "badges_count", "badges", "timestamp"]


# ============================================================
# DETECT WHICH BACKEND IS CONFIGURED
# ============================================================

def _get_sheets_config():
    """
    Returns (sheet_id, apps_script_url) from st.secrets, or (None, None).
    Both values must be present to use Google Sheets.
    """
    try:
        sheet_id = st.secrets.get("GSHEETS_ID", None)
        script_url = st.secrets.get("GSHEETS_SCRIPT_URL", None)
        if sheet_id and script_url:
            return sheet_id, script_url
    except Exception:
        pass
    return None, None


def _using_gsheets():
    sheet_id, _ = _get_sheets_config()
    return sheet_id is not None


# ============================================================
# GOOGLE SHEETS BACKEND
# ============================================================

def _load_gsheets():
    """
    Read the sheet as CSV using the public export URL.
    No API key needed — works as long as the sheet is publicly readable.
    """
    sheet_id, _ = _get_sheets_config()
    if not sheet_id:
        return None
    try:
        # Google Sheets CSV export — works for any "Anyone can view" sheet
        csv_url = (
            f"https://docs.google.com/spreadsheets/d/{sheet_id}"
            f"/export?format=csv&gid=0"
        )
        req = urllib.request.Request(
            csv_url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")

        if not content.strip():
            return []

        import io
        df = pd.read_csv(io.StringIO(content))

        # Normalise column types
        records = df.to_dict(orient="records")
        for r in records:
            try:
                r["score"] = int(float(r.get("score", 0) or 0))
            except (ValueError, TypeError):
                r["score"] = 0
            try:
                r["case_id"] = int(float(r.get("case_id", 0) or 0))
            except (ValueError, TypeError):
                r["case_id"] = 0
            try:
                r["badges_count"] = int(float(r.get("badges_count", 0) or 0))
            except (ValueError, TypeError):
                r["badges_count"] = 0
        return records

    except Exception as e:
        print(f"Google Sheets read error: {e}")
        return None


def _write_gsheets(entry):
    """
    Append one row to the sheet via a Google Apps Script Web App.

    The Apps Script acts as a free authenticated writer —
    see GOOGLE_SHEETS_SETUP.md for the 2-minute setup.
    """
    _, script_url = _get_sheets_config()
    if not script_url:
        return False
    try:
        payload = json.dumps({h: entry.get(h, "") for h in SHEET_HEADERS})
        data = urllib.parse.urlencode({"data": payload}).encode()
        req = urllib.request.Request(
            script_url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            response_text = resp.read().decode()
            return "success" in response_text.lower()
    except Exception as e:
        print(f"Google Sheets write error: {e}")
        return False


# ============================================================
# LOCAL JSON BACKEND
# ============================================================

def _load_local():
    if LEADERBOARD_FILE.exists():
        try:
            with open(LEADERBOARD_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_local(entries):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
        return True
    except IOError:
        return False


# ============================================================
# PUBLIC API
# ============================================================

def load_leaderboard():
    """Load all entries from whichever backend is active."""
    if _using_gsheets():
        data = _load_gsheets()
        if data is not None:
            return data
    return _load_local()


def add_entry(player_name, case_id, case_title, score, badges):
    """Add a score entry. Writes to Google Sheets if configured, else local."""
    if not player_name or not player_name.strip():
        return False

    entry = {
        "player": player_name.strip()[:30],
        "case_id": int(case_id),
        "case_title": str(case_title),
        "score": int(score),
        "badges_count": len(badges),
        "badges": ", ".join(badges),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    if _using_gsheets():
        ok = _write_gsheets(entry)
        if ok:
            return True
        # fall through to local if write failed

    # Local JSON
    entries = _load_local()
    entries.append(entry)
    entries.sort(key=lambda x: x["score"], reverse=True)
    return _save_local(entries[:MAX_ENTRIES])


def get_top_scores(case_id=None, limit=10):
    entries = load_leaderboard()
    if case_id is not None:
        entries = [e for e in entries if e.get("case_id") == case_id]
    return sorted(entries, key=lambda x: x.get("score", 0), reverse=True)[:limit]


def get_player_stats(player_name):
    if not player_name:
        return None
    entries = load_leaderboard()
    pe = [e for e in entries
          if str(e.get("player", "")).lower() == player_name.lower()]
    if not pe:
        return None
    return {
        "total_games": len(pe),
        "best_score": max(e["score"] for e in pe),
        "avg_score": round(sum(e["score"] for e in pe) / len(pe), 1),
        "cases_played": len(set(e["case_id"] for e in pe)),
        "total_badges": sum(e.get("badges_count", 0) for e in pe),
    }


# ============================================================
# UI COMPONENTS
# ============================================================

def show_leaderboard_page():
    st.header("🏆 Leaderboard")

    if _using_gsheets():
        st.caption("🟢 Connected to Google Sheets — live global leaderboard.")
    else:
        st.caption("🟡 Local storage — see GOOGLE_SHEETS_SETUP.md to enable global leaderboard.")

    entries = load_leaderboard()

    if not entries:
        st.info("No scores yet. Be the first to play!")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        from cases import CASES
        options = ["All cases"] + [f"{c['id']}. {c['title']}" for c in CASES]
        selected = st.selectbox("Filter by case", options)
    with col2:
        top_n = st.selectbox("Show top", [10, 25, 50, 100])

    filtered = entries if selected == "All cases" else [
        e for e in entries
        if e.get("case_id") == int(selected.split(".")[0])
    ]
    filtered = sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)[:top_n]

    if not filtered:
        st.info("No scores for this case yet.")
        return

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    df = pd.DataFrame(filtered)
    df.index = range(1, len(df) + 1)
    cols = ["player", "case_title", "score", "badges_count", "timestamp"]
    # only keep columns that exist
    cols = [c for c in cols if c in df.columns]
    df_display = df[cols].copy()
    df_display.columns = ["Player", "Case", "Score", "Badges", "Date"][:len(cols)]
    df_display.insert(0, "Rank", [medals.get(i, f"#{i}") for i in df_display.index])
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    if len(filtered) >= 3:
        st.divider()
        st.subheader("🌟 Top performers")
        c1, c2, c3 = st.columns(3)
        c1.metric("🥇", filtered[0]["player"], f"{filtered[0]['score']} pts")
        c2.metric("🥈", filtered[1]["player"], f"{filtered[1]['score']} pts")
        c3.metric("🥉", filtered[2]["player"], f"{filtered[2]['score']} pts")


def show_score_submission(case, score, badges):
    if "score_submitted" not in st.session_state:
        st.session_state.score_submitted = False

    if st.session_state.score_submitted:
        st.success("✅ Score submitted to the leaderboard!")
        return

    st.divider()
    st.subheader("📊 Submit your score")

    player_name = st.text_input(
        "Your name", max_chars=30,
        placeholder="e.g., Rahul S.",
        key="leaderboard_name_input"
    )

    if st.button("🏆 Submit to leaderboard", type="primary",
                 disabled=not (player_name or "").strip()):
        ok = add_entry(player_name, case["id"], case["title"], score, badges)
        if ok:
            st.session_state.score_submitted = True
            st.balloons()
            st.rerun()
        else:
            st.error("Failed to save. Try again.")


def show_player_lookup():
    st.subheader("🔍 Look up a player")
    name = st.text_input("Player name", placeholder="Enter player name")
    if name:
        stats = get_player_stats(name)
        if stats:
            c1, c2, c3 = st.columns(3)
            c1.metric("Best score", stats["best_score"])
            c2.metric("Games played", stats["total_games"])
            c3.metric("Cases tried", stats["cases_played"])
            c4, c5 = st.columns(2)
            c4.metric("Avg score", stats["avg_score"])
            c5.metric("Total badges", stats["total_badges"])
        else:
            st.info(f"No records for '{name}'.")
