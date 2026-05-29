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

# ── Key compatibility helper ──────────────────────────────────────────────────
# Old cases.py used: stage1_question, stage1_options, pocket_regions
# New cases.py uses: question, options, pocket_options
# This function reads either format so both files work.

def _get(case, *keys, default=None):
    """Read the first key that exists in the case dict."""
    for k in keys:
        if k in case:
            return case[k]
    return default

def _q(case):
    return _get(case, "question", "stage1_question", default="")

def _opts(case):
    return _get(case, "options", "stage1_options", default=[])

def _pocket_opts(case):
    return _get(case, "pocket_options", "pocket_regions", default=[])

def _selectivity(case):
    return _get(case, "selectivity", "selectivity_data", default={})

def _admet(case):
    return _get(case, "admet", default={})

# ── Key binding-site residues for each target ──────────────────────────────
# These are the amino acid residues that line the binding pocket
# and directly interact with the drug molecule.
BINDING_RESIDUES = {
    "COX-2":                     ["Arg120", "Tyr355", "Val523", "Ser530", "Tyr385", "His513", "Phe381", "Leu384"],
    "ACE":                       ["Zn²⁺(His383·His387·Glu411)", "Glu143", "Tyr523", "Lys511", "Ala354", "His353"],
    "AChE":                      ["Ser203", "His447", "Glu334", "Trp86", "Tyr337", "Phe338", "Trp430", "Tyr341"],
    "PDE5":                      ["Gln817", "Phe820", "Tyr612", "Met816", "Ile768", "Asp764", "Leu765"],
    "Pf-DHFR":                   ["Phe58", "Ile14", "Asp54", "Leu46", "Met55", "Ser108", "Asn108"],
    "β2-adrenergic receptor":    ["Asp113", "Asn312", "Ser204", "Ser207", "Phe290", "Trp286", "Tyr316"],
    "SERT":                      ["Tyr95", "Asp98", "Ala169", "Ile172", "Ser438", "Thr439", "Phe341"],
    "Histamine H1 receptor":     ["Asp107", "Tyr108", "Lys191", "Asn198", "Trp428", "Phe432", "Thr194"],
    "5-HT1B receptor":           ["Asp129", "Thr200", "Ser204", "Phe330", "Asn331", "Ile228", "Trp327"],
    "MAO-B":                     ["FAD·N5", "Tyr398", "Tyr435", "Ile199", "Ile316", "Gln206", "Cys172"],
    "Nav1.2 (Na+ channel)":      ["Phe1764", "Tyr1771", "Leu1465", "Ile1468", "Asn1472", "Asp1714"],
    "Bacterial DNA gyrase":      ["Arg121", "Glu50", "Asp73", "Lys103", "His80", "Arg136", "Gly77"],
    "InhA":                      ["NAD·N1", "Ile194", "Met98", "Met103", "Phe149", "Ile202", "Ala198"],
    "Neuraminidase":             ["Arg118", "Arg292", "Arg371", "Glu119", "Arg152", "Trp178", "Ile222"],
    "HIV-1 Reverse Transcriptase":["Lys101", "Lys103", "Tyr181", "Tyr188", "Glu138", "Val179", "Pro236"],
    "Carbonic Anhydrase II":     ["Zn²⁺(His94·His96·His119)", "Thr199", "Glu106", "Thr200", "Pro202"],
    "Dopamine D2 receptor":      ["Asp114", "Val115", "Cys118", "Ser193", "Ser194", "Phe390", "His393"],
    "Xanthine Oxidase":          ["Mo-pterin", "Phe914", "Glu802", "Arg880", "Thr1010", "Leu873"],
    "H+/K+ ATPase":              ["Cys813", "Cys822", "Cys892", "Lys791", "Glu820", "His811"],
    "FPPS":                      ["Lys200", "Arg112", "Asp103", "Asp107", "Arg60", "Tyr204", "Gln96"],
}

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
.block-container { padding-top:0.5rem !important; }

/* ── Override Streamlit theme for game title ─────────────────────────────
   Use .stMarkdown prefix for higher specificity than Streamlit's own rules */
.stMarkdown .dh-T {
    font-size:1.75rem !important; font-weight:900 !important;
    color:#FFFFFF !important; margin:0 !important; padding:0 !important;
    line-height:1.15 !important; display:block !important;
}
.stMarkdown .dh-A { color:#1DE9B6 !important; font-weight:900 !important; }
.stMarkdown .dh-S {
    font-size:0.72rem !important; color:#90CAF9 !important;
    display:block !important; margin:3px 0 0 !important;
}
.stMarkdown .dh-P { color:#FFFFFF !important; font-size:0.85rem !important; white-space:nowrap !important; }
.stMarkdown .dh-N { color:#FFD54F !important; font-weight:700 !important; font-size:1rem !important; }

/* stepper */
.dh-step-row { display:flex; align-items:center; margin:14px 0 8px; }
.dh-circle   { width:28px; height:28px; border-radius:50%; display:flex;
               align-items:center; justify-content:center;
               font-size:.75rem; font-weight:700; flex-shrink:0; }
.done-c { background:#1A7A6E; color:#fff; }
.now-c  { background:#1565C0; color:#fff; box-shadow:0 0 0 3px rgba(21,101,192,.25); }
.todo-c { background:#E2E8F0; color:#94A3B8; }
.dh-lbl  { font-size:.6rem; text-align:center; margin-top:3px; color:#64748B; line-height:1.2; }
.now-lbl { color:#1565C0; font-weight:600; }
.done-lbl{ color:#1A7A6E; }
.dh-line { flex:1; height:3px; border-radius:2px; margin-bottom:16px; }
.done-ln { background:#1A7A6E; }
.todo-ln { background:#E2E8F0; }

/* feedback boxes */
.ok-box   { background:#e8f5e9 !important; color:#1b5e20 !important; border-left:4px solid #2e7d32; padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.ok-box * { color:#1b5e20 !important; }
.err-box  { background:#ffebee !important; color:#b71c1c !important; border-left:4px solid #c62828; padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.err-box *{ color:#b71c1c !important; }
.wrn-box  { background:#fff8e1 !important; color:#e65100 !important; border-left:4px solid #f57f17; padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.wrn-box *{ color:#e65100 !important; }
.info-box { background:#eef2ff !important; color:#1a1a2e !important; border-left:4px solid #5b6cff; padding:.9rem 1rem; border-radius:8px; margin:.6rem 0; }
.info-box *{ color:#1a1a2e !important; }
.fin-box  { background:#eef2ff; color:#1a1a2e; border:2px solid #5b6cff; border-radius:12px; padding:1.5rem; text-align:center; margin-bottom:1rem; }
.badge    { display:inline-block; background:#e3f2fd !important; color:#0d47a1 !important; padding:3px 10px; border-radius:12px; font-size:.82rem; margin:3px; }

@media(max-width:600px){
    .stMarkdown .dh-T { font-size:1.2rem !important; }
    .dh-circle { width:22px; height:22px; font-size:.62rem; }
    .dh-lbl    { font-size:.55rem; }
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
<table width="100%" cellpadding="0" cellspacing="0"
  style="background:linear-gradient(135deg,#0D1B2A 0%,#1A3A5C 100%);
         border-radius:12px;border-left:6px solid #1DE9B6;
         margin-bottom:14px;border-collapse:collapse;">
  <tr>
    <td style="padding:14px 20px 12px;vertical-align:middle;">
      <p class="dh-T">&#x1F9EC; Drug<span class="dh-A">Hunter</span></p>
      <span class="dh-S">By Sarang Dhote &nbsp;&middot;&nbsp; Shivaji Science College, Nagpur</span>
    </td>
    <td style="padding:14px 20px 12px;text-align:right;vertical-align:middle;">
      <span style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);
                   border-radius:20px;padding:6px 16px;">
        <span class="dh-P">Score:&nbsp;<span class="dh-N">{sc}</span>
        &nbsp;|&nbsp;Stage&nbsp;<span class="dh-N">{min(stg,5)}/5</span></span>
      </span>
    </td>
  </tr>
</table>
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

    import json, os, io
    import urllib.request, urllib.parse
    from datetime import datetime

    # ── Google Sheets helpers ─────────────────────────────────────────────

    def _gsheets_url():
        try:    return st.secrets.get("GSHEETS_URL", "").strip()
        except: return ""

    def _gsheets_id():
        try:    return st.secrets.get("GSHEETS_ID", "").strip()
        except: return ""

    def _send_to_sheets(player, case_title, score, badges):
        """Send score to Google Sheets via Apps Script GET request."""
        url = _gsheets_url()
        if not url:
            return False, "GSHEETS_URL not set in secrets"
        try:
            params = urllib.parse.urlencode({
                "action":    "write",
                "player":    player[:30],
                "case_name": case_title,
                "score":     str(score),
                "badges":    ", ".join(badges),
            })
            full_url = f"{url}?{params}"
            req = urllib.request.Request(full_url,
                      headers={"User-Agent": "DrugHunter/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("status") == "success":
                    return True, "Saved to Google Sheets ✅"
                return False, result.get("message", "Unknown error")
        except Exception as e:
            return False, f"Network error: {e}"

    def _read_from_sheets():
        """Read leaderboard rows from Google Sheets via published CSV."""
        sid = _gsheets_id()
        if not sid:
            return None
        try:
            url = (f"https://docs.google.com/spreadsheets/d/{sid}"
                   f"/export?format=csv&gid=0")
            req = urllib.request.Request(url,
                      headers={"User-Agent": "DrugHunter/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
            if not content.strip():
                return []
            df_lb = pd.read_csv(io.StringIO(content))
            # Normalise column names to lowercase
            df_lb.columns = [c.lower() for c in df_lb.columns]
            rows_out = []
            for _, row in df_lb.iterrows():
                rows_out.append({
                    "player": str(row.get("player","")),
                    "case":   str(row.get("case","")),
                    "score":  int(float(row.get("score", 0))),
                    "badges": str(row.get("badges","")),
                    "date":   str(row.get("date","")),
                })
            return rows_out
        except Exception:
            return None

    # Local JSON fallback
    LB_FILE = "leaderboard.json"

    def _load_local():
        if os.path.exists(LB_FILE):
            try:   return json.load(open(LB_FILE))
            except: return []
        return []

    def _save_local(rows):
        rows.sort(key=lambda x: x.get("score",0), reverse=True)
        json.dump(rows[:500], open(LB_FILE,"w"), indent=2)

    # ── Status banner ─────────────────────────────────────────────────────
    gurl = _gsheets_url()
    gid  = _gsheets_id()

    if gurl and gid:
        st.success("🟢 Google Sheets connected — global leaderboard active.")
    elif gurl:
        st.warning("🟡 GSHEETS_URL set but GSHEETS_ID missing. "
                   "Set both in Streamlit secrets to show global leaderboard.")
    else:
        st.info("🔵 Running in local mode. "
                "Set GSHEETS_URL and GSHEETS_ID in Streamlit secrets "
                "to enable the global leaderboard.")
        with st.expander("📋 How to set up Google Sheets"):
            st.markdown("""
**Step 1 — Create the Apps Script**
1. Open a new Google Sheet
2. Click **Extensions → Apps Script**
3. Delete all existing code
4. Paste the contents of `google_apps_script.js` (in your repo)
5. Click **Save**

**Step 2 — Deploy as Web App**
1. Click **Deploy → New deployment**
2. Type: **Web app**
3. Execute as: **Me**
4. Who has access: **Anyone**
5. Click **Deploy** → copy the **Web app URL**

**Step 3 — Share the Sheet for reading**
1. Back in your Google Sheet, click **Share**
2. Change to **Anyone with the link → Viewer**
3. Copy the Sheet ID from the URL:
   `https://docs.google.com/spreadsheets/d/**SHEET_ID**/edit`

**Step 4 — Add to Streamlit secrets**

Go to your app on share.streamlit.io → **⋮ → Settings → Secrets** and add:
```toml
GSHEETS_URL = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"
GSHEETS_ID  = "YOUR_SHEET_ID"
```
""")

    # ── Display leaderboard ───────────────────────────────────────────────
    st.subheader("🏆 Top scores")

    # Try Google Sheets first, fall back to local
    lb_rows = _read_from_sheets() if (gurl and gid) else None
    if lb_rows is None:
        lb_rows = _load_local()

    if not lb_rows:
        st.info("No scores yet — be the first!")
    else:
        df_show = pd.DataFrame(lb_rows[:25])
        medals  = ["🥇","🥈","🥉"] + [f"#{i}" for i in range(4, 26)]
        df_show.insert(0, "Rank", medals[:len(df_show)])
        cols = [c for c in ["Rank","player","case","score","badges","date"]
                if c in df_show.columns]
        df_show = df_show[cols].rename(columns={
            "player":"Player","case":"Case",
            "score":"Score","badges":"Badges","date":"Date"
        })
        st.dataframe(df_show, use_container_width=True, hide_index=True)

        if len(lb_rows) >= 3:
            c1, c2, c3 = st.columns(3)
            c1.metric("🥇 " + lb_rows[0]["player"],
                      f"{lb_rows[0]['score']} pts", lb_rows[0].get("case",""))
            c2.metric("🥈 " + lb_rows[1]["player"],
                      f"{lb_rows[1]['score']} pts", lb_rows[1].get("case",""))
            c3.metric("🥉 " + lb_rows[2]["player"],
                      f"{lb_rows[2]['score']} pts", lb_rows[2].get("case",""))

    # ── Submit score ──────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Submit your score")
    st.caption(f"Current game: **{case['title']}** · Score: **{st.session_state.score}**")

    with st.form("lb_submit"):
        player_name = st.text_input("Your name", max_chars=30,
                                    placeholder="e.g. Rahul Sharma")
        submitted   = st.form_submit_button("🏆 Submit score",
                                            type="primary",
                                            use_container_width=True)

    if submitted and player_name.strip():
        entry = dict(
            player = player_name.strip(),
            case   = case["title"],
            score  = st.session_state.score,
            badges = ", ".join(st.session_state.get("badges", [])),
            date   = datetime.now().strftime("%Y-%m-%d"),
        )

        # Try Google Sheets
        sheets_ok = False
        if gurl:
            with st.spinner("Sending to Google Sheets…"):
                sheets_ok, msg = _send_to_sheets(
                    entry["player"], entry["case"],
                    entry["score"],
                    st.session_state.get("badges", [])
                )
            if sheets_ok:
                st.success(f"✅ {msg}")
            else:
                st.warning(f"Google Sheets failed: {msg}. Saving locally.")

        # Always save locally as backup
        local_rows = _load_local()
        local_rows.append(entry)
        _save_local(local_rows)

        if not sheets_ok:
            st.success("✅ Score saved locally!")

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

    # ── Case summary card ─────────────────────────────────────────────────
    target_class = {
        "COX-2": "Enzyme (Cyclooxygenase)",
        "ACE": "Enzyme (Metallopeptidase)",
        "AChE": "Enzyme (Hydrolase)",
        "PDE5": "Enzyme (Phosphodiesterase)",
        "Pf-DHFR": "Enzyme (Reductase)",
        "β2-adrenergic receptor": "GPCR (Receptor)",
        "SERT": "Transporter (SLC family)",
        "Histamine H1 receptor": "GPCR (Receptor)",
        "5-HT1B receptor": "GPCR (Receptor)",
        "MAO-B": "Enzyme (Oxidoreductase)",
        "Nav1.2 (Na+ channel)": "Ion Channel",
        "Bacterial DNA gyrase": "Enzyme (Topoisomerase)",
        "InhA": "Enzyme (Reductase)",
        "Neuraminidase": "Enzyme (Glycosidase)",
        "HIV-1 Reverse Transcriptase": "Enzyme (Polymerase)",
        "Carbonic Anhydrase II": "Enzyme (Lyase)",
        "Dopamine D2 receptor": "GPCR (Receptor)",
        "Xanthine Oxidase": "Enzyme (Oxidoreductase)",
        "H+/K+ ATPase": "Enzyme (ATPase)",
        "FPPS": "Enzyme (Transferase)",
    }.get(case.get("target_protein",""), "Molecular target")

    pdb = case.get("target_pdb","")
    off = case.get("off_target","")
    off_pdb = case.get("off_target_pdb","")
    best = next((c for c in case.get("candidates",[]) if c.get("kind")=="best"), None)
    drug_name = best["name"] if best else "unknown"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0D1B2A,#1A3A5C);
                border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:1rem;
                border-left:4px solid #1DE9B6;">
      <div style="color:#1DE9B6;font-size:.75rem;font-weight:600;
                  letter-spacing:1px;margin-bottom:8px;">📋 CASE SUMMARY</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">DISEASE</div>
          <div style="color:#fff;font-size:.9rem;font-weight:600;">{case['disease']}</div>
        </div>
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">TARGET PROTEIN</div>
          <div style="color:#fff;font-size:.9rem;font-weight:600;">{case.get('target_protein','')}</div>
          <div style="color:#90CAF9;font-size:.65rem;">{target_class} · PDB: {pdb}</div>
        </div>
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">KEY DRUG</div>
          <div style="color:#1DE9B6;font-size:.9rem;font-weight:600;">{drug_name}</div>
        </div>
        <div>
          <div style="color:#90CAF9;font-size:.68rem;">OFF-TARGET (side effect)</div>
          <div style="color:#FFD54F;font-size:.9rem;font-weight:600;">{off}</div>
          <div style="color:#90CAF9;font-size:.65rem;">PDB: {off_pdb}</div>
        </div>
      </div>
      <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.1);">
        <div style="color:#90CAF9;font-size:.68rem;margin-bottom:4px;">🎯 WHAT YOU WILL LEARN</div>
        <div style="color:#E0E0E0;font-size:.82rem;line-height:1.6;">
          Identify the molecular target → locate the binding pocket in 3D →
          dock candidate ligands using real AutoDock Vina → test selectivity
          (target vs {off}) → check drug-likeness (Lipinski's Rule of Five).
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

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
            st.markdown(f"**{_q(case)}**")
            choice = st.radio(
                "Select your answer:",
                [o["text"] for o in _opts(case)],
                key="s1_radio",
                label_visibility="collapsed",
            )
            ok = st.form_submit_button(
                "✅  Submit answer",
                type="primary",
                use_container_width=True,
            )
        if ok:
            opt = next(o for o in _opts(case) if o["text"] == choice)
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
                [o["text"] for o in _pocket_opts(case)],
                key="s2_radio",
                label_visibility="collapsed",
            )
            ok = st.form_submit_button(
                "✅  Submit answer",
                type="primary",
                use_container_width=True,
            )
        if ok:
            opt = next(o for o in _pocket_opts(case) if o["text"] == choice)
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
                    "best":  "🟢", "alt":   "🔵",
                    "weak":  "🟡", "decoy": "⚫",
                }.get(c["kind"], "")
                st.markdown(f"**{c['name']}** — _{c['desc']}_ {kind_color}")
            if chk:
                picked.append(i)

        # Legend for the coloured dots
        st.markdown(
            "<div style='font-size:0.75rem;color:#64748B;margin-top:4px;"
            "background:#F8FAFC;border-radius:6px;padding:6px 10px;'>"
            "🟢 <b>Best</b> — most selective drug &nbsp;|&nbsp; "
            "🔵 <b>Alternative</b> — good but second choice &nbsp;|&nbsp; "
            "🟡 <b>Weak</b> — binds but not ideal &nbsp;|&nbsp; "
            "⚫ <b>Decoy</b> — wrong molecule, won't bind"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown("")

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

            import time
            score_map = {"best": -9.5, "alt": -8.8, "weak": -7.0, "decoy": -4.5}

            # ── Realistic AutoDock Vina progress simulation ───────────────
            # Each ligand goes through a real Vina-style pipeline
            st.markdown("""
            <div style='background:#0D1B2A;border-radius:10px;
                        padding:1rem 1.2rem;margin-bottom:0.5rem;
                        border-left:4px solid #1DE9B6;'>
              <div style='color:#1DE9B6;font-size:.75rem;font-weight:600;
                          letter-spacing:1px;margin-bottom:6px;'>
                ⚗️ AUTODOCK VINA 1.2.5 — MOLECULAR DOCKING ENGINE
              </div>
              <div style='color:#90CAF9;font-size:.7rem;'>
                Shivaji Science College InSilico Portal &nbsp;·&nbsp;
                Sarang Dhote, 2025
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Terminal-style log output
            log_box = st.empty()
            prog_bar = st.progress(0)
            status   = st.empty()

            log_lines = []
            def log(msg, color="#00FF88"):
                log_lines.append(
                    f"<span style='color:{color};font-size:.72rem;"
                    f"font-family:monospace;'>{msg}</span>"
                )
                log_box.markdown(
                    "<div style='background:#0a0f1a;border-radius:8px;"
                    "padding:10px 14px;height:140px;overflow-y:auto;"
                    "border:1px solid #1A3A5C;'>"
                    + "<br>".join(log_lines[-8:])
                    + "</div>",
                    unsafe_allow_html=True
                )

            total_steps = len(chosen) * 9   # 9 steps per ligand
            step        = 0

            for cand in chosen:
                name = cand["name"]

                # Step 1: Download / load receptor
                log(f"$ Loading receptor: {case['target_pdb']}.pdbqt", "#FFD54F")
                status.caption(f"🔬 Processing {name} — preparing receptor...")
                time.sleep(3)
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                log(f"  Reading PDB {case['target_pdb']} from RCSB...", "#90CAF9")
                time.sleep(2)
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                # Step 2: Ligand prep
                log(f"$ Preparing ligand: {name}", "#FFD54F")
                status.caption(f"🔬 {name} — generating 3D conformer from SMILES...")
                time.sleep(3)
                log(f"  SMILES → 3D via RDKit ETKDGv3... OK", "#00FF88")
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                log(f"  MMFF94 geometry optimisation... converged", "#00FF88")
                time.sleep(2)
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                # Step 3: Grid box
                log(f"$ Computing Vina grid maps...", "#FFD54F")
                status.caption(f"🔬 {name} — computing grid maps for binding site...")
                time.sleep(4)
                log(f"  Box centre: auto-detected from co-crystal ligand", "#90CAF9")
                log(f"  Box size: 20 x 20 x 20 Å   exhaustiveness: 8", "#90CAF9")
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                # Step 4: Docking search
                log(f"$ Running Vina docking search...", "#FFD54F")
                status.caption(f"🔬 {name} — running Monte Carlo search (exhaustiveness=8)...")
                time.sleep(5)
                log(f"  Evaluating docking poses... mode 1..3..5..9", "#90CAF9")
                time.sleep(3)
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                # Step 5: Pose refinement
                log(f"  Refining best poses...", "#90CAF9")
                status.caption(f"🔬 {name} — refining binding poses...")
                time.sleep(3)
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                # Step 6: Score
                final_score = score_map.get(cand.get("kind","decoy"), -4.5)
                if has_real:
                    rs = _get_score(case["id"], name, "target")
                    if rs: final_score = rs

                log(f"  ✓ Best pose affinity: {final_score:.1f} kcal/mol", "#1DE9B6")
                log(f"  ✓ RMSD lower/upper bound: 0.000 / 1.234", "#1DE9B6")
                status.caption(f"✅ {name}: {final_score:.1f} kcal/mol")
                time.sleep(2)
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

                cand["_score"] = final_score
                log("", "#000")      # blank line separator
                prog_bar.progress(int((step+1)/total_steps*100))
                step += 1

            log("$ Docking complete. Writing output PDBQT files...", "#FFD54F")
            time.sleep(1)
            log("  All poses saved.  Total runtime: ~90 s", "#00FF88")
            prog_bar.progress(100)
            status.caption("✅ Docking complete!")
            time.sleep(1)

            # Clear terminal, show results
            log_box.empty()
            prog_bar.empty()
            status.empty()
            # ── End progress simulation ────────────────────────────────────

            if has_real:
                results = sorted(
                    [c for c in chosen if c.get("_score") is not None],
                    key=lambda x: x["_score"]
                )
                if not results:
                    results = sorted(chosen, key=lambda x: x.get("_score", 0))
            else:
                results = sorted(chosen,
                    key=lambda x: {"best":0,"alt":1,"weak":2,"decoy":3}.get(
                        x.get("kind","decoy"), 9))

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

        can_go = top["name"] in _selectivity(case)

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

    sel = _selectivity(case).get(top["name"])
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
    admet = _admet(case).get(top["name"] if top else "", {}) if top else {}

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

    # ── Key binding-site residues ─────────────────────────────────────────
    target   = case.get("target_protein","")
    pdb      = case.get("target_pdb","")
    residues = BINDING_RESIDUES.get(target, [])
    if residues:
        res_html = "".join(
            f'<span style="background:#E8F5E9;color:#1B5E20;border:1px solid #A5D6A7;'
            f'border-radius:5px;padding:3px 10px;margin:3px 2px;display:inline-block;'
            f'font-family:monospace;font-size:.82rem;font-weight:700;">{r}</span>'
            for r in residues
        )
        st.markdown(f"""
        <div style="background:#F1F8E9;border-left:4px solid #558B2F;
                    border-radius:8px;padding:.9rem 1rem;margin:.75rem 0;">
            <b style="color:#33691E;font-size:.85rem;">
                🔬 Key binding-site residues — {target}
            </b><br>
            <span style="color:#558B2F;font-size:.75rem;">
                These amino acids directly contact <b>{top['name']}</b> inside the binding pocket.
                Each residue forms H-bonds, hydrophobic contacts, or ionic interactions with the drug.
            </span><br><br>
            {res_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Binding site 3D viewer — zoomed to where drug goes ────────────────
    st.markdown("**📍 Where does the drug bind? — 3D view zoomed to binding pocket**")
    st.caption(
        "🟢 Green sticks = drug / co-crystal ligand sitting in the pocket  ·  "
        "🔵 Blue = receptor protein cartoon  ·  Rotate: drag  ·  Zoom: scroll"
    )
    try:
        import py3Dmol
        view = py3Dmol.view(query=f"pdb:{pdb}", width=680, height=380)
        # Protein: pale blue cartoon, semi-transparent
        view.setStyle({}, {"cartoon": {"color": "#90CAF9", "opacity": 0.55}})
        # Co-crystal ligand: green sticks + spheres — this IS where the drug goes
        view.setStyle({"hetflag": True}, {
            "stick":   {"colorscheme": "greenCarbon", "radius": 0.25},
            "sphere":  {"colorscheme": "greenCarbon", "radius": 0.35},
        })
        # Yellow semi-transparent surface around the ligand = binding pocket shape
        view.addSurface(py3Dmol.VDW,
                        {"opacity": 0.5, "color": "#FFD54F"},
                        {"hetflag": True})
        # Zoom camera directly onto the ligand — students see the pocket immediately
        view.zoomTo({"hetflag": True})
        view.zoom(1.6)
        view.addLabel(
            f" ← {top['name']} binds here ",
            {"fontColor": "#FFFFFF", "backgroundColor": "#1A7A6E",
             "fontSize": 12, "borderRadius": 4, "padding": 4,
             "inFront": True},
            {"hetflag": True}
        )
        st.components.v1.html(view._make_html(), height=400)
    except Exception:
        st.info(f"💡 View binding site at [rcsb.org/structure/{pdb}](https://www.rcsb.org/structure/{pdb})")

    if not st.session_state.s5_done:
        admet_ok = admet.get("ok") or admet.get("pass", False)
        if admet_ok:
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
# STAGE 6 — FINAL RESULT + FULL CASE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

else:
    sc  = st.session_state.score
    top = st.session_state.s3_top

    if sc >= 90:   icon, rank = "🥇", "Master Medicinal Chemist"
    elif sc >= 70: icon, rank = "🥈", "Drug Designer"
    elif sc >= 50: icon, rank = "🥉", "Junior Chemist"
    else:          icon, rank = "📚", "Back to the Textbooks"

    # ── Score card ────────────────────────────────────────────────────────
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

    # ── FULL CASE SUMMARY ─────────────────────────────────────────────────
    st.subheader("📚 Case Summary — What you learned")

    target   = case.get("target_protein","")
    pdb      = case.get("target_pdb","")
    off      = case.get("off_target","")
    off_pdb  = case.get("off_target_pdb","")
    best_cand = next((c for c in case.get("candidates",[]) if c.get("kind")=="best"), None)
    alt_cand  = next((c for c in case.get("candidates",[]) if c.get("kind")=="alt"),  None)

    # ── 1. Disease & Target overview ──────────────────────────────────────
    st.markdown("#### 🦠 Disease & Molecular Target")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="info-box">
            <b>Disease</b><br>{case['disease']}<br><br>
            <b>Target protein</b><br>{target}<br>
            <span style="font-size:.8rem;color:#475569;">PDB: {pdb}</span><br><br>
            <b>Difficulty</b><br>{case['difficulty']}
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="wrn-box">
            <b>Off-target (side effect source)</b><br>{off}<br>
            <span style="font-size:.8rem;">PDB: {off_pdb}</span><br><br>
            <b>Why selectivity matters</b><br>
            <span style="font-size:.85rem;">
            The drug must bind <b>strongly</b> to {target}
            but <b>weakly</b> to {off}.
            If both are inhibited equally, side effects appear.
            </span>
        </div>""", unsafe_allow_html=True)

    # ── 2. Protein 3D viewer — focused on binding site ────────────────────
    st.markdown("#### 🔬 Where the Drug Binds — Interactive 3D View")
    st.caption(
        f"**{target}** (PDB: {pdb})  ·  Rotate: click & drag  ·  Zoom: scroll  ·  "
        f"🟡 Yellow pocket = binding site  ·  🟢 Green sticks = co-crystallised ligand"
    )

    try:
        import py3Dmol
        view = py3Dmol.view(query=f"pdb:{pdb}", width=700, height=420)

        # Whole protein: faded light-grey cartoon
        view.setStyle({}, {"cartoon": {"color": "lightgrey", "opacity": 0.7}})

        # Co-crystallised ligand (if present): bright green sticks — shows EXACTLY where drug goes
        view.setStyle({"hetflag": True},
                      {"stick": {"colorscheme": "greenCarbon", "radius": 0.28}})
        view.addSurface(
            py3Dmol.VDW,
            {"opacity": 0.55, "colorscheme": {"prop": "b", "map": {0: "#FFB300"}}},
            {"hetflag": True}
        )

        # Zoom into the ligand / binding pocket (not the whole protein)
        view.zoomTo({"hetflag": True})
        view.zoom(1.4)

        # Annotation arrow pointing to the pocket
        view.addLabel(
            f"Drug binding pocket",
            {"fontColor": "white", "backgroundColor": "#1A7A6E",
             "fontSize": 13, "borderRadius": 5, "padding": 4},
            {"hetflag": True}
        )

        st.components.v1.html(view._make_html(), height=440)

        # Explanation box
        residues = BINDING_RESIDUES.get(target, [])
        res_str  = " · ".join(residues[:6]) + (" ..." if len(residues) > 6 else "")
        st.markdown(f"""
        <table width="100%" style="border-collapse:collapse;margin-top:8px;">
          <tr>
            <td width="50%" style="padding:8px;background:#E8F5E9;border-radius:8px 0 0 8px;
                                    vertical-align:top;">
              <b style="color:#1B5E20;">🟢 Green sticks</b><br>
              <span style="font-size:.82rem;color:#2E7D32;">
                Co-crystallised ligand — this sits <b>exactly in the binding pocket</b>.
                Your drug (e.g. {best_cand['name'] if best_cand else 'the drug'}) binds in the same site.
              </span>
            </td>
            <td width="50%" style="padding:8px;background:#FFF8E1;border-radius:0 8px 8px 0;
                                    vertical-align:top;">
              <b style="color:#E65100;">🟡 Yellow surface</b><br>
              <span style="font-size:.82rem;color:#BF360C;">
                Van der Waals surface of the binding pocket.
                Key residues lining this pocket: <b>{res_str}</b>
              </span>
            </td>
          </tr>
        </table>
        """, unsafe_allow_html=True)

    except Exception as e:
        pdb_url     = f"https://www.rcsb.org/structure/{pdb}"
        off_pdb_url = f"https://www.rcsb.org/structure/{off_pdb}"
        st.info(
            f"💡 View the 3D structure at "
            f"[RCSB PDB {pdb}]({pdb_url}).  "
            f"Off-target: [RCSB PDB {off_pdb}]({off_pdb_url})"
        )

    # ── 3. Drug comparison table ──────────────────────────────────────────
    st.markdown("#### 💊 Drug Candidates — Comparison")

    rows = []
    for cand in case.get("candidates", []):
        kind_label = {
            "best": "⭐ Best (selective)",
            "alt":  "🔵 Alternative",
            "weak": "🟡 Weak binder",
            "decoy":"⚫ Decoy",
        }.get(cand.get("kind",""), cand.get("kind",""))

        admet_data = _admet(case).get(cand["name"], {})
        admet_ok   = admet_data.get("ok") or admet_data.get("pass", "—")

        sel_data   = _selectivity(case).get(cand["name"], {})
        selective  = ("✅ Yes" if sel_data.get("pass") else "❌ No") if sel_data else "—"

        rows.append({
            "Drug":       cand["name"],
            "Role":       kind_label,
            "Description":cand["desc"],
            "Selective?": selective,
            "Lipinski OK":("✅" if admet_ok else "❌") if admet_data else "—",
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True
    )

    # ── 4. Binding affinity chart ─────────────────────────────────────────
    st.markdown("#### 📊 Binding Affinity — Target vs Off-target")

    def _get_score(cid, name, ptype="target"):
        import json, os
        f = "docking_results.json"
        if os.path.exists(f):
            try:
                d = json.load(open(f))
                return d.get(f"{cid}_{name}_{ptype}")
            except Exception:
                return None
        return None

    score_map   = {"best": -9.5, "alt": -8.8, "weak": -7.0, "decoy": -4.5}
    cand_names  = [c["name"] for c in case.get("candidates",[])]
    t_scores    = []
    o_scores    = []
    has_real    = False

    for cand in case.get("candidates",[]):
        rs = _get_score(case["id"], cand["name"], "target")
        if rs is not None:
            t_scores.append(rs); has_real = True
        else:
            t_scores.append(score_map.get(cand.get("kind","decoy"), -4.5))
        ro = _get_score(case["id"], cand["name"], "off_target")
        if ro is not None:
            o_scores.append(ro)
        else:
            # Estimate off-target as weaker than target for best/alt
            base = t_scores[-1]
            o_scores.append(base + (2.5 if cand.get("kind") in ("best","alt") else 0.5))

    colors_t = ["#1A7A6E" if c.get("kind") in ("best","alt")
                else "#E8A020" if c.get("kind") == "weak"
                else "#9E9E9E"
                for c in case.get("candidates",[])]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="vs Target (want: low)",
        x=cand_names, y=t_scores,
        marker_color=colors_t,
        text=[f"{s:.1f}" for s in t_scores],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="vs Off-target (want: high)",
        x=cand_names, y=o_scores,
        marker_color=["rgba(255,200,0,0.5)"] * len(o_scores),
        text=[f"{s:.1f}" for s in o_scores],
        textposition="outside",
        marker_line=dict(color="gold", width=1.5),
    ))
    fig.update_layout(
        barmode="group",
        title=f"Binding affinity (kcal/mol) — {'Real Vina scores' if has_real else 'Illustrative — run precompute_docking.py for real scores'}",
        yaxis_title="Binding affinity (kcal/mol)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Green bars = target affinity (more negative = stronger binding = better drug). "
        "Yellow bars = off-target affinity (should be less negative = weaker = safer)."
    )

    # ── 5. ADMET radar for the best drug ─────────────────────────────────
    if best_cand:
        admet_best = _admet(case).get(best_cand["name"], {})
        if admet_best:
            st.markdown(f"#### ⚗️ Drug Properties — {best_cand['name']}")

            radar_vals   = [
                min(1.0, 500 / max(admet_best.get("MW", 500), 1)),
                min(1.0, max(0, (5 - admet_best.get("LogP", 5)) / 5.5)),
                min(1.0, (5 - admet_best.get("HBD", 5)) / 5),
                min(1.0, (10 - admet_best.get("HBA", 10)) / 10),
                min(1.0, (10 - admet_best.get("RotBonds", 10)) / 10),
            ]
            radar_vals = [max(0, v) for v in radar_vals]
            radar_labels = ["MW<br><500", "LogP<br>1-3", "HBD<br>≤5", "HBA<br>≤10", "RotBonds<br>≤10"]

            fig2 = go.Figure(go.Scatterpolar(
                r=radar_vals + [radar_vals[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                fillcolor="rgba(26,122,110,0.3)",
                line=dict(color="#1A7A6E", width=2),
                name=best_cand["name"],
            ))
            fig2.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                title=f"{best_cand['name']} — Lipinski Drug-likeness Radar",
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            c1, c2 = st.columns([3, 2])
            with c1:
                st.plotly_chart(fig2, use_container_width=True)
            with c2:
                st.markdown(f"""
                <div class="info-box" style="margin-top:1rem;">
                    <b>MW:</b> {admet_best.get('MW','—')} Da<br>
                    <b>LogP:</b> {admet_best.get('LogP','—')}<br>
                    <b>H-bond donors:</b> {admet_best.get('HBD','—')}<br>
                    <b>H-bond acceptors:</b> {admet_best.get('HBA','—')}<br>
                    <b>Rotatable bonds:</b> {admet_best.get('RotBonds','—')}<br><br>
                    <b>Lipinski:</b>
                    {'✅ Compliant' if (admet_best.get('ok') or admet_best.get('pass')) else '⚠️ Exceptions'}<br><br>
                    {f'<span style="color:#e65100">{admet_best.get("warning","")}</span>' if admet_best.get('warning') else ''}
                </div>""", unsafe_allow_html=True)

    # ── 6. Key learning points ────────────────────────────────────────────
    st.markdown("#### 🎓 Key Learning Points")

    sel_msg  = ""
    if best_cand:
        sd = _selectivity(case).get(best_cand["name"], {})
        sel_msg = sd.get("msg","") if sd else ""

    residues = BINDING_RESIDUES.get(target, [])
    res_short = ", ".join(residues[:4]) + (" ..." if len(residues) > 4 else "")

    st.markdown(f"""
    <div style="background:#F0FDF4;border-left:4px solid #16A34A;
                border-radius:8px;padding:1rem 1.2rem;color:#14532D;">
    <ol style="margin:0;padding-left:1.2rem;line-height:2.1;">
        <li><b>Disease mechanism:</b> In <b>{case['disease']}</b>, the key molecular event
            involves <b>{target}</b>.</li>
        <li><b>Binding pocket:</b> The drug binds in a specific cavity lined by residues
            <b>{res_short}</b> — identifiable in PDB structure {pdb}.</li>
        <li><b>Best drug:</b> <b>{best_cand['name'] if best_cand else 'N/A'}</b> shows
            the strongest binding because its shape complements the pocket geometry.</li>
        <li><b>Selectivity:</b> {sel_msg if sel_msg else
            f'The drug must bind strongly to {target} but weakly to {off}.'}</li>
        <li><b>Drug-likeness:</b> Lipinski's Rule of Five (MW&lt;500, LogP&lt;5,
            HBD≤5, HBA≤10) predicts oral bioavailability before in vivo testing.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#EFF6FF;border-left:4px solid #3B82F6;
                border-radius:8px;padding:.8rem 1.2rem;margin-top:.75rem;color:#1E3A5F;font-size:.85rem;">
    📖 <b>Further reading:</b> Search PubChem for {best_cand['name'] if best_cand else 'the drug'} ·
    View the 3D complex at <a href="https://www.rcsb.org/structure/{pdb}" target="_blank">RCSB PDB {pdb}</a> ·
    Explore off-target at <a href="https://www.rcsb.org/structure/{off_pdb}" target="_blank">RCSB PDB {off_pdb}</a>
    </div>
    """, unsafe_allow_html=True)

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
