"""
Calendar Service for fetching calendar events
"""
from typing import List, Dict, Any
from config import settings
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CalendarService:
    """Service for fetching events from Google Calendar"""

    def __init__(self):
        self.credentials = settings.GOOGLE_CALENDAR_CREDENTIALS

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(settings.GOOGLE_CALENDAR_CREDENTIALS)

    async def fetch_today_events(self) -> List[Dict[str, Any]]:
        """
        Fetch calendar events for the next 7 days, with a flag for today.

        Returns:
            List of event dictionaries with time, title, description, etc., and is_today flag.
        """
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            from datetime import datetime, timedelta, timezone

            creds = Credentials(
                token=None,
                refresh_token=self.credentials,
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET,
                token_uri='https://oauth2.googleapis.com/token'
            )
            if creds.expired or not creds.valid:
                creds.refresh(Request())
            service = build('calendar', 'v3', credentials=creds)

            now = datetime.utcnow().replace(tzinfo=timezone.utc)
            week_later = (now + timedelta(days=7)).isoformat().replace('+00:00', 'Z')
            now_iso = now.isoformat().replace('+00:00', 'Z')

            events_result = service.events().list(
                calendarId='primary',
                timeMin=now_iso,
                timeMax=week_later,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            logger.info("Fetching calendar events for next 7 days")
            logger.debug(f"Raw Calendar API response: {events_result}")

            events = events_result.get('items', [])
            if not events:
                logger.info("No calendar events found for next 7 days.")
                return []

            # Helper to check if event is today
            def is_event_today(event_start_str):
                try:
                    # Handles both dateTime and date (all-day)
                    if 'T' in event_start_str:
                        event_dt = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                    else:
                        event_dt = datetime.strptime(event_start_str, '%Y-%m-%d')
                    today_utc = now.date()
                    return event_dt.date() == today_utc
                except Exception:
                    return False

            event_list = []
            for event in events:
                start_str = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                end_str = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
                event_list.append({
                    'id': event.get('id'),
                    'summary': event.get('summary'),
                    'description': event.get('description'),
                    'location': event.get('location'),
                    'start': start_str,
                    'end': end_str,
                    'is_today': is_event_today(start_str)
                })
            return event_list

        except Exception as e:
            logger.error(f"Error fetching calendar events: {str(e)}")
            return []
