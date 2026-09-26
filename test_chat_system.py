#!/usr/bin/env python3
"""
Test script for the ICQ Chat Bridge System
Tests Web3, OSC, Flask, and chat functionality
"""

import requests
import time
import json
from pythonosc import udp_client

def test_web3_connection():
    """Test Web3 connectivity"""
    print("Testing Web3 connection...")
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/YOUR_INFURA_KEY'))
        print(f"Web3 connected: {w3.is_connected()}")
        return w3.is_connected()
    except Exception as e:
        print(f"Web3 test failed: {e}")
        return False

def test_flask_api():
    """Test Flask chat API"""
    print("Testing Flask API...")
    try:
        # Test chat history endpoint
        response = requests.get('http://localhost:5000/chat/history', timeout=5)
        if response.status_code == 200:
            print("Chat history API: OK")
            return True
        else:
            print(f"Chat history API failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Flask API test failed (server not running?): {e}")
        return False

def test_osc_communication():
    """Test OSC communication"""
    print("Testing OSC communication...")
    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
        client.send_message("/test", [1, 2, 3])
        print("OSC message sent successfully")
        return True
    except Exception as e:
        print(f"OSC test failed: {e}")
        return False

def test_chat_commands():
    """Test chat command processing"""
    print("Testing chat commands...")
    try:
        test_commands = [
            {'message': '/vdmx play', 'sender': 'TestUser'},
            {'message': '/nls test query', 'sender': 'TestUser'},
            {'message': '/browse https://example.com', 'sender': 'TestUser'},
            {'message': 'Hello from test!', 'sender': 'TestUser'}
        ]

        for cmd in test_commands:
            response = requests.post('http://localhost:5000/chat/send',
                                   json=cmd, timeout=5)
            if response.status_code == 200:
                print(f"Command '{cmd['message']}' sent successfully")
            else:
                print(f"Command '{cmd['message']}' failed: {response.status_code}")
                return False
            time.sleep(0.1)

        return True
    except requests.exceptions.RequestException as e:
        print(f"Chat command test failed: {e}")
        return False

def test_prometheus_metrics():
    """Test Prometheus metrics endpoint"""
    print("Testing Prometheus metrics...")
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        if response.status_code == 200:
            print("Prometheus metrics: OK")
            return True
        else:
            print(f"Prometheus metrics failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Prometheus test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing ICQ Chat Bridge System")
    print("=" * 50)

    tests = [
        ("Web3 Connection", test_web3_connection),
        ("Flask API", test_flask_api),
        ("OSC Communication", test_osc_communication),
        ("Chat Commands", test_chat_commands),
        ("Prometheus Metrics", test_prometheus_metrics)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        result = test_func()
        results.append((test_name, result))
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   Result: {status}")

    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All systems operational! Form follows function achieved.")
    else:
        print("⚠️  Some systems need attention. Check configuration and dependencies.")

    return passed == total

if __name__ == "__main__":
    main()
