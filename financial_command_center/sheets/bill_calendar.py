"""
📅 Bill Calendar — Tab 6

Visual monthly calendar grid with bills overlaid on due dates.
Color coding: green=paid, red=unpaid/overdue, yellow=due within 3 days.

Layout (0-based rows):
  0     : Navigation bar
  1     : Sheet title + month/year navigator
  2     : Day-of-week headers (Sun–Sat)
  3–8   : Calendar grid (6 rows × 7 cols)
  9     : (spacer)
  10    : ── Bill Registry header ──
  11    : Registry column headers
  12+   : Bill rows
"""

import datetime
import calendar as cal_module

from financial_command_center.sheets.base import BaseSheetBuilder
from financial_command_center.config import (
    COLORS,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA,
    COL_WIDTH_DEFAULT, COL_WIDTH_WIDE,
)
from financial_command_center.utils.formatting import (
    merge_cells_request, section_header_request, header_format_request,
    row_height_request, data_row_format_request, currency_format_request,
    date_format_request, banding_request, dropdown_from_list_request,
    color, hex_to_rgb, repeat_cell_request,
    conditional_format_custom_formula, conditional_format_text_eq,
    outer_border_request,
)
from financial_command_center.utils.sample_data import get_bill_registry_rows


# Calendar grid occupies columns B–H (indices 1–7)
CAL_START_COL  = 1   # 0-based
CAL_END_COL    = 8   # exclusive
CAL_START_ROW  = 2   # 0-based (row 3 in 1-based)
CAL_END_ROW    = 8   # exclusive (6 weeks)

# Bill Registry table starts below calendar
REGISTRY_HEADER_ROW_0 = 10
REGISTRY_DATA_ROW_0   = 12
REGISTRY_DATA_ROW_1   = 13

REG_NAME  = 0
REG_AMT   = 1
REG_DAY   = 2
REG_AUTO  = 3
REG_ACCT  = 4
REG_CAT   = 5
REG_PAID  = 6
REG_ACTIVE = 7
NUM_REG_COLS = 8


class BillCalendarBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = 9

    def build(self, tab_gids: list) -> None:
        ws   = self.worksheet
        sid  = self.sheet_id
        now  = datetime.date.today()
        year = now.year
        month = now.month

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, f"📅  Bill Calendar — {now.strftime('%B %Y')}")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Day-of-week headers ───────────────────────────────────────────
        dow_headers = ["", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", ""]
        ws.update([dow_headers], range_name="A3", value_input_option="USER_ENTERED")
        self.add(header_format_request(sid, 2, 0, self.NUM_COLS,
                                       h_align="CENTER"))
        self.add(row_height_request(sid, 2, 3, ROW_HEIGHT_HEADER))

        # ── Calendar grid ─────────────────────────────────────────────────
        # Build calendar for current month
        first_dow = cal_module.monthrange(year, month)[0]  # 0=Monday
        # Adjust to Sunday start: Sunday=0
        start_offset = (first_dow + 1) % 7  # days before 1st
        days_in_month = cal_module.monthrange(year, month)[1]

        # Build 6-row × 7-col grid of day numbers (0 = empty cell)
        grid = []
        day = 1
        for week in range(6):
            row = []
            for dow in range(7):
                cell_num = week * 7 + dow
                if cell_num < start_offset or day > days_in_month:
                    row.append(None)
                else:
                    row.append(day)
                    day += 1
            grid.append(row)

        # Write day numbers into calendar cells and add bill lookup formulas
        # Bills are looked up from the registry below
        # Format: day number on first line, then bill name + amount if due that day
        for week_idx, week_row in enumerate(grid):
            cal_row_0  = CAL_START_ROW + week_idx
            cal_row_1b = cal_row_0 + 1

            for dow_idx, day_num in enumerate(week_row):
                col_0  = CAL_START_COL + dow_idx
                col_1b = col_0 + 1

                if day_num is None:
                    cell_val = ""
                else:
                    # Show day number + any bills due on that day from registry
                    # Registry: name=col A (reg), due_day=col C (reg), active=col H
                    registry_name_col   = "A"
                    registry_day_col    = "C"
                    registry_amt_col    = "B"
                    registry_auto_col   = "D"
                    registry_active_col = "H"
                    r_start = REGISTRY_DATA_ROW_1
                    r_end   = r_start + 20

                    # Build a formula: day number + list of bill names due that day
                    cell_val = (
                        f'={day_num}&IFERROR('
                        f'CHAR(10)&TEXTJOIN(CHAR(10),TRUE,'
                        f'IF(({registry_day_col}{r_start}:{registry_day_col}{r_end}={day_num})'
                        f'*({registry_active_col}{r_start}:{registry_active_col}{r_end}="Yes"),'
                        f'{registry_name_col}{r_start}:{registry_name_col}{r_end}'
                        f'&" $"&TEXT({registry_amt_col}{r_start}:{registry_amt_col}{r_end},"#,##0.00"),'
                        f'"")),""))'
                    )

                ws.update_cell(cal_row_1b, col_1b, cell_val if day_num else "")

                # Style each calendar cell
                bg = COLORS["bg_secondary"] if day_num else COLORS["bg_primary"]
                cell_fmt = {
                    "backgroundColor": hex_to_rgb(bg),
                    "textFormat": {
                        "fontSize": 9,
                        "foregroundColor": color("text_primary"),
                    },
                    "verticalAlignment": "TOP",
                    "horizontalAlignment": "LEFT",
                    "wrapStrategy": "WRAP",
                }
                self.add(repeat_cell_request(sid, cal_row_0, cal_row_0 + 1,
                                             col_0, col_0 + 1, cell_fmt))

                # Highlight today
                if day_num == now.day:
                    self.add(repeat_cell_request(sid, cal_row_0, cal_row_0 + 1,
                                                 col_0, col_0 + 1, {
                        "backgroundColor": hex_to_rgb(COLORS["accent_gold"]),
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": color("text_dark"),
                            "fontSize": 9,
                        },
                        "verticalAlignment": "TOP",
                        "horizontalAlignment": "LEFT",
                        "wrapStrategy": "WRAP",
                    }))

            # Row height for calendar rows
            self.add(row_height_request(sid, cal_row_0, cal_row_0 + 1, 70))

        # Column widths for calendar (Sun–Sat each gets equal width)
        for c in range(CAL_START_COL, CAL_END_COL):
            self.add(__import__(
                "financial_command_center.utils.formatting",
                fromlist=["col_width_request"]
            ).col_width_request(sid, c, c + 1, 110))
        # Left label col
        self.add(__import__(
            "financial_command_center.utils.formatting",
            fromlist=["col_width_request"]
        ).col_width_request(sid, 0, 1, 80))

        # ── Bill Registry ─────────────────────────────────────────────────
        self.section_divider(REGISTRY_HEADER_ROW_0, "BILL REGISTRY", 0, NUM_REG_COLS)
        reg_headers = [
            "Bill Name", "Amount ($)", "Due Day", "Auto-Pay?",
            "Account", "Category", "Paid This Month?", "Active?",
        ]
        self.col_header_row(REGISTRY_HEADER_ROW_0 + 1, reg_headers, 0)

        bill_rows = get_bill_registry_rows()
        # Add "Paid?" column (No by default)
        bill_rows_with_paid = [row + ["No"] for row in bill_rows]
        self.write_rows(REGISTRY_DATA_ROW_1, 1, bill_rows_with_paid)

        # Dropdowns for registry
        num_bills = len(bill_rows)
        reg_end_0 = REGISTRY_DATA_ROW_0 + num_bills + 20

        self.add(dropdown_from_list_request(
            sid, REGISTRY_DATA_ROW_0, reg_end_0, REG_AUTO, REG_AUTO + 1, ["Yes", "No"]
        ))
        self.add(dropdown_from_list_request(
            sid, REGISTRY_DATA_ROW_0, reg_end_0, REG_PAID, REG_PAID + 1, ["Yes", "No"]
        ))
        self.add(dropdown_from_list_request(
            sid, REGISTRY_DATA_ROW_0, reg_end_0, REG_ACTIVE, REG_ACTIVE + 1, ["Yes", "No"]
        ))

        # Conditional formatting on registry:
        # Green = paid, Red = overdue (today > due day and not paid), Yellow = due soon
        for i in range(num_bills + 20):
            row_1b = REGISTRY_DATA_ROW_1 + i
            row_0b = row_1b - 1
            # Paid = green
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, 0, NUM_REG_COLS,
                f'=$G{row_1b}="Yes"', "success", index=0,
            ))
            # Overdue = red (today's day > due day in current month and not paid)
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, 0, NUM_REG_COLS,
                f'=AND($H{row_1b}="Yes",$G{row_1b}<>"Yes",DAY(TODAY())>$C{row_1b})',
                "danger", index=1,
            ))
            # Due within 3 days = yellow
            self.add(conditional_format_custom_formula(
                sid, row_0b, row_0b + 1, 0, NUM_REG_COLS,
                f'=AND($H{row_1b}="Yes",$G{row_1b}<>"Yes",'
                f'DAY(TODAY())<=$C{row_1b},$C{row_1b}-DAY(TODAY())<=3)',
                "warning", index=2,
            ))

        self.add(banding_request(sid, REGISTRY_DATA_ROW_0, reg_end_0, 0, NUM_REG_COLS))
        self.add(currency_format_request(sid, REGISTRY_DATA_ROW_0, reg_end_0,
                                         REG_AMT, REG_AMT + 1))
        self.add(row_height_request(sid, REGISTRY_DATA_ROW_0, reg_end_0,
                                    ROW_HEIGHT_DATA))

        # Registry column widths
        self.set_col_widths([
            (REG_NAME, REG_NAME + 1, COL_WIDTH_WIDE),
            (REG_AMT,  REG_AMT + 1,  100),
            (REG_DAY,  REG_DAY + 1,   70),
            (REG_AUTO, REG_AUTO + 1,  80),
            (REG_ACCT, REG_ACCT + 1, 120),
            (REG_CAT,  REG_CAT + 1,  130),
            (REG_PAID, REG_PAID + 1, 120),
            (REG_ACTIVE, REG_ACTIVE + 1, 70),
        ])

        self.flush()
