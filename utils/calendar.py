from __future__ import print_function
import os.path
import datetime
import parsedatetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def add_event(summary: str, raw_date_text: str):
    cal = parsedatetime.Calendar()
    parsed_date, status = cal.parseDT(raw_date_text)

    if status == 0:
        raise ValueError(f"Could not parse date: '{raw_date_text}'")

    date_only = parsed_date.date()

    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'date': date_only.isoformat()},
        'end': {'date': (date_only + datetime.timedelta(days=1)).isoformat()},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('htmlLink')
