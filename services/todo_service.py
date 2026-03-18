"""
Todo Service for fetching todo list items
"""
from typing import List, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class TodoService:
    """Service for fetching todos from Todoist"""

    def __init__(self):
        self.api_key = settings.TODOIST_API_KEY
        self._api = None

    def _get_api(self):
        """Lazy initialize the Todoist API client"""
        if self._api is None and self.is_configured():
            try:
                from todoist_api_python.api import TodoistAPI
                self._api = TodoistAPI(self.api_key)
                logger.info("✅ Todoist API client initialized successfully")
            except ImportError as e:
                logger.error(f"todoist-api-python not installed: {e}")
                logger.error("Run: pip install todoist-api-python")
            except Exception as e:
                logger.error(f"Failed to initialize Todoist API: {e}")
        return self._api

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(settings.TODOIST_API_KEY)

    async def fetch_todos(self) -> List[Dict[str, Any]]:
        """
        Fetch today's and overdue todo items

        Returns:
            List of todo dictionaries
        """

        api = self._get_api()

        if api is None:
            logger.warning("Todoist API not available")
            return []

        try:
            # Call the SDK directly (it's synchronous but fast)
            # Running in async context is fine for quick API calls
            tasks = api.get_tasks()

            logger.info(f"✅ Fetched {len(tasks)} tasks from Todoist")

            # Convert Task objects to dictionaries
            todo_list = []
            for task in tasks:
                todo_item = {
                    "id": task.id,
                    "content": task.content,
                    "description": task.description or "",
                    "priority": task.priority,
                    "project_id": task.project_id,
                    "labels": task.labels,
                    "due": None,
                    "is_overdue": False
                }

                # Handle due date if present
                if task.due:
                    from datetime import date
                    todo_item["due"] = task.due.string

                    # Check if overdue
                    if task.due.date:
                        today = date.today()
                        todo_item["is_overdue"] = task.due.date < today

                todo_list.append(todo_item)

            return todo_list

        except Exception as e:
            logger.error(f"Error fetching todos: {e}")
            return []
