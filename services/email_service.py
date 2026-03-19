"""
Email Service for fetching and processing emails with full body extraction
"""
from typing import List, Dict, Any
from config import settings
import logging
import base64
import re
from html.parser import HTMLParser

logger = logging.getLogger(__name__)

# Max characters of body text to keep per email to avoid overloading Claude
MAX_BODY_CHARS = 3000


class _HTMLTextExtractor(HTMLParser):
    """Simple HTML to plain-text converter."""

    def __init__(self):
        super().__init__()
        self._text_parts: list = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False
        if tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4"):
            self._text_parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._text_parts.append(data)

    def get_text(self) -> str:
        raw = "".join(self._text_parts)
        # Collapse whitespace but keep newlines
        lines = [" ".join(line.split()) for line in raw.splitlines()]
        return "\n".join(line for line in lines if line).strip()


def _html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    try:
        parser.feed(html)
        return parser.get_text()
    except Exception:
        # Fallback: strip tags with regex
        return re.sub(r"<[^>]+>", " ", html)


def _decode_body(payload: dict) -> str:
    """
    Recursively walk the Gmail message payload and extract the best
    plain-text body.  Prefers text/plain, falls back to text/html.
    """
    plain_parts = []
    html_parts = []

    def _walk(part: dict):
        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data", "")

        if data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            if mime == "text/plain":
                plain_parts.append(decoded)
            elif mime == "text/html":
                html_parts.append(decoded)

        for child in part.get("parts", []):
            _walk(child)

    _walk(payload)

    if plain_parts:
        return "\n".join(plain_parts)
    if html_parts:
        return _html_to_text("\n".join(html_parts))
    return ""


class EmailService:
    """Service for fetching emails from Gmail API with full body content"""

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
        Fetch recent unread emails from Gmail with full body content.

        Args:
            max_results: Maximum number of emails to fetch

        Returns:
            List of email dicts with sender, subject, date, snippet, and body.
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

            # Fetch unread inbox messages
            results = service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results or settings.MAX_EMAILS_TO_FETCH
            ).execute()

            logger.info("Fetching emails from Gmail")

            messages = results.get('messages', [])
            if not messages:
                logger.info("No unread emails found.")
                return []

            emails = []
            for msg in messages:
                try:
                    # Fetch full message (includes body)
                    msg_detail = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()

                    headers = msg_detail.get('payload', {}).get('headers', [])
                    header_map = {h['name']: h['value'] for h in headers}

                    # Extract and truncate body
                    body = _decode_body(msg_detail.get('payload', {}))
                    if len(body) > MAX_BODY_CHARS:
                        body = body[:MAX_BODY_CHARS] + "\n[...truncated]"

                    email_data = {
                        'id': msg['id'],
                        'from': header_map.get('From', ''),
                        'to': header_map.get('To', ''),
                        'subject': header_map.get('Subject', ''),
                        'date': header_map.get('Date', ''),
                        'snippet': msg_detail.get('snippet', ''),
                        'body': body,
                    }
                    emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error fetching email {msg['id']}: {str(e)}")

            logger.info(f"Fetched {len(emails)} emails with body content")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
