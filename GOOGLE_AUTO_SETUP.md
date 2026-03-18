# Google OAuth - Auto-Setup Guide

**Your wish is granted!** 🎉 Google OAuth tokens now generate automatically on first run.

## How It Works

### The Old Way ❌
1. Download credentials.json
2. Run `python setup/get_google_tokens.py`
3. Authenticate in browser
4. Copy tokens to .env
5. Start app

### The New Way ✅
1. Download credentials.json → save to `setup/google_credentials/credentials.json`
2. **Start the app** → Browser opens automatically
3. Click "Allow" once
4. Done! All future starts are automatic

## Quick Start

### Step 1: Get OAuth Credentials (One-Time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail & Calendar APIs
3. Create OAuth Client → Choose **"Desktop App"**
4. Download JSON file
5. Save as: `setup/google_credentials/credentials.json`

See [GOOGLE_SETUP.md](GOOGLE_SETUP.md) for detailed steps.

### Step 2: Start the Application

```bash
# Option 1: Use quickstart script
./quickstart.sh

# Option 2: Use Python directly
python -m uvicorn main:app --reload

# Option 3: Use start script
bash start.sh
```

### Step 3: Authenticate (First Run Only)

**Automatic behavior on first run:**

1. ✅ App detects credentials but no tokens
2. 🌐 Browser opens automatically
3. 🔐 Sign in to Google
4. ✅ Click "Allow" to grant permissions
5. 💾 Tokens saved to `setup/google_credentials/tokens.json`
6. 🚀 App continues startup

**All subsequent runs:** No browser, no authentication - fully automatic!

## What Happens Under the Hood

```
App Startup
    ↓
Check for tokens?
    ├─ Found → ✅ Load and continue
    └─ Not found → Check for credentials.json
           ├─ Found → 🌐 Open browser for auth
           │          ↓
           │      User clicks "Allow"
           │          ↓
           │      💾 Save tokens
           │          ↓
           │      ✅ Continue startup
           └─ Not found → ⚠️ Log warning, use sample data
```

## File Locations

The app checks these locations in order:

### For OAuth Credentials (input - you provide):
1. `setup/google_credentials/credentials.json` ✅ Recommended
2. `credentials.json` (project root)

### For Generated Tokens (output - auto-created):
1. **Environment variables** (`.env` file) - Highest priority
2. `setup/google_credentials/tokens.json` ✅ Auto-saved here
3. `token.json` (project root) - Backward compatibility

## Deployment to Remote Server

### Option A: Pre-generate Tokens (Recommended)

```bash
# On your LOCAL machine (with browser):
python setup/get_google_tokens.py

# Copy tokens to server:
scp setup/google_credentials/tokens.json user@server:/path/to/app/setup/google_credentials/

# Start app on server - no browser needed!
ssh user@server "cd /path/to/app && ./start.sh"
```

### Option B: Use Environment Variables

```bash
# Extract tokens on local machine
python setup/get_google_tokens.py

# Add to .env on server
GMAIL_CLIENT_ID=xxx
GMAIL_CLIENT_SECRET=xxx
GMAIL_REFRESH_TOKEN=xxx

# Deploy
```

### Note on Headless Servers

You **cannot** run the initial OAuth flow on a headless server (no browser). You must:
1. Generate tokens on a machine with a browser (your laptop)
2. Copy tokens to server
3. Server uses tokens automatically

This is a Google OAuth security requirement - cannot be bypassed.

## Troubleshooting

### Browser doesn't open automatically

**Cause**: Running on headless server or SSH session without X11 forwarding

**Solution**: Generate tokens on your local machine first:
```bash
# Local machine:
python setup/get_google_tokens.py

# Then copy tokens to server
```

### "redirect_uri_mismatch" error

**Cause**: OAuth client is "Web App" instead of "Desktop App"

**Solution**:
- Create new OAuth client as "Desktop App"
- Or add `http://localhost` to authorized redirect URIs

### App can't find credentials.json

**Cause**: File in wrong location

**Solution**:
```bash
# Move to correct location
mv credentials.json setup/google_credentials/credentials.json
```

### Tokens not loading

**Cause**: File permissions or path issues

**Solution**:
```bash
# Check file exists
ls -la setup/google_credentials/tokens.json

# Check file has correct permissions
chmod 600 setup/google_credentials/tokens.json

# Check logs on app startup
```

## Security Notes

- 🔒 Tokens are like passwords - keep them secure!
- 📁 Files are auto-added to `.gitignore`
- 🔄 Rotate tokens periodically
- ⚠️ Never commit credentials to git
- 🗑️ Revoke old tokens at [Google Account](https://myaccount.google.com/permissions)

## Summary

✅ **Zero manual steps after placing credentials.json**
✅ **One-time browser authentication**
✅ **All future runs are fully automatic**
✅ **Works for both local and remote deployments**
✅ **Backward compatible with manual .env setup**

Just place `credentials.json` and start the app - it handles the rest! 🚀
