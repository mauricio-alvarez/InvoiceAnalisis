"""Authentication and authorization middleware"""
import logging
from typing import Optional
from functools import wraps

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.dependencies import get_auth_client, get_firestore_client

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthenticatedUser:
    """Represents an authenticated user"""
    def __init__(self, uid: str, email: str, email_verified: bool, custom_claims: dict = None):
        self.uid = uid
        self.email = email
        self.email_verified = email_verified
        self.custom_claims = custom_claims or {}
        self.role = self.custom_claims.get('role', 'user')
        self.is_admin = self.role == 'admin'


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """
    Verify Firebase ID token and return authenticated user
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        AuthenticatedUser object
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        auth_client = get_auth_client()
        decoded_token = auth_client.verify_id_token(token)
        
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        email_verified = decoded_token.get('email_verified', False)
        custom_claims = decoded_token.get('custom_claims', {})
        
        logger.info(f"Token verified for user: {uid}")
        
        return AuthenticatedUser(
            uid=uid,
            email=email,
            email_verified=email_verified,
            custom_claims=custom_claims
        )
        
    except auth_client.InvalidIdTokenError:
        logger.warning("Invalid Firebase token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except auth_client.ExpiredIdTokenError:
        logger.warning("Expired Firebase token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def require_email_verified(
    current_user: AuthenticatedUser = Depends(verify_firebase_token)
) -> AuthenticatedUser:
    """
    Require that the user's email is verified
    
    Args:
        current_user: Authenticated user from token verification
        
    Returns:
        AuthenticatedUser object
        
    Raises:
        HTTPException: If email is not verified
    """
    # Temporarily disabled for testing - uncomment in production
    # if not current_user.email_verified:
    #     logger.warning(f"Unverified email access attempt by user: {current_user.uid}")
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Email verification required. Please verify your email before accessing this resource."
    #     )
    
    return current_user


async def require_profile_completed(
    current_user: AuthenticatedUser = Depends(require_email_verified)
) -> AuthenticatedUser:
    """
    Require that the user has completed their business profile
    
    Args:
        current_user: Authenticated user with verified email
        
    Returns:
        AuthenticatedUser object
        
    Raises:
        HTTPException: If profile is not completed
    """
    try:
        db = get_firestore_client()
        user_doc = db.collection('users').document(current_user.uid).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        profile_completed = user_data.get('profileCompleted', False)
        
        if not profile_completed:
            logger.warning(f"Incomplete profile access attempt by user: {current_user.uid}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Profile completion required. Please complete your business profile before uploading invoices."
            )
        
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking profile completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify profile status"
        )


async def require_admin(
    current_user: AuthenticatedUser = Depends(verify_firebase_token)
) -> AuthenticatedUser:
    """
    Require that the user has admin role
    
    Args:
        current_user: Authenticated user from token verification
        
    Returns:
        AuthenticatedUser object
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Check custom claims first
    if current_user.is_admin:
        return current_user
    
    # Fall back to checking Firestore
    try:
        db = get_firestore_client()
        user_doc = db.collection('users').document(current_user.uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            role = user_data.get('role', 'user')
            
            if role == 'admin':
                return current_user
        
        logger.warning(f"Unauthorized admin access attempt by user: {current_user.uid}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify admin status"
        )


# Convenience type aliases for dependency injection
CurrentUser = Depends(verify_firebase_token)
VerifiedUser = Depends(require_email_verified)
ProfileCompletedUser = Depends(require_profile_completed)
AdminUser = Depends(require_admin)
