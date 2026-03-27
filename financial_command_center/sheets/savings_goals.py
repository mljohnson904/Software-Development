"""
🎯 Savings Goals — Tab 7

Visual progress tracking for up to 6 savings goals with progress bars,
status labels (ON TRACK / BEHIND / COMPLETED), and monthly contribution guidance.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title
  2     : ── Overall Summary ──
  3     : Summary column headers
  4     : Summary totals row
  5     : (spacer)
  6     : ── Goals section header ──
  7     : Goal column headers
  8+    : Goal rows (6 goals, each occupying 1 row in the table)

Goal columns:
  A Goal Name | B Target Amount | C Current Saved | D Target Date |
  E Monthly Contribution Needed | F Progress Bar | G % Complete | H Status
"""

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_WIDE, COL_WIDTH_DEFAULT, COL_WIDTH_AMOUNT, COL_WIDTH_DATE,
)
from financial_command_center.utils.formatting import (
    merge_cells_request, section_header_request, header_format_request,
    row_height_request, totals_row_format_request, data_row_format_request,
    currency_format_request, percent_format_request, date_format_request,
    banding_request, color, hex_to_rgb, repeat_cell_request,
    conditional_format_custom_formula, conditional_format_text_eq,
    outer_border_request,
)
from financial_command_center.utils.sample_data import get_goal_rows


# Goal table layout
GOAL_FIRST_ROW_0 = 7
GOAL_FIRST_ROW_1 = 8

C_GOAL_NAME  = 0
C_TARGET     = 1
C_SAVED      = 2
C_DATE       = 3
C_MONTHLY    = 4
C_BAR        = 5
C_PCT        = 6
C_STATUS     = 7
NUM_GOAL_COLS = 8


class SavingsGoalsBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = NUM_GOAL_COLS

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "🎯  Savings Goals")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Overall Summary ───────────────────────────────────────────────
        self.section_divider(2, "OVERALL GOAL SUMMARY", 0, self.NUM_COLS)

        summary_headers = [
            "Total Saved (All Goals)", "Total Target (All Goals)",
            "Overall % Complete", "Goals Completed", "Goals On Track", "Goals Behind", "", "",
        ]
        ws.update([summary_headers], range_name="A4", value_input_option="USER_ENTERED")
        self.add(header_format_request(sid, 3, 0, self.NUM_COLS, h_align="CENTER"))
        self.add(row_height_request(sid, 3, 4, ROW_HEIGHT_DATA))

        # Summary formulas reference the goal rows below
        goals = get_goal_rows()
        num_goals = len(goals)
        goal_end_row_1b = GOAL_FIRST_ROW_1 + num_goals - 1

        total_saved_f   = f"=SUM(C{GOAL_FIRST_ROW_1}:C{goal_end_row_1b})"
        total_target_f  = f"=SUM(B{GOAL_FIRST_ROW_1}:B{goal_end_row_1b})"
        pct_complete_f  = f"=IFERROR(A5/B5,0)"
        completed_f     = f'=COUNTIF(H{GOAL_FIRST_ROW_1}:H{goal_end_row_1b},"COMPLETED")'
        on_track_f      = f'=COUNTIF(H{GOAL_FIRST_ROW_1}:H{goal_end_row_1b},"ON TRACK")'
        behind_f        = f'=COUNTIF(H{GOAL_FIRST_ROW_1}:H{goal_end_row_1b},"BEHIND")'

        ws.update(
            [[total_saved_f, total_target_f, pct_complete_f,
              completed_f, on_track_f, behind_f, "", ""]],
            range_name="A5",
            value_input_option="USER_ENTERED",
        )
        self.add(totals_row_format_request(sid, 4, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 4, 5, ROW_HEIGHT_DATA))
        self.add(currency_format_request(sid, 4, 5, 0, 2))
        self.add(percent_format_request(sid, 4, 5, 2, 3))

        # ── Goals table ───────────────────────────────────────────────────
        self.section_divider(5, "INDIVIDUAL GOALS", 0, self.NUM_COLS)
        goal_headers = [
            "Goal Name", "Target Amount ($)", "Currently Saved ($)", "Target Date",
            "Monthly Needed ($)", "Progress", "% Complete", "Status",
        ]
        self.col_header_row(6, goal_headers, 0)

        for i, goal in enumerate(goals):
            row_1b = GOAL_FIRST_ROW_1 + i
            row_0b = row_1b - 1

            name, target, saved, target_date, monthly_contrib, _ = goal

            # Monthly contribution needed formula
            monthly_formula = (
                f"=IFERROR(MAX(0,(B{row_1b}-C{row_1b})"
                f"/MAX(1,DATEDIF(TODAY(),D{row_1b},\"M\"))),0)"
            )

            # Progress bar formula (20 blocks)
            bar_formula = (
                f'=IFERROR('
                f'REPT("█",ROUND(C{row_1b}/B{row_1b}*20,0))'
                f'&REPT("░",20-ROUND(C{row_1b}/B{row_1b}*20,0)),'
                f'REPT("░",20))'
            )

            # Percent complete
            pct_formula = f"=IFERROR(C{row_1b}/B{row_1b},0)"

            # Status label
            status_formula = (
                f'=IF(C{row_1b}>=B{row_1b},"COMPLETED",'
                f'IF(E{row_1b}<=0,"ON TRACK",'
                f'IF(C{row_1b}/B{row_1b}>=0.5,"ON TRACK",'
                f'"BEHIND")))'
            )

            row_data = [
                name, target, saved, target_date,
                monthly_formula, bar_formula, pct_formula, status_formula,
            ]
            ws.update(
                [row_data],
                range_name=f"A{row_1b}",
                value_input_option="USER_ENTERED",
            )

            alt = (i % 2 == 0)
            self.add(data_row_format_request(sid, row_0b, row_0b + 1, 0, self.NUM_COLS, alt))
            self.add(row_height_request(sid, row_0b, row_0b + 1, ROW_HEIGHT_DATA + 6))

            # Status conditional formatting
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, C_STATUS, C_STATUS + 1,
                f'=$H{row_1b}="COMPLETED"', "success",
                text_color="text_dark", bold=True, index=0,
            ))
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, C_STATUS, C_STATUS + 1,
                f'=$H{row_1b}="ON TRACK"', "info_blue",
                text_color="text_primary", bold=True, index=1,
            ))
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, C_STATUS, C_STATUS + 1,
                f'=$H{row_1b}="BEHIND"', "danger",
                text_color="text_primary", bold=True, index=2,
            ))

            # Highlight completed goals across entire row
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, 0, self.NUM_COLS,
                f'=$H{row_1b}="COMPLETED"',
                "success",
                text_color="text_dark",
                index=3,
            ))

        # Number formats
        goal_end_0 = GOAL_FIRST_ROW_0 + num_goals
        self.add(currency_format_request(sid, GOAL_FIRST_ROW_0, goal_end_0,
                                         C_TARGET, C_TARGET + 1))
        self.add(currency_format_request(sid, GOAL_FIRST_ROW_0, goal_end_0,
                                         C_SAVED, C_SAVED + 1))
        self.add(date_format_request(sid, GOAL_FIRST_ROW_0, goal_end_0,
                                     C_DATE, C_DATE + 1))
        self.add(currency_format_request(sid, GOAL_FIRST_ROW_0, goal_end_0,
                                         C_MONTHLY, C_MONTHLY + 1))
        self.add(percent_format_request(sid, GOAL_FIRST_ROW_0, goal_end_0,
                                        C_PCT, C_PCT + 1))

        # Banding
        self.add(banding_request(sid, GOAL_FIRST_ROW_0, goal_end_0 + 10, 0, self.NUM_COLS))

        # ── Tip row ───────────────────────────────────────────────────────
        tip_row_0  = goal_end_0 + 2
        tip_row_1b = tip_row_0 + 1
        ws.update_cell(tip_row_1b, 1,
            "💡 TIP: To stay on track with your Emergency Fund, "
            "automate transfers on payday. VA Disability and GI Bill BAH "
            "are non-taxable — they can go directly to savings goals.")
        self.add(merge_cells_request(sid, tip_row_0, tip_row_0 + 1, 0, self.NUM_COLS))
        self.add(repeat_cell_request(sid, tip_row_0, tip_row_0 + 1, 0, self.NUM_COLS, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"italic": True, "foregroundColor": color("text_secondary"),
                           "fontSize": 10},
            "wrapStrategy": "WRAP",
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, tip_row_0, tip_row_0 + 1, 40))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (C_GOAL_NAME, C_GOAL_NAME + 1, 220),
            (C_TARGET,    C_TARGET + 1,    130),
            (C_SAVED,     C_SAVED + 1,     130),
            (C_DATE,      C_DATE + 1,      COL_WIDTH_DATE),
            (C_MONTHLY,   C_MONTHLY + 1,   140),
            (C_BAR,       C_BAR + 1,       180),
            (C_PCT,       C_PCT + 1,        90),
            (C_STATUS,    C_STATUS + 1,    110),
        ])

        self.flush()
