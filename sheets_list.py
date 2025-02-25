import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID

# Load Google Sheets API credentials
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)

# List available worksheets
sheets = client.open_by_key(SPREADSHEET_ID).worksheets()
print([s.title for s in sheets])  # Prints all sheet names
