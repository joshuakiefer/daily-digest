# Google Credentials Directory

## Setup Instructions

### 1. Place Your OAuth Credentials Here

Download your OAuth 2.0 Desktop App credentials from Google Cloud Console and save as:
```
setup/google_credentials/credentials.json
```

### 2. Generate Tokens (Local Machine Only)

Run this command on your **local machine** (requires browser):
```bash
python setup/get_google_tokens.py
```

This will:
- Open a browser for Google authentication
- Generate a refresh token
- Save tokens to `setup/google_credentials/tokens.json`
- Update your `.env` file

### 3. Deploy to Server

When deploying to a remote server, you have two options:

#### Option A: Copy .env file (Recommended for simple deploys)
```bash
# Copy your .env with tokens to the server
scp .env user@server:/path/to/app/
```

#### Option B: Use tokens.json file
```bash
# Copy tokens to server
scp setup/google_credentials/tokens.json user@server:/path/to/app/setup/google_credentials/
```

The application will automatically use tokens from either location.

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `credentials.json` or `tokens.json` to git
- Keep these files secure - they provide access to your Gmail/Calendar
- Rotate tokens periodically
- Use environment variables in production when possible

## File Structure

```
setup/google_credentials/
├── README.md                 (this file)
├── credentials.json          (OAuth client - place here)
└── tokens.json              (Generated tokens - created by script)
```
