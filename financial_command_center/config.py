"""
Configuration constants for the Financial Command Center spreadsheet builder.
Colors, tab names, column definitions, and shared lookup data.
"""

# ---------------------------------------------------------------------------
# Color Palette (hex strings — converted to RGB by utils/formatting.py)
# ---------------------------------------------------------------------------
COLORS = {
    "bg_primary":     "#1A1A2E",  # deep navy — main background
    "bg_secondary":   "#16213E",  # card navy — alternating rows / cards
    "accent_gold":    "#E8B84B",  # gold — headers, borders, highlights
    "accent_gold_lt": "#F5D78E",  # light gold — totals rows
    "success":        "#4CAF50",  # green — under budget / positive
    "warning":        "#FFC107",  # yellow — near budget limit
    "danger":         "#F44336",  # red — over budget / overdue
    "info_blue":      "#1E88E5",  # blue — recurring items
    "text_primary":   "#FFFFFF",  # white
    "text_secondary": "#B0BEC5",  # light gray
    "text_dark":      "#1A1A2E",  # dark text on gold backgrounds
    "row_alt1":       "#1E2A45",  # alternating row 1
    "row_alt2":       "#16213E",  # alternating row 2
    "nav_bg":         "#E8B84B",  # navigation bar background
    "transparent":    "#FFFFFF",  # used for clearing formats
}

# ---------------------------------------------------------------------------
# Sheet Tab Names (order matters — this is the final tab order)
# ---------------------------------------------------------------------------
SHEET_NAMES = [
    "🏠 Dashboard",
    "💰 Monthly Budget",
    "📊 Income Tracker",
    "🧾 Expense Log",
    "💳 Debt Tracker",
    "📅 Bill Calendar",
    "🎯 Savings Goals",
    "📈 Net Worth Tracker",
    "🔄 Recurring Transactions",
    "⚙️ Settings & Reference",
]

# Short aliases used in navigation bar labels
NAV_LABELS = [
    "🏠 Dashboard",
    "💰 Budget",
    "📊 Income",
    "🧾 Expenses",
    "💳 Debt",
    "📅 Bills",
    "🎯 Goals",
    "📈 Net Worth",
    "🔄 Recurring",
    "⚙️ Settings",
]

# ---------------------------------------------------------------------------
# Row / Column sizing
# ---------------------------------------------------------------------------
ROW_HEIGHT_HEADER = 32   # pixels for section header rows
ROW_HEIGHT_DATA   = 22   # pixels for data rows
ROW_HEIGHT_NAV    = 30   # pixels for navigation bar

COL_WIDTH_DEFAULT = 120  # pixels
COL_WIDTH_NARROW  =  80
COL_WIDTH_WIDE    = 200
COL_WIDTH_DATE    = 110
COL_WIDTH_AMOUNT  = 100
COL_WIDTH_NOTE    = 220

# ---------------------------------------------------------------------------
# Number / Date formats
# ---------------------------------------------------------------------------
FMT_CURRENCY    = '"$"#,##0.00'
FMT_CURRENCY_K  = '"$"#,##0'
FMT_PERCENT     = '0.0%'
FMT_DATE        = 'MMM DD, YYYY'
FMT_DATE_SHORT  = 'MM/DD/YYYY'
FMT_INTEGER     = '#,##0'

# ---------------------------------------------------------------------------
# Income categories
# ---------------------------------------------------------------------------
INCOME_CATEGORIES = [
    "W2 Employment",
    "1099/Self-Employed",
    "VA Disability (Non-Taxable)",
    "GI Bill BAH (Non-Taxable)",
    "Separation Pay",
    "Bonus",
    "Side Hustle",
    "Investment",
    "Other",
]

# ---------------------------------------------------------------------------
# Expense categories and their subcategories
# ---------------------------------------------------------------------------
EXPENSE_CATEGORIES = [
    "Housing",
    "Transportation",
    "Food",
    "Healthcare",
    "Education & Career",
    "Personal",
    "Family",
    "Financial",
    "Debt Payments",
    "Other",
]

EXPENSE_SUBCATEGORIES = {
    "Housing":            ["Rent/Mortgage", "Utilities", "Internet", "Renters Insurance", "Repairs", "Other"],
    "Transportation":     ["Car Payment", "Auto Insurance", "Gas", "Maintenance", "Parking/Tolls", "Other"],
    "Food":               ["Groceries", "Dining Out", "Work Lunches", "Coffee", "Other"],
    "Healthcare":         ["Insurance Premium", "Copays", "Medications", "Dental", "Vision", "Other"],
    "Education & Career": ["Certification Fees", "Books", "Online Courses", "Professional Dues", "Other"],
    "Personal":           ["Clothing", "Haircuts", "Subscriptions", "Entertainment", "Gym", "Other"],
    "Family":             ["Childcare", "Pet Care", "Gifts", "School Supplies", "Other"],
    "Financial":          ["Emergency Fund", "Investments", "Life Insurance", "Other"],
    "Debt Payments":      ["Credit Card", "Auto Loan", "Student Loan", "Personal Loan", "Other"],
    "Other":              ["Miscellaneous"],
}

# ---------------------------------------------------------------------------
# Payment methods
# ---------------------------------------------------------------------------
PAYMENT_METHODS = [
    "Checking",
    "Savings",
    "Credit Card 1",
    "Credit Card 2",
    "Cash",
    "Venmo/Zelle",
]

# ---------------------------------------------------------------------------
# Recurring frequency options
# ---------------------------------------------------------------------------
FREQUENCIES = [
    "Weekly",
    "Bi-Weekly",
    "Monthly",
    "Quarterly",
    "Annual",
]

# ---------------------------------------------------------------------------
# Payoff methods
# ---------------------------------------------------------------------------
PAYOFF_METHODS = [
    "Avalanche (Highest APR First)",
    "Snowball (Lowest Balance First)",
]

# ---------------------------------------------------------------------------
# Month names for dropdowns
# ---------------------------------------------------------------------------
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# ---------------------------------------------------------------------------
# Settings sheet — column locations for dropdown source data
# (column indices are 0-based for the Sheets API)
# Hidden columns P+ (index 15+) store validation lists
# ---------------------------------------------------------------------------
SETTINGS_VALIDATION_COL = 15   # Column P — start of hidden dropdown source data

# Named ranges (used in cross-sheet formula references)
NAMED_RANGES = {
    "SELECTED_MONTH":     "💰 Monthly Budget",   # B1 on Monthly Budget
    "PAYOFF_METHOD":      "💳 Debt Tracker",      # B1 on Debt Tracker
}
