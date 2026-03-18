# Deployment Guide - Daily Digest API

Complete guide for deploying your Daily Digest application to a remote server.

## Quick Overview

### Setup Process (Do Once)
1. **Local Machine**: Generate Google OAuth tokens (requires browser)
2. **Remote Server**: Deploy application with tokens
3. **Remote Server**: Run and enjoy automated digests

---

## Part 1: Local Setup (One-Time Token Generation)

### Step 1: Place Your Google Credentials

Copy your Desktop App OAuth credentials JSON file to:
```bash
setup/google_credentials/credentials.json
```

Or use the full filename (the script will find it):
```bash
cp client_secret_*.json setup/google_credentials/credentials.json
```

### Step 2: Generate OAuth Tokens

Run the token generation script on your **local machine** (requires browser):

```bash
python setup/get_google_tokens.py
```

This will:
- ✅ Open your browser for Google authentication
- ✅ Generate a refresh token
- ✅ Save to `setup/google_credentials/tokens.json`
- ✅ Optionally update your `.env` file

**Important**: This step MUST be done on a machine with a browser. You cannot do this on a headless server.

---

## Part 2: Deploying to Remote Server

### Option A: Using tokens.json (Recommended)

The application will **automatically load tokens** from `setup/google_credentials/tokens.json`.

```bash
# Copy entire project to server
scp -r /path/to/daily-digest/ user@server:/home/user/

# SSH into server
ssh user@server

# Run installation
cd daily-digest
bash install.sh
```

When the installer asks about Gmail, choose **"Use existing tokens.json"** and it will auto-configure.

### Option B: Using Environment Variables

If you prefer to use environment variables:

```bash
# Copy .env file to server
scp .env user@server:/home/user/daily-digest/

# SSH and run
ssh user@server
cd daily-digest
bash install.sh
```

### Option C: Manual Environment Setup

Add these to your `.env` file on the server:

```bash
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here
GMAIL_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_CALENDAR_CREDENTIALS=your_refresh_token_here
```

---

## Part 3: How Token Auto-Loading Works

The application checks for tokens in this priority order:

1. **Environment variables** (`.env` file) - Highest priority
2. **tokens.json** in `setup/google_credentials/tokens.json`
3. **tokens.json** in project root `token.json`

If environment variables are set, they take precedence. Otherwise, the app automatically loads from `tokens.json`.

This means you can:
- ✅ Deploy without manually editing `.env`
- ✅ Just copy `tokens.json` with your code
- ✅ Keep credentials in a separate secure file

---

## Part 4: Security Best Practices

### Files to Never Commit to Git

Add these to `.gitignore`:

```gitignore
.env
token.json
setup/google_credentials/credentials.json
setup/google_credentials/tokens.json
client_secret_*.json
```

### Secure File Transfer

Use SCP with proper permissions:

```bash
# Copy tokens with restricted permissions
scp -p setup/google_credentials/tokens.json user@server:/path/to/app/setup/google_credentials/
ssh user@server "chmod 600 /path/to/app/setup/google_credentials/tokens.json"
```

### Token Rotation

Periodically rotate your tokens:

1. Revoke old tokens in [Google Cloud Console](https://console.cloud.google.com/)
2. Run `python setup/get_google_tokens.py` again
3. Redeploy updated tokens to server
4. Restart application

---

## Part 5: Troubleshooting

### "No tokens found" on Server

**Problem**: Application can't find Google credentials

**Solution**:
```bash
# Check if tokens.json exists
ls -la setup/google_credentials/tokens.json

# If missing, copy from local machine
scp setup/google_credentials/tokens.json user@server:/path/to/app/setup/google_credentials/
```

### "redirect_uri_mismatch" Error During Token Generation

**Problem**: OAuth client is set as "Web application" instead of "Desktop app"

**Solution**:
- Create a new OAuth client as "Desktop app" in Google Cloud Console
- Download the new credentials JSON
- Use it for token generation

### Tokens Expire or Stop Working

**Problem**: Refresh token was revoked or expired

**Solution**:
1. Go to [Google Account Security](https://myaccount.google.com/permissions)
2. Remove your app's permissions
3. Re-run `python setup/get_google_tokens.py`
4. Redeploy new tokens

### Application Can't Access Gmail/Calendar

**Problem**: APIs not enabled or scopes missing

**Solution**:
1. Enable Gmail API and Calendar API in [Google Cloud Console](https://console.cloud.google.com/)
2. Verify scopes in OAuth consent screen:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/calendar.readonly`
3. Regenerate tokens with correct scopes

---

## Part 6: Docker Deployment

If using Docker, include tokens in your container:

### Option A: Mount tokens.json

```yaml
# docker-compose.yml
services:
  daily-digest:
    volumes:
      - ./setup/google_credentials/tokens.json:/app/setup/google_credentials/tokens.json:ro
```

### Option B: Use environment variables

```yaml
# docker-compose.yml
services:
  daily-digest:
    environment:
      - GMAIL_CLIENT_ID=${GMAIL_CLIENT_ID}
      - GMAIL_CLIENT_SECRET=${GMAIL_CLIENT_SECRET}
      - GMAIL_REFRESH_TOKEN=${GMAIL_REFRESH_TOKEN}
```

Then create a `.env` file alongside `docker-compose.yml`:

```bash
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
```

---

## Part 7: CI/CD Integration

For automated deployments:

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Copy tokens to server
        env:
          GMAIL_CLIENT_ID: ${{ secrets.GMAIL_CLIENT_ID }}
          GMAIL_CLIENT_SECRET: ${{ secrets.GMAIL_CLIENT_SECRET }}
          GMAIL_REFRESH_TOKEN: ${{ secrets.GMAIL_REFRESH_TOKEN }}
        run: |
          # Create .env on server
          ssh user@server "cd /path/to/app && cat > .env << EOF
          GMAIL_CLIENT_ID=$GMAIL_CLIENT_ID
          GMAIL_CLIENT_SECRET=$GMAIL_CLIENT_SECRET
          GMAIL_REFRESH_TOKEN=$GMAIL_REFRESH_TOKEN
          EOF"
```

Store credentials as GitHub Secrets, not in tokens.json.

---

## Summary Checklist

- [ ] Generate tokens on local machine with browser
- [ ] Copy `tokens.json` to server OR set environment variables
- [ ] Run `install.sh` on server
- [ ] Verify application loads tokens (check logs)
- [ ] Test Gmail and Calendar endpoints
- [ ] Set up automatic restarts (systemd/pm2)
- [ ] Add to .gitignore: `.env`, `tokens.json`, `credentials.json`

---

## Quick Commands Reference

```bash
# Local: Generate tokens (one-time)
python setup/get_google_tokens.py

# Deploy to server
scp -r . user@server:/home/user/daily-digest/
ssh user@server "cd daily-digest && bash install.sh"

# Check if tokens loaded
ssh user@server "cd daily-digest && python -c 'from config import settings; print(bool(settings.GMAIL_REFRESH_TOKEN))'"

# Restart service
ssh user@server "sudo systemctl restart daily-digest"
```

---

For more details on Google OAuth setup, see [GOOGLE_SETUP.md](GOOGLE_SETUP.md).
