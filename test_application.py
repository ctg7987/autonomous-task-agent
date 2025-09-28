#!/usr/bin/env python3
"""
Simple test script for the Autonomous AI Task Agent
Run this script to verify the application is working correctly.
"""

import asyncio
import websockets
import json
import sys
import requests
from typing import Dict, Any

def test_backend_api() -> bool:
    """Test if the backend API is responding."""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok" and data.get("ws") == "/ws":
                print("✅ Backend API: OK")
                return True
    except Exception as e:
        print(f"❌ Backend API: Failed - {e}")
    return False

def test_frontend() -> bool:
    """Test if the frontend is accessible."""
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200 and "Autonomous Multi-Tool AI Task Agent" in response.text:
            print("✅ Frontend: OK")
            return True
    except Exception as e:
        print(f"❌ Frontend: Failed - {e}")
    return False

async def test_websocket() -> bool:
    """Test WebSocket functionality with a sample query."""
    try:
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            # Test with a simple query
            brief = {"brief": "Test quantum computing research"}
            await websocket.send(json.dumps(brief))
            
            report_received = False
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('event') == 'log':
                        print(f"  📝 {data.get('data', '')}")
                    elif data.get('event') == 'report':
                        report = data.get('data', {})
                        summary = report.get('summary', '')
                        citations = report.get('citations', [])
                        
                        if summary and citations:
                            print("✅ WebSocket: OK")
                            print(f"  📄 Generated summary: {summary[:100]}...")
                            print(f"  🔗 Found {len(citations)} citations")
                            report_received = True
                            break
                except json.JSONDecodeError:
                    print(f"❌ WebSocket: Invalid JSON received")
                    return False
            
            return report_received
            
    except Exception as e:
        print(f"❌ WebSocket: Failed - {e}")
        return False

async def run_tests():
    """Run all tests and report results."""
    print("🧪 Testing Autonomous AI Task Agent")
    print("=" * 50)
    
    # Test backend API
    backend_ok = test_backend_api()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Test WebSocket if backend is available
    websocket_ok = False
    if backend_ok:
        print("\n🔌 Testing WebSocket functionality...")
        websocket_ok = await test_websocket()
    else:
        print("⏭️  Skipping WebSocket test (backend not available)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  Backend API:   {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"  Frontend:      {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"  WebSocket:     {'✅ PASS' if websocket_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok and websocket_ok:
        print("\n🎉 All tests passed! The application is working correctly.")
        print("🌐 Open http://localhost:3000 to use the interface.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the setup:")
        if not backend_ok:
            print("   - Ensure backend is running: uvicorn backend.app:app --reload")
        if not frontend_ok:
            print("   - Ensure frontend is running: cd frontend && npm run dev")
        if backend_ok and not websocket_ok:
            print("   - Check WebSocket connection and server logs")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
