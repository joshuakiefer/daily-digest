# Setup Scripts

This directory contains helper scripts for setting up API integrations.

## Directory Structure

```
setup/
├── get_google_tokens.py       # OAuth token generator
├── google_credentials/         # Store Google credentials here
│   ├── credentials.json        # OAuth client (you provide)
│   └── tokens.json            # Generated tokens (script creates)
└── README.md                   # This file
```

## get_google_tokens.py

Generates OAuth refresh tokens for Gmail and Google Calendar access.

### Quick Start:

1. **Place your OAuth credentials**:
   ```bash
   # Copy your Desktop App credentials to:
   setup/google_credentials/credentials.json
   ```

2. **Run the token generator**:
   ```bash
   python setup/get_google_tokens.py
   ```

3. **Authenticate in browser**:
   - Browser opens automatically
   - Sign in with Google
   - Grant permissions
   - Tokens saved automatically

4. **Deploy** (tokens auto-load):
   - Local: Tokens loaded from `setup/google_credentials/tokens.json`
   - Server: Copy tokens.json with your code OR use .env

### What it does:

- ✅ Finds credentials in `setup/google_credentials/` or project root
- ✅ Authenticates with Google OAuth (requires browser)
- ✅ Requests read-only access to Gmail and Calendar
- ✅ Generates a refresh token (persists until revoked)
- ✅ Saves to `setup/google_credentials/tokens.json`
- ✅ Optionally updates your `.env` file
- ✅ Application auto-loads tokens on startup

### How Token Auto-Loading Works:

The application (`config.py`) automatically checks for tokens in this order:

1. **Environment variables** (`.env` file) - Highest priority
2. **`setup/google_credentials/tokens.json`** - Recommended location
3. **`token.json`** in project root - Backward compatibility

You don't need to manually add tokens to `.env` if `tokens.json` exists!

### Security Notes:

- ⚠️  Never commit `credentials.json` or `tokens.json` to git
- ✅ Files are already in `.gitignore`
- 🔒 Keep your refresh token secure (it's like a password)
- 🔄 Revoke access in [Google Account settings](https://myaccount.google.com/permissions) if compromised
- 🔁 Rotate tokens periodically for security

### Troubleshooting:

**"credentials.json not found"**
```bash
# Solution: Place OAuth credentials in the right location
cp client_secret_*.json setup/google_credentials/credentials.json
```

**"redirect_uri_mismatch"**
- Make sure you created **"Desktop app"** not "Web application"
- Or add `http://localhost` to authorized redirect URIs

**"invalid_grant" error**
- Refresh token expired or revoked
- Re-run the script to generate new tokens
- Check if user is still in test users list (for external apps)

**"Access blocked"**
- Add your email to test users in OAuth consent screen
- Verify APIs are enabled in Google Cloud

For detailed instructions, see [GOOGLE_SETUP.md](../GOOGLE_SETUP.md)
