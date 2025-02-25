import openai
import json
from config import OPENAI_API_KEY
from zendesk_api import HEVO_AGENT_IDS, assignee_name
from openai_prompt import generate_ticket_analysis_prompt, generate_ticket_summary_prompt

openai.api_key = OPENAI_API_KEY

def analyze_ticket_with_openai(ticket_id, ticket_subject, ticket_description, comments):
    """Analyze a Zendesk ticket using OpenAI and generate both analysis and summary."""
    first_support_agent_id = None
    for c in comments:
        if str(c.get("author_id")) in HEVO_AGENT_IDS:
            first_support_agent_id = str(c.get("author_id"))
            break

    spoc_name = assignee_name.get(first_support_agent_id, "Unknown")

    # Generate the analysis prompt
    analysis_prompt = generate_ticket_analysis_prompt(ticket_id, ticket_subject, ticket_description, comments)

    try:
        # Send OpenAI request for assessment
        response_analysis = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a Technical Support Engineer at Hevo. Your job is to analyze customer support tickets and ensure responses align with Hevo's customer support standards. Always return responses in strict JSON format."},
                      {"role": "user", "content": analysis_prompt}],
            max_tokens=1000,
            temperature=0.2
        )

        result_text = response_analysis["choices"][0]["message"]["content"].strip()
        analysis_json = json.loads(result_text)
        analysis_json["Ticket ID"] = ticket_id
        analysis_json["SPOC"] = spoc_name

    except Exception as e:
        print(f"❌ OpenAI API Error (Analysis): {e}")
        return {"error": "Failed to process ticket analysis", "SPOC": spoc_name}

    # Generate the summary prompt
    summary_prompt = generate_ticket_summary_prompt(ticket_id, ticket_subject, ticket_description, comments)

    try:
        # Send OpenAI request for summary
        response_summary = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a technical support summarization assistant. Summarize the ticket interactions clearly in 2-3 sentences."},
                      {"role": "user", "content": summary_prompt}],
            max_tokens=1000,
            temperature=0.2
        )

        summary_text = response_summary["choices"][0]["message"]["content"].strip()
        analysis_json["Summary"] = summary_text

    except Exception as e:
        print(f"❌ OpenAI API Error (Summary): {e}")
        analysis_json["Summary"] = "Summary not available due to API error."

    return analysis_json
