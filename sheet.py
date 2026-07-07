import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_info(
    json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON")),
    scopes=SCOPES
)

client = gspread.authorize(creds)

SHEET_ID = "1-vTfyVwgQU3ZodQ4WODNeo7PXPfK5FgC8JDyV-8p_os"

sheet = client.open_by_key(SHEET_ID).sheet1
