"""
Drug Hunter — Leaderboard
Developed by Sarang Dhote, Shivaji Science College, Nagpur

Local JSON storage by default.
Google Sheets when GSHEETS_ID + GSHEETS_SCRIPT_URL are in st.secrets.
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

LEADERBOARD_FILE = Path("leaderboard.json")
HEADERS = ["player","case_id","case_title","score","badges_count","badges","timestamp"]


def _sheet_id():
    try:
        return st.secrets.get("GSHEETS_ID", None)
    except Exception:
        return None


def _script_url():
    try:
        return st.secrets.get("GSHEETS_SCRIPT_URL", None)
    except Exception:
        return None


def _load_sheets():
    sid = _sheet_id()
    if not sid:
        return None
    try:
        import io
        url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid=0"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read().decode("utf-8")
        if not content.strip():
            return []
        df = pd.read_csv(io.StringIO(content))
        records = df.to_dict(orient="records")
        for r in records:
            for col in ["score","case_id","badges_count"]:
                try:
                    r[col] = int(float(r.get(col, 0) or 0))
                except Exception:
                    r[col] = 0
        return records
    except Exception:
        return None


def _write_sheets(entry):
    url = _script_url()
    if not url:
        return False
    try:
        payload = json.dumps({h: entry.get(h, "") for h in HEADERS})
        data = urllib.parse.urlencode({"data": payload}).encode()
        req  = urllib.request.Request(url, data=data, method="POST",
                                      headers={"Content-Type":"application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return "success" in r.read().decode().lower()
    except Exception:
        return False


def _load_local():
    if LEADERBOARD_FILE.exists():
        try:
            with open(LEADERBOARD_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_local(entries):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
        return True
    except Exception:
        return False


def load_leaderboard():
    if _sheet_id():
        data = _load_sheets()
        if data is not None:
            return data
    return _load_local()


def add_entry(player, case_id, case_title, score, badges):
    if not (player or "").strip():
        return False
    entry = {
        "player":       player.strip()[:30],
        "case_id":      int(case_id),
        "case_title":   str(case_title),
        "score":        int(score),
        "badges_count": len(badges),
        "badges":       ", ".join(badges),
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    if _sheet_id():
        if _write_sheets(entry):
            return True
    entries = _load_local()
    entries.append(entry)
    entries.sort(key=lambda x: x["score"], reverse=True)
    return _save_local(entries[:500])


def get_player_stats(name):
    if not name:
        return None
    entries = [e for e in load_leaderboard()
               if str(e.get("player","")).lower() == name.lower()]
    if not entries:
        return None
    return {
        "total_games":  len(entries),
        "best_score":   max(e["score"] for e in entries),
        "avg_score":    round(sum(e["score"] for e in entries) / len(entries), 1),
        "cases_played": len(set(e["case_id"] for e in entries)),
        "total_badges": sum(e.get("badges_count", 0) for e in entries),
    }


# ── UI ────────────────────────────────────────────────────────────────────────

def show_leaderboard_page():
    st.header("🏆 Leaderboard")
    if _sheet_id():
        st.caption("🟢 Connected to Google Sheets — live global leaderboard.")
    else:
        st.caption("🟡 Local storage. See README for Google Sheets setup.")

    entries = load_leaderboard()
    if not entries:
        st.info("No scores yet. Be the first!")
        return

    from cases import CASES
    opts = ["All cases"] + [f"{c['id']}. {c['title']}" for c in CASES]
    col1, col2 = st.columns([3, 1])
    with col1:
        sel = st.selectbox("Filter by case", opts)
    with col2:
        top_n = st.selectbox("Show", [10, 25, 50])

    filtered = entries if sel == "All cases" else [
        e for e in entries if e.get("case_id") == int(sel.split(".")[0])
    ]
    filtered = sorted(filtered, key=lambda x: x.get("score",0), reverse=True)[:top_n]
    if not filtered:
        st.info("No scores for this case yet.")
        return

    medals = {1:"🥇", 2:"🥈", 3:"🥉"}
    rows = []
    for i, e in enumerate(filtered, 1):
        rows.append({
            "Rank":    medals.get(i, f"#{i}"),
            "Player":  e.get("player",""),
            "Case":    e.get("case_title",""),
            "Score":   e.get("score", 0),
            "Badges":  e.get("badges_count", 0),
            "Date":    e.get("timestamp",""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if len(filtered) >= 3:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("🥇", filtered[0]["player"], f"{filtered[0]['score']} pts")
        c2.metric("🥈", filtered[1]["player"], f"{filtered[1]['score']} pts")
        c3.metric("🥉", filtered[2]["player"], f"{filtered[2]['score']} pts")


def show_score_submission(case, score, badges):
    if st.session_state.get("score_submitted"):
        st.success("✅ Score submitted!")
        return
    st.divider()
    st.subheader("📊 Submit your score")
    name = st.text_input("Your name", max_chars=30,
                         placeholder="e.g. Rahul S.",
                         key="lb_name")
    if st.button("🏆 Submit", type="primary", disabled=not (name or "").strip()):
        if add_entry(name, case["id"], case["title"], score, badges):
            st.session_state.score_submitted = True
            st.balloons()
            st.rerun()
        else:
            st.error("Failed to save. Try again.")


def show_player_lookup():
    st.subheader("🔍 Player stats")
    name = st.text_input("Enter player name")
    if name:
        s = get_player_stats(name)
        if s:
            c1, c2, c3 = st.columns(3)
            c1.metric("Best score",   s["best_score"])
            c2.metric("Games played", s["total_games"])
            c3.metric("Cases tried",  s["cases_played"])
        else:
            st.info(f"No records for '{name}'.")
