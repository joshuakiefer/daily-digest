# Daily Digest API

A FastAPI-based daily digest service that aggregates information from multiple sources (emails, calendar, news, weather, traffic, todos) and provides AI-powered summaries using Claude AI.

## Features

- 📧 **Email Integration** - Fetch unread emails from Gmail
- 📅 **Calendar Events** - Get today's schedule from Google Calendar
- 📰 **News Aggregation** - Top headlines from NewsAPI
- 🌤️ **Weather** - Current weather and forecast
- 🚗 **Traffic** - Real-time traffic using Google Routes API
- ✅ **Todo Lists** - Today's tasks from Todoist
- 🤖 **AI Summaries** - Intelligent summaries powered by Claude AI

## Architecture

This API is designed to run on-demand (not scheduled) for maximum flexibility. You can trigger it via:
- External schedulers (cron, GitHub Actions, etc.)
- Webhooks
- Manual API calls
- Third-party automation tools (Zapier, IFTTT, etc.)

## Setup

### 🚀 Quick Install (Ubuntu/Debian)

**One-line installation** - handles everything automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/joshuakiefer/daily-digest/main/install.sh | bash
```

The installer will:
- Install all dependencies
- Set up Python environment
- Interactively ask for API keys
- Configure systemd service
- Start the application

### 📦 Manual Installation

```bash

# Clone or download the project
git clone https://github.com/joshuakiefer/daily-digest.git
cd daily-digest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)

**The app works with sample data without ANY API keys!** Great for testing.

For real integrations, you have two options:

#### Option A: Automatic Setup (Recommended for Google OAuth)

For **Gmail & Calendar** (requires one-time browser authentication):

1. Download OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/)
2. Save as: `setup/google_credentials/credentials.json`
3. Start the app - **it will auto-open your browser** for one-time authentication
4. Click "Allow" - tokens are saved automatically
5. All future starts are fully automatic!

See [GOOGLE_SETUP.md](GOOGLE_SETUP.md) for detailed instructions.

#### Option B: Manual .env Configuration

Create `.env` file and add your keys:

```bash
cp env.example .env
# Edit .env with your favorite editor
```

**Quick Setup Guides**:
- 📖 **[API_SETUP.md](API_SETUP.md)** - Quick reference for ALL API keys
- 🔐 **[GOOGLE_SETUP.md](GOOGLE_SETUP.md)** - Detailed Google OAuth setup

**API Keys Available**:
- **Anthropic (Claude AI)**: [Get key](https://console.anthropic.com/) - AI summaries
- **Gmail API**: Auto-setup via OAuth (see above)
- **Google Calendar**: Auto-setup via OAuth (same as Gmail)
- **NewsAPI**: [Get key](https://newsapi.org/) - News headlines
- **OpenWeatherMap**: [Get key](https://openweathermap.org/api) - Weather
- **Google Routes API**: [Setup guide](ROUTES_API_SETUP.md) - Traffic data
- **Todoist**: [Get key](https://todoist.com/app/settings/integrations) - Todo lists

### 3. Run the Application

**Quick start** (checks for credentials automatically):
```bash
./quickstart.sh
```

Or **manually**:
```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

**First Run with Google Credentials?**
- Browser will open automatically for authentication
- Click "Allow" once
- Tokens saved - never needed again!

The API will be available at `http://localhost:8000`

## API Endpoints

### `GET /`
Health check

### `GET /health`
Detailed health check with service status

### `POST /digest`
Generate full daily digest

**Request Body:**
```json
{
  "include_email": true,
  "include_news": true,
  "include_calendar": true,
  "include_weather": true,
  "include_traffic": true,
  "include_todos": true,
  "location": "Marysville, OH"
}
```

**Response:**
```json
{
  "summary": "AI-generated summary...",
  "details": {
    "emails": [...],
    "calendar": [...],
    "news": [...],
    "weather": {...},
    "traffic": {...},
    "todos": [...]
  },
  "timestamp": "2026-03-18T10:30:00"
}
```

### `POST /digest/quick`
Generate digest with default settings (all sources enabled)
