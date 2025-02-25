import requests
from config import ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, ZENDESK_API_TOKEN
import random

# ---------------------- SPOC MAPPING ----------------------
assignee_name = {
    "6447902570905": "Abdul Razzaq",
    "6447908017433": "Lakshya Sharma",
    "6447946529049": "Mridul Juyal",
    "6497689582873": "Madhusudhan Gaddam",
    "6648021980825": "Rohit",
    "6876511338777": "Skand Agarwal",
    "6965123224217": "Aakash Saxena",
    "6965365294617": "Deepak M",
    "6965376559769": "Dipak Patil",
    "6965393434137": "Dimple",
    "6965430230809": "Sasi Kumar Reddy",
    "6965470543513": "Sneha",
    "6965423981209": "Monica Patel",
    "6965473175321": "Muskan Kesharwani",
    "6965484602009": "Sudhanshu",
    "6965489843097": "Sai Gopal Rao",
    "6965512415897": "Vishnu",
    "6965534480665": "Subham Bansal",
    "7585128664857": "Support-Team",
    "6892773239321": "Sindhura",
    "6892621488537": "Nitin",
    "6965551948441": "Veeresh Biradar",
    "7909697776665": "Geetha N",
    "1900735342848": "Chirag",
    "6965480015769": "Sarthak",
    "33221615443225": "Nishant",
    "6965494416793": "Satyam",
    "6965575297433": "Vinita"
}

HEVO_AGENT_IDS = set(assignee_name.keys())

def fetch_tickets_for_spoc(spoc_id, start_date):
    """Fetch tickets assigned to a given SPOC and select 10 random tickets."""
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/search.json?query=assignee_id:{spoc_id} created>{start_date} type:ticket"
    auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(f"❌ Error fetching tickets for SPOC {spoc_id}: {response.text}")
        return []

    tickets = response.json().get("results", [])
    return random.sample(tickets, min(len(tickets), 5))  # Select 10 random tickets

def fetch_ticket_comments(ticket_id):
    """Fetch comments for a given ticket."""
    url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets/{ticket_id}/comments.json"
    auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(f"⚠️ Error fetching comments for Ticket ID {ticket_id}: {response.text}")
        return []

    return response.json().get("comments", [])