from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
import os
import logging
from django.core.exceptions import ObjectDoesNotExist

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env (optional, if not handled in settings.py)
if not os.getenv("DJANGO_SETTINGS_MODULE"):
    from dotenv import load_dotenv
    load_dotenv()

def send_email_via_sendgrid(visitor, first_name="", last_name=""):
    """
    Send an email notification via SendGrid for a new visitor registration.
    Handles visitor data flexibly, assuming name might be a single field.
    """
    # Handle visitor name flexibly (split if possible, otherwise use full name)
    visitor_name = visitor.name.strip()
    if " " in visitor_name:
        full_name = visitor_name
        first_name, last_name = visitor_name.split(" ", 1)
    else:
        full_name = visitor_name
        first_name, last_name = visitor_name, ""

    # Format phone number (assume it's stored as phone or phone_number)
    phone = getattr(visitor, 'phone', getattr(visitor, 'phone_number', 'N/A'))

    # Format address (use single address field)
    address = getattr(visitor, 'address', 'N/A')

    # Determine visit status and date
    visit_status = "Confirmed" if getattr(visitor, 'visit_request', 'no') == "yes" else "Not Confirmed"
    visit_date = getattr(visitor, 'visit_date', 'N/A')
    visit_date = visit_date.strftime("%Y-%m-%d") if visit_date and hasattr(visitor, 'visit_date') else "N/A"
    visit_request = "Yes" if getattr(visitor, 'visit_request', 'no') == "yes" else "No"
    sms_opt_in = "Yes" if getattr(visitor, 'sms_opt_in', False) else "No"

    # Construct email
    message = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL", "visit@sarasotagospeltemple.com"),
        to_emails=os.getenv("ADMIN_EMAIL", "visit@sarasotagospeltemple.com"),
        subject=f"New Visitor Registered: {visitor_name}",
        html_content=f"""
        <h3>New Visitor Registered at Sarasota Gospel Temple</h3>
        <p>👤 <strong>Name:</strong> {full_name}</p>
        <p>📞 <strong>Phone:</strong> {phone}</p>
        <p>🏠 <strong>Address:</strong> {address}</p>
        <p>📌 <strong>Visit Status:</strong> {visit_status}</p>
        <p>📅 <strong>Visit Date:</strong> {visit_date}</p>
        <p>🏡 <strong>Home Visit Requested:</strong> {visit_request}</p>
        <p>📲 <strong>SMS Opt-In:</strong> {sms_opt_in}</p>
        """
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        if response.status_code in [200, 202]:
            logger.info(f"✅ Notification email sent to {os.getenv('ADMIN_EMAIL', 'visit@sarasotagospeltemple.com')}")
        else:
            logger.error(f"❌ Email failed with status code: {response.status_code}, Body: {response.body}")
    except Exception as e:
        logger.error(f"❌ Error sending email via SendGrid: {str(e)}")

def add_visitor_to_clearstream(phone, first_name, last_name):
    """
    Adds a visitor to the Clearstream list without double opt-in.
    Handles phone number formatting and API connectivity issues.
    """
    url = "https://api.getclearstream.com/v1/subscribers"
    api_key = os.getenv("CLEARSTREAM_API_KEY")
    list_id = os.getenv("CLEARSTREAM_LIST_ID", "284041")  # Default to 284041 if not set

    if not api_key or not list_id:
        logger.error("❌ Clearstream API key or list ID not configured in environment variables.")
        return

    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # Format phone number (ensure it’s in E.164 format, e.g., +1XXX-XXX-XXXX)
    phone = phone.strip()
    if not phone.startswith('+'):
        phone = f"+1{phone}"  # Assume US number if no country code

    data = {
        "mobile_number": phone,
        "first": first_name.strip() if first_name else "Unknown",
        "last": last_name.strip() if last_name else "",
        "lists": [list_id],
        "double_optin": False
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"✅ Visitor {phone} added to Clearstream!")
    except requests.RequestException as e:
        logger.error(f"❌ Failed to add visitor to Clearstream: {str(e)}, Response: {getattr(response, 'text', 'No response')}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Clearstream API Response: {e.response.text}")

def send_followup_sms(phone):
    """
    Sends a welcome SMS to a visitor using Clearstream API.
    Includes detailed church information and opt-out instructions.
    """
    url = "https://api.getclearstream.com/v1/threads"
    api_key = os.getenv("CLEARSTREAM_API_KEY")

    if not api_key:
        logger.error("❌ Clearstream API key not configured in environment variables.")
        return

    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Format phone number (ensure it’s in E.164 format, e.g., +1XXX-XXX-XXXX)
    phone = phone.strip()
    if not phone.startswith('+'):
        phone = f"+1{phone}"  # Assume US number if no country code

    data = {
        "mobile_number": phone,
        "reply_header": "Sarasota Gospel Temple",
        "reply_body": (
            "Thank you for visiting Sarasota Gospel Temple! We hope to see you again soon.\n"
            "If you need a ride to church, call Hans Eveillard at 941-348-0418.\n"
            "Service times: Sunday 11 AM, Tuesday & Friday 7 PM.\n"
            "Pastor Edwige Achile - 941-592-4992.\n"
            "Church Address: 3621 Tallevast Rd, Sarasota FL 34243.\n"
            "Reply STOP to opt out."
        )
    }

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"✅ Follow-up SMS sent to {phone} and is now queued!")
    except requests.RequestException as e:
        logger.error(f"❌ Failed to send SMS: {str(e)}, Response: {getattr(response, 'text', 'No response')}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Clearstream SMS Response: {e.response.text}")