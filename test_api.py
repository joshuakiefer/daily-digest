"""
Quick test script to verify the API is working
Run this after starting the server with: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_quick_digest():
    """Test the quick digest endpoint"""
    print("🔍 Testing quick digest endpoint...")
    response = requests.post(f"{BASE_URL}/digest/quick")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Digest Summary:")
        print("=" * 80)
        print(data.get('summary', 'No summary'))
        print("=" * 80)
        print(f"\n📅 Timestamp: {data.get('timestamp')}")
        print(f"\n🔢 Data collected:")
        for key, value in data.get('details', {}).items():
            if isinstance(value, list):
                print(f"  - {key}: {len(value)} items")
            else:
                print(f"  - {key}: ✓")
    else:
        print(f"Error: {response.text}\n")


def test_custom_digest():
    """Test custom digest with specific parameters"""
    print("🔍 Testing custom digest endpoint...")

    params = {
        "include_email": True,
        "include_news": True,
        "include_calendar": True,
        "include_weather": True,
        "include_traffic": False,
        "include_todos": True,
        "location": "Marysville, OH"
    }

    response = requests.post(f"{BASE_URL}/digest", json=params)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("✅ Custom digest generated successfully\n")
    else:
        print(f"Error: {response.text}\n")


if __name__ == "__main__":
    print("🧪 Daily Digest API Test Suite")
    print("=" * 80)
    print()

    try:
        # Test endpoints
        test_health()
        test_quick_digest()
        test_custom_digest()

        print("✅ All tests completed!")
        print(f"\n📚 View interactive API docs at: {BASE_URL}/docs")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API")
        print("   Make sure the server is running:")
        print("   uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
