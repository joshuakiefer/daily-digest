"""
Reclaim.ai Service for fetching calendar events and tasks
"""
from typing import List, Dict, Any
from config import settings
import logging
import httpx
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

RECLAIM_BASE_URL = "https://api.app.reclaim.ai"

# Time chunks in the Reclaim API are 15-minute increments
MINUTES_PER_CHUNK = 15


class ReclaimService:
    """Service for fetching calendar events and tasks from Reclaim.ai"""

    def __init__(self):
        self.api_key = settings.RECLAIM_API_KEY
        self.base_url = RECLAIM_BASE_URL

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(settings.RECLAIM_API_KEY)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    async def fetch_today_events(self) -> List[Dict[str, Any]]:
        """
        Fetch calendar events from today through 7 days out across all
        connected calendars.

        Returns:
            List of event dicts with: id, summary, description, location,
            start, end, is_today.
        """
        try:
            # Use Eastern Time for "today" since user is in ET
            from zoneinfo import ZoneInfo
            eastern = ZoneInfo("America/New_York")
            now_et = datetime.now(eastern)
            today = now_et.date()
            end_date = today + timedelta(days=7)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/events",
                    headers=self._headers(),
                    params={
                        "start": today.isoformat(),
                        "end": end_date.isoformat(),
                        "allConnected": "true",
                    },
                    timeout=15.0,
                )

                if response.status_code != 200:
                    logger.error(f"Reclaim events API error: {response.status_code}")
                    return []

                events = response.json()
                if not isinstance(events, list):
                    logger.warning("Unexpected Reclaim events response format")
                    return []

                event_list = []
                for event in events:
                    event_start = event.get("eventStart", "")
                    is_today = False
                    if event_start:
                        try:
                            start_dt = datetime.fromisoformat(event_start)
                            is_today = start_dt.date() == today
                        except (ValueError, TypeError):
                            pass

                    event_list.append({
                        "id": event.get("eventId", ""),
                        "summary": event.get("title", ""),
                        "description": event.get("description", ""),
                        "location": event.get("location", ""),
                        "start": event_start,
                        "end": event.get("eventEnd", ""),
                        "is_today": is_today,
                    })

                logger.info(f"Fetched {len(event_list)} events from Reclaim.ai (allConnected=true)")
                return event_list

        except Exception as e:
            logger.error(f"Error fetching Reclaim events: {str(e)}")
            return []

    async def fetch_tasks(self) -> List[Dict[str, Any]]:
        """
        Fetch current tasks from Reclaim.ai.

        Returns:
            List of task dicts with: id, content, description, priority,
            due, status, time_remaining_minutes.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/tasks",
                    headers=self._headers(),
                    params={
                        "status": "NEW,SCHEDULED,IN_PROGRESS",
                    },
                    timeout=15.0,
                )

                if response.status_code != 200:
                    logger.error(f"Reclaim tasks API error: {response.status_code}")
                    return []

                tasks = response.json()
                if not isinstance(tasks, list):
                    logger.warning("Unexpected Reclaim tasks response format")
                    return []

                task_list = []
                for task in tasks:
                    chunks_remaining = task.get("timeChunksRemaining", 0)
                    time_remaining = chunks_remaining * MINUTES_PER_CHUNK

                    task_list.append({
                        "id": task.get("id", ""),
                        "content": task.get("title", ""),
                        "description": task.get("notes", ""),
                        "priority": task.get("priority", "DEFAULT"),
                        "due": task.get("due"),
                        "status": task.get("status", ""),
                        "time_remaining_minutes": time_remaining,
                    })

                logger.info(f"Fetched {len(task_list)} tasks from Reclaim.ai")
                return task_list

        except Exception as e:
            logger.error(f"Error fetching Reclaim tasks: {str(e)}")
            return []
