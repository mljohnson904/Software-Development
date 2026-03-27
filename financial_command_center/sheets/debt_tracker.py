"""
💳 Debt Tracker — Tab 5

Full debt payoff management with avalanche/snowball method selector,
NPER-based payoff date estimates, progress bars, and payment history.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title
  2     : Payoff method selector
  3     : ── Debt Summary header ──
  4     : Column headers
  5–8   : Debt rows (4 debts)
  9     : Totals row
  10    : (spacer)
  11    : ── Priority Guidance ──
  12    : (note row)
  13    : (spacer)
  14    : ── Payment History header ──
  15    : Payment log column headers
  16+   : Payment log rows

Debt Summary columns:
  A Debt Name | B Lender | C Original Balance | D Current Balance |
  E Interest Rate | F Min Payment | G Extra Payment | H Payoff Date (Est.) |
  I Progress Bar | J % Paid
"""

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS, PAYOFF_METHODS,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_WIDE, COL_WIDTH_DEFAULT, COL_WIDTH_AMOUNT, COL_WIDTH_DATE,
)
from financial_command_center.utils.formatting import (
    merge_cells_request, section_header_request, header_format_request,
    row_height_request, totals_row_format_request, data_row_format_request,
    currency_format_request, percent_format_request, date_format_request,
    banding_request, dropdown_from_list_request, color, hex_to_rgb,
    repeat_cell_request, conditional_format_custom_formula,
    outer_border_request, line_chart_request,
)
from financial_command_center.utils.sample_data import get_debt_rows


# Column indices (0-based) for Debt Summary table
C_NAME    = 0
C_LENDER  = 1
C_ORIG    = 2
C_CURR    = 3
C_RATE    = 4
C_MIN     = 5
C_EXTRA   = 6
C_PAYOFF  = 7
C_BAR     = 8
C_PCT     = 9
NUM_DEBT_COLS = 10

DEBT_FIRST_ROW_1 = 6   # 1-based first debt data row
DEBT_FIRST_ROW_0 = 5   # 0-based

# Payment log column indices (0-based)
PL_DATE    = 0
PL_DEBT    = 1
PL_PAYMENT = 2
PL_PRINC   = 3
PL_INT     = 4
PL_NEWBAL  = 5
PL_NOTES   = 6
PL_COLS    = 7

PAYLOG_FIRST_ROW_1 = 17
PAYLOG_FIRST_ROW_0 = 16


class DebtTrackerBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = NUM_DEBT_COLS

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "💳  Debt Tracker")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Payoff method selector (row 3, index 2) ───────────────────────
        ws.update_cell(3, 1, "PAYOFF METHOD:")
        ws.update_cell(3, 2, PAYOFF_METHODS[0])
        self.add(merge_cells_request(sid, 2, 3, 0, 1))
        self.add(repeat_cell_request(sid, 2, 3, 0, 1, {
            "textFormat": {"bold": True, "foregroundColor": color("accent_gold")},
            "backgroundColor": color("bg_secondary"),
            "verticalAlignment": "MIDDLE",
        }))
        self.add(repeat_cell_request(sid, 2, 3, 1, 4, {
            "backgroundColor": color("accent_gold"),
            "textFormat": {"bold": True, "foregroundColor": color("text_dark"),
                           "fontSize": 11},
            "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE",
        }))
        self.add(merge_cells_request(sid, 2, 3, 1, 4))
        self.add(dropdown_from_list_request(sid, 2, 3, 1, 2, PAYOFF_METHODS))
        self.add(row_height_request(sid, 2, 3, ROW_HEIGHT_HEADER))

        # ── Debt Summary table ────────────────────────────────────────────
        self.section_divider(3, "DEBT OVERVIEW", 0, self.NUM_COLS)
        col_headers = [
            "Debt Name", "Lender", "Original Balance ($)", "Current Balance ($)",
            "Interest Rate", "Min Payment ($)", "Extra Payment ($)",
            "Est. Payoff Date", "Progress", "% Paid",
        ]
        self.col_header_row(4, col_headers, 0)

        debts = get_debt_rows()
        for i, debt in enumerate(debts):
            row_1b = DEBT_FIRST_ROW_1 + i
            row_0b = row_1b - 1

            name, lender, orig, curr, rate, min_pay, extra, _ = debt

            total_payment = f"=F{row_1b}+G{row_1b}"

            # NPER-based payoff date:
            # =IFERROR(TEXT(EDATE(TODAY(), NPER(E/12, -(F+G), D)), "MMM YYYY"), "N/A")
            payoff_formula = (
                f'=IFERROR(TEXT(EDATE(TODAY(),'
                f'ROUND(NPER(E{row_1b}/12,-(F{row_1b}+G{row_1b}),D{row_1b}),0)),'
                f'"MMM YYYY"),"N/A")'
            )

            # Progress bar — REPT formula
            pct_formula  = f"=IFERROR(1-(D{row_1b}/C{row_1b}),0)"
            bar_formula  = (
                f'=IFERROR(REPT("█",ROUND((1-D{row_1b}/C{row_1b})*20,0))'
                f'&REPT("░",20-ROUND((1-D{row_1b}/C{row_1b})*20,0)),REPT("░",20))'
            )

            row_data = [
                name, lender, orig, curr, rate,
                min_pay, extra,
                payoff_formula, bar_formula, pct_formula,
            ]
            ws.update(
                [row_data],
                range_name=f"A{row_1b}",
                value_input_option="USER_ENTERED",
            )
            alt = (i % 2 == 0)
            self.add(data_row_format_request(sid, row_0b, row_0b + 1, 0, self.NUM_COLS, alt))
            self.add(row_height_request(sid, row_0b, row_0b + 1, ROW_HEIGHT_DATA + 4))

        # Priority debt highlighting (Avalanche = highest rate = gold highlight)
        # When payoff method contains "Avalanche", highlight max-rate row
        for i in range(len(debts)):
            row_1b = DEBT_FIRST_ROW_1 + i
            row_0b = row_1b - 1
            # Highlight priority debt row gold when it has max interest rate
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, 0, self.NUM_COLS,
                f'=AND(NOT(ISERROR(SEARCH("Avalanche",$B$3))),'
                f'E{row_1b}=MAX($E${DEBT_FIRST_ROW_1}:$E${DEBT_FIRST_ROW_1 + len(debts) - 1}))',
                "accent_gold",
                text_color="text_dark",
                bold=True,
                index=0,
            ))
            # Snowball = lowest balance = gold highlight
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, 0, self.NUM_COLS,
                f'=AND(NOT(ISERROR(SEARCH("Snowball",$B$3))),'
                f'D{row_1b}=MIN($D${DEBT_FIRST_ROW_1}:$D${DEBT_FIRST_ROW_1 + len(debts) - 1}))',
                "accent_gold",
                text_color="text_dark",
                bold=True,
                index=1,
            ))

        # Totals row
        debts_last_row_1b = DEBT_FIRST_ROW_1 + len(debts) - 1
        total_row_1b      = debts_last_row_1b + 2
        total_row_0b      = total_row_1b - 1

        # Total interest remaining: roughly NPER*payment - balance for each debt
        ws.update(
            [[
                "TOTALS",
                "",
                f"=SUM(C{DEBT_FIRST_ROW_1}:C{debts_last_row_1b})",
                f"=SUM(D{DEBT_FIRST_ROW_1}:D{debts_last_row_1b})",
                f"=SUMPRODUCT(D{DEBT_FIRST_ROW_1}:D{debts_last_row_1b},"
                f"E{DEBT_FIRST_ROW_1}:E{debts_last_row_1b})/"
                f"SUM(D{DEBT_FIRST_ROW_1}:D{debts_last_row_1b})",   # weighted avg rate
                f"=SUM(F{DEBT_FIRST_ROW_1}:F{debts_last_row_1b})",
                f"=SUM(G{DEBT_FIRST_ROW_1}:G{debts_last_row_1b})",
                "", "", f"=IFERROR(1-J{total_row_1b},0)",
            ]],
            range_name=f"A{total_row_1b}",
            value_input_option="USER_ENTERED",
        )
        self.add(totals_row_format_request(sid, total_row_0b, 0, self.NUM_COLS))
        self.add(row_height_request(sid, total_row_0b, total_row_0b + 1, ROW_HEIGHT_DATA))

        # Number formats for debt table
        self.add(currency_format_request(sid, DEBT_FIRST_ROW_0, total_row_0b + 1,
                                         C_ORIG, C_ORIG + 1))
        self.add(currency_format_request(sid, DEBT_FIRST_ROW_0, total_row_0b + 1,
                                         C_CURR, C_CURR + 1))
        self.add(percent_format_request(sid, DEBT_FIRST_ROW_0, total_row_0b + 1,
                                        C_RATE, C_RATE + 1))
        self.add(currency_format_request(sid, DEBT_FIRST_ROW_0, total_row_0b + 1,
                                         C_MIN, C_MIN + 1))
        self.add(currency_format_request(sid, DEBT_FIRST_ROW_0, total_row_0b + 1,
                                         C_EXTRA, C_EXTRA + 1))
        self.add(percent_format_request(sid, DEBT_FIRST_ROW_0, total_row_0b + 1,
                                        C_PCT, C_PCT + 1))

        # ── Priority Guidance note ─────────────────────────────────────────
        note_row_0 = total_row_0b + 2
        note_row_1b = note_row_0 + 1
        ws.update_cell(note_row_1b, 1,
            '=IF(NOT(ISERROR(SEARCH("Avalanche",$B$3))),'
            '"🎯 AVALANCHE: Pay minimums on all debts, put extra toward highest-rate debt (highlighted gold).",'
            '"🎯 SNOWBALL: Pay minimums on all debts, put extra toward lowest-balance debt (highlighted gold).")'
        )
        self.add(merge_cells_request(sid, note_row_0, note_row_0 + 1, 0, self.NUM_COLS))
        self.add(repeat_cell_request(sid, note_row_0, note_row_0 + 1, 0, self.NUM_COLS, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"italic": True, "foregroundColor": color("text_secondary"),
                           "fontSize": 10},
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, note_row_0, note_row_0 + 1, ROW_HEIGHT_DATA))

        # ── Payment History Log ───────────────────────────────────────────
        paylog_section_row_0 = note_row_0 + 2
        self.section_divider(paylog_section_row_0, "PAYMENT HISTORY", 0, PL_COLS)
        paylog_header_row_0 = paylog_section_row_0 + 1
        paylog_headers = [
            "Date", "Debt Name", "Payment ($)", "Principal ($)",
            "Interest ($)", "New Balance ($)", "Notes",
        ]
        self.col_header_row(paylog_header_row_0, paylog_headers, 0)

        # Sample payment history rows
        sample_payments = [
            [f"2026-01-01", "2021 Toyota Tacoma Auto Loan",    385.00, 285.00, 100.00, 18420.00, "Jan payment"],
            [f"2026-01-01", "Chase Freedom Unlimited (CC1)",   115.00,  87.00,  28.00,  3180.00, "Jan min+extra"],
            [f"2026-01-01", "Citi Double Cash (CC2)",           45.00,  11.00,  34.00,  1790.00, "Jan min"],
            [f"2026-01-01", "Federal Student Loan",            130.00,  84.00,  46.00, 12050.00, "Jan payment"],
            [f"2026-02-01", "2021 Toyota Tacoma Auto Loan",    385.00, 286.00,  99.00, 18134.00, "Feb payment"],
            [f"2026-02-01", "Chase Freedom Unlimited (CC1)",   115.00,  88.00,  27.00,  3092.00, "Feb min+extra"],
        ]
        self.write_rows(PAYLOG_FIRST_ROW_1, 1, sample_payments)
        self.add(banding_request(sid, PAYLOG_FIRST_ROW_0,
                                 PAYLOG_FIRST_ROW_0 + 100, 0, PL_COLS))
        self.add(date_format_request(sid, PAYLOG_FIRST_ROW_0, PAYLOG_FIRST_ROW_0 + 100,
                                     PL_DATE, PL_DATE + 1))
        for col in [PL_PAYMENT, PL_PRINC, PL_INT, PL_NEWBAL]:
            self.add(currency_format_request(sid, PAYLOG_FIRST_ROW_0,
                                             PAYLOG_FIRST_ROW_0 + 100, col, col + 1))
        self.add(row_height_request(sid, PAYLOG_FIRST_ROW_0,
                                    PAYLOG_FIRST_ROW_0 + 50, ROW_HEIGHT_DATA))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (C_NAME,   C_NAME + 1,   220),
            (C_LENDER, C_LENDER + 1, 150),
            (C_ORIG,   C_ORIG + 1,   130),
            (C_CURR,   C_CURR + 1,   130),
            (C_RATE,   C_RATE + 1,    90),
            (C_MIN,    C_MIN + 1,    110),
            (C_EXTRA,  C_EXTRA + 1,  110),
            (C_PAYOFF, C_PAYOFF + 1, 130),
            (C_BAR,    C_BAR + 1,    160),
            (C_PCT,    C_PCT + 1,     80),
        ])

        self.flush()
