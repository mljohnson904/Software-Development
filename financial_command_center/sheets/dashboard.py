"""
🏠 Dashboard — Tab 1 (built LAST — references all other sheets)

The command center overview. All values pulled from other sheets via
direct cross-sheet references and IMPORTRANGE-style formulas.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title + tagline
  2     : ── Row A: Net Worth | Cash Flow | Budget Score ──
  3–5   : KPI cards (3 columns wide each)
  6     : ── Row B: Goal Progress ──
  7–12  : Goal progress bars
  13    : ── Row C: Upcoming Bills ──
  14–20 : Bills due next 7 days
  21    : ── Row D: Monthly Trend Sparklines ──
  22–26 : Sparkline section
  27    : ── Row E: Top Spending Categories ──
  28–32 : Chart placeholder + category list
"""

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_WIDE, COL_WIDTH_DEFAULT, COL_WIDTH_AMOUNT,
)
from financial_command_center.utils.formatting import (
    merge_cells_request, section_header_request, header_format_request,
    row_height_request, data_row_format_request, currency_format_request,
    percent_format_request, color, hex_to_rgb, repeat_cell_request,
    conditional_format_custom_formula, column_chart_request, line_chart_request,
    outer_border_request,
)


class DashboardBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = 12

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "🏠  Financial Command Center — Veteran's Budget Tracker")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER + 4))

        # ── KPI Cards Row ─────────────────────────────────────────────────
        # Card 1: Net Worth (cols 0–3)
        # Card 2: Monthly Cash Flow (cols 4–7)
        # Card 3: Budget Health Score (cols 8–11)
        self._write_kpi_card(
            label="💰 NET WORTH",
            formula="=IFERROR('📈 Net Worth Tracker'!B4,0)",
            row_label=2, row_value=3, row_sub=4,
            start_col=0, end_col=4,
            sub_formula=(
                '=IFERROR(IF(\'📈 Net Worth Tracker\'!D4>0,'
                '"▲ "&TEXT(\'📈 Net Worth Tracker\'!D4,"$#,##0"),'
                '"▼ "&TEXT(ABS(\'📈 Net Worth Tracker\'!D4),"$#,##0")),"—")'
            ),
            sub_label="vs Last Month",
        )
        self._write_kpi_card(
            label="📊 MONTHLY CASH FLOW",
            formula="=IFERROR('💰 Monthly Budget'!C11-'💰 Monthly Budget'!C{grand},0)".replace("{grand}", "0"),
            row_label=2, row_value=3, row_sub=4,
            start_col=4, end_col=8,
            sub_formula=(
                '=IFERROR("Income: "&TEXT(\'💰 Monthly Budget\'!C11,"$#,##0"),'
                '"Check Monthly Budget tab")'
            ),
            sub_label="This Month",
        )
        self._write_kpi_card(
            label="🎯 BUDGET HEALTH SCORE",
            formula=(
                '=IFERROR(MIN(100,MAX(0,ROUND('
                'IF(\'💰 Monthly Budget\'!C11>0,'
                '(1-\'💰 Monthly Budget\'!D11/\'💰 Monthly Budget\'!B11)*40,20)'
                '+IFERROR((1-\'💳 Debt Tracker\'!D10/\'💳 Debt Tracker\'!C10)*30,15)'
                '+IFERROR(\'🎯 Savings Goals\'!C5/\'🎯 Savings Goals\'!B5*30,10)'
                ',0))),50)'
            ),
            row_label=2, row_value=3, row_sub=4,
            start_col=8, end_col=12,
            sub_formula=(
                '=IF(IFERROR(MIN(100,MAX(0,ROUND('
                'IF(\'💰 Monthly Budget\'!C11>0,'
                '(1-\'💰 Monthly Budget\'!D11/\'💰 Monthly Budget\'!B11)*40,20)'
                '+IFERROR((1-\'💳 Debt Tracker\'!D10/\'💳 Debt Tracker\'!C10)*30,15)'
                '+IFERROR(\'🎯 Savings Goals\'!C5/\'🎯 Savings Goals\'!B5*30,10)'
                ',0))),50)>=70,"✅ GOOD","⚠️ NEEDS WORK")'
            ),
            sub_label="/ 100",
            fmt="integer",
        )

        # ── Spacer ────────────────────────────────────────────────────────
        self.add(row_height_request(sid, 5, 6, 12))

        # ── Goal Progress Bars ────────────────────────────────────────────
        self.section_divider(6, "🎯 SAVINGS GOAL PROGRESS", 0, self.NUM_COLS)
        goal_headers = ["Goal", "Saved", "Target", "Progress", "% Done", "Status", "", "", "", "", "", ""]
        ws.update([goal_headers[:self.NUM_COLS]], range_name="A8", value_input_option="USER_ENTERED")
        self.add(header_format_request(sid, 7, 0, 6, h_align="LEFT"))
        self.add(row_height_request(sid, 7, 8, ROW_HEIGHT_DATA))

        for i in range(6):
            goal_row_0 = 8 + i
            goal_row_1 = goal_row_0 + 1
            src_row_1  = 8 + i  # row in Savings Goals sheet (1-based)

            name_f   = f"=IFERROR('🎯 Savings Goals'!A{src_row_1},\"\")"
            saved_f  = f"=IFERROR('🎯 Savings Goals'!C{src_row_1},0)"
            target_f = f"=IFERROR('🎯 Savings Goals'!B{src_row_1},0)"
            bar_f    = f"=IFERROR('🎯 Savings Goals'!F{src_row_1},REPT(\"░\",20))"
            pct_f    = f"=IFERROR('🎯 Savings Goals'!G{src_row_1},0)"
            status_f = f"=IFERROR('🎯 Savings Goals'!H{src_row_1},\"\")"

            ws.update(
                [[name_f, saved_f, target_f, bar_f, pct_f, status_f, "", "", "", "", "", ""]],
                range_name=f"A{goal_row_1}",
                value_input_option="USER_ENTERED",
            )
            alt = (i % 2 == 0)
            self.add(data_row_format_request(sid, goal_row_0, goal_row_0 + 1, 0, 6, alt))
            self.add(row_height_request(sid, goal_row_0, goal_row_0 + 1, ROW_HEIGHT_DATA))
            self.add(currency_format_request(sid, goal_row_0, goal_row_0 + 1, 1, 3))
            self.add(percent_format_request(sid, goal_row_0, goal_row_0 + 1, 4, 5))

            # Status color
            self.add(conditional_format_custom_formula(
                sid, goal_row_0, goal_row_0 + 1, 5, 6,
                f'=$F{goal_row_1}="COMPLETED"', "success",
                text_color="text_dark", bold=True, index=0,
            ))
            self.add(conditional_format_custom_formula(
                sid, goal_row_0, goal_row_0 + 1, 5, 6,
                f'=$F{goal_row_1}="BEHIND"', "danger",
                text_color="text_primary", bold=True, index=1,
            ))

        # ── Spacer ────────────────────────────────────────────────────────
        self.add(row_height_request(sid, 14, 15, 12))

        # ── Upcoming Bills ────────────────────────────────────────────────
        self.section_divider(15, "📅 UPCOMING BILLS (Next 7 Days)", 0, 6)
        bills_headers = ["Bill Name", "Amount ($)", "Due Day", "Account",
                         "Auto-Pay?", "Days Away", "", "", "", "", "", ""]
        ws.update([bills_headers[:self.NUM_COLS]], range_name="A17",
                  value_input_option="USER_ENTERED")
        self.add(header_format_request(sid, 16, 0, 6))
        self.add(row_height_request(sid, 16, 17, ROW_HEIGHT_DATA))

        # Pull bills due within 7 days from Bill Calendar registry
        # Bill Calendar registry is at rows 13+ (1-based), columns A-H
        # We do a simple lookup for each of the next 7 day numbers
        for i in range(7):
            row_0 = 17 + i
            row_1 = row_0 + 1
            # Look up bills where due_day >= today+i and due_day <= today+i+1 and active
            day_num = f"=DAY(TODAY()+{i})"
            bill_name_f = (
                f'=IFERROR(INDEX(\'📅 Bill Calendar\'!$A$13:$A$30,'
                f'MATCH(DAY(TODAY()+{i}),\'📅 Bill Calendar\'!$C$13:$C$30,0)),"")'
            )
            bill_amt_f = (
                f'=IFERROR(INDEX(\'📅 Bill Calendar\'!$B$13:$B$30,'
                f'MATCH(DAY(TODAY()+{i}),\'📅 Bill Calendar\'!$C$13:$C$30,0)),"")'
            )
            bill_day_f = (
                f'=IFERROR(INDEX(\'📅 Bill Calendar\'!$C$13:$C$30,'
                f'MATCH(DAY(TODAY()+{i}),\'📅 Bill Calendar\'!$C$13:$C$30,0)),"")'
            )
            bill_acct_f = (
                f'=IFERROR(INDEX(\'📅 Bill Calendar\'!$E$13:$E$30,'
                f'MATCH(DAY(TODAY()+{i}),\'📅 Bill Calendar\'!$C$13:$C$30,0)),"")'
            )
            bill_auto_f = (
                f'=IFERROR(INDEX(\'📅 Bill Calendar\'!$D$13:$D$30,'
                f'MATCH(DAY(TODAY()+{i}),\'📅 Bill Calendar\'!$C$13:$C$30,0)),"")'
            )
            days_away_f = f'=IF(A{row_1}<>"",{i},"")'

            ws.update(
                [[bill_name_f, bill_amt_f, bill_day_f, bill_acct_f, bill_auto_f,
                  days_away_f, "", "", "", "", "", ""]],
                range_name=f"A{row_1}",
                value_input_option="USER_ENTERED",
            )
            alt = (i % 2 == 0)
            self.add(data_row_format_request(sid, row_0, row_0 + 1, 0, 6, alt))
            self.add(row_height_request(sid, row_0, row_0 + 1, ROW_HEIGHT_DATA))

            # Highlight if due today
            self.add(conditional_format_custom_formula(
                sid, row_0, row_0 + 1, 0, 6,
                f'=AND($A{row_1}<>"",$F{row_1}=0)',
                "warning", text_color="text_dark", index=0,
            ))

        self.add(currency_format_request(sid, 16, 24, 1, 2))
        self.add(row_height_request(sid, 24, 25, 12))  # spacer

        # ── Monthly Trend Sparklines ──────────────────────────────────────
        self.section_divider(25, "📈 6-MONTH TRENDS", 0, self.NUM_COLS)
        trend_headers = ["Metric", "Trend (6 Months)", "Current", "", "", "", "", "", "", "", "", ""]
        ws.update([trend_headers[:self.NUM_COLS]], range_name="A27",
                  value_input_option="USER_ENTERED")
        self.add(header_format_request(sid, 26, 0, 4))
        self.add(row_height_request(sid, 26, 27, ROW_HEIGHT_DATA))

        sparkline_data = [
            (
                "Monthly Income",
                "=SPARKLINE('📊 Income Tracker'!B5:G5,{\"charttype\",\"line\";\"color\",\"#E8B84B\"})",
                "=IFERROR('📊 Income Tracker'!B5,0)",
            ),
            (
                "Monthly Expenses",
                "=SPARKLINE('🧾 Expense Log'!B5:G5,{\"charttype\",\"line\";\"color\",\"#F44336\"})",
                "=IFERROR('🧾 Expense Log'!B5,0)",
            ),
            (
                "Net Worth",
                "=SPARKLINE('📈 Net Worth Tracker'!D25:D36,{\"charttype\",\"line\";\"color\",\"#4CAF50\"})",
                "=IFERROR('📈 Net Worth Tracker'!B4,0)",
            ),
        ]

        for i, (label, sparkline_f, current_f) in enumerate(sparkline_data):
            row_0 = 27 + i
            row_1 = row_0 + 1
            ws.update(
                [[label, sparkline_f, current_f, "", "", "", "", "", "", "", "", ""]],
                range_name=f"A{row_1}",
                value_input_option="USER_ENTERED",
            )
            alt = (i % 2 == 0)
            self.add(data_row_format_request(sid, row_0, row_0 + 1, 0, 4, alt))
            self.add(row_height_request(sid, row_0, row_0 + 1, 40))

        self.add(currency_format_request(sid, 27, 30, 2, 3))

        # ── Top Spending Categories section ───────────────────────────────
        self.section_divider(30, "💳 THIS MONTH'S TOP SPENDING", 0, 6)
        spend_headers = ["Category", "Amount ($)", "% of Expenses", "Budget", "Remaining", ""]
        ws.update([spend_headers[:6]], range_name="A32", value_input_option="USER_ENTERED")
        self.add(header_format_request(sid, 31, 0, 6))
        self.add(row_height_request(sid, 31, 32, ROW_HEIGHT_DATA))

        # Top 5 categories — reference Monthly Budget actual column
        # Budget tab: col C = actuals, categories are in rows based on the template
        # We hard-reference the subtotal rows by name here for the top categories
        top_cats = [
            ("Housing",         "=IFERROR('💰 Monthly Budget'!C21,0)", "=IFERROR('💰 Monthly Budget'!B21,0)"),
            ("Transportation",  "=IFERROR('💰 Monthly Budget'!C27,0)", "=IFERROR('💰 Monthly Budget'!B27,0)"),
            ("Debt Payments",   "=IFERROR('💰 Monthly Budget'!C59,0)", "=IFERROR('💰 Monthly Budget'!B59,0)"),
            ("Food",            "=IFERROR('💰 Monthly Budget'!C33,0)", "=IFERROR('💰 Monthly Budget'!B33,0)"),
            ("Personal",        "=IFERROR('💰 Monthly Budget'!C46,0)", "=IFERROR('💰 Monthly Budget'!B46,0)"),
        ]
        total_expenses_f = "=IFERROR(SUM(B33:B37),1)"
        for i, (cat, actual_f, budget_f) in enumerate(top_cats):
            row_0 = 32 + i
            row_1 = row_0 + 1
            pct_f = f"=IFERROR(B{row_1}/{total_expenses_f},0)"
            remain_f = f"=IFERROR(D{row_1}-B{row_1},0)"
            ws.update(
                [[cat, actual_f, pct_f, budget_f, remain_f, ""]],
                range_name=f"A{row_1}",
                value_input_option="USER_ENTERED",
            )
            alt = (i % 2 == 0)
            self.add(data_row_format_request(sid, row_0, row_0 + 1, 0, 6, alt))
            self.add(row_height_request(sid, row_0, row_0 + 1, ROW_HEIGHT_DATA))

        self.add(currency_format_request(sid, 32, 37, 1, 2))
        self.add(percent_format_request(sid, 32, 37, 2, 3))
        self.add(currency_format_request(sid, 32, 37, 3, 5))

        # Bar chart for top spending categories
        self.add(column_chart_request(
            sheet_id=sid,
            title="Top Spending This Month",
            data_sheet_id=sid,
            domain_start_row=32, domain_end_row=37,
            domain_col=0,
            series_start_row=32, series_end_row=37,
            series_col=1,
            anchor_row=32, anchor_col=6,
        ))

        # ── Veterans Tips panel ───────────────────────────────────────────
        self.add(row_height_request(sid, 37, 38, 12))
        self.section_divider(38, "🎖️ VETERAN FINANCE TIPS", 0, self.NUM_COLS)
        tips = [
            "✅ VA Disability and GI Bill BAH are non-taxable — route them directly to savings/debt payoff.",
            "✅ Maximize TSP contributions while still on active duty if separating mid-year.",
            "✅ SBA veteran loans available for business startups — no prepayment penalty.",
            "✅ Review your VA home loan benefit — 0% down, no PMI, competitive rates.",
        ]
        for i, tip in enumerate(tips):
            row_0 = 39 + i
            row_1 = row_0 + 1
            ws.update_cell(row_1, 1, tip)
            self.add(merge_cells_request(sid, row_0, row_0 + 1, 0, self.NUM_COLS))
            self.add(repeat_cell_request(sid, row_0, row_0 + 1, 0, self.NUM_COLS, {
                "backgroundColor": color("bg_secondary"),
                "textFormat": {"foregroundColor": color("text_secondary"),
                               "fontSize": 10, "italic": False},
                "verticalAlignment": "MIDDLE",
                "wrapStrategy": "WRAP",
            }))
            self.add(row_height_request(sid, row_0, row_0 + 1, 28))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (0,  1,  180),
            (1,  2,  120),
            (2,  3,  100),
            (3,  4,  100),
            (4,  5,  100),
            (5,  6,  100),
            (6,  7,  100),
            (7,  8,  100),
            (8,  9,  100),
            (9,  10, 100),
            (10, 11, 100),
            (11, 12, 100),
        ])

        self.flush()

    # ------------------------------------------------------------------
    # KPI card helper
    # ------------------------------------------------------------------

    def _write_kpi_card(self, label: str, formula: str,
                         row_label: int, row_value: int, row_sub: int,
                         start_col: int, end_col: int,
                         sub_formula: str = "", sub_label: str = "",
                         fmt: str = "currency") -> None:
        sid = self.sheet_id
        ws  = self.worksheet

        # Label row
        ws.update_cell(row_label + 1, start_col + 1, label)
        self.add(merge_cells_request(sid, row_label, row_label + 1, start_col, end_col))
        self.add(repeat_cell_request(sid, row_label, row_label + 1, start_col, end_col, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"bold": True, "foregroundColor": color("accent_gold"),
                           "fontSize": 10},
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, row_label, row_label + 1, ROW_HEIGHT_HEADER))

        # Value row
        ws.update_cell(row_value + 1, start_col + 1, formula)
        self.add(merge_cells_request(sid, row_value, row_value + 1, start_col, end_col))
        self.add(repeat_cell_request(sid, row_value, row_value + 1, start_col, end_col, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"bold": True, "foregroundColor": color("text_primary"),
                           "fontSize": 22},
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, row_value, row_value + 1, 50))

        if fmt == "currency":
            self.add(currency_format_request(sid, row_value, row_value + 1,
                                             start_col, start_col + 1))

        # Sub-label row
        if sub_formula:
            ws.update_cell(row_sub + 1, start_col + 1, sub_formula)
        if sub_label:
            ws.update_cell(row_sub + 1, start_col + 2, sub_label)
        self.add(merge_cells_request(sid, row_sub, row_sub + 1, start_col, end_col))
        self.add(repeat_cell_request(sid, row_sub, row_sub + 1, start_col, end_col, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"foregroundColor": color("text_secondary"), "fontSize": 9},
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, row_sub, row_sub + 1, 24))

        # Gold border around the entire card
        self.add(outer_border_request(sid, row_label, row_sub + 1, start_col, end_col))
