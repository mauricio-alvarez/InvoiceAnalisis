"""Admin API endpoints"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.core.security import AuthenticatedUser, require_admin
from app.models.user import UserListResponse
from app.models.invoice import InvoiceListResponse, InvoiceStatistics
from app.services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class UserUpdateRequest(BaseModel):
    """Request model for updating user"""
    role: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: AuthenticatedUser = Depends(require_admin)
) -> UserListResponse:
    """
    Get all users (admin only)
    
    Retrieves a paginated list of all registered users.
    Only accessible by users with admin role.
    
    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 50, max: 100)
        current_user: Authenticated admin user
        
    Returns:
        UserListResponse with paginated users
        
    Raises:
        401: Invalid or expired token
        403: Not an admin user
        500: Failed to retrieve users
    """
    firestore_service = FirestoreService()
    return await firestore_service.get_all_users(page=page, limit=limit)


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UserUpdateRequest,
    current_user: AuthenticatedUser = Depends(require_admin)
) -> dict:
    """
    Update user properties (admin only)
    
    Updates user role or account status.
    Only accessible by users with admin role.
    
    Args:
        user_id: User ID to update
        update_data: Fields to update (role, is_active)
        current_user: Authenticated admin user
        
    Returns:
        Dictionary with success message
        
    Raises:
        401: Invalid or expired token
        403: Not an admin user
        404: User not found
        400: Invalid update data
        500: Failed to update user
    """
    firestore_service = FirestoreService()
    
    # Prepare update data
    firestore_update = {}
    
    if update_data.role is not None:
        # Validate role
        if update_data.role not in ['user', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'user' or 'admin'"
            )
        firestore_update['role'] = update_data.role
    
    if update_data.is_active is not None:
        firestore_update['isActive'] = update_data.is_active
    
    if not firestore_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Update user
    await firestore_service.update_user(user_id, firestore_update)
    
    logger.info(f"Admin {current_user.uid} updated user {user_id}")
    
    return {
        'message': 'User updated successfully',
        'userId': user_id,
        'updates': firestore_update
    }


@router.get("/invoices", response_model=InvoiceListResponse)
async def get_all_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format)"),
    current_user: AuthenticatedUser = Depends(require_admin)
) -> InvoiceListResponse:
    """
    Get all invoices with filters (admin only)
    
    Retrieves a paginated list of all invoices across all users.
    Supports filtering by user, status, and date range.
    Only accessible by users with admin role.
    
    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 50, max: 100)
        user_id: Filter by user ID (optional)
        status_filter: Filter by status - processing, processed, or failed (optional)
        start_date: Filter by start date in ISO format (optional)
        end_date: Filter by end date in ISO format (optional)
        current_user: Authenticated admin user
        
    Returns:
        InvoiceListResponse with paginated invoices
        
    Raises:
        401: Invalid or expired token
        403: Not an admin user
        500: Failed to retrieve invoices
    """
    firestore_service = FirestoreService()
    
    # Validate status filter
    if status_filter and status_filter not in ['processing', 'processed', 'failed']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'processing', 'processed', or 'failed'"
        )
    
    return await firestore_service.get_all_invoices(
        page=page,
        limit=limit,
        user_id=user_id,
        status_filter=status_filter,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/statistics", response_model=InvoiceStatistics)
async def get_statistics(
    current_user: AuthenticatedUser = Depends(require_admin)
) -> InvoiceStatistics:
    """
    Get platform statistics (admin only)
    
    Retrieves aggregate statistics including total invoices,
    total amount, success rate, and status counts.
    Only accessible by users with admin role.
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        InvoiceStatistics with aggregate data
        
    Raises:
        401: Invalid or expired token
        403: Not an admin user
        500: Failed to retrieve statistics
    """
    try:
        firestore_service = FirestoreService()
        
        # Get all invoices (without pagination)
        all_invoices = await firestore_service.get_all_invoices(
            page=1,
            limit=10000  # Large limit to get all
        )
        
        # Calculate statistics
        total_invoices = all_invoices.total
        total_amount = 0.0
        processing_count = 0
        processed_count = 0
        failed_count = 0
        
        for invoice in all_invoices.invoices:
            if invoice.total_amount:
                total_amount += invoice.total_amount
            
            if invoice.status == 'processing':
                processing_count += 1
            elif invoice.status == 'processed':
                processed_count += 1
            elif invoice.status == 'failed':
                failed_count += 1
        
        # Calculate success rate
        completed_invoices = processed_count + failed_count
        success_rate = (processed_count / completed_invoices * 100) if completed_invoices > 0 else 0.0
        
        return InvoiceStatistics(
            total_invoices=total_invoices,
            total_amount=total_amount,
            success_rate=success_rate,
            processing_count=processing_count,
            processed_count=processed_count,
            failed_count=failed_count
        )
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
