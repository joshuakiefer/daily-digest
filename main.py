"""
Daily Digest API
FastAPI application that aggregates emails, news, calendar, weather, traffic, and todos
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
import sys
import glob

from services.email_service import EmailService
from services.news_service import NewsService
from services.calendar_service import CalendarService
from services.weather_service import WeatherService
from services.traffic_service import TrafficService
from services.todo_service import TodoService
from services.claude_service import ClaudeService
from services.delivery_service import DeliveryService
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Daily Digest API",
    description="Aggregates daily information from multiple sources and provides AI-powered summaries",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_and_generate_google_tokens():
    """
    Auto-generate Google OAuth tokens if not present.
    This runs on app startup and handles first-time authentication.
    """
    # Check if tokens already exist
    token_paths = [
        'setup/google_credentials/tokens.json',
        'token.json'
    ]

    tokens_exist = any(os.path.exists(path) for path in token_paths)
    env_tokens_exist = bool(settings.GMAIL_REFRESH_TOKEN)

    if tokens_exist or env_tokens_exist:
        logger.info("✅ Google OAuth tokens found - Gmail/Calendar ready")
        return

    # Check if credentials exist - look for any client_secret_*.json file first
    credentials_path = None

    # First, check for any client_secret_*.json in google_credentials/
    if os.path.exists('setup/google_credentials'):
        pattern = 'setup/google_credentials/client_secret_*.json'
        matches = glob.glob(pattern)
        if matches:
            credentials_path = matches[0]  # Use first match

    # Fallback to standard names
    if not credentials_path:
        credentials_paths = [
            'setup/google_credentials/credentials.json',
            'credentials.json'
        ]

        for path in credentials_paths:
            if os.path.exists(path):
                credentials_path = path
                break

    if not credentials_path:
        logger.warning("⚠️  No Google OAuth credentials found")
        logger.warning("📝 To enable Gmail/Calendar:")
        logger.warning("   1. Download OAuth credentials from Google Cloud Console")
        logger.warning("   2. Save to: setup/google_credentials/ directory")
        logger.warning("   3. Keep original filename (client_secret_*.json)")
        logger.warning("   4. Restart the app - it will auto-open browser for auth")
        logger.warning("   See GOOGLE_SETUP.md for details")
        return

    # Credentials exist but no tokens - trigger OAuth flow
    logger.info("🔐 Google credentials found but no tokens yet")
    logger.info("🌐 Opening browser for one-time authentication...")
    logger.info("=" * 70)

    try:
        # Import and run token generation
        from setup.get_google_tokens import get_refresh_token

        logger.info("Please authenticate in your browser to grant permissions")
        logger.info("This only needs to be done once!")
        logger.info("=" * 70)

        get_refresh_token()

        logger.info("=" * 70)
        logger.info("✅ Google OAuth setup complete!")
        logger.info("🔄 Reloading configuration...")

        # Reload config to pick up new tokens
        import importlib
        import config
        importlib.reload(config)

        logger.info("✅ Gmail and Calendar are now ready!")

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Authentication cancelled")
        logger.info("Gmail/Calendar will not be available")
        logger.info("Run 'python setup/get_google_tokens.py' manually later")
    except Exception as e:
        logger.error(f"❌ Failed to generate tokens: {e}")
        logger.info("Run 'python setup/get_google_tokens.py' manually")


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Starting Daily Digest API...")

    # Auto-generate Google tokens if needed
    check_and_generate_google_tokens()

    logger.info("✅ Daily Digest API is ready!")
    logger.info(f"📍 Default location: {settings.DEFAULT_LOCATION}")
    if settings.DEBUG:
        logger.info("🐛 Debug mode enabled")


class DigestRequest(BaseModel):
    """Request model for digest generation"""
    include_email: bool = True
    include_news: bool = True
    include_calendar: bool = True
    include_weather: bool = True
    include_traffic: bool = True
    include_todos: bool = True
    location: Optional[str] = None  # For weather and traffic


class DigestResponse(BaseModel):
    """Response model for digest"""
    summary: str
    details: Dict[str, Any]
    timestamp: str
    email_sent: bool = False


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Daily Digest API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "email": EmailService.is_configured(),
            "news": NewsService.is_configured(),
            "calendar": CalendarService.is_configured(),
            "weather": WeatherService.is_configured(),
            "traffic": TrafficService.is_configured(),
            "todos": TodoService.is_configured(),
            "claude": ClaudeService.is_configured(),
        }
    }


@app.post("/digest", response_model=DigestResponse)
async def generate_digest(request: DigestRequest, background_tasks: BackgroundTasks):
    """
    Generate daily digest from all configured sources

    This endpoint collects data from various sources in parallel and uses Claude AI
    to generate a comprehensive summary of action items and important information.
    """
    try:
        logger.info("Starting digest generation")

        # Initialize services
        email_service = EmailService()
        news_service = NewsService()
        calendar_service = CalendarService()
        weather_service = WeatherService()
        traffic_service = TrafficService()
        todo_service = TodoService()
        claude_service = ClaudeService()

        # Collect data from all sources
        digest_data = {}

        if request.include_email:
            logger.info("Fetching emails...")
            digest_data['emails'] = await email_service.fetch_recent_emails()

        if request.include_news:
            logger.info("Fetching news...")
            digest_data['news'] = await news_service.fetch_top_stories()

        if request.include_calendar:
            logger.info("Fetching calendar events...")
            digest_data['calendar'] = await calendar_service.fetch_today_events()

        if request.include_weather:
            logger.info("Fetching weather...")
            digest_data['weather'] = await weather_service.fetch_weather(request.location)

        if request.include_traffic:
            logger.info("Fetching traffic...")
            digest_data['traffic'] = await traffic_service.fetch_traffic(request.location)

        if request.include_todos:
            logger.info("Fetching todos...")
            digest_data['todos'] = await todo_service.fetch_todos()

        logger.info(f"Digest data collected: {list(digest_data.keys())}")

        # Generate AI summary using Claude
        logger.info("Generating AI summary with Claude...")
        summary = await claude_service.generate_summary(digest_data)

        # Get current timestamp
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()

        # Auto-send email if configured
        email_sent = False
        if settings.AUTO_SEND_EMAIL and settings.DIGEST_RECIPIENT_EMAIL:
            try:
                delivery_service = DeliveryService()
                email_sent = await delivery_service.send_digest_email(summary)
            except Exception as e:
                logger.error(f"Auto-send email failed: {str(e)}")

        logger.info("Digest generation completed successfully")

        return DigestResponse(
            summary=summary,
            details=digest_data,
            timestamp=timestamp,
            email_sent=email_sent,
        )

    except Exception as e:
        logger.error(f"Error generating digest: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate digest: {str(e)}")


@app.post("/digest/quick")
async def generate_quick_digest():
    """
    Generate a quick digest with default settings
    Useful for scheduled calls
    """
    request = DigestRequest()
    background_tasks = BackgroundTasks()
    return await generate_digest(request, background_tasks)


@app.post("/digest/send", response_model=DigestResponse)
async def generate_and_send_digest(request: DigestRequest = None):
    """
    Generate a digest and send it via email.

    Always sends the email regardless of AUTO_SEND_EMAIL setting.
    Requires DIGEST_RECIPIENT_EMAIL to be configured.
    """
    if not DeliveryService.is_configured():
        raise HTTPException(
            status_code=400,
            detail="Email delivery not configured. Set DIGEST_RECIPIENT_EMAIL and Gmail OAuth credentials.",
        )

    if request is None:
        request = DigestRequest()
    background_tasks = BackgroundTasks()

    # Generate the digest
    response = await generate_digest(request, background_tasks)

    # Send the email (always, regardless of AUTO_SEND_EMAIL)
    if not response.email_sent:
        try:
            delivery_service = DeliveryService()
            response.email_sent = await delivery_service.send_digest_email(response.summary)
        except Exception as e:
            logger.error(f"Failed to send digest email: {str(e)}")

    if not response.email_sent:
        logger.warning("Email delivery was requested but sending failed")

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
