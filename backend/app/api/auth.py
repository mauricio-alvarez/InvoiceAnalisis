"""Authentication API endpoints"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import (
    verify_firebase_token,
    AuthenticatedUser,
    CurrentUser
)
from app.models.user import (
    UserCreate,
    UserProfile,
    UserProfileUpdate,
    UserResponse
)
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> Dict[str, Any]:
    """
    Register a new user
    
    Creates a new user account in Firebase Auth and Firestore.
    Sends email verification link to the provided email.
    
    Args:
        user_data: User registration data (email, password)
        
    Returns:
        Dictionary with user UID, email, and success message
        
    Raises:
        409: Email already registered
        500: Registration failed
    """
    auth_service = AuthService()
    return await auth_service.register_user(user_data)


@router.post("/verify-token")
async def verify_token(
    current_user: AuthenticatedUser = CurrentUser
) -> Dict[str, Any]:
    """
    Verify Firebase authentication token
    
    Validates the provided Firebase ID token and returns user information.
    
    Args:
        current_user: Authenticated user from token verification
        
    Returns:
        Dictionary with user UID, email, email verification status, and role
        
    Raises:
        401: Invalid or expired token
    """
    return {
        "uid": current_user.uid,
        "email": current_user.email,
        "emailVerified": current_user.email_verified,
        "role": current_user.role
    }


@router.post("/resend-verification")
async def resend_verification(
    current_user: AuthenticatedUser = CurrentUser
) -> Dict[str, str]:
    """
    Resend email verification link
    
    Sends a new email verification link to the user's email address.
    
    Args:
        current_user: Authenticated user from token verification
        
    Returns:
        Dictionary with success message
        
    Raises:
        401: Invalid or expired token
        404: User not found
        500: Failed to send verification email
    """
    auth_service = AuthService()
    return await auth_service.resend_verification_email(
        current_user.uid,
        current_user.email
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: AuthenticatedUser = CurrentUser
) -> UserResponse:
    """
    Get user profile
    
    Retrieves the complete user profile from Firestore.
    
    Args:
        current_user: Authenticated user from token verification
        
    Returns:
        UserResponse with complete profile information
        
    Raises:
        401: Invalid or expired token
        404: User profile not found
        500: Failed to retrieve profile
    """
    auth_service = AuthService()
    return await auth_service.get_user_profile(current_user.uid)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfile,
    current_user: AuthenticatedUser = CurrentUser
) -> UserResponse:
    """
    Update user business profile
    
    Updates the user's business profile with RUC, Razón Social,
    Representante Legal, Dirección, and optional Teléfono.
    Marks profile as completed.
    
    Args:
        profile_data: Business profile data
        current_user: Authenticated user from token verification
        
    Returns:
        Updated UserResponse
        
    Raises:
        401: Invalid or expired token
        400: Validation error (invalid RUC format, etc.)
        404: User not found
        500: Failed to update profile
    """
    auth_service = AuthService()
    return await auth_service.update_user_profile(current_user.uid, profile_data)


@router.patch("/profile", response_model=UserResponse)
async def partial_update_profile(
    profile_data: UserProfileUpdate,
    current_user: AuthenticatedUser = CurrentUser
) -> UserResponse:
    """
    Partially update user profile
    
    Updates only the provided fields in the user's profile.
    
    Args:
        profile_data: Partial profile data to update
        current_user: Authenticated user from token verification
        
    Returns:
        Updated UserResponse
        
    Raises:
        401: Invalid or expired token
        400: Validation error
        404: User not found
        500: Failed to update profile
    """
    auth_service = AuthService()
    return await auth_service.partial_update_user_profile(
        current_user.uid,
        profile_data
    )
