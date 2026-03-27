"""
Financial Command Center — Build Script
=======================================

Creates the complete 10-tab "Financial Command Center" Google Sheets
spreadsheet for a veteran transitioning to civilian employment.

Usage:
    python financial_command_center/build_tracker.py

Prerequisites:
    1. pip install -r requirements.txt
    2. Create credentials.json (see README.md)
    3. Run this script — the spreadsheet URL is printed on completion.
"""

import os
import sys
import time
import datetime

# Allow running as: python financial_command_center/build_tracker.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_command_center.auth import get_client
from financial_command_center.config import SHEET_NAMES

# Sheet builders (imported in build order)
from financial_command_center.sheets.settings_ref   import SettingsSheetBuilder
from financial_command_center.sheets.monthly_budget import MonthlyBudgetBuilder
from financial_command_center.sheets.income_tracker import IncomeTrackerBuilder
from financial_command_center.sheets.expense_log    import ExpenseLogBuilder
from financial_command_center.sheets.debt_tracker   import DebtTrackerBuilder
from financial_command_center.sheets.bill_calendar  import BillCalendarBuilder
from financial_command_center.sheets.savings_goals  import SavingsGoalsBuilder
from financial_command_center.sheets.net_worth      import NetWorthBuilder
from financial_command_center.sheets.recurring      import RecurringBuilder
from financial_command_center.sheets.dashboard      import DashboardBuilder

# Mapping from SHEET_NAMES index to builder class
# Order in this list is the BUILD order (Settings first, Dashboard last)
# Index corresponds to the tab position in SHEET_NAMES
BUILD_ORDER = [
    # (sheet_name_index, BuilderClass)
    (9,  SettingsSheetBuilder),    # ⚙️ Settings — must be first (defines dropdowns)
    (1,  MonthlyBudgetBuilder),    # 💰 Monthly Budget
    (2,  IncomeTrackerBuilder),    # 📊 Income Tracker
    (3,  ExpenseLogBuilder),       # 🧾 Expense Log
    (4,  DebtTrackerBuilder),      # 💳 Debt Tracker
    (5,  BillCalendarBuilder),     # 📅 Bill Calendar
    (6,  SavingsGoalsBuilder),     # 🎯 Savings Goals
    (7,  NetWorthBuilder),         # 📈 Net Worth Tracker
    (8,  RecurringBuilder),        # 🔄 Recurring Transactions
    (0,  DashboardBuilder),        # 🏠 Dashboard — must be last (cross-sheet refs)
]

# Seconds to sleep between sheet builds to avoid hitting API rate limits
SLEEP_BETWEEN_SHEETS = 2


def create_spreadsheet(client) -> object:
    """Create the spreadsheet and all 10 named tabs."""
    year  = datetime.date.today().year
    title = f"Financial Command Center — {year}"

    print(f"\n📊 Creating spreadsheet: '{title}' ...")
    spreadsheet = client.create(title)

    # The first sheet is created automatically; rename it to our first tab
    worksheets = spreadsheet.worksheets()
    first_ws = worksheets[0]
    first_ws.update_title(SHEET_NAMES[0])

    # Create the remaining 9 tabs
    for name in SHEET_NAMES[1:]:
        print(f"   + Adding tab: {name}")
        spreadsheet.add_worksheet(title=name, rows=200, cols=30)
        time.sleep(0.5)  # brief pause between worksheet creation calls

    print(f"✅ Spreadsheet created with {len(SHEET_NAMES)} tabs.")
    return spreadsheet


def set_background_for_all_sheets(spreadsheet) -> None:
    """Set navy background as base for all sheets (before per-sheet builders run)."""
    from financial_command_center.config import COLORS
    from financial_command_center.utils.formatting import hex_to_rgb, repeat_cell_request

    print("🎨 Applying base background colors ...")
    all_requests = []
    for ws in spreadsheet.worksheets():
        bg_request = {
            "repeatCell": {
                "range": {
                    "sheetId":          ws.id,
                    "startRowIndex":    0,
                    "endRowIndex":      200,
                    "startColumnIndex": 0,
                    "endColumnIndex":   30,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": hex_to_rgb(COLORS["bg_primary"]),
                        "textFormat": {
                            "foregroundColor": hex_to_rgb(COLORS["text_primary"]),
                            "fontSize": 10,
                            "fontFamily": "Arial",
                        },
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        }
        all_requests.append(bg_request)

    if all_requests:
        spreadsheet.batch_update({"requests": all_requests})
    print("✅ Base formatting applied.")


def get_tab_gids(spreadsheet) -> list:
    """Return list of integer GIDs in SHEET_NAMES order."""
    ws_by_name = {ws.title: ws.id for ws in spreadsheet.worksheets()}
    return [ws_by_name.get(name, 0) for name in SHEET_NAMES]


def share_spreadsheet(spreadsheet, email: str = None) -> None:
    """Optionally share the spreadsheet with an email address."""
    if not email:
        email = os.environ.get("SHARE_WITH_EMAIL")
    if email:
        print(f"📧 Sharing spreadsheet with: {email}")
        spreadsheet.share(email, perm_type="user", role="writer")
        print("✅ Shared.")
    else:
        print("ℹ️  Tip: Set SHARE_WITH_EMAIL env var to auto-share the spreadsheet.")


def build_all_sheets(spreadsheet) -> None:
    """Run each sheet builder in the correct dependency order."""
    tab_gids   = get_tab_gids(spreadsheet)
    ws_by_name = {ws.title: ws for ws in spreadsheet.worksheets()}
    total      = len(BUILD_ORDER)

    for step, (sheet_idx, BuilderClass) in enumerate(BUILD_ORDER, start=1):
        sheet_name = SHEET_NAMES[sheet_idx]
        print(f"\n[{step}/{total}] Building: {sheet_name}")

        ws      = ws_by_name[sheet_name]
        builder = BuilderClass(
            spreadsheet=spreadsheet,
            worksheet=ws,
            sheet_index=sheet_idx,
        )

        try:
            builder.build(tab_gids)
            print(f"       ✅ Done.")
        except Exception as exc:
            print(f"       ⚠️  Warning — sheet build encountered an error: {exc}")
            print(f"           The sheet may be partially formatted. Continuing ...")

        if step < total:
            time.sleep(SLEEP_BETWEEN_SHEETS)


def reorder_tabs(spreadsheet) -> None:
    """
    Reorder the tabs so Dashboard is first (index 0).
    The API uses updateSheetProperties.index for ordering.
    """
    print("\n🔀 Reordering tabs to final display order ...")
    ws_by_name = {ws.title: ws.id for ws in spreadsheet.worksheets()}
    requests   = []

    for final_index, sheet_name in enumerate(SHEET_NAMES):
        sheet_id = ws_by_name.get(sheet_name)
        if sheet_id is None:
            continue
        requests.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "index":   final_index,
                },
                "fields": "index",
            }
        })

    if requests:
        spreadsheet.batch_update({"requests": requests})
    print("✅ Tabs reordered.")


def main() -> None:
    print("=" * 60)
    print("  🎖️  Financial Command Center — Build Script")
    print("  Veteran Transition Budget Tracker")
    print("=" * 60)

    # ── Authenticate ──────────────────────────────────────────────────
    print("\n🔑 Authenticating with Google Sheets API ...")
    client = get_client()
    print("✅ Authenticated.")

    # ── Create spreadsheet & tabs ─────────────────────────────────────
    spreadsheet = create_spreadsheet(client)

    # ── Apply base background to all sheets ───────────────────────────
    set_background_for_all_sheets(spreadsheet)

    # ── Build each sheet ──────────────────────────────────────────────
    build_all_sheets(spreadsheet)

    # ── Reorder tabs to final display order ───────────────────────────
    reorder_tabs(spreadsheet)

    # ── Optionally share ──────────────────────────────────────────────
    share_spreadsheet(spreadsheet)

    # ── Done ─────────────────────────────────────────────────────────
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
    print("\n" + "=" * 60)
    print("  🎉 BUILD COMPLETE!")
    print(f"\n  Spreadsheet URL:")
    print(f"  {url}")
    print("\n  Tips:")
    print("  • Open the URL above in your browser")
    print("  • Start on the ⚙️ Settings tab to enter your name")
    print("  • Update the 💰 Monthly Budget month selector (cell B3)")
    print("  • Add your own income/expenses to the log tabs")
    print("  • The Dashboard updates automatically as you add data")
    print("=" * 60)


if __name__ == "__main__":
    main()
