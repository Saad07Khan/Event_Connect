import os
import re
import traceback
from datetime import datetime
from typing import Dict, Optional, Tuple

import schedule
import time
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# MongoDB connection
MONGO_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGO_URI)
db = client.campus_connect
events_collection = db.events

def get_gmail_service():
    """Get Gmail API service."""
    creds = None

    # Load credentials from token.json if it exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If credentials are not valid, refresh or get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("\n==== GMAIL OAUTH AUTHENTICATION ====\n")
            print("A browser window will open for you to authenticate with Google.")
            print("Please sign in and grant the requested permissions.")

            # Create the flow using desktop app credentials
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)

            # For desktop apps, this will open a browser and use a localhost server
            # with an automatically assigned free port
            creds = flow.run_local_server(
                port=0,  # Use port 0 to let the OS choose an available port
                open_browser=True,
                authorization_prompt_message="Please visit this URL to authorize the application: {url}"
            )
            print("\nAuthentication successful!")

        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date from string using multiple formats."""
    date_formats = [
        '%d/%m/%Y',    # DD/MM/YYYY
        '%d-%m-%Y',    # DD-MM-YYYY
        '%m/%d/%Y',    # MM/DD/YYYY
        '%m-%d-%Y',    # MM-DD-YYYY
        '%Y-%m-%d',    # YYYY-MM-DD (ISO)
        '%d %B %Y',    # 01 January 2023
        '%d %b %Y',    # 01 Jan 2023
        '%B %d, %Y',   # January 01, 2023
        '%b %d, %Y',   # Jan 01, 2023
        '%d %b, %Y',   # 01 Jan, 2023
        '%Y/%m/%d',    # YYYY/MM/DD
    ]

    # Clean up the date string
    cleaned_date = re.sub(r'(st|nd|rd|th|,)', '', date_str).strip()

    for fmt in date_formats:
        try:
            return datetime.strptime(cleaned_date, fmt)
        except ValueError:
            continue

    return None

def extract_date_time(text: str) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Extract date and time from text.
    Returns tuple: (date_str, time_str, used_default_date)
    """
    # Common date patterns
    date_patterns = [
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',  # DD Month YYYY
        r'(?:on|date)\s*[:\-]?\s*(\d{1,2}\s*(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+\d{2,4})?)',  # on: 5th June 2025
        r'(?:on|date)\s*[:\-]?\s*(\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?)',  # on: 5/6/2025
        r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD (ISO format)
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{2,4})?)'  # Month DD(st/nd/rd/th), YYYY
    ]

    # Common time patterns
    time_patterns = [
        r'(\d{1,2}:\d{2}(?:\s*[AaPp][Mm])?)',  # HH:MM AM/PM
        r'(\d{1,2}(?:\s*[AaPp][Mm]))',  # HH AM/PM
        r'(?:at|time)\s*[:\-]?\s*(\d{1,2}(?::\d{2})?\s*(?:[AaPp][Mm])?)',  # at: 5:30PM or at: 5 PM
        r'(\d{1,2}\s*(?:to|-|–|—)\s*\d{1,2}\s*[AaPp][Mm])'  # 5-7PM or 5 to 7 PM
    ]

    date = None
    time_str = None
    used_default_date = False

    # Try to find date
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date = match.group(1)
            print(f"Found date: {date}")
            break

    # If date not found, use today's date and set flag
    if not date:
        today = datetime.now().strftime('%d/%m/%Y')
        print(f"No date found, using today's date: {today}")
        date = today
        used_default_date = True

    # Try to find time
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            time_str = match.group(1)
            print(f"Found time: {time_str}")
            break

    # If time not found, use a default time
    if not time_str:
        default_time = "12:00 PM"
        print(f"No time found, using default time: {default_time}")
        time_str = default_time

    return date, time_str, used_default_date

def extract_venue(text: str) -> Optional[str]:
    """Extract venue from text."""
    # Common venue indicators
    venue_indicators = [
        r'venue[:\s]+([^.\n]+)',
        r'location[:\s]+([^.\n]+)',
        r'at[:\s]+([^.\n]+)',
        r'in[:\s]+([^.\n]+)',
        r'place[:\s]+([^.\n]+)',
        r'hall[:\s]+([^.\n]+)',
        r'auditorium[:\s]+([^.\n]+)',
        r'room[:\s]+([^.\n]+)',
        r'building[:\s]+([^.\n]+)',
        r'held\s+at\s+([^.\n]+)',
        r'conducted\s+at\s+([^.\n]+)',
        r'organized\s+at\s+([^.\n]+)',
    ]

    for pattern in venue_indicators:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            venue = match.group(1).strip()
            print(f"Found venue: {venue}")
            return venue

    # If no venue found, use a default venue
    default_venue = "Campus"
    print(f"No venue found, using default venue: {default_venue}")
    return default_venue

def extract_registration_link(text: str) -> Optional[str]:
    """Extract registration link from text."""
    # Common registration link patterns
    link_patterns = [
        r'(?:register|registration|sign up|signup|apply|join|attend|rsvp)[:\s]+(https?://[^\s]+)',
        r'(?:click here|register here|link|url|form)[:\s]+(https?://[^\s]+)',
        r'(?:register|registration|sign up|signup)[^\n.]*?\s+(https?://[^\s]+)',
        r'(https?://forms\.(?:gle|office|google)\.com/[^\s]+)',
        r'(https?://docs\.google\.com/forms/[^\s]+)'
    ]

    # First try patterns
    for pattern in link_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            link = match.group(1).strip()
            # Clean up the link by removing any trailing punctuation or words
            link = re.sub(r'[.,;:!?]+$', '', link)
            link = re.sub(r'\s+(?:Registration|Register|Here|Click|Link)$', '', link, flags=re.IGNORECASE)
            print(f"Found registration link: {link}")
            return link

    # If no patterns match, try to find any URL
    urls = re.findall(r'(https?://[^\s]+)', text)
    if urls:
        link = urls[0].strip()
        # Clean up the link
        link = re.sub(r'[.,;:!?]+$', '', link)
        link = re.sub(r'\s+(?:Registration|Register|Here|Click|Link)$', '', link, flags=re.IGNORECASE)
        print(f"Found URL as registration link: {link}")
        return link

    print("No registration link found")
    return ""

def is_future_event(event_date: str) -> bool:
    """Check if event date is in the future."""
    try:
        # Parse the event date
        event_dt = parse_date(event_date)
        if not event_dt:
            print(f"Could not parse date: {event_date}")
            return False

        # Compare with current date
        current_date = datetime.now().date()
        return event_dt.date() >= current_date

    except Exception as e:
        print(f"Error checking event date: {str(e)}")
        return False

def clean_subject(subject: str) -> str:
    """
    Remove prefixes like "Re:", "Fwd:", etc., from email subjects.
    """
    # Strip common reply/forward prefixes
    cleaned = re.sub(r'^(?:\s*(?:RE|FWD)\s*:\s*)+', '', subject, flags=re.IGNORECASE).strip()
    return cleaned

def generate_summary(text: str) -> str:
    """Generate a concise summary of the event description using OpenAI."""
    try:
        print("\nGenerating summary for text...")
        truncated_text = text[:3000]  # Limit to 3000 characters
        print(f"Text length: {len(truncated_text)} characters")
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes event descriptions. Create a concise, informative summary in 2-3 sentences."},
                {"role": "user", "content": f"Please summarize this event description: {truncated_text}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content.strip()
        print(f"Generated summary: {summary}")
        return summary
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return text[:200] + "..."  # Fallback to first 200 characters if summary fails

def parse_email_content(message) -> Optional[Dict]:
    """Parse email content and extract event information."""
    try:
        # Get email body
        if 'parts' in message['payload']:
            parts = message['payload']['parts']
            body = ''
            for part in parts:
                if part['mimeType'] == 'text/html':
                    body = part['body'].get('data', '')
                    break
        else:
            body = message['payload']['body'].get('data', '')

        if not body:
            return None

        # Decode and parse HTML
        import base64
        from urllib.parse import unquote
        body = base64.urlsafe_b64decode(body).decode('utf-8')
        soup = BeautifulSoup(body, 'html.parser')
        text = soup.get_text()

        # Find subject in headers
        subject = None
        for header in message['payload']['headers']:
            if header['name'].lower() == 'subject':
                subject = header['value']
                break

        if not subject:
            print("Email has no subject, skipping...")
            return None

        # Skip emails that have "pre placement" in subject or body
        if 'pre placement' in subject.lower() or 'pre placement' in text.lower():
            print(f"Skipping email due to 'pre placement' mention: {subject}")
            return None

        # Clean subject by removing "Re:", "Fwd:" prefixes
        cleaned_subject = clean_subject(subject)
        print(f"Processing email with subject: {cleaned_subject}")

        # Skip if subject doesn't contain event-related keywords
        keywords = ['event', 'register', 'seminar', 'workshop', 'talk', 'conference', 'meetup', 'hackathon', 'fest']
        if not any(keyword in cleaned_subject.lower() for keyword in keywords):
            print(f"Subject doesn't contain event keywords, skipping: {cleaned_subject}")
            return None

        # Extract date and time from email body text
        date_str, time_str, used_default_date = extract_date_time(text)

        # Only check date if we didn't use the default (meaning a date was found in the email)
        if not used_default_date:
            if not is_future_event(date_str):
                print(f"Event date has passed: {date_str}, skipping...")
                return None
        else:
            print("Using default date - skipping date check")

        venue = extract_venue(text)
        registration_link = extract_registration_link(text)

        # Print debug info
        print(f"Extracted event details:\n  Date: {date_str}\n  Time: {time_str}\n  Venue: {venue}\n  Registration: {registration_link or 'None'}")

        # Format the date properly for storage
        try:
            event_dt = parse_date(date_str)
            if event_dt:
                formatted_date = event_dt.date().isoformat()
                print(f"Formatted date: {formatted_date}")
            else:
                formatted_date = date_str
                print(f"Could not parse date, storing as string: {date_str}")
        except Exception as e:
            print(f"Error formatting date '{date_str}': {str(e)}")
            formatted_date = date_str  # Store original string

        # Create clean description
        description = text[:1000].strip()  # Take more text for better description
        
        # Generate AI summary
        summary = generate_summary(description)
        print(f"Generated summary: {summary}")

        # Prepare the event object
        event_data = {
            'title': cleaned_subject,
            'description': description,
            'summary': summary,
            'date': formatted_date,
            'time': time_str,
            'venue': venue,
            'registrationLink': registration_link or '',
            'createdAt': datetime.now().isoformat(),
            'attendees': [],
            'usedDefaultDate': used_default_date  # Add flag for default date
        }

        print(f"Created event object with title: {cleaned_subject}")
        return event_data

    except Exception as e:
        print(f"Error parsing email: {str(e)}")
        return None

def process_emails(service=None):
    """Process emails and store event information in MongoDB."""
    try:
        # Get Gmail service if not provided
        if service is None:
            service = get_gmail_service()

        print("\n===== SEARCHING FOR EVENT EMAILS =====\n")

        # Search for emails with event-related keywords (expanded query)
        query = 'subject:(event OR register OR seminar OR workshop OR conference OR meetup OR hackathon OR talk OR fest OR competition)'
        print(f"Searching for emails with query: {query}")

        results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No emails found matching the search criteria.")
            print("\nTroubleshooting: Try these steps:")
            print("1. Check if you have event-related emails in your inbox")
            print("2. Try running the scraper with a different email account that has event emails")
            print("3. Manually add an event to the database for testing the web app")
            return

        print(f"Found {len(messages)} emails matching search criteria")
        events_found = 0

        for message in messages:
            try:
                print(f"\n----- Processing email ID: {message['id']} -----")
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                event_data = parse_email_content(msg)

                if event_data:
                    # Check if event already exists
                    existing_event = events_collection.find_one({
                        'title': event_data['title'],
                        'date': event_data['date']
                    })

                    if not existing_event:
                        result = events_collection.insert_one(event_data)
                        print(f"✅ Added new event: {event_data['title']} (ID: {result.inserted_id})")
                        events_found += 1
                    else:
                        print(f"⚠️ Event already exists: {event_data['title']}")
                else:
                    print("❌ Could not extract event data from this email")
            except Exception as email_error:
                print(f"Error processing individual email: {str(email_error)}")
                continue  # Continue with next email

        print(f"\n===== EMAIL PROCESSING COMPLETED =====")
        print(f"Total emails processed: {len(messages)}")
        print(f"New events added to database: {events_found}")
        print(f"\nDatabase collection: {events_collection.name}")
        print(f"Current event count in database: {events_collection.count_documents({})}")

        # List some events for verification
        print("\nRecent events in database:")
        for event in events_collection.find().sort('createdAt', -1).limit(5):
            print(f"  - {event.get('title')} ({event.get('date')})")

    except Exception as e:
        print(f"\n❌ ERROR PROCESSING EMAILS: {str(e)}")
        print("Traceback:", traceback.format_exc())

def main():
    """Main function to run the email scraper."""
    print("Starting email scraper...")

    # Initialize Gmail service once
    gmail_service = get_gmail_service()

    # Run immediately on startup
    process_emails(gmail_service)

    # Schedule to run every 6 hours with the same service instance
    schedule.every(6).hours.do(process_emails, gmail_service)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()
