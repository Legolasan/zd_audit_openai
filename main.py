import concurrent.futures
import time
from datetime import datetime, timedelta, timezone
from zendesk_api import fetch_tickets_for_spoc, fetch_ticket_comments, assignee_name
from openai_analysis import analyze_ticket_with_openai
from google_sheets import queue_write_to_google_sheets, wait_for_queue_to_empty


def process_spoc(spoc_id, spoc_name, start_date):
    results = []
    tickets = fetch_tickets_for_spoc(spoc_id, start_date)

    for ticket in tickets:
        comments = fetch_ticket_comments(ticket["id"])

        # Skip tickets with no comments
        if not comments:
            print(f"⚠️ Skipping Ticket ID {ticket['id']} for SPOC {spoc_name} (No Comments Found)")
            continue

        analysis_result = analyze_ticket_with_openai(ticket["id"], ticket["subject"], ticket["description"], comments)

        # Skip writing empty analysis results
        if "error" in analysis_result or not analysis_result.get("Final Sentiment"):
            print(f"⚠️ Skipping Ticket ID {ticket['id']} for SPOC {spoc_name} (Analysis Failed)")
            continue

        results.append(analysis_result)

    return results

def main():
    start_time = time.time()

    start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    all_results = []

    print(f"🔍 Starting ticket analysis from {start_date}...")

    # Track timing for ticket processing
    processing_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_spoc = {
            executor.submit(process_spoc, spoc_id, spoc_name, start_date): spoc_id
            for spoc_id, spoc_name in assignee_name.items()
        }
        for future in concurrent.futures.as_completed(future_to_spoc):
            all_results.extend(future.result())

    processing_time = time.time() - processing_start
    print(f"✅ Ticket processing completed in {processing_time:.2f} seconds")

    # Track timing for Google Sheets operations
    sheets_start = time.time()
    queue_write_to_google_sheets(all_results)  # Queue results instead of writing instantly

    print("\n✅ All results added to queue. Writing to Google Sheets...")

    # Wait for the queue to empty before exiting
    if wait_for_queue_to_empty(timeout=120):
        sheets_time = time.time() - sheets_start
        print(f"✅ All data successfully written to Google Sheets in {sheets_time:.2f} seconds")
    else:
        sheets_time = time.time() - sheets_start
        print(f"⚠️ Timed out waiting for data to be written to Google Sheets after {sheets_time:.2f} seconds")
        print("Some data may not have been written. Check the spreadsheet.")

    # Total execution time
    total_time = time.time() - start_time
    print(f"\n🕒 Total execution time: {total_time:.2f} seconds ({total_time / 60:.2f} minutes)")


if __name__ == "__main__":
    main()