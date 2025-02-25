import openai
import json
from config import OPENAI_API_KEY
from zendesk_api import HEVO_AGENT_IDS, assignee_name
from openai_prompt import generate_ticket_analysis_prompt  # Importing prompt function

openai.api_key = OPENAI_API_KEY

def analyze_ticket_with_openai(ticket_id, ticket_subject, ticket_description, comments):
    """Analyze a ticket using OpenAI and identify the first SPOC who commented."""
    first_support_agent_id = None
    for c in comments:
        if str(c.get("author_id")) in HEVO_AGENT_IDS:
            first_support_agent_id = str(c.get("author_id"))
            break

    spoc_name = assignee_name.get(first_support_agent_id, "Unknown")

    # Get the formatted prompt from openai_prompts.py
    prompt = generate_ticket_analysis_prompt(ticket_id, ticket_subject, ticket_description, comments)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a Technical Support Engineer at Hevo. Your job is to analyze customer support tickets and ensure responses align with Hevo's customer support standards. Always return responses in strict JSON format."},
                      {"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.2
        )

        result_text = response["choices"][0]["message"]["content"].strip()
        analysis_json = json.loads(result_text)
        analysis_json["Ticket ID"] = ticket_id
        analysis_json["SPOC"] = spoc_name
        return analysis_json
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return {"error": "Failed to process ticket", "SPOC": spoc_name}
