# Configuring Google Routes API for Traffic Data

The traffic service now uses **Google Routes API** (the newer Routes API v2) for more accurate traffic and routing information.

## 🚀 Quick Setup

### 1. Enable Routes API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create one)
3. Navigate to **"APIs & Services"** → **"Library"**
4. Search for **"Routes API"**
5. Click **"Enable"**

### 2. Create API Key

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"API Key"**
3. Copy the API key
4. (Recommended) Click **"Restrict Key"**:
   - **API restrictions**: Select "Routes API"
   - **Application restrictions**: Set IP restrictions or HTTP referrers

### 3. Add to Configuration

Add your API key to `.env`:
```bash
TRAFFIC_API_KEY=your_google_routes_api_key_here
```

### 4. Configure Your Routes

In `.env`, add your commute routes in JSON format:

```bash
COMMUTE_ROUTES=[{"name":"Home to Work","origin":"123 Main St, Marysville, OH 43040","destination":"456 Market St, Marysville, OH 43040"},{"name":"Work to Gym","origin":"456 Market St, Marysville, OH 43040","destination":"789 Fitness Ave, Marysville, OH 43040"}]
```

Or in `config.py` (more readable):
```python
COMMUTE_ROUTES: List[dict] = [
    {
        "name": "Home to Work",
        "origin": "123 Main Street, Marysville, OH 43040",
        "destination": "456 Market Street, Marysville, OH 43040"
    },
    {
        "name": "Work to Gym",
        "origin": "456 Market Street, Marysville, OH 43040",
        "destination": "789 Fitness Avenue, Marysville, OH 43040"
    }
]
```

## 📋 Route Configuration Format

Each route object needs:
- **name**: Descriptive name for the route (e.g., "Home to Office")
- **origin**: Starting address (full address works best)
- **destination**: Ending address (full address works best)

## 🎯 Features

The Routes API provides:
- ✅ **Real-time traffic data** - Current conditions
- ✅ **Alternative routes** - Suggests faster alternatives
- ✅ **Accurate ETAs** - Traffic-aware duration
- ✅ **Distance information** - Miles/kilometers
- ✅ **Traffic levels** - Light, moderate, or heavy

## 📊 Example Response

```json
{
  "location": "Marysville, OH",
  "routes": [
    {
      "name": "Home to Work",
      "distance": "8.3 miles",
      "duration": "25 minutes",
      "traffic_level": "moderate",
      "alternative_route": "Alternative route available, saves 5 minutes",
      "origin": "123 Main St, Marysville, OH 43040",
      "destination": "456 Market St, Marysville, OH 43040"
    }
  ],
  "summary": "Moderate traffic on: Home to Work. Normal commute time expected.",
  "timestamp": "2026-03-18T10:30:00"
}
```

## 💡 Tips

### Address Format
- Use full addresses for best results: `"123 Main St, City, State ZIP"`
- Or use place names: `"Honda of America Mfg, Marysville, OH"`
- Or coordinates: Can also use lat/lng

### Multiple Routes
Add as many routes as you want - the service will check all of them:
```python
COMMUTE_ROUTES = [
    {"name": "Home to Office", "origin": "...", "destination": "..."},
    {"name": "Office to Client", "origin": "...", "destination": "..."},
    {"name": "Home to Gym", "origin": "...", "destination": "..."},
]
```

### Default Location
If no routes are configured, the service will use sample data based on `DEFAULT_LOCATION`.

## 🔧 Testing

Test your configuration:
```bash
# Start the server
uvicorn main:app --reload

# Test traffic endpoint
curl -X POST http://localhost:8000/digest \
  -H "Content-Type: application/json" \
  -d '{"include_traffic": true}'
```

Or use the test script:
```python
from services.traffic_service import TrafficService
import asyncio

async def test():
    service = TrafficService()
    if service.is_configured():
        traffic = await service.fetch_traffic()
        print(traffic)

asyncio.run(test())
```

## 💰 Pricing

**Routes API Pricing** (as of 2026):
- Routes: $5.00 per 1,000 requests
- Routes Advanced: $10.00 per 1,000 requests

**Free tier**: $200 monthly credit (covers ~40,000 basic route requests)

For daily digest (1-2 requests per day):
- Daily: 2 routes × 2 requests = $0.02/day
- Monthly: ~$0.60/month (well within free tier!)

## 🔒 Security

### Restrict Your API Key

1. **API Restrictions**:
   - Only enable Routes API
   - Disable other APIs you don't use

2. **Application Restrictions**:
   - **IP restrictions**: Limit to your server IP
   - **HTTP referrer**: If calling from web app

3. **Usage Quotas**:
   - Set daily quotas to prevent unexpected costs
   - Monitor usage in Cloud Console

### Example Restriction Setup

In Google Cloud Console → Credentials → Edit API Key:
```
API restrictions:
  ☑ Restrict key
  ☑ Routes API

Application restrictions:
  ⦿ IP addresses
  Your server IP: 123.45.67.89
```

## 📖 API Documentation

- [Routes API Overview](https://developers.google.com/maps/documentation/routes)
- [ComputeRoutes Method](https://developers.google.com/maps/documentation/routes/compute_route_directions)
- [Pricing Details](https://developers.google.com/maps/documentation/routes/usage-and-billing)

## 🐛 Troubleshooting

### "API key not valid"
- Verify the key is correct in `.env`
- Check that Routes API is enabled
- Wait a few minutes after enabling (propagation time)

### "Address not found"
- Use more complete addresses
- Try adding city and state
- Test addresses in Google Maps first

### "No routes found"
- Verify origin and destination are valid addresses
- Check that they're in supported regions
- Ensure addresses are reachable by car

### Empty traffic data
- Check `COMMUTE_ROUTES` is configured correctly
- Verify JSON format is valid
- Check application logs for errors

## 🚀 Advanced Configuration

### Custom Travel Modes
Modify `traffic_service.py` to support other modes:
```python
"travelMode": "DRIVE"  # or "BICYCLE", "WALK", "TWO_WHEELER"
```

### Route Preferences
```python
"routingPreference": "TRAFFIC_AWARE"  # or "TRAFFIC_AWARE_OPTIMAL"
```

### Avoid Tolls/Highways
```python
"routeModifiers": {
    "avoidTolls": True,
    "avoidHighways": True,
    "avoidFerries": True
}
```

---

Ready to get real-time traffic data for your daily commute! 🚗💨
