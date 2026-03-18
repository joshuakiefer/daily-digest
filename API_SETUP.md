# API Setup Quick Reference

Quick links and steps for getting all the API keys you need.

## 🔑 Required API Keys

### 1. Claude AI (Anthropic) - **Required for AI summaries**

**Get it**: https://console.anthropic.com/

**Steps**:
1. Sign up/login to Anthropic Console
2. Go to "API Keys"
3. Create new key
4. Copy and add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

**Free Tier**: $5 credit for new accounts
**Pricing**: ~$3 per million input tokens

---

### 2. Gmail API - **For email reading**

**Get it**: Google Cloud Console (requires OAuth setup)

**Steps**:
1. Follow [GOOGLE_SETUP.md](GOOGLE_SETUP.md) detailed guide
2. Or run quick setup:
   ```bash
   python setup/get_google_tokens.py
   ```

**Add to `.env`**:
```
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
```

**Free Tier**: 1 billion quota units/day (essentially unlimited for personal use)

---

### 3. Google Calendar API - **For calendar events**

**Get it**: Same as Gmail (uses same OAuth)

**Steps**:
1. Same setup as Gmail
2. Enable Calendar API in Google Cloud
3. Use same credentials

**Add to `.env`**:
```
GOOGLE_CALENDAR_CREDENTIALS=your_refresh_token
```

**Free Tier**: 1 million requests/day

---

### 4. NewsAPI - **For news headlines**

**Get it**: https://newsapi.org/

**Steps**:
1. Sign up at https://newsapi.org/register
2. Verify email
3. Copy API key from dashboard
4. Add to `.env`:
   ```
   NEWS_API_KEY=your_newsapi_key
   ```

**Free Tier**: 100 requests/day
**Paid**: $449/month for unlimited (overkill for personal use)

**Alternative**: Use RSS feeds (free) - see below

---

### 5. OpenWeatherMap - **For weather data**

**Get it**: https://openweathermap.org/api

**Steps**:
1. Sign up at https://home.openweathermap.org/users/sign_up
2. Verify email
3. Go to "API keys" tab
4. Copy key (may take 10 mins to activate)
5. Add to `.env`:
   ```
   WEATHER_API_KEY=your_openweather_key
   ```

**Free Tier**: 60 calls/minute, 1M calls/month
**Pricing**: Free tier is more than enough

---

### 6. Google Routes API - **For traffic data**

**Get it**: Google Cloud Console (same project as Gmail)

**Steps**:
1. In Google Cloud Console
2. Enable "Routes API" (the newer v2 API)
3. Create API Key (not OAuth)
4. Configure your commute routes
5. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_google_routes_api_key
   TRAFFIC_API_KEY=your_google_routes_api_key
   COMMUTE_ROUTES=[{"name":"Home to Work","origin":"123 Main St, Marysville, OH 43040","destination":"456 Office St, Marysville, OH 43040"}]
   ```

**Free Tier**: $200/month credit
**Pricing**: $5 per 1000 requests after credit (~40,000 free requests/month)

**See**: [ROUTES_API_SETUP.md](ROUTES_API_SETUP.md) for detailed setup

---

### 7. Todoist API - **For todo lists**

**Get it**: https://todoist.com/app/settings/integrations

**Steps**:
1. Login to Todoist
2. Go to Settings → Integrations
3. Scroll to "API token"
4. Copy token
5. Add to `.env`:
   ```
   TODOIST_API_KEY=your_todoist_token
   ```

**Free Tier**: Full API access on free plan
**Alternative**: Use Microsoft To Do, Google Tasks, or any todo API

---

## 🚀 Quick Setup Order

**Minimum to get started** (with sample data):
- Just run the app! It works without any keys.

**For AI summaries** (recommended):
1. ✅ Get Claude API key (5 mins)
2. Test with sample data

**For real data**:
1. ✅ Claude API key
2. ✅ Gmail + Calendar (15 mins with helper script)
3. ✅ NewsAPI (2 mins)
4. ✅ OpenWeatherMap (5 mins)
5. ⏩ Todoist (optional, 2 mins)
6. ⏩ Google Maps (optional, 5 mins)

Total setup time: ~30-45 minutes for everything

---

## 📦 Alternative Services

### News (instead of NewsAPI):

**RSS Feeds** (Free, unlimited):
```python
# Use feedparser library
import feedparser

# Popular RSS feeds
feeds = [
    'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
    'https://feeds.bbci.co.uk/news/rss.xml',
    'https://www.reddit.com/r/technology/.rss',
]
```

### Todo Lists (alternatives to Todoist):

- **Microsoft To Do**: https://docs.microsoft.com/en-us/graph/api/resources/todo-overview
- **Google Tasks**: https://developers.google.com/tasks
- **Notion**: https://developers.notion.com/

### Email (alternatives to Gmail):

- **Outlook/Microsoft 365**: https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview
- **IMAP** (universal): Use Python `imaplib`

### Weather (alternatives to OpenWeatherMap):

- **WeatherAPI.com**: 1M calls/month free
- **Weather.gov** (US only): Free, no key needed
- **Tomorrow.io**: 500 calls/day free

---

## 🔒 Security Checklist

Before deploying:

- [ ] All keys added to `.env`
- [ ] `.env` in `.gitignore`
- [ ] `credentials.json` in `.gitignore`
- [ ] `token.json` in `.gitignore`
- [ ] No keys committed to git
- [ ] API keys restricted (IP, referrer, API limits)
- [ ] OAuth test users configured
- [ ] Billing alerts set up

---

## 🧪 Testing Each Service

```bash
# Test all services at once
python test_api.py

# Or test individually in Python:
from services.email_service import EmailService
print(EmailService.is_configured())  # Should be True

from services.news_service import NewsService
print(NewsService.is_configured())  # Should be True

# etc...
```

---

## 💰 Cost Estimate

**For personal daily use** (1 digest/day):

| Service | Monthly Calls | Cost |
|---------|---------------|------|
| Claude AI | ~30 | $0.10 - $0.50 |
| Gmail | 30 | Free |
| Calendar | 30 | Free |
| NewsAPI | 30 | Free (100/day limit) |
| Weather | 30 | Free |
| Routes API | 60 | Free ($200 credit, ~$0.60) |
| Todoist | 30 | Free |
| **TOTAL** | | **< $1/month** |

**For production** (multiple users, frequent calls):
- Set up caching with Redis
- Implement rate limiting
- Monitor usage in each API console
- Use batch requests where possible

---

## 📞 Support Links

- **Claude AI**: https://docs.anthropic.com/
- **Google APIs**: https://console.cloud.google.com/
- **NewsAPI**: https://newsapi.org/docs
- **OpenWeatherMap**: https://openweathermap.org/api
- **Todoist**: https://developer.todoist.com/

---

## 🎯 Next Steps

1. Get minimum working setup (Claude + sample data)
2. Test locally
3. Add real integrations one by one
4. Verify each works before moving to next
5. Deploy to server
6. Set up scheduled calls

Good luck! 🚀
