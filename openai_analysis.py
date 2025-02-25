import openai
import json
from config import OPENAI_API_KEY
from zendesk_api import HEVO_AGENT_IDS, assignee_name

openai.api_key = OPENAI_API_KEY

def analyze_ticket_with_openai(ticket_id, ticket_subject, ticket_description, comments):
    """Analyze a ticket using OpenAI and identify the first SPOC who commented."""
    first_support_agent_id = None
    for c in comments:
        if str(c.get("author_id")) in HEVO_AGENT_IDS:
            first_support_agent_id = str(c.get("author_id"))
            break

    spoc_name = assignee_name.get(first_support_agent_id, "Unknown")

    conversation_text = f"### Ticket ID: {ticket_id}\n### Subject: {ticket_subject}\n\n### Description:\n{ticket_description}\n\n"
    conversation_text += "### Comments:\n" + "\n".join([c["body"] for c in comments if "body" in c])

    prompt = f"""
            Analyze the following customer support conversation and provide an assessment based on the following parameters. 
            Each response should be tailored to the specific ticket context. DO NOT include explanations, extra text, or Markdown code blocks.

            {conversation_text}

            ### **Assessment Criteria**
            Evaluate the conversation in the following categories, providing a score between **1-5** (where 1 is low and 5 is excellent, and "Not Applicable" when the certain parameter is not applicable. For instance not all the tickets are escalated. If the ticket is escalatd, you will have words like "escalate". Onlyy then assess it against that parameter). 
            If escalation isn't mentioned in the ticket, put "Not Applicable" for that parameter.

            #### **1. Communication**
            - **Politeness & Professionalism:** Was the support team courteous and professional?
            - **Clarity of Responses:** Were the responses clear and easy to understand?
            - **Timeliness of Updates:** How quickly did the team provide updates?
            - **Proactive Communication:** Did the team proactively reach out or only respond when prompted?
            - **Escalation Handling:** How effectively was the issue escalated and addressed (if applicable)?

            #### **2. Technical Knowledge**
            - **Asking the Right Questions:** Did the support team ask relevant diagnostic questions?
            - **Finding the Root Cause Timely:** How efficiently was the root cause identified?
            - **Product Understanding:** Did the team understand technical constraints with respect to the product (if applicable)?
            - **Effective Troubleshooting Steps:** Were troubleshooting steps well thought out?
            - **Workaround Provided:** Was a temporary workaround or alternative solution suggested?

            #### **3. Empathy**
            - **Acknowledging Customer Impact:** Did the team recognize the business impact of the issue?
            - **Apologies for Delays:** Were delays acknowledged with sincere apologies?
            - **Prioritization of Urgent Issues:** How quickly was the issue escalated based on urgency?
            - **Understanding Customer Frustration:** Did the team recognize and address the customer's frustration?

            ### **Expected Output Format**
            {{
                "Ticket ID": {ticket_id},
                "Communication": {{
                    "Politeness & Professionalism": 4,
                    "Clarity of Responses": 5,
                    "Timeliness of Updates": 3,
                    "Proactive Communication": 2,
                    "Escalation Handling": 5
                }},
                "Technical Knowledge": {{
                    "Asking the Right Questions": 4,
                    "Finding the Root Cause Timely": 4,
                    "Product Understanding": 3,
                    "Effective Troubleshooting Steps": 4,
                    "Workaround Provided": 5
                }},
                "Empathy": {{
                    "Acknowledging Customer Impact": 5,
                    "Apologies for Delays": 4,
                    "Prioritization of Urgent Issues": 5,
                    "Understanding Customer Frustration": 4
                }},
                "Final Sentiment": "Positive",
                "Areas of Improvement": "Improve proactive communication"
            }}
            DO NOT INCLUDE MARKDOWN FORMATTING (```json ... ```) OR EXTRA TEXT.
    """
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
    except:
        return {"error": "Failed to process ticket", "SPOC": spoc_name}
