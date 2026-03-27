"""
📈 Net Worth Tracker — Tab 8

Assets and liabilities tables with monthly history log and a line chart
showing net worth trend over time.

Layout (0-based rows):
  0       : Navigation bar
  1       : Sheet title
  2       : ── Net Worth Snapshot ──
  3       : Net Worth value (large, prominent)
  4       : (spacer)
  5       : ── ASSETS header ──
  6       : Asset column headers
  7–11    : Asset rows
  12      : Assets TOTAL row
  13      : (spacer)
  14      : ── LIABILITIES header ──
  15      : Liability column headers
  16–19   : Liability rows
  20      : Liabilities TOTAL row
  21      : (spacer)
  22      : ── Monthly History header ──
  23      : History column headers
  24+     : Monthly history rows (12 months of data)
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
    conditional_format_custom_formula, line_chart_request,
)
from financial_command_center.utils.sample_data import (
    get_asset_rows, get_liability_rows, get_net_worth_history,
)


# Table start rows
ASSET_FIRST_ROW_0    = 6
ASSET_FIRST_ROW_1    = 7
LIAB_FIRST_ROW_0     = 15
LIAB_FIRST_ROW_1     = 16
HISTORY_HEADER_ROW_0 = 22
HISTORY_FIRST_ROW_0  = 24
HISTORY_FIRST_ROW_1  = 25

# Asset columns (0-based)
A_NAME    = 0
A_CAT     = 1
A_VALUE   = 2
A_UPDATED = 3
NUM_ASSET_COLS = 4

# Liability columns
L_NAME  = 0
L_CAT   = 1
L_BAL   = 2
L_RATE  = 3
NUM_LIAB_COLS = 4

# History columns
H_MONTH  = 0
H_ASSETS = 1
H_LIAB   = 2
H_NW     = 3
H_CHANGE = 4
NUM_HIST_COLS = 5


class NetWorthBuilder(BaseSheetBuilder):
    TAB_COLOR = COLORS["bg_primary"]
    NUM_COLS  = 6

    def build(self, tab_gids: list) -> None:
        ws  = self.worksheet
        sid = self.sheet_id

        self.apply_base_formatting(frozen_rows=2)
        self.apply_nav_bar(tab_gids)

        # ── Sheet title ───────────────────────────────────────────────────
        ws.update_cell(2, 1, "📈  Net Worth Tracker")
        self.add(merge_cells_request(sid, 1, 2, 0, self.NUM_COLS))
        self.add(section_header_request(sid, 1, 0, self.NUM_COLS))
        self.add(row_height_request(sid, 1, 2, ROW_HEIGHT_HEADER))

        # ── Net Worth Snapshot ────────────────────────────────────────────
        self.section_divider(2, "NET WORTH SNAPSHOT", 0, self.NUM_COLS)
        ws.update_cell(4, 1, "CURRENT NET WORTH:")
        ws.update_cell(4, 2, f"=C13-C21")   # Total assets - total liabilities
        ws.update_cell(4, 3, "Change (MoM):")
        ws.update_cell(4, 4,
            f'=IFERROR(IF(D{HISTORY_FIRST_ROW_1+1}-D{HISTORY_FIRST_ROW_1}>0,'
            f'"▲ $"&TEXT(D{HISTORY_FIRST_ROW_1+1}-D{HISTORY_FIRST_ROW_1},"#,##0"),'
            f'"▼ $"&TEXT(ABS(D{HISTORY_FIRST_ROW_1+1}-D{HISTORY_FIRST_ROW_1}),"#,##0")),"N/A")'
        )

        self.add(repeat_cell_request(sid, 3, 4, 0, 1, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"bold": True, "foregroundColor": color("accent_gold"),
                           "fontSize": 11},
            "verticalAlignment": "MIDDLE",
        }))
        self.add(repeat_cell_request(sid, 3, 4, 1, 2, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"bold": True, "foregroundColor": color("text_primary"),
                           "fontSize": 18},
            "horizontalAlignment": "LEFT",
            "verticalAlignment": "MIDDLE",
        }))
        self.add(repeat_cell_request(sid, 3, 4, 2, 4, {
            "backgroundColor": color("bg_secondary"),
            "textFormat": {"foregroundColor": color("text_secondary"), "fontSize": 10},
            "verticalAlignment": "MIDDLE",
        }))
        self.add(row_height_request(sid, 3, 4, 40))
        self.add(currency_format_request(sid, 3, 4, 1, 2))

        # ── ASSETS ───────────────────────────────────────────────────────
        self.section_divider(4, "ASSETS", 0, NUM_ASSET_COLS)
        asset_headers = ["Asset / Account", "Category", "Current Value ($)", "Last Updated"]
        self.col_header_row(5, asset_headers, 0)

        assets = get_asset_rows()
        self.write_rows(ASSET_FIRST_ROW_1, 1, assets)

        num_assets = len(assets)
        asset_last_0 = ASSET_FIRST_ROW_0 + num_assets
        asset_last_1 = asset_last_0 + 1

        # Totals row
        ws.update(
            [[
                "TOTAL ASSETS", "",
                f"=SUM(C{ASSET_FIRST_ROW_1}:C{asset_last_0})", "",
            ]],
            range_name=f"A{asset_last_1 + 1}",
            value_input_option="USER_ENTERED",
        )
        assets_total_row_1b = asset_last_1 + 1
        assets_total_row_0  = assets_total_row_1b - 1
        self.add(totals_row_format_request(sid, assets_total_row_0, 0, NUM_ASSET_COLS))
        self.add(row_height_request(sid, assets_total_row_0, assets_total_row_0 + 1,
                                    ROW_HEIGHT_DATA))

        self.add(banding_request(sid, ASSET_FIRST_ROW_0, asset_last_0, 0, NUM_ASSET_COLS))
        self.add(currency_format_request(sid, ASSET_FIRST_ROW_0, assets_total_row_0 + 1,
                                         A_VALUE, A_VALUE + 1))
        self.add(date_format_request(sid, ASSET_FIRST_ROW_0, asset_last_0,
                                     A_UPDATED, A_UPDATED + 1))
        self.add(row_height_request(sid, ASSET_FIRST_ROW_0, asset_last_0, ROW_HEIGHT_DATA))

        # ── LIABILITIES ───────────────────────────────────────────────────
        liab_section_row_0 = assets_total_row_0 + 2
        self.section_divider(liab_section_row_0, "LIABILITIES", 0, NUM_LIAB_COLS)
        liab_header_row_0 = liab_section_row_0 + 1
        liab_headers = ["Liability / Debt", "Category", "Current Balance ($)", "Interest Rate"]
        self.col_header_row(liab_header_row_0, liab_headers, 0)

        liab_first_row_1 = liab_header_row_0 + 2
        liab_first_row_0 = liab_first_row_1 - 1

        liabilities = get_liability_rows()
        self.write_rows(liab_first_row_1, 1, liabilities)

        num_liabs = len(liabilities)
        liab_last_0  = liab_first_row_0 + num_liabs
        liab_last_1  = liab_last_0 + 1
        liabs_total_row_1b = liab_last_1 + 1
        liabs_total_row_0  = liabs_total_row_1b - 1

        ws.update(
            [[
                "TOTAL LIABILITIES", "",
                f"=SUM(C{liab_first_row_1}:C{liab_last_0})", "",
            ]],
            range_name=f"A{liabs_total_row_1b}",
            value_input_option="USER_ENTERED",
        )
        self.add(totals_row_format_request(sid, liabs_total_row_0, 0, NUM_LIAB_COLS))
        self.add(row_height_request(sid, liabs_total_row_0, liabs_total_row_0 + 1,
                                    ROW_HEIGHT_DATA))

        self.add(banding_request(sid, liab_first_row_0, liab_last_0, 0, NUM_LIAB_COLS))
        self.add(currency_format_request(sid, liab_first_row_0, liabs_total_row_0 + 1,
                                         L_BAL, L_BAL + 1))
        self.add(percent_format_request(sid, liab_first_row_0, liab_last_0,
                                        L_RATE, L_RATE + 1))
        self.add(row_height_request(sid, liab_first_row_0, liab_last_0, ROW_HEIGHT_DATA))

        # ── Monthly History ───────────────────────────────────────────────
        history_section_row_0 = liabs_total_row_0 + 2
        self.section_divider(history_section_row_0, "MONTHLY NET WORTH HISTORY", 0, NUM_HIST_COLS)
        hist_header_row_0 = history_section_row_0 + 1
        hist_headers = ["Month", "Total Assets ($)", "Total Liabilities ($)",
                        "Net Worth ($)", "Change ($)"]
        self.col_header_row(hist_header_row_0, hist_headers, 0)

        hist_first_row_1 = hist_header_row_0 + 2
        hist_first_row_0 = hist_first_row_1 - 1

        history = get_net_worth_history()

        # Write history data with calculated change column
        history_rows = []
        for i, (month_label, assets_val, liabs_val, nw_val) in enumerate(history):
            if i == 0:
                change = ""  # no prior month for first entry
            else:
                change = f"=D{hist_first_row_1 + i}-D{hist_first_row_1 + i - 1}"
            history_rows.append([month_label, assets_val, liabs_val, nw_val, change])

        self.write_rows(hist_first_row_1, 1, history_rows)

        num_hist = len(history)
        hist_end_0 = hist_first_row_0 + num_hist

        self.add(banding_request(sid, hist_first_row_0, hist_end_0, 0, NUM_HIST_COLS))
        self.add(currency_format_request(sid, hist_first_row_0, hist_end_0,
                                         H_ASSETS, H_ASSETS + 1))
        self.add(currency_format_request(sid, hist_first_row_0, hist_end_0,
                                         H_LIAB, H_LIAB + 1))
        self.add(currency_format_request(sid, hist_first_row_0, hist_end_0,
                                         H_NW, H_NW + 1))
        self.add(currency_format_request(sid, hist_first_row_0, hist_end_0,
                                         H_CHANGE, H_CHANGE + 1))
        self.add(row_height_request(sid, hist_first_row_0, hist_end_0, ROW_HEIGHT_DATA))

        # Conditional: positive change = green arrow, negative = red
        for i in range(1, num_hist):
            row_0 = hist_first_row_0 + i
            row_1 = row_0 + 1
            self.add(conditional_format_custom_formula(
                sid, row_0, row_0 + 1, H_CHANGE, H_CHANGE + 1,
                f"=E{row_1}>0", "success", index=0,
            ))
            self.add(conditional_format_custom_formula(
                sid, row_0, row_0 + 1, H_CHANGE, H_CHANGE + 1,
                f"=E{row_1}<0", "danger", index=1,
            ))

        # ── Net Worth Line Chart ───────────────────────────────────────────
        self.add(line_chart_request(
            sheet_id=sid,
            title="Net Worth Trend",
            data_sheet_id=sid,
            domain_start_row=hist_first_row_0,
            domain_end_row=hist_end_0,
            domain_col=H_MONTH,
            series_configs=[
                {
                    "start_row": hist_first_row_0, "end_row": hist_end_0,
                    "col": H_NW, "color_hex": COLORS["accent_gold"],
                },
                {
                    "start_row": hist_first_row_0, "end_row": hist_end_0,
                    "col": H_ASSETS, "color_hex": COLORS["success"],
                },
                {
                    "start_row": hist_first_row_0, "end_row": hist_end_0,
                    "col": H_LIAB, "color_hex": COLORS["danger"],
                },
            ],
            anchor_row=3,
            anchor_col=5,
        ))

        # ── Column widths ─────────────────────────────────────────────────
        self.set_col_widths([
            (0, 1, COL_WIDTH_WIDE),
            (1, 2, 150),
            (2, 3, 150),
            (3, 4, 130),
            (4, 5, 120),
        ])

        # Fix the asset/liab total row references — update them now that we know actual rows
        ws.update_cell(4, 3, f"=C{assets_total_row_1b}")
        ws.update_cell(4, 5, f"=C{liabs_total_row_1b}")

        # Rewrite snapshot formula with correct total rows
        ws.update_cell(4, 2,
            f"=IFERROR(C{assets_total_row_1b}-C{liabs_total_row_1b},0)"
        )

        self.flush()
