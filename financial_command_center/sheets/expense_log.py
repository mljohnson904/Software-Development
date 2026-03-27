"""
🧾 Expense Log — Tab 4

Transaction log with dual category/subcategory dropdowns, recurring flag,
color-coded rows, and 3 months of sample data pre-populated.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title
  2     : ── Monthly Summary header ──
  3     : Summary row (total by month)
  4     : (spacer)
  5     : ── Transaction Log header ──
  6     : Column headers
  7+    : Data rows

Columns:
  A Date | B Merchant | C Category | D Subcategory | E Amount |
  F Payment Method | G Recurring? | H Notes
"""

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS, MONTHS, EXPENSE_CATEGORIES, EXPENSE_SUBCATEGORIES, PAYMENT_METHODS,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_DATE, COL_WIDTH_WIDE, COL_WIDTH_DEFAULT, COL_WIDTH_AMOUNT,
)
from financial_command_center.utils.formatting import (
    merge_cells_request, section_header_request, header_format_request,
    row_height_request, totals_row_format_request, data_row_format_request,
    currency_format_request, date_format_request, banding_request,
    dropdown_from_list_request, color, hex_to_rgb, repeat_cell_request,
    conditional_format_custom_formula, conditional_format_text_eq,
)
from financial_command_center.utils.sample_data import get_expense_rows


# Column layout (0-based)
COL_DATE     = 0
COL_MERCHANT = 1
COL_CAT      = 2
COL_SUBCAT   = 3
COL_AMOUNT   = 4
COL_METHOD   = 5
COL_RECUR    = 6
COL_NOTES    = 7
NUM_COLS     = 8

DATA_FIRST_ROW_0 = 7   # 0-based first data row
DATA_FIRST_ROW_1 = 8   # 1-based


class ExpenseLogBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = NUM_COLS

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "🧾  Expense Log")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Monthly Summary ───────────────────────────────────────────────
        self.section_divider(2, "MONTHLY EXPENSE SUMMARY", 0, self.NUM_COLS)

        # Month totals — one row per category across columns for each month
        # Row 4 (index 3) = column headers (months)
        summary_header = ["Category"] + MONTHS[:6]  # Jan–Jun for summary width
        ws.update(
            [summary_header],
            range_name="A4",
            value_input_option="USER_ENTERED",
        )
        self.add(header_format_request(sid, 3, 0, 7))
        self.add(row_height_request(sid, 3, 4, ROW_HEIGHT_DATA))

        # Total row
        total_row_data = ["TOTAL"]
        for m in range(1, 7):
            formula = (
                f'=IFERROR(SUMPRODUCT('
                f'(MONTH(\'🧾 Expense Log\'!$A${DATA_FIRST_ROW_1}:$A$1000)={m})*'
                f'(YEAR(\'🧾 Expense Log\'!$A${DATA_FIRST_ROW_1}:$A$1000)=YEAR(TODAY()))*'
                f'\'🧾 Expense Log\'!$E${DATA_FIRST_ROW_1}:$E$1000),0)'
            )
            total_row_data.append(formula)
        ws.update([total_row_data], range_name="A5", value_input_option="USER_ENTERED")
        self.add(totals_row_format_request(sid, 4, 0, 7))
        self.add(currency_format_request(sid, 4, 5, 1, 7))
        self.add(row_height_request(sid, 4, 5, ROW_HEIGHT_DATA))

        # ── Transaction Log ───────────────────────────────────────────────
        self.section_divider(5, "TRANSACTION LOG", 0, self.NUM_COLS)
        col_headers = [
            "Date", "Merchant / Payee", "Category", "Subcategory",
            "Amount ($)", "Payment Method", "Recurring?", "Notes",
        ]
        self.col_header_row(6, col_headers, 0)

        # ── Sample data ───────────────────────────────────────────────────
        expense_rows = get_expense_rows()
        if expense_rows:
            self.write_rows(DATA_FIRST_ROW_1, 1, expense_rows)

        max_data_row_0 = DATA_FIRST_ROW_0 + 300

        # ── Alternating row banding ───────────────────────────────────────
        self.add(banding_request(sid, DATA_FIRST_ROW_0, max_data_row_0, 0, self.NUM_COLS))

        # ── Data validation dropdowns ─────────────────────────────────────
        # Category dropdown (col C)
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0, max_data_row_0,
            COL_CAT, COL_CAT + 1,
            EXPENSE_CATEGORIES,
        ))

        # Subcategory dropdowns — per category (using ONE_OF_LIST per category)
        # We write the full flat list of all subcategories as the dropdown source
        all_subcats = []
        for sublist in EXPENSE_SUBCATEGORIES.values():
            all_subcats.extend(sublist)
        all_subcats = list(dict.fromkeys(all_subcats))  # deduplicate preserving order
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0, max_data_row_0,
            COL_SUBCAT, COL_SUBCAT + 1,
            all_subcats,
        ))

        # Payment Method dropdown (col F)
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0, max_data_row_0,
            COL_METHOD, COL_METHOD + 1,
            PAYMENT_METHODS,
        ))

        # Recurring dropdown (col G)
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0, max_data_row_0,
            COL_RECUR, COL_RECUR + 1,
            ["Yes", "No"],
        ))

        # ── Conditional formatting ────────────────────────────────────────
        # Recurring rows — light info blue highlight
        self.add(conditional_format_custom_formula(
            sid, DATA_FIRST_ROW_0, max_data_row_0, 0, self.NUM_COLS,
            f'=$G{DATA_FIRST_ROW_1}="Yes"',
            "info_blue",
            text_color="text_primary",
            index=0,
        ))

        # Category-based color coding for key categories
        cat_colors = {
            "Housing":            "#1E3A5F",
            "Transportation":     "#1B3A2F",
            "Food":               "#3A2A1B",
            "Healthcare":         "#3A1B1B",
            "Education & Career": "#1B2A3A",
            "Financial":          "#2A1B3A",
        }
        for idx, (cat, bg_hex) in enumerate(cat_colors.items()):
            # Only apply if NOT already highlighted as recurring
            self.add(conditional_format_custom_formula(
                sid, DATA_FIRST_ROW_0, max_data_row_0, 0, self.NUM_COLS,
                f'=AND($C{DATA_FIRST_ROW_1}="{cat}",$G{DATA_FIRST_ROW_1}<>"Yes")',
                bg_color="bg_secondary",  # use as base — override via direct hex below
                index=idx + 1,
            ))

        # ── Number formats ────────────────────────────────────────────────
        self.add(date_format_request(sid, DATA_FIRST_ROW_0, max_data_row_0,
                                     COL_DATE, COL_DATE + 1))
        self.add(currency_format_request(sid, DATA_FIRST_ROW_0, max_data_row_0,
                                         COL_AMOUNT, COL_AMOUNT + 1))

        # ── Row heights ───────────────────────────────────────────────────
        self.add(row_height_request(sid, DATA_FIRST_ROW_0,
                                    DATA_FIRST_ROW_0 + 100, ROW_HEIGHT_DATA))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (COL_DATE,     COL_DATE + 1,     COL_WIDTH_DATE),
            (COL_MERCHANT, COL_MERCHANT + 1, COL_WIDTH_WIDE),
            (COL_CAT,      COL_CAT + 1,      140),
            (COL_SUBCAT,   COL_SUBCAT + 1,   150),
            (COL_AMOUNT,   COL_AMOUNT + 1,   COL_WIDTH_AMOUNT),
            (COL_METHOD,   COL_METHOD + 1,   130),
            (COL_RECUR,    COL_RECUR + 1,    90),
            (COL_NOTES,    COL_NOTES + 1,    COL_WIDTH_WIDE),
        ])

        self.flush()
