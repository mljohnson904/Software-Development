"""
BaseSheetBuilder — shared infrastructure for all 10 sheet builders.

Each concrete builder:
  1. Receives a gspread.Worksheet and the parent gspread.Spreadsheet
  2. Writes cell values via worksheet.update()
  3. Accumulates Sheets API batchUpdate request dicts in self.requests
  4. Calls self.flush() once to submit all formatting in a single API call

This pattern minimises API quota usage (one batchUpdate per sheet).
"""

import time
import gspread

from financial_command_center.config import (
    COLORS, SHEET_NAMES, NAV_LABELS,
    ROW_HEIGHT_HEADER, ROW_HEIGHT_DATA, ROW_HEIGHT_NAV,
    COL_WIDTH_DEFAULT,
)
from financial_command_center.utils.formatting import (
    hide_gridlines_request,
    tab_color_request,
    freeze_request,
    row_height_request,
    nav_bar_format_request,
    merge_cells_request,
    repeat_cell_request,
    col_width_request,
    color,
    hex_to_rgb,
)


class BaseSheetBuilder:
    """
    Base class for all sheet builders.

    Subclasses must implement:
        build(self) -> None
            Write data and add formatting requests to self.requests,
            then call self.flush() at the end.
    """

    #: Override in subclasses to set the tab background color
    TAB_COLOR = COLORS["bg_primary"]

    #: Number of data columns used on this sheet (for nav bar merge width)
    NUM_COLS = 10

    def __init__(self, spreadsheet: gspread.Spreadsheet,
                 worksheet: gspread.Worksheet,
                 sheet_index: int):
        self.spreadsheet  = spreadsheet
        self.worksheet    = worksheet
        self.sheet_id     = worksheet.id          # integer GID used in API requests
        self.sheet_index  = sheet_index           # 0-based position in the workbook
        self.requests: list = []                  # accumulated batchUpdate request dicts

    # ------------------------------------------------------------------
    # Request accumulator
    # ------------------------------------------------------------------

    def add(self, request: dict) -> None:
        """Append a single batchUpdate request dict."""
        self.requests.append(request)

    def add_many(self, requests: list) -> None:
        """Append multiple batchUpdate request dicts."""
        self.requests.extend(requests)

    # ------------------------------------------------------------------
    # Flush — submit all accumulated requests in one API call
    # ------------------------------------------------------------------

    def flush(self) -> None:
        """Send all accumulated formatting requests to the Sheets API."""
        if self.requests:
            self.spreadsheet.batch_update({"requests": self.requests})
            self.requests = []

    # ------------------------------------------------------------------
    # Common sheet setup — call at the start of every build()
    # ------------------------------------------------------------------

    def apply_base_formatting(self, frozen_rows: int = 2) -> None:
        """Hide gridlines, set tab color, freeze rows."""
        self.add(hide_gridlines_request(self.sheet_id))
        self.add(tab_color_request(self.sheet_id, self.TAB_COLOR))
        self.add(freeze_request(self.sheet_id, frozen_rows=frozen_rows))

    def apply_nav_bar(self, tab_gids: list) -> None:
        """
        Write navigation hyperlinks into row 1 (index 0), one per tab.
        tab_gids: list of integer GIDs in tab display order.
        """
        # Set nav bar row height
        self.add(row_height_request(self.sheet_id, 0, 1, ROW_HEIGHT_NAV))

        # Distribute labels across columns — merge cells per label
        num_tabs  = len(SHEET_NAMES)
        cols_each = max(1, self.NUM_COLS // num_tabs)

        nav_cells = []
        for i, (label, gid) in enumerate(zip(NAV_LABELS, tab_gids)):
            start_col = i * cols_each
            end_col   = start_col + cols_each
            # Last label extends to NUM_COLS
            if i == num_tabs - 1:
                end_col = self.NUM_COLS

            nav_cells.append({
                "row": 0, "col": start_col,
                "value": f'=HYPERLINK("#gid={gid}","{label}")',
                "start_col": start_col, "end_col": end_col,
            })
            if end_col > start_col + 1:
                self.add(merge_cells_request(
                    self.sheet_id, 0, 1, start_col, end_col
                ))

        # Write the hyperlink formulas
        cell_list = []
        for item in nav_cells:
            cell = self.worksheet.cell(1, item["col"] + 1)
            cell.value = item["value"]
            cell_list.append(cell)
        if cell_list:
            self.worksheet.update_cells(cell_list, value_input_option="USER_ENTERED")

        # Apply gold styling to the entire nav row
        self.add(nav_bar_format_request(self.sheet_id, self.NUM_COLS))

    # ------------------------------------------------------------------
    # Helpers for writing data to the sheet
    # ------------------------------------------------------------------

    def write_rows(self, start_row: int, start_col: int, rows: list,
                   value_input_option: str = "USER_ENTERED") -> None:
        """
        Write a 2-D list of values starting at (start_row, start_col).
        start_row and start_col are 1-based (gspread convention).
        """
        if not rows:
            return
        self.worksheet.update(
            rows,
            range_name=self._rc_to_a1(start_row, start_col),
            value_input_option=value_input_option,
        )

    def write_cell(self, row: int, col: int, value,
                   value_input_option: str = "USER_ENTERED") -> None:
        """Write a single cell value. row/col are 1-based."""
        self.worksheet.update_cell(row, col, value)

    @staticmethod
    def _rc_to_a1(row: int, col: int) -> str:
        """Convert 1-based (row, col) to A1 notation string (e.g. 'C5')."""
        col_str = ""
        while col > 0:
            col, remainder = divmod(col - 1, 26)
            col_str = chr(65 + remainder) + col_str
        return f"{col_str}{row}"

    # ------------------------------------------------------------------
    # Convenience wrappers used across all sheets
    # ------------------------------------------------------------------

    def set_col_widths(self, widths: list) -> None:
        """
        Set column widths from a list of (start_col_0based, end_col_0based, px) tuples.
        """
        for start, end, px in widths:
            self.add(col_width_request(self.sheet_id, start, end, px))

    def set_row_heights(self, heights: list) -> None:
        """
        Set row heights from a list of (start_row_0based, end_row_0based, px) tuples.
        """
        from financial_command_center.utils.formatting import row_height_request as rhr
        for start, end, px in heights:
            self.add(rhr(self.sheet_id, start, end, px))

    def section_divider(self, row_0: int, label: str,
                        start_col: int = 0, end_col: int = None) -> None:
        """
        Write a gold section divider row with a label.
        row_0 is 0-based; the actual write uses 1-based gspread row.
        """
        from financial_command_center.utils.formatting import section_header_request
        if end_col is None:
            end_col = self.NUM_COLS
        self.worksheet.update_cell(row_0 + 1, start_col + 1, label)
        if end_col > start_col + 1:
            self.add(merge_cells_request(self.sheet_id, row_0, row_0 + 1, start_col, end_col))
        self.add(section_header_request(self.sheet_id, row_0, start_col, end_col))
        self.add(row_height_request(self.sheet_id, row_0, row_0 + 1, ROW_HEIGHT_HEADER))

    def col_header_row(self, row_0: int, headers: list,
                       start_col: int = 0) -> None:
        """Write column headers and apply standard header formatting."""
        from financial_command_center.utils.formatting import header_format_request
        self.write_rows(row_0 + 1, start_col + 1, [headers])
        self.add(header_format_request(
            self.sheet_id, row_0, start_col, start_col + len(headers)
        ))
        self.add(row_height_request(
            self.sheet_id, row_0, row_0 + 1, ROW_HEIGHT_HEADER
        ))

    def apply_currency_cols(self, col_indices: list,
                             start_row_0: int, end_row_0: int) -> None:
        """Apply $#,##0.00 format to a list of 0-based column indices."""
        from financial_command_center.utils.formatting import currency_format_request
        for col in col_indices:
            self.add(currency_format_request(
                self.sheet_id, start_row_0, end_row_0, col, col + 1
            ))

    def apply_percent_cols(self, col_indices: list,
                            start_row_0: int, end_row_0: int) -> None:
        from financial_command_center.utils.formatting import percent_format_request
        for col in col_indices:
            self.add(percent_format_request(
                self.sheet_id, start_row_0, end_row_0, col, col + 1
            ))

    def apply_date_cols(self, col_indices: list,
                         start_row_0: int, end_row_0: int) -> None:
        from financial_command_center.utils.formatting import date_format_request
        for col in col_indices:
            self.add(date_format_request(
                self.sheet_id, start_row_0, end_row_0, col, col + 1
            ))

    # ------------------------------------------------------------------
    # Abstract method
    # ------------------------------------------------------------------

    def build(self, tab_gids: list) -> None:
        """
        Build this sheet: write data, add formatting requests, then flush.
        Subclasses MUST override this method.

        Args:
            tab_gids: list of integer GIDs for all 10 tabs (used for nav bar).
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement build()"
        )
