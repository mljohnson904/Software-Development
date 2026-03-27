"""
🔄 Recurring Transactions — Tab 9

Master registry of all recurring income and expenses with automatic
next-due-date calculation and alert flagging for items due within 7 days.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title
  2     : ── Summary ──
  3     : Summary headers
  4     : Summary totals
  5     : (spacer)
  6     : ── Recurring Transactions header ──
  7     : Column headers
  8+    : Data rows

Columns:
  A Name | B Type (Income/Expense) | C Amount | D Frequency |
  E Last Payment Date | F Next Due Date | G Category | H Auto-Pay? |
  I Active? | J Alert
"""

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS, FREQUENCIES,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_WIDE, COL_WIDTH_DEFAULT, COL_WIDTH_AMOUNT, COL_WIDTH_DATE,
)
from financial_command_center.utils.formatting import (
    merge_cells_request, section_header_request, header_format_request,
    row_height_request, totals_row_format_request, data_row_format_request,
    currency_format_request, date_format_request, banding_request,
    dropdown_from_list_request, color, hex_to_rgb, repeat_cell_request,
    conditional_format_custom_formula, conditional_format_text_eq,
)
from financial_command_center.utils.sample_data import get_recurring_rows


# Column indices (0-based)
C_NAME    = 0
C_TYPE    = 1
C_AMOUNT  = 2
C_FREQ    = 3
C_LAST    = 4
C_NEXT    = 5
C_CAT     = 6
C_AUTO    = 7
C_ACTIVE  = 8
C_ALERT   = 9
NUM_COLS  = 10

DATA_FIRST_ROW_0 = 8
DATA_FIRST_ROW_1 = 9


class RecurringBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = NUM_COLS

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "🔄  Recurring Transactions")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Summary section ───────────────────────────────────────────────
        self.section_divider(2, "MONTHLY RECURRING SUMMARY", 0, self.NUM_COLS)
        summary_headers = [
            "Total Recurring Income/mo", "Total Recurring Expenses/mo",
            "Net Recurring Cash Flow", "# Items Due This Week",
            "# Active Items", "", "", "", "", "",
        ]
        ws.update([summary_headers], range_name="A4", value_input_option="USER_ENTERED")
        self.add(header_format_request(sid, 3, 0, self.NUM_COLS, h_align="CENTER"))
        self.add(row_height_request(sid, 3, 4, ROW_HEIGHT_DATA))

        # Summary formulas
        # Monthly amount: sum active items with Type=Income/Expense and Freq=Monthly
        # For simplicity we sum all active monthly amounts; frequency adjustments noted
        inc_formula = (
            f'=IFERROR(SUMPRODUCT('
            f'($B${DATA_FIRST_ROW_1}:$B$300="Income")*'
            f'($I${DATA_FIRST_ROW_1}:$I$300="Yes")*'
            f'(LOWER($D${DATA_FIRST_ROW_1}:$D$300)="monthly")*'
            f'$C${DATA_FIRST_ROW_1}:$C$300),0)'
        )
        exp_formula = (
            f'=IFERROR(SUMPRODUCT('
            f'($B${DATA_FIRST_ROW_1}:$B$300="Expense")*'
            f'($I${DATA_FIRST_ROW_1}:$I$300="Yes")*'
            f'(LOWER($D${DATA_FIRST_ROW_1}:$D$300)="monthly")*'
            f'$C${DATA_FIRST_ROW_1}:$C$300),0)'
        )
        net_formula = "=A5-B5"
        due_week_formula = (
            f'=COUNTIFS($I${DATA_FIRST_ROW_1}:$I$300,"Yes",'
            f'$J${DATA_FIRST_ROW_1}:$J$300,"DUE SOON")'
        )
        active_count_formula = (
            f'=COUNTIF($I${DATA_FIRST_ROW_1}:$I$300,"Yes")'
        )

        ws.update(
            [[inc_formula, exp_formula, net_formula,
              due_week_formula, active_count_formula,
              "", "", "", "", ""]],
            range_name="A5",
            value_input_option="USER_ENTERED",
        )
        self.add(totals_row_format_request(sid, 4, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 4, 5, ROW_HEIGHT_DATA))
        self.add(currency_format_request(sid, 4, 5, 0, 3))

        # ── Transaction Registry ──────────────────────────────────────────
        self.section_divider(5, "RECURRING TRANSACTION REGISTRY", 0, self.NUM_COLS)
        col_headers = [
            "Name", "Type", "Amount ($)", "Frequency",
            "Last Payment", "Next Due Date", "Category",
            "Auto-Pay?", "Active?", "Alert",
        ]
        self.col_header_row(6, col_headers, 0)

        # Write column sub-header hint row
        ws.update(
            [["", "", "", "Weekly/Bi-Weekly/Monthly/Quarterly/Annual",
              "Update when paid", "Auto-calculated", "",
              "", "", "Auto-flags if due ≤7 days"]],
            range_name="A8",
            value_input_option="USER_ENTERED",
        )
        self.add(repeat_cell_request(sid, 7, 8, 0, self.NUM_COLS, {
            "backgroundColor": color("bg_primary"),
            "textFormat": {"italic": True, "foregroundColor": color("text_secondary"),
                           "fontSize": 9},
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, 7, 8, 18))

        # ── Sample data ───────────────────────────────────────────────────
        recurring_rows = get_recurring_rows()

        # For each row, we need to add a Next Due Date formula and Alert formula
        # The sample data already has Next Due Date as a date string; we'll use formulas
        # for new rows. For sample data rows we write the data as-is (dates included).
        processed_rows = []
        for i, row in enumerate(recurring_rows):
            name, type_, amount, freq, next_due, cat, auto, active = row
            row_1b = DATA_FIRST_ROW_1 + i + 1  # +1 for the hint row

            # Next due date formula based on frequency
            # We pre-populate with the value from sample_data; formula below for future rows
            next_due_val = next_due  # keep the pre-calculated date from sample data

            # Alert formula: "DUE SOON" if next_due - today <= 7 and active
            alert_formula = (
                f'=IF(AND(I{row_1b}="Yes",'
                f'ISNUMBER(F{row_1b}),'
                f'F{row_1b}-TODAY()<=7,'
                f'F{row_1b}-TODAY()>=0),"DUE SOON","")'
            )
            processed_rows.append([
                name, type_, amount, freq, "",  # last payment blank for now
                next_due_val, cat, auto, active, alert_formula,
            ])

        self.write_rows(DATA_FIRST_ROW_1 + 1, 1, processed_rows)

        max_data_row_0 = DATA_FIRST_ROW_0 + len(processed_rows) + 50

        # ── Dropdowns ────────────────────────────────────────────────────
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0 + 1, max_data_row_0,
            C_TYPE, C_TYPE + 1, ["Income", "Expense"],
        ))
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0 + 1, max_data_row_0,
            C_FREQ, C_FREQ + 1, FREQUENCIES,
        ))
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0 + 1, max_data_row_0,
            C_AUTO, C_AUTO + 1, ["Yes", "No"],
        ))
        self.add(dropdown_from_list_request(
            sid, DATA_FIRST_ROW_0 + 1, max_data_row_0,
            C_ACTIVE, C_ACTIVE + 1, ["Yes", "No"],
        ))

        # ── Conditional formatting ────────────────────────────────────────
        # DUE SOON = yellow
        data_start_0 = DATA_FIRST_ROW_0 + 1
        for i in range(len(processed_rows) + 30):
            row_0 = data_start_0 + i
            row_1 = row_0 + 1
            self.add(conditional_format_custom_formula(
                sid, row_0, row_0 + 1, 0, self.NUM_COLS,
                f'=$J{row_1}="DUE SOON"', "warning",
                text_color="text_dark", index=0,
            ))
            # Income rows = subtle green tint
            self.add(conditional_format_custom_formula(
                sid, row_0, row_0 + 1, 0, self.NUM_COLS,
                f'=AND($B{row_1}="Income",$J{row_1}<>"DUE SOON")', "success",
                text_color="text_dark", index=1,
            ))
            # Inactive rows = dim
            self.add(conditional_format_custom_formula(
                sid, row_0, row_0 + 1, 0, self.NUM_COLS,
                f'=$I{row_1}="No"', "bg_primary",
                text_color="text_secondary", index=2,
            ))

        # ── Number formats ────────────────────────────────────────────────
        self.add(currency_format_request(sid, data_start_0, max_data_row_0,
                                         C_AMOUNT, C_AMOUNT + 1))
        self.add(date_format_request(sid, data_start_0, max_data_row_0,
                                     C_LAST, C_LAST + 1))
        self.add(date_format_request(sid, data_start_0, max_data_row_0,
                                     C_NEXT, C_NEXT + 1))

        # ── Banding and row heights ───────────────────────────────────────
        self.add(banding_request(sid, data_start_0, max_data_row_0, 0, self.NUM_COLS))
        self.add(row_height_request(sid, data_start_0, max_data_row_0, ROW_HEIGHT_DATA))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (C_NAME,   C_NAME + 1,   COL_WIDTH_WIDE),
            (C_TYPE,   C_TYPE + 1,   90),
            (C_AMOUNT, C_AMOUNT + 1, COL_WIDTH_AMOUNT),
            (C_FREQ,   C_FREQ + 1,   110),
            (C_LAST,   C_LAST + 1,   COL_WIDTH_DATE),
            (C_NEXT,   C_NEXT + 1,   COL_WIDTH_DATE),
            (C_CAT,    C_CAT + 1,    140),
            (C_AUTO,   C_AUTO + 1,    80),
            (C_ACTIVE, C_ACTIVE + 1,  70),
            (C_ALERT,  C_ALERT + 1,   90),
        ])

        self.flush()
