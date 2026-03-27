"""
Formatting helpers for the Google Sheets API batchUpdate request builder.

All functions return dict objects that can be collected into a list and
submitted in a single spreadsheet.batch_update({"requests": [...]}) call.
"""

from financial_command_center.config import COLORS


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_str: str) -> dict:
    """Convert a hex color string to a Sheets API RGB dict (0.0–1.0 range)."""
    h = hex_str.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return {"red": r / 255.0, "green": g / 255.0, "blue": b / 255.0}


def color(name: str) -> dict:
    """Return an RGB dict for a named color from the COLORS palette."""
    return hex_to_rgb(COLORS[name])


# ---------------------------------------------------------------------------
# Range helpers
# ---------------------------------------------------------------------------

def grid_range(sheet_id: int, start_row: int, end_row: int,
               start_col: int, end_col: int) -> dict:
    """
    Build a GridRange dict.
    Row/col indices are 0-based; end values are exclusive.
    """
    return {
        "sheetId":          sheet_id,
        "startRowIndex":    start_row,
        "endRowIndex":      end_row,
        "startColumnIndex": start_col,
        "endColumnIndex":   end_col,
    }


def single_cell_range(sheet_id: int, row: int, col: int) -> dict:
    """GridRange for a single cell (0-based)."""
    return grid_range(sheet_id, row, row + 1, col, col + 1)


# ---------------------------------------------------------------------------
# Cell format requests
# ---------------------------------------------------------------------------

def repeat_cell_request(sheet_id: int, start_row: int, end_row: int,
                        start_col: int, end_col: int,
                        cell_format: dict, fields: str = "userEnteredFormat") -> dict:
    """Bulk-apply a cell format to a range via repeatCell."""
    return {
        "repeatCell": {
            "range":  grid_range(sheet_id, start_row, end_row, start_col, end_col),
            "cell":   {"userEnteredFormat": cell_format},
            "fields": fields,
        }
    }


def header_format_request(sheet_id: int, row: int,
                          start_col: int, end_col: int,
                          bg_color: str = "bg_secondary",
                          text_color: str = "text_primary",
                          font_size: int = 10,
                          bold: bool = True,
                          h_align: str = "LEFT") -> dict:
    """Standard column-header row formatting."""
    fmt = {
        "backgroundColor": color(bg_color),
        "textFormat": {
            "bold":       bold,
            "fontSize":   font_size,
            "foregroundColor": color(text_color),
        },
        "horizontalAlignment": h_align,
        "verticalAlignment":   "MIDDLE",
    }
    return repeat_cell_request(sheet_id, row, row + 1, start_col, end_col, fmt)


def section_header_request(sheet_id: int, row: int,
                           start_col: int, end_col: int) -> dict:
    """Gold section divider / section header styling."""
    fmt = {
        "backgroundColor": color("accent_gold"),
        "textFormat": {
            "bold":            True,
            "fontSize":        12,
            "foregroundColor": color("text_dark"),
        },
        "horizontalAlignment": "CENTER",
        "verticalAlignment":   "MIDDLE",
    }
    return repeat_cell_request(sheet_id, row, row + 1, start_col, end_col, fmt)


def nav_bar_format_request(sheet_id: int, num_cols: int = 10) -> dict:
    """Gold navigation bar in row 0."""
    fmt = {
        "backgroundColor": color("nav_bg"),
        "textFormat": {
            "bold":            True,
            "fontSize":        10,
            "foregroundColor": color("text_dark"),
        },
        "horizontalAlignment": "CENTER",
        "verticalAlignment":   "MIDDLE",
    }
    return repeat_cell_request(sheet_id, 0, 1, 0, num_cols, fmt)


def totals_row_format_request(sheet_id: int, row: int,
                              start_col: int, end_col: int) -> dict:
    """Light gold totals/summary row."""
    fmt = {
        "backgroundColor": hex_to_rgb(COLORS["accent_gold_lt"]),
        "textFormat": {
            "bold":            True,
            "fontSize":        10,
            "foregroundColor": color("text_dark"),
        },
        "horizontalAlignment": "RIGHT",
        "verticalAlignment":   "MIDDLE",
    }
    return repeat_cell_request(sheet_id, row, row + 1, start_col, end_col, fmt)


def data_row_format_request(sheet_id: int, start_row: int, end_row: int,
                            start_col: int, end_col: int,
                            alt: bool = False) -> dict:
    """Standard data row with navy alternating color."""
    bg = "row_alt1" if alt else "row_alt2"
    fmt = {
        "backgroundColor": color(bg),
        "textFormat": {
            "bold":            False,
            "fontSize":        10,
            "foregroundColor": color("text_primary"),
        },
        "verticalAlignment": "MIDDLE",
    }
    return repeat_cell_request(sheet_id, start_row, end_row, start_col, end_col, fmt)


# ---------------------------------------------------------------------------
# Number format requests
# ---------------------------------------------------------------------------

def number_format_request(sheet_id: int, start_row: int, end_row: int,
                          start_col: int, end_col: int,
                          pattern: str) -> dict:
    """Apply a number/date format pattern to a range."""
    fmt = {
        "numberFormat": {"type": "NUMBER", "pattern": pattern}
    }
    return repeat_cell_request(
        sheet_id, start_row, end_row, start_col, end_col,
        fmt,
        fields="userEnteredFormat.numberFormat"
    )


def currency_format_request(sheet_id: int, start_row: int, end_row: int,
                            start_col: int, end_col: int) -> dict:
    from financial_command_center.config import FMT_CURRENCY
    return number_format_request(sheet_id, start_row, end_row,
                                 start_col, end_col, FMT_CURRENCY)


def percent_format_request(sheet_id: int, start_row: int, end_row: int,
                           start_col: int, end_col: int) -> dict:
    from financial_command_center.config import FMT_PERCENT
    return number_format_request(sheet_id, start_row, end_row,
                                 start_col, end_col, FMT_PERCENT)


def date_format_request(sheet_id: int, start_row: int, end_row: int,
                        start_col: int, end_col: int) -> dict:
    from financial_command_center.config import FMT_DATE
    return number_format_request(sheet_id, start_row, end_row,
                                 start_col, end_col, FMT_DATE)


# ---------------------------------------------------------------------------
# Dimension (row/column) sizing requests
# ---------------------------------------------------------------------------

def row_height_request(sheet_id: int, start_row: int, end_row: int,
                       height_px: int) -> dict:
    """Set pixel height for a row range."""
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId":    sheet_id,
                "dimension":  "ROWS",
                "startIndex": start_row,
                "endIndex":   end_row,
            },
            "properties": {"pixelSize": height_px},
            "fields":     "pixelSize",
        }
    }


def col_width_request(sheet_id: int, start_col: int, end_col: int,
                      width_px: int) -> dict:
    """Set pixel width for a column range."""
    return {
        "updateDimensionProperties": {
            "range": {
                "sheetId":    sheet_id,
                "dimension":  "COLUMNS",
                "startIndex": start_col,
                "endIndex":   end_col,
            },
            "properties": {"pixelSize": width_px},
            "fields":     "pixelSize",
        }
    }


# ---------------------------------------------------------------------------
# Freeze rows/columns
# ---------------------------------------------------------------------------

def freeze_request(sheet_id: int, frozen_rows: int = 2,
                   frozen_cols: int = 0) -> dict:
    """Freeze the top N rows (and optionally M columns)."""
    return {
        "updateSheetProperties": {
            "properties": {
                "sheetId":     sheet_id,
                "gridProperties": {
                    "frozenRowCount":    frozen_rows,
                    "frozenColumnCount": frozen_cols,
                },
            },
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
        }
    }


# ---------------------------------------------------------------------------
# Sheet tab appearance
# ---------------------------------------------------------------------------

def tab_color_request(sheet_id: int, hex_color: str) -> dict:
    """Set the tab color of a sheet."""
    return {
        "updateSheetProperties": {
            "properties": {
                "sheetId":  sheet_id,
                "tabColorStyle": {"rgbColor": hex_to_rgb(hex_color)},
            },
            "fields": "tabColorStyle",
        }
    }


def hide_gridlines_request(sheet_id: int) -> dict:
    """Turn off gridlines on a sheet."""
    return {
        "updateSheetProperties": {
            "properties": {
                "sheetId":    sheet_id,
                "gridProperties": {"hideGridlines": True},
            },
            "fields": "gridProperties.hideGridlines",
        }
    }


# ---------------------------------------------------------------------------
# Merge cells
# ---------------------------------------------------------------------------

def merge_cells_request(sheet_id: int, start_row: int, end_row: int,
                        start_col: int, end_col: int,
                        merge_type: str = "MERGE_ALL") -> dict:
    return {
        "mergeCells": {
            "range":     grid_range(sheet_id, start_row, end_row, start_col, end_col),
            "mergeType": merge_type,
        }
    }


# ---------------------------------------------------------------------------
# Banded (alternating) row colors
# ---------------------------------------------------------------------------

def banding_request(sheet_id: int, start_row: int, end_row: int,
                    start_col: int, end_col: int) -> dict:
    """Apply alternating row color banding to a data range."""
    return {
        "addBanding": {
            "bandedRange": {
                "range":      grid_range(sheet_id, start_row, end_row, start_col, end_col),
                "rowProperties": {
                    "headerColor":     color("accent_gold"),
                    "firstBandColor":  color("row_alt1"),
                    "secondBandColor": color("row_alt2"),
                },
            }
        }
    }


# ---------------------------------------------------------------------------
# Borders
# ---------------------------------------------------------------------------

def border_style(color_name: str = "accent_gold", style: str = "SOLID") -> dict:
    return {"style": style, "colorStyle": {"rgbColor": color(color_name)}}


def outer_border_request(sheet_id: int, start_row: int, end_row: int,
                         start_col: int, end_col: int,
                         color_name: str = "accent_gold") -> dict:
    bs = border_style(color_name)
    return {
        "updateBorders": {
            "range": grid_range(sheet_id, start_row, end_row, start_col, end_col),
            "top":    bs,
            "bottom": bs,
            "left":   bs,
            "right":  bs,
        }
    }


# ---------------------------------------------------------------------------
# Conditional formatting
# ---------------------------------------------------------------------------

def conditional_format_text_eq(sheet_id: int, start_row: int, end_row: int,
                                start_col: int, end_col: int,
                                match_text: str,
                                bg_color: str,
                                text_color: str = "text_primary") -> dict:
    """Highlight cells where text equals match_text."""
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [grid_range(sheet_id, start_row, end_row, start_col, end_col)],
                "booleanRule": {
                    "condition": {
                        "type":   "TEXT_EQ",
                        "values": [{"userEnteredValue": match_text}],
                    },
                    "format": {
                        "backgroundColor": color(bg_color),
                        "textFormat":      {"foregroundColor": color(text_color)},
                    },
                },
            },
            "index": 0,
        }
    }


def conditional_format_custom_formula(sheet_id: int, start_row: int, end_row: int,
                                       start_col: int, end_col: int,
                                       formula: str,
                                       bg_color: str,
                                       text_color: str = "text_primary",
                                       bold: bool = False,
                                       index: int = 0) -> dict:
    """Conditional format driven by a custom formula."""
    return {
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [grid_range(sheet_id, start_row, end_row, start_col, end_col)],
                "booleanRule": {
                    "condition": {
                        "type":   "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": formula}],
                    },
                    "format": {
                        "backgroundColor": color(bg_color),
                        "textFormat": {
                            "foregroundColor": color(text_color),
                            "bold": bold,
                        },
                    },
                },
            },
            "index": index,
        }
    }


# ---------------------------------------------------------------------------
# Data validation (dropdowns)
# ---------------------------------------------------------------------------

def dropdown_from_list_request(sheet_id: int, start_row: int, end_row: int,
                                start_col: int, end_col: int,
                                options: list,
                                show_dropdown: bool = True) -> dict:
    """Data validation dropdown from a hard-coded list."""
    values = [{"userEnteredValue": str(v)} for v in options]
    return {
        "setDataValidation": {
            "range": grid_range(sheet_id, start_row, end_row, start_col, end_col),
            "rule": {
                "condition": {
                    "type":   "ONE_OF_LIST",
                    "values": values,
                },
                "showCustomUi":   show_dropdown,
                "strict":         False,
            },
        }
    }


def dropdown_from_range_request(sheet_id: int, start_row: int, end_row: int,
                                 start_col: int, end_col: int,
                                 source_range: str,
                                 show_dropdown: bool = True) -> dict:
    """Data validation dropdown sourced from a range (e.g. Settings sheet)."""
    return {
        "setDataValidation": {
            "range": grid_range(sheet_id, start_row, end_row, start_col, end_col),
            "rule": {
                "condition": {
                    "type":   "ONE_OF_RANGE",
                    "values": [{"userEnteredValue": source_range}],
                },
                "showCustomUi": show_dropdown,
                "strict":       False,
            },
        }
    }


# ---------------------------------------------------------------------------
# Row grouping (collapsible sections)
# ---------------------------------------------------------------------------

def add_row_group_request(sheet_id: int, start_row: int, end_row: int,
                          collapsed: bool = False) -> dict:
    return {
        "addDimensionGroup": {
            "range": {
                "sheetId":    sheet_id,
                "dimension":  "ROWS",
                "startIndex": start_row,
                "endIndex":   end_row,
            },
            "collapsed": collapsed,
        }
    }


# ---------------------------------------------------------------------------
# Named ranges
# ---------------------------------------------------------------------------

def add_named_range_request(name: str, sheet_id: int,
                             start_row: int, end_row: int,
                             start_col: int, end_col: int) -> dict:
    return {
        "addNamedRange": {
            "namedRange": {
                "name":  name,
                "range": grid_range(sheet_id, start_row, end_row, start_col, end_col),
            }
        }
    }


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------

def chart_position(sheet_id: int, anchor_row: int, anchor_col: int,
                   offset_x: int = 0, offset_y: int = 0) -> dict:
    return {
        "overlayPosition": {
            "anchorCell": {
                "sheetId":     sheet_id,
                "rowIndex":    anchor_row,
                "columnIndex": anchor_col,
            },
            "offsetXPixels": offset_x,
            "offsetYPixels": offset_y,
            "widthPixels":   520,
            "heightPixels":  300,
        }
    }


def column_chart_request(sheet_id: int, title: str,
                          data_sheet_id: int,
                          domain_start_row: int, domain_end_row: int,
                          domain_col: int,
                          series_start_row: int, series_end_row: int,
                          series_col: int,
                          anchor_row: int, anchor_col: int) -> dict:
    """Add a vertical bar (COLUMN) chart."""
    return {
        "addChart": {
            "chart": {
                "spec": {
                    "title": title,
                    "titleTextFormat": {
                        "foregroundColor": hex_to_rgb(COLORS["accent_gold"]),
                        "bold": True,
                        "fontSize": 12,
                    },
                    "backgroundColor": hex_to_rgb(COLORS["bg_secondary"]),
                    "basicChart": {
                        "chartType": "COLUMN",
                        "legendPosition": "BOTTOM_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": ""},
                            {"position": "LEFT_AXIS",   "title": "Amount ($)"},
                        ],
                        "domains": [{
                            "domain": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId":          data_sheet_id,
                                        "startRowIndex":    domain_start_row,
                                        "endRowIndex":      domain_end_row,
                                        "startColumnIndex": domain_col,
                                        "endColumnIndex":   domain_col + 1,
                                    }]
                                }
                            }
                        }],
                        "series": [{
                            "series": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId":          data_sheet_id,
                                        "startRowIndex":    series_start_row,
                                        "endRowIndex":      series_end_row,
                                        "startColumnIndex": series_col,
                                        "endColumnIndex":   series_col + 1,
                                    }]
                                }
                            },
                            "color": hex_to_rgb(COLORS["accent_gold"]),
                        }],
                    },
                },
                "position": chart_position(sheet_id, anchor_row, anchor_col),
            }
        }
    }


def line_chart_request(sheet_id: int, title: str,
                        data_sheet_id: int,
                        domain_start_row: int, domain_end_row: int,
                        domain_col: int,
                        series_configs: list,
                        anchor_row: int, anchor_col: int) -> dict:
    """
    Add a LINE chart.
    series_configs: list of dicts with keys: start_row, end_row, col, color_hex, label
    """
    series_list = []
    for sc in series_configs:
        series_list.append({
            "series": {
                "sourceRange": {
                    "sources": [{
                        "sheetId":          data_sheet_id,
                        "startRowIndex":    sc["start_row"],
                        "endRowIndex":      sc["end_row"],
                        "startColumnIndex": sc["col"],
                        "endColumnIndex":   sc["col"] + 1,
                    }]
                }
            },
            "color": hex_to_rgb(sc.get("color_hex", COLORS["accent_gold"])),
        })

    return {
        "addChart": {
            "chart": {
                "spec": {
                    "title": title,
                    "titleTextFormat": {
                        "foregroundColor": hex_to_rgb(COLORS["accent_gold"]),
                        "bold": True,
                        "fontSize": 12,
                    },
                    "backgroundColor": hex_to_rgb(COLORS["bg_secondary"]),
                    "basicChart": {
                        "chartType": "LINE",
                        "legendPosition": "BOTTOM_LEGEND",
                        "axis": [
                            {"position": "BOTTOM_AXIS", "title": "Month"},
                            {"position": "LEFT_AXIS",   "title": "Amount ($)"},
                        ],
                        "domains": [{
                            "domain": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId":          data_sheet_id,
                                        "startRowIndex":    domain_start_row,
                                        "endRowIndex":      domain_end_row,
                                        "startColumnIndex": domain_col,
                                        "endColumnIndex":   domain_col + 1,
                                    }]
                                }
                            }
                        }],
                        "series": series_list,
                    },
                },
                "position": chart_position(sheet_id, anchor_row, anchor_col),
            }
        }
    }
