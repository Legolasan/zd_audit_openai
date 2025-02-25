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
    """Ensures that the headers are present in the sheet."""
    existing_data = sheet.get_all_values()

    if not existing_data or existing_data[0] != HEADERS:
        sheet.insert_row(HEADERS, 1)
        print("✅ Headers added to Google Sheets.")


def process_write_queue():
    """Continuously writes data from the queue to Google Sheets."""
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
                    sheet.append_rows(batch)  # Write batch data
                    print(f"✅ {len(batch)} rows written to Google Sheets.")
                except gspread.exceptions.APIError as api_error:
                    print(f"⚠️ Google Sheets API Error: {api_error.response.text}")  # Log API response
                except Exception as e:
                    print(f"❌ Unexpected Error while writing to Google Sheets: {e}")

            time.sleep(2)  # Avoid API rate limits

        except Exception as e:
            print(f"⚠️ Error in write queue processing: {e}")
            time.sleep(5)  # Delay before retrying


# Start the write processing thread
write_thread = threading.Thread(target=process_write_queue, daemon=True)
write_thread.start()


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


def wait_for_queue_to_empty(timeout=60):
    """Wait for the write queue to empty before exiting.

    Args:
        timeout: Maximum time to wait in seconds.

    Returns:
        bool: True if queue emptied, False if timed out.
    """
    start_time = time.time()
    while not write_queue.empty():
        if time.time() - start_time > timeout:
            return False
        time.sleep(1)

    # Allow some time for final processing
    time.sleep(3)
    return True