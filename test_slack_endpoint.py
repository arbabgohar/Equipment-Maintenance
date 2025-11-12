"""
Quick test script to verify the Slack endpoint is working
"""

import requests
import json

# Test the health endpoint
print("Testing health endpoint...")
try:
    response = requests.get("http://localhost:5000/health", timeout=5)
    print(f"Health check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"ERROR: Could not connect to server: {e}")
    print("Make sure slack_bot_server.py is running!")
    exit(1)

# Test the Slack command endpoint (simulating Slack's POST request)
print("\nTesting Slack command endpoint...")
test_data = {
    'token': 'test-token',
    'team_id': 'T123456',
    'team_domain': 'test',
    'channel_id': 'C123456',
    'channel_name': 'test',
    'user_id': 'U123456',
    'user_name': 'testuser',
    'command': '/maintenance',
    'text': 'list',
    'response_url': 'https://hooks.slack.com/test',
    'trigger_id': '123456'
}

try:
    response = requests.post("http://localhost:5000/slack/command", data=test_data, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")  # First 500 chars
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*60)
print("If both tests passed, your server is working!")
print("The issue is likely with Slack app configuration.")
print("="*60)

