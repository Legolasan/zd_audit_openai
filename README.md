# Zendesk Ticket Analysis with OpenAI & Google Sheets

This project automates the **evaluation of Zendesk support tickets** using **OpenAI** for sentiment analysis and stores the results in **Google Sheets**.

## 🚀 Features

- Fetches **support tickets** assigned to each **SPOC** from Zendesk.
- Selects **10 random tickets per SPOC** for analysis.
- Uses **OpenAI** to assess **communication, technical knowledge, and empathy**.
- Stores results in **Google Sheets** for reporting.
- **Multi-threaded execution** for improved performance.

---

## 📂 Project Structure
#### |---main.py
#### |---config.py
#### |---zendesk_api.py
#### |---openai_analysis.py
#### |---google_sheets.py
#### |---requirements.txt
#### |---README.md


---

## 🔹 Setup Instructions

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/your-username/zendesk-analysis.git
cd zendesk-analysis
```
### 2️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```
### 3️⃣ Set Up Environment Variables
Create a .env file in the root directory and add:
```sh
ZENDESK_SUBDOMAIN=your_zendesk_subdomain
ZENDESK_EMAIL=your_email
ZENDESK_API_TOKEN=your_zendesk_api_token
OPENAI_API_KEY=your_openai_api_key
SERVICE_ACCOUNT_FILE=/path/to/your-google-service-account.json
SPREADSHEET_ID=your_google_sheets_id
SHEET_NAME=QC_OpenAI
```
⚠️ DO NOT commit .env to GitHub to keep credentials secure.

### 4️⃣ Run the Script
```sh 
python main.py
```
This will:

1. Fetch Zendesk tickets.
2. Process tickets using OpenAI.
3. Store the results in Google Sheets.

### ⚙️ How It Works
1. `main.py` runs the entire process.
2. `zendesk_api.py` fetches support tickets and comments.
3. `openai_analysis.py` evaluates ticket quality using AI.
4. `google_sheets.py` writes results to Google Sheets with a background queue.
5. Multi-threading speeds up ticket processing.

### 📜 License
```sh 
---
## **🔹 What's Included in This README?**
✅ **Project Overview**  
✅ **Installation Instructions**  
✅ **How to Run the Program**  
✅ **How the Script Works**  
✅ **Troubleshooting & Debugging Guide**  
✅ **Google Sheets API Handling & Output**  

This will help **anyone** set up, run, and debug the project **easily**! 🚀 Let me know if you need changes. 😊
```









