# Financial Command Center — Veteran's Budget Tracker

A fully-automated, professionally-styled Google Sheets budget tracker built
for veterans transitioning from military service to civilian employment.
Covers overlapping VA benefits, GI Bill BAH, W2 income, debt payoff strategy,
and savings goals in one command center.

---

## Features

| Tab | Purpose |
|-----|---------|
| 🏠 Dashboard | Live KPI cards, goal progress bars, upcoming bills, sparklines |
| 💰 Monthly Budget | Income vs. expenses with green/yellow/red budget tracking |
| 📊 Income Tracker | Taxable vs. non-taxable income split, YTD totals |
| 🧾 Expense Log | Transaction log with dual category dropdowns, recurring flag |
| 💳 Debt Tracker | Avalanche/snowball selector, NPER payoff dates, progress bars |
| 📅 Bill Calendar | Visual monthly calendar with overdue detection |
| 🎯 Savings Goals | Progress bars, ON TRACK / BEHIND / COMPLETED status |
| 📈 Net Worth Tracker | Assets/liabilities tables, monthly history, trend chart |
| 🔄 Recurring Transactions | Registry with next-due-date formulas, 7-day alerts |
| ⚙️ Settings & Reference | Category lists, color legend, formula reference |

**Pre-loaded with realistic sample data** for a $50K/year household:
3 months of income/expenses, 4 debts, 5 savings goals, 12-month net worth history.

---

## Prerequisites

- Python 3.8+
- A Google Cloud project with the Sheets API and Drive API enabled
- A service account with credentials downloaded as `credentials.json`

---

## Setup

### Step 1 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Create Google Cloud credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable these two APIs:
   - **Google Sheets API** (`sheets.googleapis.com`)
   - **Google Drive API** (`drive.googleapis.com`)
4. Go to **IAM & Admin → Service Accounts**
5. Click **Create Service Account**
   - Name: `financial-command-center`
   - Role: Editor (or create a custom role with Sheets + Drive write access)
6. Click on the created service account → **Keys** tab → **Add Key** → **JSON**
7. Download the JSON file and save it as `credentials.json` in the project root

> **Important:** Keep `credentials.json` private — never commit it to source control.
> It is already listed in `.gitignore`.

### Step 3 — Run the build script

```bash
python financial_command_center/build_tracker.py
```

The script will:
1. Authenticate with Google Sheets API
2. Create a new spreadsheet titled `"Financial Command Center — YYYY"`
3. Build and format all 10 tabs with sample data
4. Print the spreadsheet URL when complete

The entire build takes approximately 2–4 minutes (rate limiting between sheets).

### Step 4 — Open your spreadsheet

Copy the URL printed by the script and open it in your browser.

> **Tip:** Set the `SHARE_WITH_EMAIL` environment variable to auto-share the
> spreadsheet with your Google account:
> ```bash
> SHARE_WITH_EMAIL=you@gmail.com python financial_command_center/build_tracker.py
> ```

---

## Configuration

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | Path to service account JSON |
| `SHARE_WITH_EMAIL` | _(blank)_ | Share the spreadsheet with this email |
| `USE_OAUTH` | `false` | Use OAuth user credentials instead of service account |

---

## Using the Tracker

### Getting Started
1. Open the **⚙️ Settings** tab — enter your name and verify settings
2. Open **💰 Monthly Budget** — select the current month from the dropdown (cell B3)
3. Start logging income in **📊 Income Tracker** and expenses in **🧾 Expense Log**
4. The **🏠 Dashboard** updates automatically as you add data

### Logging Income
- Enter date, source, category, and amount
- VA Disability and GI Bill BAH are marked as **Non-Taxable** — keep this correct for tax planning
- The monthly summary at the top auto-calculates by month

### Logging Expenses
- Use the **Category** and **Subcategory** dropdowns for consistent tracking
- Mark recurring items as **Yes** — they show in blue and feed the Recurring tab
- The Monthly Budget **Actual** column auto-sums your expense entries

### Debt Payoff
- Choose **Avalanche** (highest APR first = least total interest) or **Snowball** (lowest balance first = fastest wins)
- The priority debt is highlighted in gold
- Add payments to the Payment History log to track progress

### Savings Goals
- Update **Currently Saved ($)** as you make progress
- The **Monthly Needed** column shows how much to save each month to hit the goal on time
- Status auto-updates: ✅ COMPLETED / ON TRACK / 🔴 BEHIND

### Bill Calendar
- Check off **Paid This Month?** after paying each bill to clear the red/yellow warnings
- Enable **Auto-Pay?** for bills paid automatically — marked with ⚡ in the registry

---

## Color Coding Reference

| Color | Meaning |
|-------|---------|
| 🟢 Green | Under budget / positive / completed |
| 🟡 Yellow | Near budget limit / due soon (≤3 days) |
| 🔴 Red | Over budget / overdue |
| 🔵 Blue | Recurring transaction |
| 🟡 Gold | Priority debt / section headers |

---

## Project Structure

```
financial_command_center/
├── build_tracker.py          # Main entry point
├── config.py                 # Colors, constants, sheet configurations
├── auth.py                   # Google API authentication
├── utils/
│   ├── formatting.py         # Sheets API request builders
│   └── sample_data.py        # Realistic pre-loaded sample data
└── sheets/
    ├── base.py               # BaseSheetBuilder class
    ├── settings_ref.py       # ⚙️ Settings & Reference (Tab 10)
    ├── monthly_budget.py     # 💰 Monthly Budget (Tab 2)
    ├── income_tracker.py     # 📊 Income Tracker (Tab 3)
    ├── expense_log.py        # 🧾 Expense Log (Tab 4)
    ├── debt_tracker.py       # 💳 Debt Tracker (Tab 5)
    ├── bill_calendar.py      # 📅 Bill Calendar (Tab 6)
    ├── savings_goals.py      # 🎯 Savings Goals (Tab 7)
    ├── net_worth.py          # 📈 Net Worth Tracker (Tab 8)
    ├── recurring.py          # 🔄 Recurring Transactions (Tab 9)
    └── dashboard.py          # 🏠 Dashboard (Tab 1 — built last)
```

---

## Troubleshooting

**`credentials.json not found`**
→ Download your service account key from Google Cloud Console and place it in the project root.

**`403 Forbidden` / permission errors**
→ Ensure the Sheets API and Drive API are both enabled in your Google Cloud project.

**`429 Resource Exhausted` / quota errors**
→ The script includes rate limiting, but if you hit quota limits, wait 60 seconds and re-run.
The script is not idempotent — delete the partially-built spreadsheet and start fresh.

**Formulas show `#REF!` errors on the Dashboard**
→ Some Dashboard formulas reference specific row numbers in other sheets that may shift
if you add categories to the Monthly Budget template. Update the cross-sheet references
in `sheets/dashboard.py` to match the actual row layout.

---

## License

MIT — free to use, modify, and distribute.
