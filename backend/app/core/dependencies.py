"""FastAPI dependencies for Firebase, Firestore, and Cloud Storage clients"""
import os
import json
import logging
from typing import Optional
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud import storage, logging as cloud_logging
from google.cloud.secretmanager import SecretManagerServiceClient

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Singleton Firebase Admin SDK client"""
    _instance: Optional[firebase_admin.App] = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._instance is not None:
            return cls._instance
        
        settings = get_settings()
        
        try:
            # Try to get credentials from Secret Manager first
            if settings.firebase_service_account_secret:
                logger.info("Loading Firebase credentials from Secret Manager")
                client = SecretManagerServiceClient()
                response = client.access_secret_version(
                    name=settings.firebase_service_account_secret
                )
                service_account_info = json.loads(response.payload.data.decode('UTF-8'))
                cred = credentials.Certificate(service_account_info)
            # Fall back to local file
            elif settings.firebase_service_account_path and os.path.exists(
                settings.firebase_service_account_path
            ):
                logger.info("Loading Firebase credentials from file")
                cred = credentials.Certificate(settings.firebase_service_account_path)
            else:
                # Use Application Default Credentials (for Cloud Run)
                logger.info("Using Application Default Credentials")
                cred = credentials.ApplicationDefault()
            
            cls._instance = firebase_admin.initialize_app(cred, {
                'projectId': settings.gcp_project_id,
            })
            logger.info("Firebase Admin SDK initialized successfully")
            return cls._instance
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            raise
    
    @classmethod
    def get_app(cls) -> firebase_admin.App:
        """Get Firebase app instance"""
        if cls._instance is None:
            cls.initialize()
        return cls._instance


@lru_cache()
def get_firestore_client():
    """Get Firestore client instance"""
    FirebaseClient.initialize()
    settings = get_settings()
    db = firestore.client()
    logger.info("Firestore client initialized")
    return db


@lru_cache()
def get_storage_client():
    """Get Cloud Storage client instance"""
    settings = get_settings()
    client = storage.Client(project=settings.gcp_project_id)
    logger.info("Cloud Storage client initialized")
    return client


@lru_cache()
def get_storage_bucket():
    """Get Cloud Storage bucket instance"""
    settings = get_settings()
    client = get_storage_client()
    bucket = client.bucket(settings.storage_bucket_name)
    logger.info(f"Cloud Storage bucket '{settings.storage_bucket_name}' initialized")
    return bucket


def setup_logging():
    """Configure logging with Cloud Logging integration"""
    settings = get_settings()
    
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add Cloud Logging handler in production
    if settings.is_production:
        try:
            client = cloud_logging.Client(project=settings.gcp_project_id)
            client.setup_logging()
            logger.info("Cloud Logging configured")
        except Exception as e:
            logger.warning(f"Failed to setup Cloud Logging: {e}")
    else:
        logger.info("Using local logging (development mode)")


def get_auth_client():
    """Get Firebase Auth client"""
    FirebaseClient.initialize()
    return auth
