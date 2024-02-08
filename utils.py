from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime, os, pickle, pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

class CalendarTool:
#########crewai-0.1.32
    def list_events(service, start_date=None, end_date=None, summary=None, location=None, event_id = None):
        """
        List events from Google Calendar based on optional parameters.

        :param service: Authenticated Google Calendar service instance.
        :param start_date: Start date for events in YYYY-MM-DD format.
        :param end_date: End date for events in YYYY-MM-DD format.
        :param summary: Filter events containing this summary text.
        :param location: Filter events based on location.
        :return: List of events.
        """

        # Prepare the timeMin and timeMax in the correct format
        now = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).isoformat() # 'Z' indicates UTC time
        time_min = f"{start_date}T00:00:00+05:30" if start_date else None
        time_max = f"{end_date}T23:59:59+05:30" if end_date else None

        if event_id:
            event_id = event_id + "@google.com"

        # Retrieve events
        events_result = service.events().list(
            calendarId='primary',  # or a specific calendar ID if needed
            timeMin=time_min,
            timeMax=time_max,
            iCalUID = event_id,
            q=summary,  # Search query
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Filter events by location if provided
        if location:
            events = [event for event in events if 'location' in event and location in event['location']]

        return events


    def create_event(service, event_summary : str, event_location : str, start_time : str, end_time : str, email_reminder_minutes : int, popup_reminder_minutes : int) -> str:
        # Call the Calendar API 
        """Create a Calendar event based on the Args passed
        Args:
            service: Google Calendar API service instance
            event_summary: Summary of the event
            event_location: Location of the event
            start_time: Start time of the event in ISO 8601 format
            end_time: End time of the event in ISO 8601 format
            email_reminder_minutes: Email reminder minutes
            popup_reminder_minutes: Popup reminder minutes
        """

        now = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).isoformat() # 'Z' indicates UTC time
        event = {
        'summary': event_summary,
        'location': event_location,
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': email_reminder_minutes},
            {'method': 'popup', 'minutes': popup_reminder_minutes},
            ],
        },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        event_id = event.get('id')
        event = CalendarTool.list_events(service = service, event_id=event_id)
        return event[0]['iCalUID']

    def modify_event(service : str, event_id : str, event_summary : str, event_location : str, start_time : str, end_time : str, state : int) -> str:
        """
        Does not change the event_id, Modifies/updates an event in the Google Calendar
        Args:
            service: Google Calendar API service instance
            event_id: Event ID
            event_summary: Summary of the event
            event_location: Location of the event
            start_time: Start time of the event in ISO 8601 format
            end_time: End time of the event in ISO 8601 format
            state: 1 -> Modify event summary, 2 -> Modify event location, 3 -> Modify event start time, 4 -> Modify event end time
                12 -> Modify event summary and location, 13 -> Modify event summary and start time, 14 -> Modify event summary and end time
                23 -> Modify event location and start time, 24 -> Modify event location and end time, 34 -> Modify event start time and end time
                123 -> Modify event summary, location and start time, 124 -> Modify event summary, location and end time, 134 -> Modify event summary, start time and end time
                234 -> Modify event location, start time and end time, 1234 -> Modify event summary, location, start time and end time
        """
        event = service.events().get(calendarId='primary', eventId=event_id).execute()

        state_map = {
            1: {'summary': event_summary},
            2: {'location': event_location},
            3: {'start': {'dateTime': start_time}},
            4: {'end': {'dateTime': end_time}},
            12: {'summary': event_summary, 'location': event_location},
            13: {'summary': event_summary, 'start': {'dateTime': start_time}},
            14: {'summary': event_summary, 'end': {'dateTime': end_time}},
            23: {'location': event_location, 'start': {'dateTime': start_time}},
            24: {'location': event_location, 'end': {'dateTime': end_time}},
            34: {'start': {'dateTime': start_time}, 'end': {'dateTime': end_time}},
            123: {'summary': event_summary, 'location': event_location, 'start': {'dateTime': start_time}},
            124: {'summary': event_summary, 'location': event_location, 'end': {'dateTime': end_time}},
            134: {'summary': event_summary, 'start': {'dateTime': start_time}, 'end': {'dateTime': end_time}},
            234: {'location': event_location, 'start': {'dateTime': start_time}, 'end': {'dateTime': end_time}},
            1234: {'summary': event_summary, 'location': event_location, 'start': {'dateTime': start_time}, 'end': {'dateTime': end_time}},
        }

        if state in state_map:
            for key, value in state_map[state].items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        event[key][subkey] = subvalue
                else:
                    event[key] = value
        else:
            print("Invalid state")
            return

        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        print('Event updated: %s' % (updated_event.get('htmlLink')))
        return updated_event.get('id')

    def delete_event(service : str, event_id : str) -> None :
        """
        Deletes an event from the Google Calendar
        Args:
            service: Google Calendar API service instance
            event_id: Event ID
        """
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print('Deleted event with id: %s' % event_id)

    def get_busy_time(service : str, date : str) -> None:
        """
        Gets the busy time of the user on a particular date.
        Args:
            service: Google Calendar API service instance
            date: Date in datetime.date format
        """

        timeMin = datetime.datetime.combine(date, datetime.time.min).isoformat()+'+05:30'
        timeMax = datetime.datetime.combine(date, datetime.time.max).isoformat()+'+05:30'
        freebusy_request = {
            "timeMin": timeMin,
            "timeMax": timeMax,
            "timeZone": 'Asia/Calcutta',
            "items": [{"id": "primary"}]
        }
        freebusy_response = service.freebusy().query(body=freebusy_request).execute()
        for cal in freebusy_response['calendars']:
            for timePeriod in freebusy_response['calendars'][cal]['busy']:
                print("Busy from %s to %s" % (timePeriod['start'], timePeriod['end']))
            # for timePeriod in freebusy_response['calendars'][cal]['free']:
            #     print("Free from %s to %s" % (timePeriod['start'], timePeriod['end']))
    
## Test Case ##
# summary = 'N/A',
# start = '2024-01-29T11:00:00+05:30'
# end = '2024-01-29T12:00:00+05:30'
# timeZone = 'Asia/Kolkata'
# location = 'N/A'
# email_reminder_minutes = 24*60
# popup_reminder_minutes = 10
# event_id = create_event(service, summary, location, start, end, email_reminder_minutes, popup_reminder_minutes)
# print(event_id)
# event_id = modify_event(service, event_id, event_summary='Dentist appointment', event_location='Dentist clinic', start_time='2024-01-29T11:00:00+05:30', end_time='2024-01-29T13:00:00+05:30', state=34)
# print(event_id)