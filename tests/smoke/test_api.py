"""
Test script for SeoulMate K-Drama Recommendation API
Run this after starting the backend server
"""

import requests

API_URL = "http://127.0.0.1:8001"


def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_URL}/")
        print("✅ API Health Check:", response.json())
        return True
    except Exception as e:
        print("❌ API not reachable:", str(e))
        return False


def test_recommendation(title, top_n=5):
    """Test recommendation endpoint"""
    print(f"\n🔍 Getting recommendations for: '{title}'")
    print(f"   Requesting top {top_n} dramas...\n")

    try:
        response = requests.get(
            f"{API_URL}/recommend", params={"title": title, "top_n": top_n}
        )

        if response.status_code == 200:
            data = response.json()
            query = data.get("query", {})
            recommendations = data.get("recommendations", [])

            print(f"📺 Query: {query.get('Title', 'N/A')}")
            print(f"📊 Found {len(recommendations)} recommendations:\n")

            for i, drama in enumerate(recommendations, 1):
                print(f"{i}. {drama.get('Title', 'N/A')}")
                print(f"   Genre: {drama.get('Genre', 'N/A')}")
                print(f"   Rating: {drama.get('rating_value', 'N/A')}")
                print(f"   Episodes: {drama.get('episodes', 'N/A')}")
                desc = drama.get("Description", "N/A")
                if desc != "N/A" and len(desc) > 100:
                    desc = desc[:100] + "..."
                print(f"   Description: {desc}")
                print()

            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("🎬 SeoulMate K-Drama Recommendation API Test Suite")
    print("=" * 60)

    # Test 1: Health check
    if not test_api_health():
        print("\n⚠️  Start the backend server first:")
        print("   cd d:\\Projects\\SeoulMate\\backend")
        print("   python app.py")
        return

    # Test 2: Popular dramas
    test_cases = [
        ("Goblin", 5),
        ("Crash Landing on You", 5),
        ("romantic comedy", 5),
        ("historical drama", 5),
        ("action thriller", 3),
    ]

    for title, top_n in test_cases:
        test_recommendation(title, top_n)
        print("-" * 60)

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    run_tests()
