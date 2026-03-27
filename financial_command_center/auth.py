"""
Google Sheets API authentication.

Supports two modes:
  1. Service account (default) — credentials.json file in project root
  2. OAuth user credentials   — credentials_oauth.json (for personal Drive)

Set GOOGLE_CREDENTIALS_FILE env var to override the default path.
"""

import os
import sys

import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCreds
from google.oauth2.credentials import Credentials as OAuthCreds

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

DEFAULT_SA_FILE    = "credentials.json"
DEFAULT_OAUTH_FILE = "credentials_oauth.json"


def get_client(credentials_file: str = None, use_oauth: bool = False) -> gspread.Client:
    """
    Return an authenticated gspread Client.

    Args:
        credentials_file: Path to the credentials JSON file.
                          Defaults to GOOGLE_CREDENTIALS_FILE env var,
                          then 'credentials.json' in the current directory.
        use_oauth:        If True, treat the file as an OAuth token file
                          instead of a service account key.

    Returns:
        gspread.Client ready to create / open spreadsheets.
    """
    if credentials_file is None:
        credentials_file = os.environ.get(
            "GOOGLE_CREDENTIALS_FILE",
            DEFAULT_OAUTH_FILE if use_oauth else DEFAULT_SA_FILE
        )

    if not os.path.exists(credentials_file):
        print(f"\nERROR: Credentials file not found: '{credentials_file}'")
        print("Please follow the setup instructions in README.md to create")
        print("a Google Cloud service account and download credentials.json\n")
        sys.exit(1)

    try:
        if use_oauth:
            creds = OAuthCreds.from_authorized_user_file(credentials_file, SCOPES)
            return gspread.authorize(creds)
        else:
            return gspread.service_account(filename=credentials_file)
    except Exception as exc:
        print(f"\nERROR: Failed to authenticate with Google Sheets API: {exc}")
        print("Please check that your credentials file is valid and has the")
        print("correct permissions (Google Sheets API + Google Drive API).\n")
        sys.exit(1)
