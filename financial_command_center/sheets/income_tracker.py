"""
📊 Income Tracker — Tab 3

Detailed log of all income received with monthly pivot summary at the
top and taxable vs non-taxable split. Sample data pre-populated.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title
  2     : ── Monthly Summary header ──
  3     : Summary column headers (months)
  4     : Total Income row
  5     : Taxable Income row
  6     : Non-Taxable Income row
  7     : YTD Total row
  8     : (spacer)
  9     : ── Transaction Log header ──
  10    : Column headers
  11+   : Data rows
"""

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS, MONTHS, INCOME_CATEGORIES,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_DATE, COL_WIDTH_WIDE, COL_WIDTH_DEFAULT, COL_WIDTH_AMOUNT,
)
from financial_command_center.utils.formatting import (
    merge_cells_request, section_header_request, header_format_request,
    row_height_request, totals_row_format_request, data_row_format_request,
    currency_format_request, date_format_request, banding_request,
    dropdown_from_list_request, color, hex_to_rgb, repeat_cell_request,
    conditional_format_custom_formula,
)
from financial_command_center.utils.sample_data import get_income_rows


# Column indices (0-based) in the transaction log
COL_DATE       = 0
COL_SOURCE     = 1
COL_CATEGORY   = 2
COL_AMOUNT     = 3
COL_TAX_WH     = 4
COL_NET        = 5
COL_NOTES      = 6
DATA_FIRST_ROW_0 = 11   # 0-based row where data starts
DATA_FIRST_ROW_1 = 12   # 1-based


class IncomeTrackerBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = 7

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "📊  Income Tracker")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Monthly Summary pivot ─────────────────────────────────────────
        self.section_divider(2, "MONTHLY SUMMARY", 0, self.NUM_COLS)

        # Headers row — months Jan-Dec in cols B-M (indices 1-12)
        summary_header = [""] + MONTHS
        ws.update(
            [summary_header[:self.NUM_COLS + 1]],
            range_name="A4",
            value_input_option="USER_ENTERED",
        )
        self.add(header_format_request(sid, 3, 0, self.NUM_COLS + 1))
        self.add(row_height_request(sid, 3, 4, ROW_HEIGHT_DATA))

        # Summary rows — use SUMPRODUCT formulas for each month
        # Data starts at row DATA_FIRST_ROW_1 (1-based) through row 500
        summary_rows = [
            ("Total Income",       None,                   None),
            ("Taxable Income",     "W2 Employment",         True),  # True = positive match
            ("Non-Taxable Income", "Non-Taxable",           False), # False = contains match
            ("YTD Total",          None,                    None),  # running SUM
        ]

        for i, (label, cat_filter, exact) in enumerate(summary_rows):
            row_1b = 5 + i
            row_0b = row_1b - 1
            row_data = [label]
            for m, month_name in enumerate(MONTHS[:self.NUM_COLS - 1]):
                m1 = m + 1  # month number
                if label == "Total Income":
                    formula = (
                        f'=IFERROR(SUMPRODUCT('
                        f'(MONTH(\'📊 Income Tracker\'!$A${DATA_FIRST_ROW_1}:$A$500)={m1})*'
                        f'(YEAR(\'📊 Income Tracker\'!$A${DATA_FIRST_ROW_1}:$A$500)=YEAR(TODAY()))*'
                        f'\'📊 Income Tracker\'!$D${DATA_FIRST_ROW_1}:$D$500),0)'
                    )
                elif label == "Taxable Income":
                    formula = (
                        f'=IFERROR(SUMPRODUCT('
                        f'(MONTH(\'📊 Income Tracker\'!$A${DATA_FIRST_ROW_1}:$A$500)={m1})*'
                        f'(YEAR(\'📊 Income Tracker\'!$A${DATA_FIRST_ROW_1}:$A$500)=YEAR(TODAY()))*'
                        f'(ISERROR(SEARCH("Non-Taxable",\'📊 Income Tracker\'!$C${DATA_FIRST_ROW_1}:$C$500)))*'
                        f'\'📊 Income Tracker\'!$D${DATA_FIRST_ROW_1}:$D$500),0)'
                    )
                elif label == "Non-Taxable Income":
                    formula = (
                        f'=IFERROR(SUMPRODUCT('
                        f'(MONTH(\'📊 Income Tracker\'!$A${DATA_FIRST_ROW_1}:$A$500)={m1})*'
                        f'(YEAR(\'📊 Income Tracker\'!$A${DATA_FIRST_ROW_1}:$A$500)=YEAR(TODAY()))*'
                        f'(NOT(ISERROR(SEARCH("Non-Taxable",\'📊 Income Tracker\'!$C${DATA_FIRST_ROW_1}:$C$500))))*'
                        f'\'📊 Income Tracker\'!$D${DATA_FIRST_ROW_1}:$D$500),0)'
                    )
                else:  # YTD Total — cumulative sum of Total Income
                    formula = f"=SUM(B5:B5)" if m == 0 else f"=SUM(B5:{chr(65+m)}5)"
                row_data.append(formula)

            ws.update(
                [row_data],
                range_name=f"A{row_1b}",
                value_input_option="USER_ENTERED",
            )
            is_total = (label in ("Total Income", "YTD Total"))
            if is_total:
                self.add(totals_row_format_request(sid, row_0b, 0, self.NUM_COLS + 1))
            else:
                self.add(data_row_format_request(sid, row_0b, row_0b + 1, 0, self.NUM_COLS + 1, i % 2 == 0))
            self.add(row_height_request(sid, row_0b, row_0b + 1, ROW_HEIGHT_DATA))

        # Currency format on summary section
        self.add(currency_format_request(sid, 3, 9, 1, self.NUM_COLS + 1))

        # ── Transaction Log ───────────────────────────────────────────────
        self.section_divider(9, "TRANSACTION LOG", 0, self.NUM_COLS)
        col_headers = ["Date", "Source / Payer", "Category", "Amount ($)",
                       "Tax Withheld (Est.)", "Net Amount ($)", "Notes"]
        self.col_header_row(10, col_headers, 0)

        # ── Sample data ───────────────────────────────────────────────────
        income_rows = get_income_rows()
        if income_rows:
            self.write_rows(DATA_FIRST_ROW_1, 1, income_rows)

        # Apply alternating row formatting to data area
        self.add(banding_request(sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 100,
                                 0, self.NUM_COLS))

        # Category dropdown
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 200,
            COL_CATEGORY, COL_CATEGORY + 1,
            INCOME_CATEGORIES,
        ))

        # Number formats
        self.add(date_format_request(sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 200,
                                     COL_DATE, COL_DATE + 1))
        self.add(currency_format_request(sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 200,
                                         COL_AMOUNT, COL_AMOUNT + 1))
        self.add(currency_format_request(sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 200,
                                         COL_TAX_WH, COL_TAX_WH + 1))
        self.add(currency_format_request(sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 200,
                                         COL_NET, COL_NET + 1))

        # Highlight non-taxable income rows in a subtle green tint
        self.add(conditional_format_custom_formula(
            sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 200,
            0, self.NUM_COLS,
            f'=NOT(ISERROR(SEARCH("Non-Taxable",$C{DATA_FIRST_ROW_1})))',
            "success",
            text_color="text_dark",
            index=0,
        ))

        # Row heights
        self.add(row_height_request(sid, DATA_FIRST_ROW_0, DATA_FIRST_ROW_0 + 100,
                                    ROW_HEIGHT_DATA))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (COL_DATE,     COL_DATE + 1,     COL_WIDTH_DATE),
            (COL_SOURCE,   COL_SOURCE + 1,   COL_WIDTH_WIDE),
            (COL_CATEGORY, COL_CATEGORY + 1, 160),
            (COL_AMOUNT,   COL_AMOUNT + 1,   COL_WIDTH_AMOUNT),
            (COL_TAX_WH,   COL_TAX_WH + 1,   130),
            (COL_NET,      COL_NET + 1,       COL_WIDTH_AMOUNT),
            (COL_NOTES,    COL_NOTES + 1,     COL_WIDTH_WIDE),
        ])

        self.flush()
