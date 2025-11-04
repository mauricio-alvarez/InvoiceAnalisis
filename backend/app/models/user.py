"""User data models"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserProfile(BaseModel):
    """Model for user business profile"""
    ruc: str = Field(..., description="RUC (Registro Único de Contribuyentes)")
    razon_social: str = Field(..., min_length=1, description="Business legal name", alias="razonSocial")
    representante_legal: str = Field(..., min_length=1, description="Legal representative name", alias="representanteLegal")
    direccion: str = Field(..., min_length=1, description="Business address")
    telefono: Optional[str] = Field(None, description="Phone number")
    
    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
    
    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v: str) -> str:
        """Validate RUC format (11 digits for Peru)"""
        # Remove any spaces or dashes
        ruc_clean = re.sub(r'[\s-]', '', v)
        
        if not ruc_clean.isdigit():
            raise ValueError('RUC must contain only digits')
        
        if len(ruc_clean) != 11:
            raise ValueError('RUC must be exactly 11 digits')
        
        return ruc_clean
    
    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format"""
        if v is None or v == "":
            return None
        
        # Remove spaces and dashes
        phone_clean = re.sub(r'[\s-]', '', v)
        
        if not phone_clean.isdigit():
            raise ValueError('Phone number must contain only digits')
        
        if len(phone_clean) < 7 or len(phone_clean) > 15:
            raise ValueError('Phone number must be between 7 and 15 digits')
        
        return phone_clean


class UserProfileUpdate(BaseModel):
    """Model for updating user profile"""
    ruc: Optional[str] = None
    razon_social: Optional[str] = Field(None, alias="razonSocial")
    representante_legal: Optional[str] = Field(None, alias="representanteLegal")
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    
    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
    
    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v: Optional[str]) -> Optional[str]:
        """Validate RUC format if provided"""
        if v is None:
            return v
        
        ruc_clean = re.sub(r'[\s-]', '', v)
        
        if not ruc_clean.isdigit():
            raise ValueError('RUC must contain only digits')
        
        if len(ruc_clean) != 11:
            raise ValueError('RUC must be exactly 11 digits')
        
        return ruc_clean
    
    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format if provided"""
        if v is None or v == "":
            return None
        
        phone_clean = re.sub(r'[\s-]', '', v)
        
        if not phone_clean.isdigit():
            raise ValueError('Phone number must contain only digits')
        
        if len(phone_clean) < 7 or len(phone_clean) > 15:
            raise ValueError('Phone number must be between 7 and 15 digits')
        
        return phone_clean


class UserResponse(BaseModel):
    """Model for user response"""
    uid: str
    email: str
    email_verified: bool = Field(alias="emailVerified")
    role: str = "user"
    ruc: Optional[str] = None
    razon_social: Optional[str] = Field(None, alias="razonSocial")
    representante_legal: Optional[str] = Field(None, alias="representanteLegal")
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    profile_completed: bool = Field(False, alias="profileCompleted")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    is_active: bool = Field(True, alias="isActive")
    last_login_at: Optional[datetime] = Field(None, alias="lastLoginAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True


class UserListResponse(BaseModel):
    """Model for paginated user list response"""
    users: list[UserResponse]
    total: int
    page: int
    limit: int
