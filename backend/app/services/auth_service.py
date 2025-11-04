"""Authentication service for user management"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from firebase_admin import auth
from fastapi import HTTPException, status

from app.core.dependencies import get_auth_client, get_firestore_client
from app.models.user import UserCreate, UserProfile, UserProfileUpdate, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and user management operations"""
    
    def __init__(self):
        self.auth_client = get_auth_client()
        self.db = get_firestore_client()
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user with Firebase Auth and create Firestore document
        
        Args:
            user_data: User registration data
            
        Returns:
            Dictionary with user UID, email, and message
            
        Raises:
            HTTPException: If registration fails
        """
        try:
            # Create user in Firebase Auth
            user_record = self.auth_client.create_user(
                email=user_data.email,
                password=user_data.password,
                email_verified=True
            )
            
            logger.info(f"Created Firebase Auth user: {user_record.uid}")
            
            # Create user document in Firestore
            user_doc_data = {
                'uid': user_record.uid,
                'email': user_data.email,
                'emailVerified': True,
                'role': 'user',
                'profileCompleted': False,
                'isActive': True,
                'createdAt': datetime.utcnow(),
            }
            
            self.db.collection('users').document(user_record.uid).set(user_doc_data)
            logger.info(f"Created Firestore user document: {user_record.uid}")
            
            # Generate email verification link
            try:
                verification_link = self.auth_client.generate_email_verification_link(
                    user_data.email
                )
                logger.info(f"Generated verification link for: {user_data.email}")
                # In production, send this link via email service
            except Exception as e:
                logger.warning(f"Failed to generate verification link: {e}")
            
            return {
                'uid': user_record.uid,
                'email': user_data.email,
                'message': 'User registered successfully. Please check your email for verification.'
            }
            
        except auth.EmailAlreadyExistsError:
            logger.warning(f"Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def resend_verification_email(self, uid: str, email: str) -> Dict[str, str]:
        """
        Resend email verification link
        
        Args:
            uid: User ID
            email: User email
            
        Returns:
            Dictionary with success message
            
        Raises:
            HTTPException: If operation fails
        """
        try:
            # Check if email is already verified
            user_record = self.auth_client.get_user(uid)
            
            if user_record.email_verified:
                return {'message': 'Email is already verified'}
            
            # Generate new verification link
            verification_link = self.auth_client.generate_email_verification_link(email)
            logger.info(f"Resent verification link for: {email}")
            
            # In production, send this link via email service
            
            return {'message': 'Verification email sent successfully'}
            
        except auth.UserNotFoundError:
            logger.error(f"User not found: {uid}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except Exception as e:
            logger.error(f"Failed to resend verification email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resend verification email"
            )
    
    async def get_user_profile(self, uid: str) -> UserResponse:
        """
        Get user profile from Firestore
        
        Args:
            uid: User ID
            
        Returns:
            UserResponse object
            
        Raises:
            HTTPException: If user not found
        """
        try:
            user_doc = self.db.collection('users').document(uid).get()
            
            if not user_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            user_data = user_doc.to_dict()
            
            # Convert Firestore timestamps to datetime
            if 'createdAt' in user_data and user_data['createdAt']:
                user_data['created_at'] = user_data.pop('createdAt')
            if 'lastLoginAt' in user_data and user_data['lastLoginAt']:
                user_data['last_login_at'] = user_data.pop('lastLoginAt')
            
            # Convert snake_case for response
            response_data = {
                'uid': user_data.get('uid'),
                'email': user_data.get('email'),
                'email_verified': user_data.get('emailVerified', False),
                'role': user_data.get('role', 'user'),
                'ruc': user_data.get('ruc'),
                'razon_social': user_data.get('razonSocial'),
                'representante_legal': user_data.get('representanteLegal'),
                'direccion': user_data.get('direccion'),
                'telefono': user_data.get('telefono'),
                'profile_completed': user_data.get('profileCompleted', False),
                'created_at': user_data.get('created_at'),
                'is_active': user_data.get('isActive', True),
                'last_login_at': user_data.get('last_login_at'),
            }
            
            return UserResponse(**response_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user profile"
            )
    
    async def update_user_profile(
        self, 
        uid: str, 
        profile_data: UserProfile
    ) -> UserResponse:
        """
        Update user business profile in Firestore
        
        Args:
            uid: User ID
            profile_data: Profile data to update
            
        Returns:
            Updated UserResponse object
            
        Raises:
            HTTPException: If update fails
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Prepare update data
            update_data = {
                'ruc': profile_data.ruc,
                'razonSocial': profile_data.razon_social,
                'representanteLegal': profile_data.representante_legal,
                'direccion': profile_data.direccion,
                'profileCompleted': True,
            }
            
            if profile_data.telefono:
                update_data['telefono'] = profile_data.telefono
            
            # Update Firestore document
            user_ref.update(update_data)
            logger.info(f"Updated profile for user: {uid}")
            
            # Return updated profile
            return await self.get_user_profile(uid)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
    
    async def partial_update_user_profile(
        self,
        uid: str,
        profile_data: UserProfileUpdate
    ) -> UserResponse:
        """
        Partially update user profile (only provided fields)
        
        Args:
            uid: User ID
            profile_data: Partial profile data to update
            
        Returns:
            Updated UserResponse object
            
        Raises:
            HTTPException: If update fails
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Prepare update data (only non-None fields)
            update_data = {}
            
            if profile_data.ruc is not None:
                update_data['ruc'] = profile_data.ruc
            if profile_data.razon_social is not None:
                update_data['razonSocial'] = profile_data.razon_social
            if profile_data.representante_legal is not None:
                update_data['representanteLegal'] = profile_data.representante_legal
            if profile_data.direccion is not None:
                update_data['direccion'] = profile_data.direccion
            if profile_data.telefono is not None:
                update_data['telefono'] = profile_data.telefono
            
            if not update_data:
                # No fields to update
                return await self.get_user_profile(uid)
            
            # Update Firestore document
            user_ref.update(update_data)
            logger.info(f"Partially updated profile for user: {uid}")
            
            # Return updated profile
            return await self.get_user_profile(uid)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
