import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                return None
        
    service = build('calendar', 'v3', credentials=creds)
    return service

def schedule_appointment_event(user_email=None, appointment_time=None):
    """
    Schedules an appointment on Google Calendar.
    """
    service = get_calendar_service()
    if not service:
        return False, "Google Credentials not found."

    # Use provided time or fallback to tomorrow at 10 AM
    if appointment_time:
        start_time = appointment_time
    else:
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Default duration 1 hour
    end_time = start_time + datetime.timedelta(hours=1)
    
    event = {
        'summary': 'WellNest Counseling Appointment',
        'description': 'Automated appointment scheduled via WellNest Platform.',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    if user_email:
        event['attendees'] = [{'email': user_email}]

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return True, event.get('htmlLink')
    except Exception as e:
        return False, str(e)
