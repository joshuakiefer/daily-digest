#!/usr/bin/env python3
"""
Google OAuth Token Generator for Daily Digest API

This script helps you generate the refresh token needed for Gmail and Calendar access.
Run this ONCE during initial setup.

Requirements:
1. Google Cloud project with Gmail API and Calendar API enabled
2. OAuth 2.0 credentials (Desktop app) downloaded as credentials.json
3. google-auth-oauthlib package installed (pip install google-auth-oauthlib)

Usage:
    python setup/get_google_tokens.py
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os
import sys
import glob

# Scopes for Gmail (read + send) and Calendar read access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly',
]

def get_refresh_token():
    """Generate and display refresh token"""

    credentials_path = None

    # First, check for any client_secret_*.json file in google_credentials/
    if os.path.exists('setup/google_credentials'):
        pattern = 'setup/google_credentials/client_secret_*.json'
        matches = glob.glob(pattern)
        if matches:
            credentials_path = matches[0]  # Use first match
            print(f"✅ Found credentials at: {credentials_path}")

    # Fallback to standard names
    if not credentials_path:
        credentials_paths = [
            'setup/google_credentials/credentials.json',
            'credentials.json',
        ]

        for path in credentials_paths:
            if os.path.exists(path):
                credentials_path = path
                print(f"✅ Found credentials at: {path}")
                break

    if not credentials_path:
        print("\n❌ ERROR: No Google OAuth credentials found!")
        print("\n📝 Steps to get credentials:")
        print("=" * 70)
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project (or create one)")
        print("3. Enable Gmail API and Google Calendar API")
        print("4. Go to 'APIs & Services' → 'Credentials'")
        print("5. Create 'OAuth 2.0 Client ID' (choose 'Desktop app')")
        print("6. Download the JSON file")
        print("7. Save it to 'setup/google_credentials/' directory")
        print("   (Keep the original filename - no need to rename)")
        print("=" * 70)
        print("\nSee GOOGLE_SETUP.md for detailed instructions.\n")
        sys.exit(1)

    try:
        print("\n🔐 Starting Google OAuth Flow...")
        print("=" * 70)
        print("A browser window will open for authentication.")
        print("Please sign in with your Google account and grant permissions.")
        print("=" * 70)
        print()

        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,
            SCOPES
        )

        # Run local server for OAuth flow
        creds = flow.run_local_server(
            port=0,
            success_message='Authorization successful! You can close this window.',
        )

        # Display credentials
        print("\n✅ SUCCESS! Authorization complete!")
        print("=" * 70)
        print("\n📋 Your Google API Credentials:")
        print("-" * 70)
        print(f"Client ID:      {creds.client_id}")
        print(f"Client Secret:  {creds.client_secret}")
        print(f"Refresh Token:  {creds.refresh_token}")
        print("-" * 70)

        print("\n📝 Add these to your .env file:")
        print("=" * 70)
        print(f"GMAIL_CLIENT_ID={creds.client_id}")
        print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
        print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
        print()
        print("# For Google Calendar (uses same credentials)")
        print(f"GOOGLE_CALENDAR_CREDENTIALS={creds.refresh_token}")
        print("=" * 70)

        # Save to tokens.json in the credentials directory
        token_data = {
            'refresh_token': creds.refresh_token,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': SCOPES
        }

        # Ensure directory exists
        os.makedirs('setup/google_credentials', exist_ok=True)

        tokens_path = 'setup/google_credentials/tokens.json'
        with open(tokens_path, 'w') as token_file:
            json.dump(token_data, token_file, indent=2)

        # Also save to root for backward compatibility
        with open('token.json', 'w') as token_file:
            json.dump(token_data, token_file, indent=2)

        print(f"\n💾 Credentials saved to: {tokens_path}")
        print("💾 Backup also saved to: token.json")
        print("⚠️  IMPORTANT: Keep this file secure! Never commit it to git!")

        # Check if .env exists and offer to append
        if os.path.exists('.env'):
            print("\n❓ Would you like to append these to your .env file? (y/n): ", end='')
            response = input().lower().strip()
            if response == 'y':
                with open('.env', 'a') as env_file:
                    env_file.write("\n# Google API Credentials\n")
                    env_file.write(f"GMAIL_CLIENT_ID={creds.client_id}\n")
                    env_file.write(f"GMAIL_CLIENT_SECRET={creds.client_secret}\n")
                    env_file.write(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}\n")
                    env_file.write(f"GOOGLE_CALENDAR_CREDENTIALS={creds.refresh_token}\n")
                print("✅ Credentials appended to .env file!")
        else:
            print("\n⚠️  No .env file found. Create one and add the credentials above.")

        print("\n🎉 Setup complete! You can now use Gmail and Calendar APIs.")
        print("\n📖 Next steps:")
        print("   1. Update your .env file with the credentials above")
        print("   2. Test the connection: python test_api.py")
        print("   3. Check GOOGLE_SETUP.md for more details\n")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nIf you see 'redirect_uri_mismatch' error:")
        print("  - Make sure you created OAuth client as 'Desktop app' (not Web)")
        print("\nFor other errors, check GOOGLE_SETUP.md troubleshooting section.\n")
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 70)
    print(" Google OAuth Token Generator for Daily Digest API")
    print("=" * 70)
    print("\nThis script will help you get your Google API refresh token.")
    print("You only need to run this once during initial setup.\n")

    # Check if required package is installed
    try:
        import google_auth_oauthlib
    except ImportError:
        print("❌ Required package not found!")
        print("\nPlease install it with:")
        print("   pip install google-auth-oauthlib")
        print("\nOr install all requirements:")
        print("   pip install -r requirements.txt\n")
        sys.exit(1)

    try:
        get_refresh_token()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
