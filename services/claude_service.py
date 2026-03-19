"""
Claude AI Service for generating intelligent summaries
"""
import anthropic
from typing import Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Claude AI API"""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Claude API key not configured")

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(settings.ANTHROPIC_API_KEY)

    async def generate_summary(self, digest_data: Dict[str, Any]) -> str:
        """
        Generate an AI-powered summary of the digest data

        Args:
            digest_data: Dictionary containing all collected data

        Returns:
            Formatted summary string with action items and priorities
        """
        try:
            # Prepare the context for Claude
            context_parts = self._format_context(digest_data)
            full_context = "\n".join(context_parts)

            # Call Claude API
            def call_claude(prompt):
                message = self.client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                return message.content[0].text

            calendar = str(digest_data["calendar"]) if "calendar" in digest_data else ""
            emails = str(digest_data["emails"]) if "emails" in digest_data else ""
            todos = str(digest_data["todos"]) if "todos" in digest_data else ""
            news = str(digest_data["news"]) if "news" in digest_data else ""

            locations_context = "\n".join([calendar, emails, todos])
            locations_parser_prompt = (
                "You are a personal assistant analyzing identifying two things from a list of caldendar events, emails, and to do items. "
                "The first thing you need to identify are any specific locations that are mentioned. If the user mentions any specific locations, extract those locations and put them into a list. For example: ['New York', 'San Francisco', 'San Jose']. "
                "The second thing you need to identify are any trips that are mentioned where the user is likely driving. A trip is defined as an origin and destination pair. If the user mentions any trips, extract those the origin and destination and put them into a list of lists. From 'Home: San Francisco, I'm driving to to San Jose to visit family.', you would extract [['San Francisco', 'San Jose']]. "
                "After extracting the location names and trips, return them as properly formatted JSON with 'locations' and/or 'trips' as keys. "
                "For example, {'locations': ['New York', 'San Francisco', 'San Jose'], 'trips': [['San Francisco', 'San Jose'], ['San Jose', 'San Francisco']]}. If there are no locations, return an empty dictionary. "
                "Respond with only the raw JSON object, without any code block formatting, language tags, or extra text. "
                "Here is the context: \n\n"
                f"{locations_context}"
            )

            locations_response = call_claude(locations_parser_prompt)

            logger.info(f"Claude locations inference response: {locations_response}")

            import json
            import re
            from services.traffic_service import TrafficService
            from services.weather_service import WeatherService

            traffic_service = TrafficService()
            weather_service = WeatherService()

            def strip_code_block(text):
                # Remove triple backtick code blocks and language tags
                if text.strip().startswith('```'):
                    # Remove the first line (``` or ```json)
                    lines = text.strip().splitlines()
                    # Remove first and last line if they are backticks
                    if lines[0].startswith('```'):
                        lines = lines[1:]
                    if lines and lines[-1].startswith('```'):
                        lines = lines[:-1]
                    return '\n'.join(lines).strip()
                return text.strip()

            locations_data = {}
            try:
                clean_response = strip_code_block(locations_response)
                locations_data = json.loads(clean_response)
            except Exception as e:
                logger.warning(f"Could not parse locations response as JSON: {e}")
                locations_data = {}

            traffic_results = []
            weather_results = []

            # Handle locations
            locations = locations_data.get('locations', []) if isinstance(locations_data, dict) else []

            for loc in locations:
                try:
                    weather = await weather_service.fetch_weather(location=loc)
                    weather_results.append({"location": loc, "weather": weather})
                except Exception as e:
                    logger.warning(f"Error getting weather for {loc}: {e}")

            # Handle trips (origin/destination)
            trips = locations_data.get('trips', []) if isinstance(locations_data, dict) else []

            for trip in trips:
                if isinstance(trip, list) and len(trip) >= 2:
                    try:
                        origin = trip[0]
                        destination = trip[-1]
                        async with __import__('httpx').AsyncClient() as client:
                            traffic = await traffic_service._fetch_route(client, origin, destination, f"Trip: {origin} to {destination}")
                        traffic_results.append({"trip": trip, "traffic": traffic})
                    except Exception as e:
                        logger.warning(f"Error getting traffic for trip {trip}: {e}")

            # Add traffic and weather results to digest_data for summary
            digest_data["traffic"] = traffic_results
            digest_data["weather"] = weather_results

            # Create the prompt
            final_summary_prompt = f"""You are a personal executive assistant creating a daily briefing for a busy business owner who runs multiple companies (Scalable Bookkeeping, Flywheel Bookkeeping, Flywheel CFO, and works with Kevin Barry & Associates).

Create a concise, actionable daily digest organized into these sections:

## 📬 EMAIL SUMMARY & ACTION ITEMS
For each email that requires attention:
- One-line summary of what the email is about
- **Action needed**: What specifically the user should do (reply, review, approve, etc.)
- **Deadline/urgency**: If there's a time-sensitive element, flag it
- **Follow-up**: Any follow-up actions needed

Group emails by priority:
1. 🔴 URGENT — needs response today
2. 🟡 ACTION NEEDED — needs response this week  
3. 🟢 FYI — informational, no action needed

Skip spam, marketing, and automated notifications unless they contain something actionable.

## 📅 TODAY'S SCHEDULE
List today's events (marked is_today=True) in chronological order with:
- Time, event name, and any prep needed
- Flag any back-to-back meetings

## 📋 UPCOMING (Next 7 Days)
Briefly note important upcoming meetings or deadlines.

## ✅ ACTION ITEM CHECKLIST
A consolidated checklist of everything the user needs to do today, pulled from emails, calendar, and todos. Format as a simple numbered list.

Rules:
- Be direct and specific — no filler
- If an email is from a client or team member, always surface it
- If an email asks a question or requests something, always flag the action item
- Skip boilerplate email signatures and legal disclaimers when summarizing
- Use the actual names of people and companies

Here's the data:

{full_context}

Provide the digest now."""

            final_summary = call_claude(final_summary_prompt)
            logger.info(f"Claude final summary response: {final_summary}")

            return final_summary

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return "Unable to generate AI summary. Please check your Anthropic API key configuration."

    def _format_context(self, digest_data: Dict[str, Any]) -> str:
        """Format the digest data into a readable context for Claude"""
        context_parts = []

        if 'emails' in digest_data and digest_data['emails']:
            email_lines = ["EMAILS:"]
            for i, email in enumerate(digest_data['emails'], 1):
                email_lines.append(f"\n--- Email {i} ---")
                email_lines.append(f"From: {email.get('from', 'Unknown')}")
                email_lines.append(f"To: {email.get('to', '')}")
                email_lines.append(f"Subject: {email.get('subject', 'No subject')}")
                email_lines.append(f"Date: {email.get('date', '')}")
                body = email.get('body', '')
                if body:
                    email_lines.append(f"Body:\n{body}")
                else:
                    snippet = email.get('snippet', '')
                    if snippet:
                        email_lines.append(f"Preview: {snippet}")
            context_parts.append("\n".join(email_lines))

        if 'calendar' in digest_data:
            context_parts.append("\nCALENDAR EVENTS:\n" + str(digest_data['calendar']))

        if 'news' in digest_data:
            context_parts.append("\nNEWS:\n" + str(digest_data['news']))

        if 'weather' in digest_data:
            context_parts.append("\nWEATHER:\n" + str(digest_data['weather']))

        if 'traffic' in digest_data:
            context_parts.append("\nTRAFFIC:\n" + str(digest_data['traffic']))

        if 'todos' in digest_data:
            context_parts.append("\nTODOS:\n" + str(digest_data['todos']))

        return context_parts
