"""
Traffic Service for fetching traffic/commute information using Google Routes API
"""
from typing import Dict, Any, Optional, List
from config import settings
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class TrafficService:
    """Service for fetching traffic data from Google Routes API"""

    def __init__(self):
        self.api_key = settings.TRAFFIC_API_KEY or settings.GOOGLE_API_KEY
        self.base_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        self.routes = settings.COMMUTE_ROUTES or []

    @staticmethod
    def is_configured() -> bool:
        """Check if the service is properly configured"""
        return bool(settings.TRAFFIC_API_KEY or settings.GOOGLE_API_KEY)

    async def fetch_traffic(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch traffic information for configured routes using Google Routes API

        Args:
            location: Origin location (can override default)

        Returns:
            Dictionary with traffic information for all routes
        """
        location = location or settings.DEFAULT_LOCATION

        if not self.is_configured():
            logger.warning("Traffic API not configured")
            return {}

        try:
            # If no routes configured, return empty data
            if not self.routes:
                logger.warning("No commute routes configured")

            # Fetch traffic for all configured routes
            routes_data = []

            async with httpx.AsyncClient() as client:
                for route in self.routes:
                    try:
                        route_info = await self._fetch_route(
                            client,
                            route.get('origin', location),
                            route.get('destination'),
                            route.get('name', 'Unnamed Route')
                        )
                        if route_info:
                            routes_data.append(route_info)
                    except Exception as e:
                        logger.error(f"Error fetching route {route.get('name')}: {str(e)}")
                        continue

            if not routes_data:
                logger.warning("Failed to fetch any routes")

            # Generate summary
            summary = self._generate_summary(routes_data)

            return {
                "location": location,
                "routes": routes_data,
                "summary": summary,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching traffic: {str(e)}")
            return {}

    async def _fetch_route(
        self,
        client: httpx.AsyncClient,
        origin: str,
        destination: str,
        route_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single route using Google Routes API

        Args:
            client: HTTP client
            origin: Starting location
            destination: Ending location
            route_name: Name for this route

        Returns:
            Route information dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs.duration,routes.legs.distanceMeters,routes.localizedValues,routes.description"
        }

        # Request body for Routes API
        request_body = {
            "origin": {
                "address": origin
            },
            "destination": {
                "address": destination
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": True,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US",
            "units": "IMPERIAL"
        }

        response = await client.post(
            self.base_url,
            json=request_body,
            headers=headers,
            timeout=10.0
        )

        if response.status_code != 200:
            logger.error(f"Routes API error: {response.status_code} - {response.text}")
            return None

        data = response.json()

        # Parse the response
        if not data.get('routes'):
            logger.warning(f"No routes found for {route_name}")
            return None

        # Get the primary route (first one)
        primary_route = data['routes'][0]

        # Extract duration and distance
        duration_seconds = int(primary_route.get('duration', '0s').rstrip('s'))
        distance_meters = primary_route.get('distanceMeters', 0)

        # Convert to readable format
        duration_minutes = duration_seconds // 60
        distance_miles = distance_meters * 0.000621371  # meters to miles

        # Determine traffic level based on expected vs actual time
        traffic_level = self._determine_traffic_level(duration_minutes, distance_miles)

        # Check for alternative routes
        alternative_route = None
        if len(data['routes']) > 1:
            alt_route = data['routes'][1]
            alt_duration = int(alt_route.get('duration', '0s').rstrip('s')) // 60
            if alt_duration < duration_minutes:
                time_saved = duration_minutes - alt_duration
                alternative_route = f"Alternative route available, saves {time_saved} minutes"

        return {
            "name": route_name,
            "distance": f"{distance_miles:.1f} miles",
            "duration": f"{duration_minutes} minutes",
            "duration_seconds": duration_seconds,
            "traffic_level": traffic_level,
            "alternative_route": alternative_route,
            "origin": origin,
            "destination": destination
        }

    def _determine_traffic_level(self, duration_minutes: int, distance_miles: float) -> str:
        """
        Determine traffic level based on speed

        Args:
            duration_minutes: Travel time in minutes
            distance_miles: Distance in miles

        Returns:
            Traffic level: light, moderate, or heavy
        """
        if duration_minutes == 0:
            return "unknown"

        avg_speed = (distance_miles / duration_minutes) * 60  # mph

        if avg_speed > 45:
            return "light"
        elif avg_speed > 30:
            return "moderate"
        else:
            return "heavy"

    def _generate_summary(self, routes: List[Dict[str, Any]]) -> str:
        """Generate a summary of traffic conditions"""
        if not routes:
            return "No traffic data available"

        heavy_traffic = [r for r in routes if r.get('traffic_level') == 'heavy']
        moderate_traffic = [r for r in routes if r.get('traffic_level') == 'moderate']

        if heavy_traffic:
            route_names = ", ".join([r['name'] for r in heavy_traffic])
            return f"Heavy traffic on: {route_names}. Consider leaving early or using alternatives."
        elif moderate_traffic:
            route_names = ", ".join([r['name'] for r in moderate_traffic])
            return f"Moderate traffic on: {route_names}. Normal commute time expected."
        else:
            return "Light traffic on all routes. Good time to travel!"
