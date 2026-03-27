"""
💰 Monthly Budget — Tab 2

Master budget planning sheet with income at the top and collapsible
expense category groups below. Actual spending is pulled from the
Expense Log via SUMIFS formulas that respect the month/year selector.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title
  2     : Month/Year selector row
  3     : ── INCOME section header ──
  4     : Income column headers
  5–9   : Income rows (5 sources)
  10    : Income TOTAL row
  11    : ── EXPENSES section header ──
  12    : Expense column headers
  13+   : Expense rows grouped by category (collapsible)
  last  : Remaining Spendable row
"""

import datetime
from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS, MONTHS,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA, COL_WIDTH_DATE,
    COL_WIDTH_WIDE, COL_WIDTH_DEFAULT, COL_WIDTH_AMOUNT,
    EXPENSE_BUDGET_TEMPLATE, INCOME_BUDGET_TEMPLATE,
)
from financial_command_center.utils.formatting import (
    merge_cells_request,
    section_header_request,
    header_format_request,
    row_height_request,
    col_width_request,
    data_row_format_request,
    totals_row_format_request,
    currency_format_request,
    conditional_format_custom_formula,
    dropdown_from_list_request,
    add_row_group_request,
    color,
    hex_to_rgb,
    grid_range,
    repeat_cell_request,
)


# Expense Log sheet name for SUMIFS cross-references
EXPENSE_SHEET = "🧾 Expense Log"


class MonthlyBudgetBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = 6

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id
        cy  = datetime.date.today().year
        cm  = datetime.date.today().month

        self.apply_base_formatting(frozen_rows=3)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "💰  Monthly Budget")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Month / Year selector (row 3, index 2) ────────────────────────
        ws.update_cell(3, 1, "SELECT MONTH:")
        ws.update_cell(3, 2, MONTHS[cm - 1])   # B3 — month dropdown
        ws.update_cell(3, 3, str(cy))           # C3 — year (manual entry)
        self.add(dropdown_from_list_request(sid, 2, 3, 1, 2, MONTHS))
        self.add(merge_cells_request(sid, 2, 3, 0, 1))
        self.add(repeat_cell_request(sid, 2, 3, 0, 1, {
            "textFormat": {"bold": True, "foregroundColor": color("accent_gold")},
            "backgroundColor": color("bg_secondary"),
            "verticalAlignment": "MIDDLE",
        }))
        self.add(repeat_cell_request(sid, 2, 3, 1, 3, {
            "backgroundColor": color("accent_gold"),
            "textFormat": {"bold": True, "foregroundColor": color("text_dark"),
                           "fontSize": 11},
            "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, 2, 3, ROW_HEIGHT_HEADER))

        # ── INCOME section ────────────────────────────────────────────────
        self.section_divider(3, "INCOME", 0, self.NUM_COLS)
        income_headers = ["Source", "Expected ($)", "Actual ($)", "Difference ($)", "Notes", ""]
        self.col_header_row(4, income_headers, 0)

        # Helper: SUMIFS formula filtering Income Tracker by source & month/year
        # Income Tracker: Date=colA, Source=colB, Amount=colD
        def income_actual_formula(source_name: str) -> str:
            return (
                f'=IFERROR(SUMIFS(\'📊 Income Tracker\'!$D:$D,'
                f'\'📊 Income Tracker\'!$B:$B,A{{row}},'
                f'\'📊 Income Tracker\'!$C:$C,"<>VA Disability*",'  # rough taxable filter
                f'MONTH(\'📊 Income Tracker\'!$A:$A),MATCH($B$3,{{"January","February","March","April","May","June","July","August","September","October","November","December"}},0),'
                f'YEAR(\'📊 Income Tracker\'!$A:$A),$C$3),0)'
            )

        income_start = 5  # 1-based row
        for i, (source, expected) in enumerate(INCOME_BUDGET_TEMPLATE):
            row_1b = income_start + i
            row_0b = row_1b - 1
            # For actual we use a simplified SUMIFS — users can adjust
            actual_formula = (
                f'=IFERROR(SUMPRODUCT('
                f'(\'📊 Income Tracker\'!$B$5:$B$500=A{row_1b})*'
                f'(MONTH(\'📊 Income Tracker\'!$A$5:$A$500)=MATCH($B$3,'
                f'{{"January","February","March","April","May","June",'
                f'"July","August","September","October","November","December"}},0))*'
                f'(YEAR(\'📊 Income Tracker\'!$A$5:$A$500)=VALUE($C$3))*'
                f'\'📊 Income Tracker\'!$D$5:$D$500),0)'
            )
            diff_formula = f"=C{row_1b}-B{row_1b}"
            ws.update(
                [[source, expected, actual_formula, diff_formula, "", ""]],
                range_name=f"A{row_1b}",
                value_input_option="USER_ENTERED",
            )
            alt = (i % 2 == 0)
            self.add(data_row_format_request(sid, row_0b, row_0b + 1, 0, self.NUM_COLS, alt))
            self.add(row_height_request(sid, row_0b, row_0b + 1, ROW_HEIGHT_DATA))

        # Income TOTAL row
        income_end_1b = income_start + len(INCOME_BUDGET_TEMPLATE)
        total_row_1b  = income_end_1b + 1
        total_row_0b  = total_row_1b - 1
        ws.update(
            [[
                "TOTAL INCOME",
                f"=SUM(B{income_start}:B{income_end_1b})",
                f"=SUM(C{income_start}:C{income_end_1b})",
                f"=SUM(D{income_start}:D{income_end_1b})",
                "", "",
            ]],
            range_name=f"A{total_row_1b}",
            value_input_option="USER_ENTERED",
        )
        self.add(totals_row_format_request(sid, total_row_0b, 0, self.NUM_COLS))
        self.add(row_height_request(sid, total_row_0b, total_row_0b + 1, ROW_HEIGHT_DATA))

        # Apply currency format to income numeric cols
        self.add(currency_format_request(sid, 4, total_row_0b + 1, 1, 4))

        # ── EXPENSES section ──────────────────────────────────────────────
        exp_section_row_0 = total_row_0b + 1
        self.section_divider(exp_section_row_0, "EXPENSES", 0, self.NUM_COLS)
        exp_header_row_0 = exp_section_row_0 + 1
        exp_headers = ["Category / Item", "Budgeted ($)", "Actual ($)", "Difference ($)", "Status", "Notes"]
        self.col_header_row(exp_header_row_0, exp_headers, 0)

        current_row_1b = exp_header_row_0 + 2  # 1-based, start of first category

        cat_total_cells = []   # collect per-category total refs for grand total

        for cat, items in EXPENSE_BUDGET_TEMPLATE.items():
            # Category header row
            cat_row_0 = current_row_1b - 1
            ws.update_cell(current_row_1b, 1, f"▸  {cat}")
            self.add(merge_cells_request(sid, cat_row_0, cat_row_0 + 1, 0, self.NUM_COLS))
            self.add(repeat_cell_request(sid, cat_row_0, cat_row_0 + 1, 0, self.NUM_COLS, {
                "backgroundColor": hex_to_rgb(COLORS["bg_secondary"]),
                "textFormat": {"bold": True, "foregroundColor": color("accent_gold"), "fontSize": 10},
                "verticalAlignment": "MIDDLE",
            }))
            self.add(row_height_request(sid, cat_row_0, cat_row_0 + 1, ROW_HEIGHT_HEADER))
            current_row_1b += 1

            group_start_0 = current_row_1b - 1  # 0-based start of collapsible group

            for j, (item_name, budgeted) in enumerate(items):
                row_1b = current_row_1b
                row_0b = row_1b - 1
                actual_formula = (
                    f'=IFERROR(SUMPRODUCT('
                    f'(\'🧾 Expense Log\'!$D$5:$D$500=B{row_1b})*'
                    f'(MONTH(\'🧾 Expense Log\'!$A$5:$A$500)=MATCH($B$3,'
                    f'{{"January","February","March","April","May","June",'
                    f'"July","August","September","October","November","December"}},0))*'
                    f'(YEAR(\'🧾 Expense Log\'!$A$5:$A$500)=VALUE($C$3))*'
                    f'\'🧾 Expense Log\'!$E$5:$E$500),0)'
                )
                diff_formula   = f"=C{row_1b}-B{row_1b}"
                status_formula = (
                    f'=IF(B{row_1b}=0,"",IF(C{row_1b}<=B{row_1b},"✅ OK",'
                    f'IF(C{row_1b}<=B{row_1b}*1.1,"⚠️ NEAR","🔴 OVER")))'
                )
                ws.update(
                    [[item_name, budgeted, actual_formula, diff_formula, status_formula, ""]],
                    range_name=f"A{row_1b}",
                    value_input_option="USER_ENTERED",
                )
                alt = (j % 2 == 0)
                self.add(data_row_format_request(sid, row_0b, row_0b + 1, 0, self.NUM_COLS, alt))
                self.add(row_height_request(sid, row_0b, row_0b + 1, ROW_HEIGHT_DATA))

                # Conditional formatting: difference col (D) — green/yellow/red
                self.add(conditional_format_custom_formula(
                    sid, row_0b, row_0b + 1, 3, 4,
                    f"=AND(B{row_1b}>0,C{row_1b}<=B{row_1b})", "success",
                    index=0,
                ))
                self.add(conditional_format_custom_formula(
                    sid, row_0b, row_0b + 1, 3, 4,
                    f"=AND(B{row_1b}>0,C{row_1b}>B{row_1b},C{row_1b}<=B{row_1b}*1.1)", "warning",
                    index=1,
                ))
                self.add(conditional_format_custom_formula(
                    sid, row_0b, row_0b + 1, 3, 4,
                    f"=AND(B{row_1b}>0,C{row_1b}>B{row_1b}*1.1)", "danger",
                    index=2,
                ))
                current_row_1b += 1

            # Category subtotal row
            sub_row_1b = current_row_1b
            sub_row_0b = sub_row_1b - 1
            sub_start  = group_start_0 + 1  # 1-based first item of this group
            sub_end    = current_row_1b - 1
            ws.update(
                [[
                    f"  {cat} Total",
                    f"=SUM(B{sub_start}:B{sub_end})",
                    f"=SUM(C{sub_start}:C{sub_end})",
                    f"=SUM(D{sub_start}:D{sub_end})",
                    "", "",
                ]],
                range_name=f"A{sub_row_1b}",
                value_input_option="USER_ENTERED",
            )
            self.add(totals_row_format_request(sid, sub_row_0b, 0, self.NUM_COLS))
            self.add(row_height_request(sid, sub_row_0b, sub_row_0b + 1, ROW_HEIGHT_DATA))
            cat_total_cells.append(f"C{sub_row_1b}")

            # Collapsible row group for the items (exclude category header + subtotal)
            if current_row_1b - group_start_0 > 1:
                self.add(add_row_group_request(sid, group_start_0, sub_row_0b))

            current_row_1b += 1

        # ── Grand Total Expenses ──────────────────────────────────────────
        grand_row_1b = current_row_1b + 1
        grand_row_0b = grand_row_1b - 1
        exp_total_formula = "=SUM(" + ",".join(cat_total_cells) + ")"
        ws.update(
            [[
                "TOTAL EXPENSES",
                f"=SUMIF(B{exp_header_row_0+2}:B{grand_row_1b-2},\">0\")",
                exp_total_formula,
                f"=C{grand_row_1b}-B{grand_row_1b}",
                "", "",
            ]],
            range_name=f"A{grand_row_1b}",
            value_input_option="USER_ENTERED",
        )
        self.add(totals_row_format_request(sid, grand_row_0b, 0, self.NUM_COLS))
        self.add(row_height_request(sid, grand_row_0b, grand_row_0b + 1, ROW_HEIGHT_DATA + 4))

        # ── Remaining Spendable ───────────────────────────────────────────
        remain_row_1b = grand_row_1b + 2
        remain_row_0b = remain_row_1b - 1
        ws.update(
            [[
                "💵  REMAINING SPENDABLE",
                f"=B{total_row_1b}-B{grand_row_1b}",
                f"=C{total_row_1b}-C{grand_row_1b}",
                f"=D{total_row_1b}-D{grand_row_1b}",
                "", "",
            ]],
            range_name=f"A{remain_row_1b}",
            value_input_option="USER_ENTERED",
        )
        self.add(repeat_cell_request(sid, remain_row_0b, remain_row_0b + 1, 0, self.NUM_COLS, {
            "backgroundColor": hex_to_rgb(COLORS["accent_gold"]),
            "textFormat": {"bold": True, "fontSize": 11,
                           "foregroundColor": color("text_dark")},
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, remain_row_0b, remain_row_0b + 1, ROW_HEIGHT_HEADER))

        # Apply currency format to all expense numeric cols
        self.add(currency_format_request(sid, exp_header_row_0 + 1, remain_row_0b + 1, 1, 4))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (0, 1, COL_WIDTH_WIDE),
            (1, 2, COL_WIDTH_AMOUNT),
            (2, 3, COL_WIDTH_AMOUNT),
            (3, 4, COL_WIDTH_AMOUNT),
            (4, 5, 100),
            (5, 6, COL_WIDTH_DEFAULT),
        ])

        self.flush()
