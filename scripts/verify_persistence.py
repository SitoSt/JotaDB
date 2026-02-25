import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

def verify_implementation():
    print("🔍 Verifying JotaDB Persistence Implementation...")
    
    # 1. Verify Models Import
    try:
        from src.core.models import InferenceClient, Conversation, Message, Client
        print("✅ Models imported successfully.")
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return

    # 2. Verify API and Routers
    # Patch init_db to avoid connection attempts during import/startup
    with patch("src.core.database.init_db") as mock_init:
        try:
            from src.api.api import app
            
            # Check if routers are included
            routes = {route.path for route in app.routes}
            expected_routes = [
                "/auth/internal",
                "/auth/client",
                "/chat/conversation",
                "/chat/conversations",
                "/chat/{conversation_id}/messages"
            ]
            
            missing = []
            for expected in expected_routes:
                if expected not in routes:
                    missing.append(expected)
            
            if missing:
                print(f"❌ Missing endpoints: {missing}")
                # Print all routes for debugging
                print("Available routes:")
                for r in routes:
                    print(f" - {r}")
            else:
                print("✅ All expected endpoints are registered.")
                
            # 3. Basic Health Check
            client = TestClient(app)
            response = client.get("/health")
            if response.status_code == 200:
                print("✅ Health check passed.")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ API Verification failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verify_implementation()
