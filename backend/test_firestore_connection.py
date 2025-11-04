"""Test script to verify Firestore connectivity and permissions"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.dependencies import get_firestore_client
from app.core.config import get_settings

def test_firestore_connection():
    """Test Firestore read/write operations"""
    print("=" * 60)
    print("FIRESTORE CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Get settings
        settings = get_settings()
        print(f"\n✓ Settings loaded")
        print(f"  Project ID: {settings.gcp_project_id}")
        
        # Initialize Firestore client
        db = get_firestore_client()
        print(f"\n✓ Firestore client initialized")
        
        # Test 1: List collections
        print(f"\n[TEST 1] Listing collections...")
        collections = list(db.collections())
        print(f"✓ Found {len(collections)} collections:")
        for col in collections:
            print(f"  - {col.id}")
        
        # Test 2: Try to read from users collection
        print(f"\n[TEST 2] Reading from 'users' collection...")
        users_ref = db.collection('users')
        users = list(users_ref.limit(5).stream())
        print(f"✓ Found {len(users)} users")
        for user_doc in users:
            user_data = user_doc.to_dict()
            print(f"  - {user_doc.id}: {user_data.get('email', 'N/A')}")
        
        # Test 3: Try to write a test document
        print(f"\n[TEST 3] Writing test document to 'users' collection...")
        test_uid = f"test_{datetime.utcnow().timestamp()}"
        test_data = {
            'uid': test_uid,
            'email': 'test@example.com',
            'emailVerified': True,
            'role': 'user',
            'profileCompleted': False,
            'isActive': True,
            'createdAt': datetime.utcnow(),
            'test': True  # Mark as test document
        }
        
        db.collection('users').document(test_uid).set(test_data)
        print(f"✓ Test document created: {test_uid}")
        
        # Test 4: Read back the test document
        print(f"\n[TEST 4] Reading back test document...")
        test_doc = db.collection('users').document(test_uid).get()
        if test_doc.exists:
            print(f"✓ Test document retrieved successfully")
            print(f"  Data: {test_doc.to_dict()}")
        else:
            print(f"✗ Test document not found!")
            return False
        
        # Test 5: Update the test document
        print(f"\n[TEST 5] Updating test document...")
        db.collection('users').document(test_uid).update({
            'profileCompleted': True,
            'updatedAt': datetime.utcnow()
        })
        print(f"✓ Test document updated")
        
        # Test 6: Delete the test document
        print(f"\n[TEST 6] Deleting test document...")
        db.collection('users').document(test_uid).delete()
        print(f"✓ Test document deleted")
        
        # Verify deletion
        test_doc_after = db.collection('users').document(test_uid).get()
        if not test_doc_after.exists:
            print(f"✓ Deletion verified")
        else:
            print(f"✗ Document still exists after deletion!")
        
        print(f"\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nFirestore is working correctly!")
        print("The issue might be in the application logic or deployment.")
        return True
        
    except Exception as e:
        print(f"\n" + "=" * 60)
        print("TEST FAILED ✗")
        print("=" * 60)
        print(f"\nError: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print(f"\nThis indicates a Firestore permission or configuration issue.")
        
        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_firestore_connection()
    sys.exit(0 if success else 1)
