"""Tests for authentication service"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.auth_service import AuthService
from app.models.user import UserCreate, UserProfile


@pytest.fixture
def auth_service():
    """Create auth service instance with mocked dependencies"""
    with patch('app.services.auth_service.get_auth_client'), \
         patch('app.services.auth_service.get_firestore_client'):
        service = AuthService()
        service.auth_client = Mock()
        service.db = Mock()
        return service


@pytest.mark.asyncio
async def test_register_user_success(auth_service):
    """Test successful user registration"""
    # Mock Firebase Auth user creation
    mock_user_record = Mock()
    mock_user_record.uid = 'test-uid-123'
    auth_service.auth_client.create_user.return_value = mock_user_record
    
    # Mock Firestore document creation
    mock_doc_ref = Mock()
    auth_service.db.collection.return_value.document.return_value = mock_doc_ref
    
    # Test registration
    user_data = UserCreate(email='test@example.com', password='password123')
    result = await auth_service.register_user(user_data)
    
    # Assertions
    assert result['uid'] == 'test-uid-123'
    assert result['email'] == 'test@example.com'
    assert 'message' in result
    auth_service.auth_client.create_user.assert_called_once()
    mock_doc_ref.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_profile_success(auth_service):
    """Test retrieving user profile"""
    # Mock Firestore document
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        'uid': 'test-uid',
        'email': 'test@example.com',
        'emailVerified': True,
        'role': 'user',
        'profileCompleted': False,
        'isActive': True,
        'createdAt': datetime.utcnow()
    }
    auth_service.db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Test profile retrieval
    profile = await auth_service.get_user_profile('test-uid')
    
    # Assertions
    assert profile.uid == 'test-uid'
    assert profile.email == 'test@example.com'
    assert profile.email_verified is True


@pytest.mark.asyncio
async def test_update_user_profile_success(auth_service):
    """Test updating user profile"""
    # Mock Firestore document
    mock_doc = Mock()
    mock_doc.exists = True
    mock_doc_ref = Mock()
    mock_doc_ref.get.return_value = mock_doc
    auth_service.db.collection.return_value.document.return_value = mock_doc_ref
    
    # Mock get_user_profile to return updated profile
    with patch.object(auth_service, 'get_user_profile') as mock_get_profile:
        mock_get_profile.return_value = Mock(
            uid='test-uid',
            ruc='12345678901',
            razon_social='Test Company'
        )
        
        # Test profile update
        profile_data = UserProfile(
            ruc='12345678901',
            razon_social='Test Company',
            representante_legal='John Doe',
            direccion='123 Test St'
        )
        result = await auth_service.update_user_profile('test-uid', profile_data)
        
        # Assertions
        mock_doc_ref.update.assert_called_once()
        assert result.uid == 'test-uid'
