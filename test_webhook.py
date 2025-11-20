"""
Test script for JotForm webhook integration

Run this script to test the webhook endpoint locally
"""
import requests
import json
from utils import generate_test_jotform_data


def test_webhook(url='http://localhost:5000/csd-webhook'):
    """
    Send a test webhook to the local server

    Args:
        url: Webhook endpoint URL
    """
    print("=" * 60)
    print("JotForm Webhook Test Script")
    print("=" * 60)

    # Generate test data
    print("\n1. Generating test JotForm data...")
    test_data = generate_test_jotform_data()

    print("\n2. Test data generated:")
    print(json.dumps(test_data, indent=2))

    # Send webhook
    print(f"\n3. Sending POST request to {url}...")

    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        print(f"\n4. Response received:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            print("\n✓ Webhook test SUCCESSFUL!")
        else:
            print(f"\n✗ Webhook test FAILED with status {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to server.")
        print("   Make sure the Flask app is running: python app.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")

    print("\n" + "=" * 60)


def test_health_check(base_url='http://localhost:5000'):
    """Test the health check endpoint"""
    print("\nTesting health check endpoint...")

    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Health check failed: {str(e)}")


if __name__ == '__main__':
    import sys

    # Check if custom URL provided
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]
    else:
        webhook_url = 'http://localhost:5000/csd-webhook'

    # Extract base URL
    base_url = webhook_url.replace('/csd-webhook', '')

    # Run tests
    test_health_check(base_url)
    print()
    test_webhook(webhook_url)

    print("\nNext steps:")
    print("1. Check the logs/submissions.log file")
    print("2. View the dashboard at http://localhost:5000")
    print("3. Check the database: sqlite3 submissions.db 'SELECT * FROM submissions;'")
