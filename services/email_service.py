"""
Email Service for fetching and processing emails
"""
from typing import List, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for fetching emails from Gmail API"""

    def __init__(self):
        self.client_id = settings.GMAIL_CLIENT_ID
        self.client_secret = settings.GMAIL_CLIENT_SECRET
        self.refresh_token = settings.GMAIL_REFRESH_TOKEN

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(
            settings.GMAIL_CLIENT_ID and
            settings.GMAIL_CLIENT_SECRET and
            settings.GMAIL_REFRESH_TOKEN
        )

    async def fetch_recent_emails(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Fetch recent unread emails from Gmail

        Args:
            max_results: Maximum number of emails to fetch

        Returns:
            List of email dictionaries with sender, subject, snippet, etc.
        """

        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_uri='https://oauth2.googleapis.com/token'
            )
            if creds.expired or not creds.valid:
                creds.refresh(Request())

            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results or settings.MAX_EMAILS_TO_FETCH
            ).execute()

            logger.info("Fetching emails from Gmail")
            logger.debug(f"Raw Gmail API response: {results}")

            messages = results.get('messages', [])
            if not messages:
                logger.info("No unread emails found.")
                return []

            # Fetch full details for each message
            emails = []
            for msg in messages:
                try:
                    msg_detail = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']
                    ).execute()
                    headers = msg_detail.get('payload', {}).get('headers', [])
                    email_data = {
                        'id': msg['id'],
                        'snippet': msg_detail.get('snippet', ''),
                        'from': next((h['value'] for h in headers if h['name'] == 'From'), None),
                        'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), None),
                        'date': next((h['value'] for h in headers if h['name'] == 'Date'), None),
                    }
                    emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error fetching email details for ID {msg['id']}: {str(e)}")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
