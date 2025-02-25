import gspread
import threading
import queue
import time
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, SHEET_NAME

# Load Google Sheets API credentials
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# Queue to store write requests
write_queue = queue.Queue()

# Define the expected headers
HEADERS = [
    "Ticket ID", "SPOC", "Summary", "Politeness & Professionalism", "Clarity of Responses",
    "Timeliness of Updates", "Proactive Communication", "Escalation Handling",
    "Asking the Right Questions", "Finding the Root Cause Timely", "Product Understanding",
    "Effective Troubleshooting Steps", "Workaround Provided", "Acknowledging Customer Impact",
    "Apologies for Delays", "Prioritization of Urgent Issues", "Understanding Customer Frustration",
    "Final Sentiment", "Areas of Improvement"
]

def ensure_headers_exist():
    existing_data = sheet.get_all_values()
    if not existing_data or existing_data[0] != HEADERS:
        sheet.insert_row(HEADERS, 1)
        print("✅ Headers added to Google Sheets.")

def process_write_queue():
    global write_queue  # Ensure queue access

    while True:
        try:
            batch = []
            while not write_queue.empty():
                row = write_queue.get()
                print("📝 Queued row for writing:", row)  # Debug log
                batch.append(row)

            if batch:
                ensure_headers_exist()  # Ensure headers exist
                try:
                    sheet.append_rows(batch)  # Write in batch
                    print(f"✅ {len(batch)} rows written to Google Sheets.")
                except gspread.exceptions.APIError as api_error:
                    print(f"⚠️ Google Sheets API Error: {api_error.response.text}")  # Log API response
                except Exception as e:
                    print(f"❌ Unexpected Error while writing to Google Sheets: {e}")

            time.sleep(2)  # Delay to avoid API rate limits

        except Exception as e:
            print(f"⚠️ Error in write queue processing: {e}")
            time.sleep(5)  # Delay before retrying
def wait_for_queue_to_empty(queue, timeout=120):
    """
    Waits for the queue to be empty within a given timeout period.

    Args:
        queue (queue.Queue): The queue to monitor.
        timeout (int): Maximum time to wait for the queue to empty (in seconds).

    Returns:
        bool: True if the queue is emptied within the timeout, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if queue.empty():
            return True
        time.sleep(1)  # Wait before checking again
    return False

def queue_write_to_google_sheets(results):
    """Queues results to be written to Google Sheets."""
    if not results:
        print("No results to queue.")
        return

    for result in results:
        row = [
            result.get("Ticket ID", ""),
            result.get("SPOC", "Unknown"),
            result.get("Summary", ""),  # Add the summary column
            result.get("Communication", {}).get("Politeness & Professionalism", ""),
            result.get("Communication", {}).get("Clarity of Responses", ""),
            result.get("Communication", {}).get("Timeliness of Updates", ""),
            result.get("Communication", {}).get("Proactive Communication", ""),
            result.get("Communication", {}).get("Escalation Handling", ""),
            result.get("Technical Knowledge", {}).get("Asking the Right Questions", ""),
            result.get("Technical Knowledge", {}).get("Finding the Root Cause Timely", ""),
            result.get("Technical Knowledge", {}).get("Product Understanding", ""),
            result.get("Technical Knowledge", {}).get("Effective Troubleshooting Steps", ""),
            result.get("Technical Knowledge", {}).get("Workaround Provided", ""),
            result.get("Empathy", {}).get("Acknowledging Customer Impact", ""),
            result.get("Empathy", {}).get("Apologies for Delays", ""),
            result.get("Empathy", {}).get("Prioritization of Urgent Issues", ""),
            result.get("Empathy", {}).get("Understanding Customer Frustration", ""),
            result.get("Final Sentiment", ""),
            result.get("Areas of Improvement", "")
        ]
        write_queue.put(row)

    print(f"📌 {len(results)} valid rows added to write queue.")
