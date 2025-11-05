"""Firestore database service for data operations"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import HTTPException, status
from google.cloud.firestore_v1 import FieldFilter

from app.core.dependencies import get_firestore_client
from app.models.user import UserResponse, UserListResponse
from app.models.invoice import InvoiceResponse, InvoiceListResponse

logger = logging.getLogger(__name__)


class FirestoreService:
    """Service for Firestore database operations"""
    
    def __init__(self):
        self.db = get_firestore_client()
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user document in Firestore
        
        Args:
            user_data: User data dictionary
            
        Returns:
            User UID
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            uid = user_data.get('uid')
            if not uid:
                raise ValueError("User UID is required")
            
            self.db.collection('users').document(uid).set(user_data)
            logger.info(f"Created user document: {uid}")
            return uid
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user document by UID
        
        Args:
            uid: User ID
            
        Returns:
            User data dictionary or None if not found
        """
        try:
            user_doc = self.db.collection('users').document(uid).get()
            
            if not user_doc.exists:
                return None
            
            return user_doc.to_dict()
            
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user"
            )
    
    async def update_user(self, uid: str, update_data: Dict[str, Any]) -> None:
        """
        Update user document
        
        Args:
            uid: User ID
            update_data: Data to update
            
        Raises:
            HTTPException: If update fails
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            
            # Check if user exists
            if not user_ref.get().exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user_ref.update(update_data)
            logger.info(f"Updated user: {uid}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    
    async def get_user_invoices(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 50,
        sort_by: str = "uploadedAt",
        order: str = "desc"
    ) -> InvoiceListResponse:
        """
        Get invoices for a specific user with pagination
        
        Args:
            user_id: User ID
            page: Page number (1-indexed)
            limit: Number of items per page
            sort_by: Field to sort by
            order: Sort order (asc or desc)
            
        Returns:
            InvoiceListResponse with paginated invoices
        """
        try:
            # Build query
            query = self.db.collection('invoices').where(
                filter=FieldFilter('userId', '==', user_id)
            )
            
            # Apply sorting
            direction = 'DESCENDING' if order.lower() == 'desc' else 'ASCENDING'
            query = query.order_by(sort_by, direction=direction)
            
            # Get total count
            total = len(list(query.stream()))
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
            
            # Execute query
            docs = query.stream()
            
            invoices = []
            for doc in docs:
                invoice_data = doc.to_dict()
                invoice_data['id'] = doc.id
                
                # Convert Firestore timestamps
                if 'uploadedAt' in invoice_data:
                    invoice_data['uploaded_at'] = invoice_data.pop('uploadedAt')
                if 'processedAt' in invoice_data:
                    invoice_data['processed_at'] = invoice_data.pop('processedAt')
                
                # Convert camelCase to snake_case
                invoice_response_data = {
                    'id': invoice_data.get('id'),
                    'user_id': invoice_data.get('userId'),
                    'file_name': invoice_data.get('fileName'),
                    'storage_url': invoice_data.get('storageUrl'),
                    'status': invoice_data.get('status'),
                    'invoice_number': invoice_data.get('invoiceNumber'),
                    'invoice_date': invoice_data.get('invoiceDate'),
                    'vendor_name': invoice_data.get('vendorName'),
                    'total_amount': invoice_data.get('totalAmount'),
                    'currency': invoice_data.get('currency'),
                    'line_items': invoice_data.get('lineItems'),
                    'uploaded_at': invoice_data.get('uploaded_at'),
                    'processed_at': invoice_data.get('processed_at'),
                    'error_message': invoice_data.get('errorMessage'),
                }
                
                invoices.append(InvoiceResponse(**invoice_response_data))
            
            return InvoiceListResponse(
                invoices=invoices,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to get user invoices: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve invoices"
            )
    
    async def get_all_users(
        self,
        page: int = 1,
        limit: int = 50
    ) -> UserListResponse:
        """
        Get all users with pagination (admin only)
        
        Args:
            page: Page number (1-indexed)
            limit: Number of items per page
            
        Returns:
            UserListResponse with paginated users
        """
        try:
            # Build query
            query = self.db.collection('users').order_by('createdAt', direction='DESCENDING')
            
            # Get total count
            total = len(list(query.stream()))
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)
            
            # Execute query
            docs = query.stream()
            
            users = []
            for doc in docs:
                user_data = doc.to_dict()
                
                # Convert Firestore timestamps
                if 'createdAt' in user_data:
                    user_data['created_at'] = user_data.pop('createdAt')
                if 'lastLoginAt' in user_data:
                    user_data['last_login_at'] = user_data.pop('lastLoginAt')
                
                # Convert camelCase to snake_case
                user_response_data = {
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
                
                users.append(UserResponse(**user_response_data))
            
            return UserListResponse(
                users=users,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve users"
            )
    
    async def get_all_invoices(
        self,
        page: int = 1,
        limit: int = 50,
        user_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> InvoiceListResponse:
        """
        Get all invoices with filters and pagination (admin only)
        
        Args:
            page: Page number (1-indexed)
            limit: Number of items per page
            user_id: Filter by user ID
            status_filter: Filter by status
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            
        Returns:
            InvoiceListResponse with paginated invoices
        """
        try:
            # Build query
            query = self.db.collection('invoices')
            
            # Apply filters
            if user_id:
                query = query.where(filter=FieldFilter('userId', '==', user_id))
            
            if status_filter:
                query = query.where(filter=FieldFilter('status', '==', status_filter))
            
            # Sort by upload date
            query = query.order_by('uploadedAt', direction='DESCENDING')
            
            # Get total count (before pagination)
            all_docs = list(query.stream())
            
            # Apply date filters in memory (Firestore has limitations on range queries)
            if start_date or end_date:
                filtered_docs = []
                for doc in all_docs:
                    doc_data = doc.to_dict()
                    uploaded_at = doc_data.get('uploadedAt')
                    
                    if uploaded_at:
                        # Convert to datetime if it's a Firestore timestamp
                        if hasattr(uploaded_at, 'timestamp'):
                            uploaded_at = datetime.fromtimestamp(uploaded_at.timestamp())
                        
                        if start_date:
                            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                            if uploaded_at < start_dt:
                                continue
                        
                        if end_date:
                            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                            if uploaded_at > end_dt:
                                continue
                    
                    filtered_docs.append(doc)
                
                all_docs = filtered_docs
            
            total = len(all_docs)
            
            # Apply pagination
            offset = (page - 1) * limit
            paginated_docs = all_docs[offset:offset + limit]
            
            invoices = []
            for doc in paginated_docs:
                invoice_data = doc.to_dict()
                invoice_data['id'] = doc.id
                
                # Convert Firestore timestamps
                if 'uploadedAt' in invoice_data:
                    invoice_data['uploaded_at'] = invoice_data.pop('uploadedAt')
                if 'processedAt' in invoice_data:
                    invoice_data['processed_at'] = invoice_data.pop('processedAt')
                
                # Convert camelCase to snake_case
                invoice_response_data = {
                    'id': invoice_data.get('id'),
                    'user_id': invoice_data.get('userId'),
                    'file_name': invoice_data.get('fileName'),
                    'storage_url': invoice_data.get('storageUrl'),
                    'status': invoice_data.get('status'),
                    'invoice_number': invoice_data.get('invoiceNumber'),
                    'invoice_date': invoice_data.get('invoiceDate'),
                    'vendor_name': invoice_data.get('vendorName'),
                    'total_amount': invoice_data.get('totalAmount'),
                    'currency': invoice_data.get('currency'),
                    'line_items': invoice_data.get('lineItems'),
                    'uploaded_at': invoice_data.get('uploaded_at'),
                    'processed_at': invoice_data.get('processed_at'),
                    'error_message': invoice_data.get('errorMessage'),
                }
                
                invoices.append(InvoiceResponse(**invoice_response_data))
            
            return InvoiceListResponse(
                invoices=invoices,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to get all invoices: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve invoices"
            )
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> str:
        """
        Create a new invoice document in Firestore
        
        Args:
            invoice_data: Invoice data dictionary
            
        Returns:
            Invoice document ID
        """
        try:
            doc_ref = self.db.collection('invoices').document()
            invoice_data['id'] = doc_ref.id
            doc_ref.set(invoice_data)
            logger.info(f"Created invoice document: {doc_ref.id}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create invoice"
            )
    
    async def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get invoice document by ID
        
        Args:
            invoice_id: Invoice document ID
            
        Returns:
            Invoice data dictionary or None if not found
        """
        try:
            invoice_doc = self.db.collection('invoices').document(invoice_id).get()
            
            if not invoice_doc.exists:
                return None
            
            invoice_data = invoice_doc.to_dict()
            invoice_data['id'] = invoice_doc.id
            return invoice_data
            
        except Exception as e:
            logger.error(f"Failed to get invoice: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve invoice"
            )
    
    async def update_invoice(self, invoice_id: str, update_data: Dict[str, Any]) -> None:
        """
        Update invoice document
        
        Args:
            invoice_id: Invoice document ID
            update_data: Data to update
        """
        try:
            invoice_ref = self.db.collection('invoices').document(invoice_id)
            
            if not invoice_ref.get().exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invoice not found"
                )
            
            invoice_ref.update(update_data)
            logger.info(f"Updated invoice: {invoice_id}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update invoice: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update invoice"
            )
    
    async def update_invoice_feedback(
        self,
        invoice_id: str,
        field_name: str,
        user_id: str,
        vote: str
    ) -> Dict[str, Any]:
        """
        Update feedback for a specific field in an invoice
        
        Args:
            invoice_id: Invoice document ID
            field_name: Name of the field being rated
            user_id: ID of the user providing feedback
            vote: Vote type (upvote, downvote, or remove)
            
        Returns:
            Updated invoice data
            
        Raises:
            HTTPException: If update fails or invoice not found
        """
        try:
            invoice_ref = self.db.collection('invoices').document(invoice_id)
            invoice_doc = invoice_ref.get()
            
            if not invoice_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invoice not found"
                )
            
            invoice_data = invoice_doc.to_dict()
            
            # Get existing feedback or initialize empty dict
            field_feedback = invoice_data.get('fieldFeedback', {})
            
            if vote == 'remove':
                # Remove feedback for this field
                if field_name in field_feedback:
                    del field_feedback[field_name]
                    logger.info(f"Removed feedback for field {field_name} on invoice {invoice_id}")
            else:
                # Add or update feedback
                field_feedback[field_name] = {
                    'vote': vote,
                    'userId': user_id,
                    'timestamp': datetime.utcnow()
                }
                logger.info(f"Updated feedback for field {field_name} on invoice {invoice_id}: {vote}")
            
            # Update the invoice document
            invoice_ref.update({'fieldFeedback': field_feedback})
            
            # Return updated invoice data
            updated_invoice = invoice_ref.get().to_dict()
            updated_invoice['id'] = invoice_id
            return updated_invoice
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update invoice feedback: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update feedback"
            )
