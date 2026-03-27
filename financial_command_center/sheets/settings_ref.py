"""
⚙️ Settings & Reference — Tab 10

Built FIRST at runtime because it defines the dropdown source lists
used by data validation rules on all other sheets.

Layout:
  Row 1        : Navigation bar
  Row 2        : Sheet title
  Rows 4–10    : User Profile section
  Rows 12–14   : Budget Settings
  Rows 16–20   : Color Legend
  Rows 22–25   : Formula Reference
  Col P+ (idx 15+): Hidden dropdown source data for all sheets
"""

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS,
    INCOME_CATEGORIES, EXPENSE_CATEGORIES, EXPENSE_SUBCATEGORIES,
    PAYMENT_METHODS, FREQUENCIES, PAYOFF_METHODS, MONTHS,
    SETTINGS_VALIDATION_COL,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_WIDE, COL_WIDTH_DEFAULT,
)
from financial_command_center.utils.formatting import (
    repeat_cell_request,
    section_header_request,
    header_format_request,
    row_height_request,
    col_width_request,
    merge_cells_request,
    color,
    hex_to_rgb,
    data_row_format_request,
)


class SettingsSheetBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = 10

    def build(self, tab_gids: list) -> None:
        ws = self.worksheet
        sid = self.sheet_id

        # ── Base formatting ──────────────────────────────────────────────
        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title (row 2, index 1) ─────────────────────────────────
        ws.update_cell(2, 1, "⚙️  Settings & Reference")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── User Profile ─────────────────────────────────────────────────
        self.section_divider(3, "👤  User Profile", 0, 4)
        profile_headers = ["Field", "Value", "Notes", ""]
        self.col_header_row(4, profile_headers, 0)

        profile_data = [
            ["Your Name",            "Veteran Transitioning",    "Displayed on Dashboard",                   ""],
            ["Currency Symbol",      "$",                        "USD",                                      ""],
            ["Pay Frequency",        "Bi-Weekly",                "Weekly / Bi-Weekly / Monthly",              ""],
            ["Budget Start Day",     "1",                        "Day of month budget period begins",         ""],
            ["Current Month",        f"=TEXT(TODAY(),\"MMMM\")", "Auto-detected — override if needed",       ""],
            ["Current Year",         "=YEAR(TODAY())",           "Auto-detected",                            ""],
        ]
        self.write_rows(6, 1, profile_data)
        self.add(data_row_format_request(sid, 5, 11, 0, 4))

        # ── Budget Settings ───────────────────────────────────────────────
        self.section_divider(11, "⚙️  Budget Settings", 0, 4)
        budget_settings = [
            ["Rollover Unused Budget",  "No",   "Yes = carry leftover to next month",  ""],
            ["Show Cents",              "Yes",  "Yes = $#,##0.00 / No = $#,##0",       ""],
            ["Alert Threshold (%)",     "10",   "% over budget before yellow warning", ""],
        ]
        self.write_rows(13, 1, budget_settings)
        self.add(data_row_format_request(sid, 12, 15, 0, 4))

        # ── Color Legend ──────────────────────────────────────────────────
        self.section_divider(15, "🎨  Color Legend", 0, 4)
        legend_headers = ["Color", "Hex Code", "Meaning", ""]
        self.col_header_row(16, legend_headers, 0)

        legend_data = [
            ["Deep Navy Background", COLORS["bg_primary"],    "Main background color",                 ""],
            ["Card Navy",            COLORS["bg_secondary"],  "Secondary background / alternating rows",""],
            ["Accent Gold",          COLORS["accent_gold"],   "Headers, borders, highlights",           ""],
            ["Success Green",        COLORS["success"],       "Under budget / positive trend",          ""],
            ["Warning Yellow",       COLORS["warning"],       "Within 10% of budget limit",             ""],
            ["Danger Red",           COLORS["danger"],        "Over budget / overdue",                  ""],
            ["Info Blue",            COLORS["info_blue"],     "Recurring transactions",                 ""],
        ]
        self.write_rows(18, 1, legend_data)
        self.add(data_row_format_request(sid, 17, 25, 0, 4))

        # ── Formula Reference ─────────────────────────────────────────────
        self.section_divider(25, "📐  Formula Reference", 0, 4)
        formula_data = [
            ["Debt Payoff Date",         "=IFERROR(TEXT(EDATE(TODAY(),NPER(rate/12,-payment,balance)),\"MMM YYYY\"),\"N/A\")", "Uses NPER function", ""],
            ["Goal Monthly Contribution","=(target-saved)/MAX(1,DATEDIF(TODAY(),target_date,\"M\"))",                           "Months remaining calc", ""],
            ["Progress Bar",             "=REPT(\"█\",ROUND(pct*20))&REPT(\"░\",20-ROUND(pct*20))",                           "Text-based progress", ""],
            ["Budget Variance",          "=actual-budgeted (negative = under, positive = over)",                                "Used for color coding", ""],
        ]
        self.write_rows(27, 1, formula_data)
        self.add(data_row_format_request(sid, 26, 31, 0, 4))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (0, 1, COL_WIDTH_WIDE),
            (1, 2, COL_WIDTH_WIDE),
            (2, 3, COL_WIDTH_WIDE),
            (3, 4, COL_WIDTH_DEFAULT),
        ])

        # ── Hidden dropdown source lists (Col P+ = index 15+) ────────────
        self._write_validation_lists()

        # ── Row heights ───────────────────────────────────────────────────
        self.add(row_height_request(sid, 5, 40, ROW_HEIGHT_DATA))

        self.flush()

    # ------------------------------------------------------------------
    # Write all validation source lists to hidden columns (P+)
    # ------------------------------------------------------------------

    def _write_validation_lists(self) -> None:
        """
        Write dropdown source data to columns P–Z+ (index 15+).
        These columns are used by ONE_OF_RANGE data validation on other sheets.
        Each list is written with a header in row 1 and data below.
        """
        col = SETTINGS_VALIDATION_COL  # 0-based index, starts at col P (15)
        ws  = self.worksheet

        # Helper — write a header + list to a column, return next free col
        def write_list(header: str, items: list, c: int) -> int:
            col_letter = self._0based_col_letter(c)
            ws.update_cell(1, c + 1, header)
            for i, item in enumerate(items):
                ws.update_cell(i + 2, c + 1, item)
            return c + 1

        col = write_list("income_categories",  INCOME_CATEGORIES,  col)
        col = write_list("expense_categories", EXPENSE_CATEGORIES, col)
        col = write_list("payment_methods",    PAYMENT_METHODS,    col)
        col = write_list("frequencies",        FREQUENCIES,        col)
        col = write_list("payoff_methods",     PAYOFF_METHODS,     col)
        col = write_list("months",             MONTHS,             col)

        # Subcategory lists (one column per expense category)
        for cat, subcats in EXPENSE_SUBCATEGORIES.items():
            col = write_list(f"sub_{cat[:8]}", subcats, col)

    @staticmethod
    def _0based_col_letter(idx: int) -> str:
        """Convert 0-based column index to A1-style letter(s)."""
        result = ""
        idx += 1
        while idx > 0:
            idx, r = divmod(idx - 1, 26)
            result = chr(65 + r) + result
        return result
