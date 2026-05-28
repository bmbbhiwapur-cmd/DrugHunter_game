# 🔗 Google Sheets Leaderboard Setup

Complete setup takes about 5 minutes. No Google Cloud account needed.

---

## What you need to do (overview)

| Step | What | Time |
|---|---|---|
| 1 | Create the Google Sheet | 1 min |
| 2 | Create the Apps Script writer | 2 min |
| 3 | Add secrets to Streamlit | 1 min |
| Done | Leaderboard goes live | — |

---

## Step 1: Create the Google Sheet

1. Go to **sheets.google.com** → click **Blank spreadsheet**
2. Name it: **DockQuest Leaderboard**
3. In Row 1, type these exact headers (one per cell A1→G1):

```
player    case_id    case_title    score    badges_count    badges    timestamp
```

4. Click **Share** (top right)
   - Under "General access" → set to **Anyone with the link**
   - Permission: **Editor**
   - Click **Done**

5. Copy the URL. Extract the Sheet ID from it:
   ```
   https://docs.google.com/spreadsheets/d/ ← SHEET_ID → /edit
   ```
   Save the Sheet ID — you'll need it in Step 3.

---

## Step 2: Create the Apps Script Web App (the writer)

Google Sheets doesn't allow direct writes without authentication.
A free Apps Script acts as the authenticated writer. Setup takes 2 minutes.

### 2a. Open Apps Script

In your Google Sheet, click:
**Extensions → Apps Script**

A new tab opens with a code editor.

### 2b. Replace all the code with this

Delete everything in the editor and paste this exactly:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
    var data = JSON.parse(e.parameter.data);
    var headers = ["player", "case_id", "case_title", "score",
                   "badges_count", "badges", "timestamp"];
    var row = headers.map(function(h) { return data[h] || ""; });
    sheet.appendRow(row);
    return ContentService.createTextOutput("success").setMimeType(
      ContentService.MimeType.TEXT
    );
  } catch(err) {
    return ContentService.createTextOutput("error: " + err).setMimeType(
      ContentService.MimeType.TEXT
    );
  }
}

// Keep the script alive (optional health check)
function doGet(e) {
  return ContentService.createTextOutput("DockQuest leaderboard writer is running.");
}
```

### 2c. Save and Deploy

1. Click **💾 Save** (Ctrl+S)
2. Click **Deploy → New deployment**
3. Click the gear icon ⚙ next to "Select type" → choose **Web app**
4. Fill in:
   - **Description:** DockQuest Leaderboard Writer
   - **Execute as:** Me (your Google account)
   - **Who has access:** Anyone
5. Click **Deploy**
6. Google will ask you to **Authorize** — click through and allow it
7. Copy the **Web app URL** — it looks like:
   ```
   https://script.google.com/macros/s/AKfycbw.../exec
   ```
   Save this URL — you'll need it in Step 3.

> ⚠️ **Important:** Every time you edit the script, you must click
> **Deploy → Manage deployments → Edit → New version → Deploy** to update it.

---

## Step 3: Add secrets to Streamlit Cloud

1. Go to **share.streamlit.io**
2. Find your app → click **⋮ (three dots)** → **Settings**
3. Click the **Secrets** tab
4. Paste this (replace with YOUR actual values):

```toml
GSHEETS_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
GSHEETS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw.../exec"
```

5. Click **Save**

The app restarts automatically. The leaderboard page now shows
**🟢 Connected to Google Sheets**.

---

## Testing it works

1. Play through any case and submit your score
2. Open your Google Sheet — a new row should appear within seconds
3. Go to the Leaderboard page in the game — your score should appear

If the score doesn't appear in the sheet:
- Check the Apps Script URL is correct (no trailing spaces)
- Make sure the script is deployed as "Anyone" can access
- Re-deploy the script as a **new version** if you edited it

---

## Running locally (for development)

Create a file `.streamlit/secrets.toml` in your project folder:

```toml
GSHEETS_ID = "your-sheet-id"
GSHEETS_SCRIPT_URL = "your-script-url"
```

Then run `streamlit run app.py` — it will pick up the secrets automatically.

---

## How it works (technical)

```
Student submits score
        ↓
leaderboard.py → POST to Apps Script URL
        ↓
Apps Script (runs as your Google account) → appends row to Sheet
        ↓
leaderboard.py → reads Sheet via CSV export URL (no auth needed for read)
        ↓
Leaderboard page shows live data
```

Reading uses the public CSV export (free, no API key).
Writing uses the Apps Script (free, no Cloud Console needed).

---

## Without Google Sheets (local mode)

If you don't add the secrets, the leaderboard still works — it saves to
`leaderboard.json` on the Streamlit server. This is fine for:
- Local classroom use (one server, one session)
- Testing

The downside: scores reset when the server restarts. For persistent
classroom use, Google Sheets is the better option.
