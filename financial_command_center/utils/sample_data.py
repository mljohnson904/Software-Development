"""
Realistic sample data for a veteran transitioning to civilian employment.
Household income approximately $50,000–$55,000/year (single income).
Data covers January–March of the current year.
"""

import datetime

CURRENT_YEAR = datetime.date.today().year


# ---------------------------------------------------------------------------
# Income rows — 3 months of entries
# Date | Source | Category | Amount | Tax Withheld (Est.) | Net Amount | Notes
# ---------------------------------------------------------------------------

def get_income_rows() -> list:
    rows = []
    months = [
        (1,  "Jan"),
        (2,  "Feb"),
        (3,  "Mar"),
    ]
    for month_num, _ in months:
        # Primary paycheck (bi-weekly — 2 per month shown as 1 monthly entry)
        rows.append([
            f"{CURRENT_YEAR}-{month_num:02d}-01",
            "Employer Direct Deposit",
            "W2 Employment",
            3800.00,
            570.00,
            3230.00,
            "Bi-weekly net after federal/state withholding",
        ])
        # VA Disability (non-taxable)
        rows.append([
            f"{CURRENT_YEAR}-{month_num:02d}-01",
            "VA Disability Payment",
            "VA Disability (Non-Taxable)",
            500.00,
            0.00,
            500.00,
            "30% disability rating — non-taxable",
        ])
        # GI Bill BAH (non-taxable)
        rows.append([
            f"{CURRENT_YEAR}-{month_num:02d}-15",
            "GI Bill BAH",
            "GI Bill BAH (Non-Taxable)",
            1200.00,
            0.00,
            1200.00,
            "Housing allowance while enrolled in courses — non-taxable",
        ])
        # Occasional side income in Feb
        if month_num == 2:
            rows.append([
                f"{CURRENT_YEAR}-{month_num:02d}-20",
                "Freelance IT Consulting",
                "1099/Self-Employed",
                350.00,
                52.50,
                297.50,
                "Weekend consulting — set aside SE tax",
            ])
    return rows


# ---------------------------------------------------------------------------
# Expense rows — 3 months of entries across all categories
# Date | Merchant | Category | Subcategory | Amount | Payment Method | Recurring? | Notes
# ---------------------------------------------------------------------------

def get_expense_rows() -> list:
    rows = []
    months = [1, 2, 3]

    # Fixed/recurring entries per month
    recurring_fixed = [
        # Merchant, Category, Subcategory, Amount, Method, Notes
        ("Landlord - Park View Apts", "Housing",        "Rent/Mortgage",  1450.00, "Checking",       "Monthly rent"),
        ("Dominion Energy",           "Housing",        "Utilities",        95.00, "Checking",       "Electric"),
        ("Comcast Xfinity",           "Housing",        "Internet",         79.99, "Checking",       "1Gbps plan"),
        ("State Farm",                "Housing",        "Renters Insurance", 22.00, "Checking",      "Monthly premium"),
        ("Navy Federal CU",           "Transportation", "Car Payment",      385.00, "Checking",      "2021 Toyota Tacoma"),
        ("GEICO",                     "Transportation", "Auto Insurance",   142.00, "Checking",       "Full coverage"),
        ("T-Mobile",                  "Personal",       "Subscriptions",     85.00, "Checking",       "Phone plan"),
        ("Netflix",                   "Personal",       "Subscriptions",     17.99, "Credit Card 1",  "Streaming"),
        ("Spotify",                   "Personal",       "Subscriptions",      9.99, "Credit Card 1",  "Music"),
        ("Planet Fitness",            "Personal",       "Gym",               24.99, "Credit Card 1",  "Membership"),
        ("BCBS Insurance",            "Healthcare",     "Insurance Premium", 187.00, "Checking",      "ACA marketplace plan"),
        ("Citi Card Min",             "Debt Payments",  "Credit Card",       65.00, "Checking",       "CC1 minimum payment"),
        ("Chase Card Min",            "Debt Payments",  "Credit Card",       45.00, "Checking",       "CC2 minimum payment"),
        ("NAVIENT",                   "Debt Payments",  "Student Loan",     130.00, "Checking",       "Student loan payment"),
    ]

    for month in months:
        for merchant, cat, subcat, amt, method, note in recurring_fixed:
            rows.append([
                f"{CURRENT_YEAR}-{month:02d}-01",
                merchant, cat, subcat, amt, method, "Yes", note,
            ])

        # Variable monthly expenses
        variable = [
            # Merchant, Category, Subcategory, Amount, Method, Recurring
            ("Giant Food",        "Food",              "Groceries",          320.00, "Checking",      "No",  "Weekly groceries"),
            ("Wawa",              "Food",              "Coffee",              28.00, "Cash",           "No",  "Morning coffee"),
            ("Chipotle",          "Food",              "Dining Out",          45.00, "Credit Card 1",  "No",  "Lunch x3"),
            ("Applebees",         "Food",              "Dining Out",          62.00, "Credit Card 1",  "No",  "Team dinner"),
            ("BP Gas Station",    "Transportation",    "Gas",                 85.00, "Credit Card 1",  "No",  "Fill up x2"),
            ("Jiffy Lube",        "Transportation",    "Maintenance",         45.00, "Checking",       "No",  "Oil change"),
            ("CVS Pharmacy",      "Healthcare",        "Medications",         28.50, "Checking",       "No",  "Prescription"),
            ("CompTIA Store",     "Education & Career","Certification Fees", 329.00 if month == 1 else 0, "Credit Card 1", "No",
             "Security+ exam voucher" if month == 1 else ""),
            ("Amazon",            "Education & Career","Books",               42.00, "Credit Card 1",  "No",  "Study materials"),
            ("Target",            "Personal",          "Clothing",            78.00, "Credit Card 1",  "No",  "Work clothes"),
            ("Great Clips",       "Personal",          "Haircuts",            18.00, "Cash",           "No",  "Haircut"),
            ("Amazon Prime",      "Personal",          "Subscriptions",       14.99, "Credit Card 1",  "Yes", "Prime membership"),
            ("Regal Cinemas",     "Personal",          "Entertainment",       24.00, "Credit Card 1",  "No",  "Movie night"),
            ("PetSmart",          "Family",            "Pet Care",            55.00, "Credit Card 1",  "No",  "Dog food + supplies"),
            ("Savings Transfer",  "Financial",         "Emergency Fund",     200.00, "Savings",        "Yes", "Auto-transfer to emergency fund"),
            ("Fidelity",          "Financial",         "Investments",        100.00, "Checking",       "Yes", "Roth IRA contribution"),
        ]

        for merchant, cat, subcat, amt, method, recurring, note in variable:
            if amt == 0:
                continue
            rows.append([
                f"{CURRENT_YEAR}-{month:02d}-15",
                merchant, cat, subcat, amt, method, recurring, note,
            ])

    return rows


# ---------------------------------------------------------------------------
# Debt rows
# Name | Lender | Original Balance | Current Balance | Interest Rate | Min Payment | Extra Payment | Priority
# ---------------------------------------------------------------------------

def get_debt_rows() -> list:
    return [
        ["2021 Toyota Tacoma Auto Loan",  "Navy Federal CU",        28500.00, 18420.00, 0.059, 385.00, 100.00, ""],
        ["Chase Freedom Unlimited (CC1)", "Chase Bank",              4500.00,  3180.00, 0.199,  65.00,  50.00, ""],
        ["Citi Double Cash (CC2)",        "Citibank",                2800.00,  1790.00, 0.229,  45.00,   0.00, ""],
        ["Federal Student Loan",          "NAVIENT / Dept of Ed",   18000.00, 12050.00, 0.045, 130.00,   0.00, ""],
    ]


# ---------------------------------------------------------------------------
# Savings goal rows
# Name | Target Amount | Current Saved | Target Date | Monthly Contribution | Status
# ---------------------------------------------------------------------------

def get_goal_rows() -> list:
    target_year = CURRENT_YEAR + 1
    return [
        ["Emergency Fund (3–6 mo expenses)",  6000.00,  2400.00, f"{target_year}-06-01",  150.00, ""],
        ["Vacation / Travel Fund",             3000.00,   450.00, f"{target_year}-12-01",  100.00, ""],
        ["New Vehicle Down Payment",          15000.00,   750.00, f"{target_year + 2}-01-01", 200.00, ""],
        ["Home Down Payment",                 30000.00,  1500.00, f"{target_year + 4}-01-01", 200.00, ""],
        ["Certifications & Education",         2500.00,  1000.00, f"{CURRENT_YEAR}-12-01",  100.00, ""],
        ["Investment Seed Fund",               5000.00,   300.00, f"{target_year + 1}-01-01", 100.00, ""],
    ]


# ---------------------------------------------------------------------------
# Net worth history — 12 months trending upward
# Month | Total Assets | Total Liabilities | Net Worth | Change
# ---------------------------------------------------------------------------

def get_net_worth_history() -> list:
    rows = []
    current_month = datetime.date.today().month
    current_year  = datetime.date.today().year

    # Start 11 months back
    assets      = 18500.00
    liabilities = 37200.00

    for i in range(12):
        month_offset = (current_month - 12 + i)
        year  = current_year + (month_offset - 1) // 12
        month = ((month_offset - 1) % 12) + 1
        label = datetime.date(year, month, 1).strftime("%b %Y")

        net_worth = assets - liabilities
        rows.append([label, round(assets, 2), round(liabilities, 2), round(net_worth, 2)])

        # Simulate gradual improvement each month
        assets      += 280.00   # savings + asset appreciation
        liabilities -= 180.00   # debt paydown

    return rows


# ---------------------------------------------------------------------------
# Recurring transaction rows
# Name | Type | Amount | Frequency | Next Due Date | Category | Auto? | Active?
# ---------------------------------------------------------------------------

def get_recurring_rows() -> list:
    today     = datetime.date.today()
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    fmt = "%Y-%m-%d"

    return [
        ["Monthly Rent",          "Expense", 1450.00, "Monthly",   next_month.strftime(fmt), "Housing",            "No",  "Yes"],
        ["Electric Bill",         "Expense",   95.00, "Monthly",   next_month.strftime(fmt), "Housing",            "Yes", "Yes"],
        ["Internet",              "Expense",   79.99, "Monthly",   next_month.strftime(fmt), "Housing",            "Yes", "Yes"],
        ["Car Insurance (GEICO)", "Expense",  142.00, "Monthly",   next_month.strftime(fmt), "Transportation",     "Yes", "Yes"],
        ["T-Mobile Phone Plan",   "Expense",   85.00, "Monthly",   next_month.strftime(fmt), "Personal",           "Yes", "Yes"],
        ["Planet Fitness",        "Expense",   24.99, "Monthly",   next_month.strftime(fmt), "Personal",           "Yes", "Yes"],
        ["Netflix",               "Expense",   17.99, "Monthly",   next_month.strftime(fmt), "Personal",           "Yes", "Yes"],
        ["Amazon Prime",          "Expense",  139.00, "Annual",    f"{today.year + 1}-03-15", "Personal",          "Yes", "Yes"],
        ["BCBS Health Insurance", "Expense",  187.00, "Monthly",   next_month.strftime(fmt), "Healthcare",         "Yes", "Yes"],
        ["Emergency Fund Auto-Transfer", "Expense", 200.00, "Monthly", next_month.strftime(fmt), "Financial",      "Yes", "Yes"],
        ["Roth IRA Contribution", "Expense",  100.00, "Monthly",   next_month.strftime(fmt), "Financial",          "Yes", "Yes"],
        ["Primary Salary (W2)",   "Income",  3800.00, "Bi-Weekly", next_month.strftime(fmt), "W2 Employment",      "Yes", "Yes"],
        ["VA Disability",         "Income",   500.00, "Monthly",   next_month.strftime(fmt), "VA Disability (Non-Taxable)", "Yes", "Yes"],
        ["GI Bill BAH",           "Income",  1200.00, "Monthly",   next_month.strftime(fmt), "GI Bill BAH (Non-Taxable)",   "Yes", "Yes"],
    ]


# ---------------------------------------------------------------------------
# Bill registry rows (for Bill Calendar)
# Name | Amount | Due Day | Auto-Pay? | Account | Category | Active?
# ---------------------------------------------------------------------------

def get_bill_registry_rows() -> list:
    return [
        ["Monthly Rent",           1450.00,  1, "No",  "Checking",      "Housing",        "Yes"],
        ["Electric Bill",            95.00,  5, "Yes", "Checking",      "Housing",        "Yes"],
        ["Internet",                 79.99,  8, "Yes", "Checking",      "Housing",        "Yes"],
        ["Renters Insurance",        22.00, 10, "Yes", "Checking",      "Housing",        "Yes"],
        ["Health Insurance",        187.00, 15, "Yes", "Checking",      "Healthcare",     "Yes"],
        ["Car Insurance",           142.00,  1, "Yes", "Checking",      "Transportation", "Yes"],
        ["Car Payment",             385.00, 20, "Yes", "Checking",      "Transportation", "Yes"],
        ["Student Loan",            130.00, 25, "Yes", "Checking",      "Debt Payments",  "Yes"],
        ["Chase CC1 Min",            65.00, 22, "No",  "Credit Card 1", "Debt Payments",  "Yes"],
        ["Citi CC2 Min",             45.00, 18, "No",  "Credit Card 2", "Debt Payments",  "Yes"],
        ["T-Mobile",                 85.00, 12, "Yes", "Checking",      "Personal",       "Yes"],
        ["Netflix",                  17.99, 14, "Yes", "Credit Card 1", "Personal",       "Yes"],
        ["Spotify",                   9.99, 14, "Yes", "Credit Card 1", "Personal",       "Yes"],
        ["Planet Fitness",           24.99,  1, "Yes", "Credit Card 1", "Personal",       "Yes"],
    ]


# ---------------------------------------------------------------------------
# Monthly budget template rows (expected amounts)
# Income: source | expected | actual (formula) | difference (formula)
# Expense: category | subcategory | budgeted | actual (formula) | difference
# ---------------------------------------------------------------------------

INCOME_BUDGET_TEMPLATE = [
    ["Primary Salary (W2)",      3800.00],
    ["Secondary / 1099 Income",   350.00],
    ["VA Disability",             500.00],
    ["GI Bill BAH",              1200.00],
    ["Side Income",                 0.00],
]

EXPENSE_BUDGET_TEMPLATE = {
    "Housing": [
        ("Rent/Mortgage",    1450.00),
        ("Utilities",          95.00),
        ("Internet",           79.99),
        ("Renters Insurance",  22.00),
    ],
    "Transportation": [
        ("Car Payment",       385.00),
        ("Auto Insurance",    142.00),
        ("Gas",               100.00),
        ("Maintenance",        30.00),
    ],
    "Food": [
        ("Groceries",         320.00),
        ("Dining Out",        120.00),
        ("Work Lunches",       60.00),
        ("Coffee",             30.00),
    ],
    "Healthcare": [
        ("Insurance Premium", 187.00),
        ("Copays",             25.00),
        ("Medications",        30.00),
        ("Dental",              0.00),
    ],
    "Education & Career": [
        ("Certification Fees",  0.00),
        ("Books",              50.00),
        ("Online Courses",      0.00),
        ("Professional Dues",   0.00),
    ],
    "Personal": [
        ("Clothing",           50.00),
        ("Haircuts",           20.00),
        ("Subscriptions",     137.97),
        ("Entertainment",      50.00),
        ("Gym",                24.99),
    ],
    "Family": [
        ("Pet Care",           60.00),
        ("Gifts",              25.00),
    ],
    "Financial": [
        ("Emergency Fund",    200.00),
        ("Investments",       100.00),
        ("Life Insurance",      0.00),
    ],
    "Debt Payments": [
        ("Auto Loan",         385.00),
        ("Credit Card 1",      65.00),
        ("Credit Card 2",      45.00),
        ("Student Loan",      130.00),
    ],
}


# ---------------------------------------------------------------------------
# Assets / Liabilities for Net Worth Tracker
# ---------------------------------------------------------------------------

def get_asset_rows() -> list:
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    return [
        ["Checking Account (Navy Federal)",   "Checking",       2450.00,  today_str],
        ["Savings Account (High Yield)",      "Savings",        3800.00,  today_str],
        ["TSP / Roth IRA (Fidelity)",         "Retirement",     4200.00,  today_str],
        ["2021 Toyota Tacoma",                "Vehicle",       22000.00,  today_str],
        ["Taxable Brokerage (Fidelity)",      "Other",           300.00,  today_str],
    ]


def get_liability_rows() -> list:
    return [
        ["Auto Loan — 2021 Tacoma",  "Auto Loan",     18420.00, 0.059],
        ["Chase Freedom Unlimited",  "Credit Card",    3180.00, 0.199],
        ["Citi Double Cash",         "Credit Card",    1790.00, 0.229],
        ["Federal Student Loan",     "Student Loan",  12050.00, 0.045],
    ]
