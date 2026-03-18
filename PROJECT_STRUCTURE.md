# Daily Digest API - Project Structure

```
daily-digest/
│
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration and settings management
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
│
├── services/                    # Service modules for data collection
│   ├── __init__.py
│   ├── claude_service.py        # Claude AI integration
│   ├── email_service.py         # Gmail API integration
│   ├── news_service.py          # NewsAPI integration
│   ├── calendar_service.py      # Google Calendar integration
│   ├── weather_service.py       # OpenWeatherMap integration
│   ├── traffic_service.py       # Google Routes API integration
│   └── todo_service.py          # Todoist integration
│
├── setup/                       # Setup scripts and credentials
│   ├── README.md
│   ├── get_google_tokens.py     # Google OAuth token generator
│   └── google_credentials/      # Store Google credentials here
│       ├── .gitignore
│       └── README.md
│
├── env.example                  # Environment variables template
├── .env                         # Your actual API keys (git-ignored)
├── .gitignore                   # Git ignore rules
│
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Docker Compose configuration
│
├── install.sh                   # One-line installer script
├── quickstart.sh                # Quick start with credential checks
├── start.sh                     # Development start script
└── test_api.py                  # API testing script
```

## File Descriptions

### Core Files

- **main.py**: Main FastAPI application with routes and endpoints
  - `/` - Health check
  - `/health` - Detailed service status
  - `/digest` - Generate custom digest
  - `/digest/quick` - Quick digest with defaults

- **config.py**: Centralized configuration using Pydantic Settings
  - Loads from environment variables
  - Validates configuration
  - Type-safe settings
  - COMMUTE_ROUTES parsed from JSON env var

### Services Directory

Each service follows a consistent pattern:
- `is_configured()` - Check if API keys are set
- `fetch_*()` - Retrieve data from external API
- Consistent error handling (returns empty list/dict, never None)

### Deployment Files

- **Dockerfile**: Container image for production deployment
- **docker-compose.yml**: Multi-container setup (add Redis, etc.)
- **install.sh**: One-line installer for Ubuntu/Debian
- **quickstart.sh**: Quick start with credential auto-detection
- **start.sh**: Quick local development script

### Configuration Files

- **requirements.txt**: Python package dependencies
- **env.example**: Template showing required environment variables
- **.gitignore**: Prevents committing secrets and cache files

## Adding New Services

1. Create new service file in `services/`:
   ```python
   # services/new_service.py
   class NewService:
       def __init__(self):
           self.api_key = settings.NEW_API_KEY

       @staticmethod
       def is_configured():
           return bool(settings.NEW_API_KEY)

       async def fetch_data(self):
           # Implementation
           return data
   ```

2. Add to `services/__init__.py`:
   ```python
   from .new_service import NewService
   __all__ = [..., "NewService"]
   ```

3. Import and use in `main.py`:
   ```python
   from services import NewService

   new_service = NewService()
   digest_data['new'] = await new_service.fetch_data()
   ```

4. Add configuration to `config.py`:
   ```python
   NEW_API_KEY: str = ""
   ```

5. Update `env.example` with new key

## Development Workflow

1. **Local Development**:
   ```bash
   ./start.sh
   # or
   uvicorn main:app --reload
   ```

2. **Testing**:
   ```bash
   python test_api.py
   ```

3. **Docker Testing**:
   ```bash
   docker-compose up
   ```

4. **Deploy**:
   - Push to GitHub
   - Deploy via server with install.sh
   - Or build and push Docker image

## Directory Best Practices

- Keep services independent and reusable
- Use async/await for all I/O operations
- Handle errors gracefully with fallbacks
- Log important events
- Keep secrets in environment variables
- Write tests for each service
- Document API changes in README.md
