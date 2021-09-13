# Google Calendar Automation

Adding many meetings to Google Calendar is a pain, particularly if the meetings are in multiple timezones.

This script makes it easier by letting you create meetings from a simple text file.

# Setup

1. Install Python requriements with: pip install -r requirements.txt
2. Copy settings.py.example to settings.py
3. Copy meetings.txt.example to meetings.txt
4. Create a project in Google Developer Console and download the credentials by following steps 1 and 2 in https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/

Save the credentials as 'credentials.json', or the filename you've specified in settings.py.

# Modifying settings.py

Modify settings.py to set the primary calendar meetings will be added to, your default timezone, and whether dates like 02/03/2022 should default to date first (2 March 2022, instead of 3 February 2022).

To check your calendar names, run: python check_calendars.py

# Modifying meetings.txt

The meetings file is where you add all your meeting information.

Meetings inherit properties from the previous meeting, so if every meeting is 40 minutes you only need to specify that at the start. If the third meeting is 60 minutes instead, then for the 3rd meeting you'd add "Minutes: 60" and for the 4th meeting you'd add "Minutes: 40" again to change it back to 40.

Lines starting with # are ignored.

## Variables
You can set variables by starting a line with these keywords then a value:

**Timezone:**
The timezone of the meeting in the TZ format listed in https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
There are shortcuts for HK, Sydney, NYC, LA, SF, Tokyo, London, Paris, and Warsaw.

**Color:** or **Colour:**
The colour of the meeting in Google Calendar.
Valid values: Lavender, Sage, Grape, Flamingo, Banana, Tangerine, Peacock, Graphite, Bluberry, Basil, Tomato

**Pretitle:**
If set, this pretitle will be added to the beginning of meeting names.
This is useful for conference names and similar.

**Minutes:**
How long the meeting goes for in minutes.

**When:**
When the meeting is. Since meetings inherit date and time from the previous meeting, you can have a series of meetings like this and it will get the daet right:
When: 14/9/21 11:50am
When: 3pm
When: 5pm
When: 15/9/21 9am
When: 4pm

## Meeting text

Any text after **When:** that isn't a property or a comment is interpreted as the meeting text.
The first line of the meeting text will be interpreted as the title, but will be added to the description as well.

# Adding meetings

To add meetings: python add_meetings.py

# About

Created by <a href="https://www.thomasrice.com/">Thomas Rice</a> to ease the pain of adding lots of meetings in other timezones to Google Calendar.
