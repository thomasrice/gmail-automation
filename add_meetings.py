import datetime
import dateutil.parser
import pickle
import os.path
import copy
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import settings

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendar(object):
    def __init__(self):
        self.service = self.connect()

    def connect(self):
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
                    settings.CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service

    def list_calendars(self):
        # Call the Calendar API
        print('Getting list of calendars')
        calendars_result = self.service.calendarList().list().execute()

        calendars = calendars_result.get('items', [])

        if not calendars:
            print('No calendars found.')
        for calendar in calendars:
            summary = calendar['summary']
            id = calendar['id']
            primary = "Primary" if calendar.get('primary') else ""
            print("%s\t%s\t%s" % (summary, id, primary))


class Meeting(object):

    def __init__(self):
        self.timezone = settings.DEFAULT_TIMEZONE
        self.pretitle = ''
        self.summary = ''
        self.description = ''
        self.minutes = 30
        self.colour = 9
        self.date = datetime.datetime(2022, 12, 31)
        self.time = datetime.time(8, 0)
        self.calendar = None

    def cleanup_description(self):
        self.description = self.description.rstrip()

    def add_event(self):
        """
        Add event to calendar
        """
        if not self.calendar:
            return False

        self.cleanup_description()
        datetime_obj = datetime.datetime.combine(self.date, self.time)
        start = datetime_obj.isoformat()
        end = (datetime_obj + datetime.timedelta(minutes=self.minutes)).isoformat()

        # If Summary is missing, use first line of description that isn't blank
        summary = self.summary.strip()
        if not len(summary):
            lines = self.description.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 0:
                    summary = line
                    break

        if self.pretitle:
            summary = '%s %s' % (self.pretitle, summary)

        body = {
            "summary": summary,
            "description": self.description,
            "start": {"dateTime": start, "timeZone": self.timezone},
            "end": {"dateTime": end, "timeZone": self.timezone},
        }

        if self.colour:
            body['colorId'] = self.colour

        event_result = self.calendar.service.events().insert(calendarId=settings.CALENDAR,
                                                             body=body
                                                             ).execute()

        print("--[NEW EVENT CREATED]--------------------")
        print("ID: ", event_result['id'])
        print("Summary: ", event_result['summary'])
        print("Starts at: ", event_result['start']['dateTime'])
        print("Ends at: ", event_result['end']['dateTime'])


class Parser(object):
    def __init__(self):
        self.meetings = []
        self.working_meeting = None  # The meeting we're currently working on
        self.valid_properties = ['timezone', 'colour', 'color', 'pretitle', 'minutes', 'when']
        self.valid_colours = {
            'lavender': 1,
            'sage': 2,
            'grape': 3,
            'flamingo': 4,
            'banana': 5,
            'tangerine': 6,
            'peacock': 7,
            'graphite': 8,
            'blueberry': 9,
            'basil': 10,
            'tomato': 11
        }
        self.timezone_shortcuts = {
            'hk': 'Asia/Hong_Kong',
            'sydney': 'Australia/Sydney',
            'nyc': 'America/New_York',
            'sf': 'America/Los_Angeles',
            'la': 'America/Los_Angeles',
            'tokyo': 'Asia/Tokyo',
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'warsaw': 'Europe/Warsaw'
        }
        self.line_number = 0
        self.first_meeting = True

    def parse(self):
        """
        Parse the Meetings.txt file and return a list of Meetings or -1 if it fails
        """
        self.setup_first_meeting()

        f = open("meetings.txt", "r", encoding="utf8")
        lines = f.read().split('\n')
        for line in lines:
            self.process_line(line)

        # Add final meeting
        self.meetings.append(self.working_meeting)
        for meeting in self.meetings:
            meeting.add_event()

    def setup_first_meeting(self):
        calendar = GoogleCalendar()
        meeting = Meeting()
        meeting.calendar = calendar
        self.working_meeting = meeting

    def process_line(self, line):
        self.line_number += 1

        # Blank line before description has started
        if len(line) == 0 and self.working_meeting.description == '':
            return

        # Comment
        if line[0:1] == '#':
            return

        # When alias
        if line[0:1] == '@':
            line = "When: " + line[1:]

        split_parts = line.split(":", 1)
        if len(split_parts) == 2 and split_parts[0].lower() in self.valid_properties:
            prop = split_parts[0].lower()
            value = split_parts[1].strip()

            if prop == 'color':
                prop = 'colour'

            if prop == 'when':
                if self.first_meeting:
                    self.first_meeting = False
                else:
                    self.meetings.append(self.working_meeting)
                    new_meeting = copy.copy(self.working_meeting)
                    new_meeting.summary = ''
                    new_meeting.description = ''
                    self.working_meeting = new_meeting

            self.update_property(prop, value)
            return

        if line.rstrip() == '!NEW' and 0:
            self.meetings.append(self.working_meeting)
            new_meeting = copy.copy(self.working_meeting)
            new_meeting.summary = ''
            new_meeting.description = ''
            self.working_meeting = new_meeting
            return

        # If we're here, add to description
        self.working_meeting.description = self.working_meeting.description + line + '\n'
        return

    def update_property(self, prop, value):
        error = False

        if prop == 'timezone':
            if value.lower() in self.timezone_shortcuts.keys():
                # Check for shortcuts
                self.working_meeting.timezone = self.timezone_shortcuts[value.lower()]
            else:
                self.working_meeting.timezone = value
            return

        if prop == 'colour':
            if value.lower() in self.valid_colours.keys():
                self.working_meeting.colour = self.valid_colours[value.lower()]
            return

        if prop == 'pretitle':
            self.working_meeting.pretitle = value

        if prop == 'minutes':
            self.working_meeting.minutes = int(value)
            return

        if prop == 'when':
            if ' ' in value:
                # Date + Time
                try:
                    datetime = dateutil.parser.parse(value, dayfirst=settings.DAYFIRST)
                    self.working_meeting.date = datetime.date()
                    self.working_meeting.time = datetime.time()
                except:
                    error = True
            else:
                # Time only
                try:
                    self.working_meeting.time = dateutil.parser.parse(value, dayfirst=settings.DAYFIRST).time()
                except:
                    error = True
            if error:
                print("Line %i error: Couldn't process this WHEN value: %s" % (self.line_number, value))
            return


if __name__ == '__main__':
    parser = Parser()
    parser.parse()
