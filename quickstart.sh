#!/bin/bash
#
# Quick Start Script for Daily Digest API
# Automatically handles Google OAuth setup on first run

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║         Daily Digest API - Quick Start            ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for credentials (look for any client_secret_*.json or credentials.json)
FOUND_CREDS=false

if [ -d "setup/google_credentials" ]; then
    if ls setup/google_credentials/client_secret_*.json 1> /dev/null 2>&1; then
        FOUND_CREDS=true
    elif [ -f "setup/google_credentials/credentials.json" ]; then
        FOUND_CREDS=true
    fi
fi

if [ -f "credentials.json" ]; then
    FOUND_CREDS=true
fi

if [ "$FOUND_CREDS" = false ]; then
    echo -e "${YELLOW}⚠️  No Google OAuth credentials found${NC}"
    echo ""
    echo "Gmail and Calendar will not be available on first start."
    echo ""
    echo "To enable them later:"
    echo "  1. Download OAuth credentials from Google Cloud Console"
    echo "  2. Save to: setup/google_credentials/ directory"
    echo "  3. Keep the original filename (no need to rename)"
    echo "  4. Restart the app"
    echo ""
    echo "See GOOGLE_SETUP.md for detailed instructions."
    echo ""
fi

# Check if tokens exist
if [ -f "setup/google_credentials/tokens.json" ] || [ -f "token.json" ]; then
    echo -e "${GREEN}✅ Google OAuth tokens found${NC}"
elif [ "$FOUND_CREDS" = true ]; then
    echo -e "${BLUE}🔐 Google credentials found${NC}"
    echo ""
    echo "On first startup, your browser will open for authentication."
    echo "This is a one-time setup - just click 'Allow' when prompted."
    echo ""
fi

# Start the application
echo -e "${GREEN}🚀 Starting Daily Digest API...${NC}"
echo ""

# Use start.sh if it exists, otherwise use uvicorn directly
if [ -f "start.sh" ]; then
    bash start.sh
else
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Start with uvicorn
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
