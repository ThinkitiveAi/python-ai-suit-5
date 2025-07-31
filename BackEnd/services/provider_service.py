"""
Provider service containing business logic for provider registration and management.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from db.database import get_sql_db, get_mongodb
from db.models.provider import ProviderSQL, ProviderMongo, AuditLogSQL, AuditLog
from schemas.provider import ProviderRegistrationRequest, ProviderResponse
from services.validation_service import ValidationService
from services.email_service import email_service
from utils.password_utils import PasswordValidator
from core.config import settings
from core.security import security
import uuid

logger = logging.getLogger(__name__)


class ProviderService:
    """Service for provider registration and management operations."""
    
    def __init__(self):
        self.validation_service = ValidationService()
    
    async def register_provider(
        self, 
        provider_data: ProviderRegistrationRequest, 
        client_ip: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Register a new provider with comprehensive validation and security measures.
        
        Args:
            provider_data: Provider registration data
            client_ip: Client IP address for audit logging
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            # Step 1: Comprehensive validation
            validation_result = await self._validate_provider_data(provider_data)
            if not validation_result["is_valid"]:
                await self._log_audit_event(
                    client_ip, provider_data.email, "registration_attempt", 
                    "validation_failed", str(validation_result["errors"])
                )
                return False, {
                    "message": "Validation failed",
                    "errors": validation_result["errors"]
                }
            
            # Step 2: Check for existing provider (email, phone, license)
            uniqueness_check = await self._check_provider_uniqueness(provider_data)
            if not uniqueness_check["is_unique"]:
                await self._log_audit_event(
                    client_ip, provider_data.email, "registration_attempt", 
                    "duplicate_found", uniqueness_check["message"]
                )
                return False, {
                    "message": uniqueness_check["message"],
                    "field": uniqueness_check["field"]
                }
            
            # Step 3: Hash password
            hashed_password = PasswordValidator.hash_password(provider_data.password)
            
            # Step 4: Generate verification token
            verification_token = email_service.generate_verification_token()
            
            # Step 5: Create provider record
            provider_id = await self._create_provider_record(
                provider_data, hashed_password, verification_token
            )
            
            if not provider_id:
                await self._log_audit_event(
                    client_ip, provider_data.email, "registration_attempt", 
                    "database_error", "Failed to create provider record"
                )
                return False, {
                    "message": "Failed to create provider account. Please try again."
                }
            
            # Step 6: Send verification email
            full_name = f"{provider_data.first_name} {provider_data.last_name}"
            email_sent = await email_service.send_verification_email(
                provider_data.email, full_name, verification_token
            )
            
            if not email_sent:
                logger.warning(f"Failed to send verification email to {provider_data.email}")
                # Don't fail registration if email fails, but log it
            
            # Step 7: Log successful registration
            await self._log_audit_event(
                client_ip, provider_data.email, "registration_attempt", 
                "success", f"Provider registered with ID: {provider_id}"
            )
            
            # Step 8: Return success response
            return True, {
                "message": "Provider registered successfully. Please check your email for verification instructions.",
                "data": ProviderResponse(
                    provider_id=str(provider_id),
                    email=provider_data.email,
                    verification_status="pending"
                )
            }
            
        except Exception as e:
            logger.error(f"Error during provider registration: {e}")
            await self._log_audit_event(
                client_ip, provider_data.email, "registration_attempt", 
                "system_error", str(e)
            )
            return False, {
                "message": "An unexpected error occurred. Please try again later."
            }
    
    async def _validate_provider_data(
        self, 
        provider_data: ProviderRegistrationRequest
    ) -> Dict[str, Any]:
        """
        Perform comprehensive validation of provider data.
        
        Args:
            provider_data: Provider registration data
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        # Validate names
        first_name_valid, first_name_error = self.validation_service.validate_name(
            provider_data.first_name, "First name"
        )
        if not first_name_valid:
            errors.append(first_name_error)
        
        last_name_valid, last_name_error = self.validation_service.validate_name(
            provider_data.last_name, "Last name"
        )
        if not last_name_valid:
            errors.append(last_name_error)
        
        # Validate email
        email_valid, email_error = self.validation_service.validate_email(
            provider_data.email
        )
        if not email_valid:
            errors.append(email_error)
        
        # Validate phone number
        phone_valid, phone_error, _ = self.validation_service.validate_phone_number(
            provider_data.phone_number
        )
        if not phone_valid:
            errors.append(phone_error)
        
        # Validate password
        password_valid, password_errors = self.validation_service.validate_password(
            provider_data.password, provider_data.confirm_password
        )
        if not password_valid:
            errors.extend(password_errors)
        
        # Validate specialization
        spec_valid, spec_error = self.validation_service.validate_specialization(
            provider_data.specialization
        )
        if not spec_valid:
            errors.append(spec_error)
        
        # Validate license number
        license_valid, license_error = self.validation_service.validate_license_number(
            provider_data.license_number
        )
        if not license_valid:
            errors.append(license_error)
        
        # Validate years of experience
        exp_valid, exp_error = self.validation_service.validate_years_of_experience(
            provider_data.years_of_experience
        )
        if not exp_valid:
            errors.append(exp_error)
        
        # Validate clinic address
        address_dict = provider_data.clinic_address.dict()
        address_valid, address_errors = self.validation_service.validate_clinic_address(
            address_dict
        )
        if not address_valid:
            errors.extend(address_errors)
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _check_provider_uniqueness(
        self, 
        provider_data: ProviderRegistrationRequest
    ) -> Dict[str, Any]:
        """
        Check if provider email, phone, and license number are unique.
        
        Args:
            provider_data: Provider registration data
            
        Returns:
            Dictionary with uniqueness check results
        """
        try:
            if settings.DATABASE_TYPE == "mongodb":
                return await self._check_uniqueness_mongodb(provider_data)
            else:
                return await self._check_uniqueness_sql(provider_data)
                
        except Exception as e:
            logger.error(f"Error checking provider uniqueness: {e}")
            return {
                "is_unique": False,
                "message": "Unable to verify account uniqueness. Please try again.",
                "field": "system"
            }
    
    async def _check_uniqueness_sql(
        self, 
        provider_data: ProviderRegistrationRequest
    ) -> Dict[str, Any]:
        """Check uniqueness in SQL database."""
        db = next(get_sql_db())
        try:
            # Check email
            existing_email = db.query(ProviderSQL).filter(
                ProviderSQL.email == provider_data.email.lower()
            ).first()
            if existing_email:
                return {
                    "is_unique": False,
                    "message": "An account with this email address already exists",
                    "field": "email"
                }
            
            # Check phone number
            existing_phone = db.query(ProviderSQL).filter(
                ProviderSQL.phone_number == provider_data.phone_number
            ).first()
            if existing_phone:
                return {
                    "is_unique": False,
                    "message": "An account with this phone number already exists",
                    "field": "phone_number"
                }
            
            # Check license number
            existing_license = db.query(ProviderSQL).filter(
                ProviderSQL.license_number == provider_data.license_number.upper()
            ).first()
            if existing_license:
                return {
                    "is_unique": False,
                    "message": "An account with this license number already exists",
                    "field": "license_number"
                }
            
            return {"is_unique": True}
            
        finally:
            db.close()
    
    async def _check_uniqueness_mongodb(
        self, 
        provider_data: ProviderRegistrationRequest
    ) -> Dict[str, Any]:
        """Check uniqueness in MongoDB."""
        db = get_mongodb()
        collection = db[ProviderMongo.get_collection_name()]
        
        # Check email
        existing_email = await collection.find_one(
            {"email": provider_data.email.lower()}
        )
        if existing_email:
            return {
                "is_unique": False,
                "message": "An account with this email address already exists",
                "field": "email"
            }
        
        # Check phone number
        existing_phone = await collection.find_one(
            {"phone_number": provider_data.phone_number}
        )
        if existing_phone:
            return {
                "is_unique": False,
                "message": "An account with this phone number already exists",
                "field": "phone_number"
            }
        
        # Check license number
        existing_license = await collection.find_one(
            {"license_number": provider_data.license_number.upper()}
        )
        if existing_license:
            return {
                "is_unique": False,
                "message": "An account with this license number already exists",
                "field": "license_number"
            }
        
        return {"is_unique": True}
    
    async def _create_provider_record(
        self, 
        provider_data: ProviderRegistrationRequest, 
        hashed_password: str, 
        verification_token: str
    ) -> Optional[str]:
        """
        Create provider record in database.
        
        Args:
            provider_data: Provider registration data
            hashed_password: Hashed password
            verification_token: Email verification token
            
        Returns:
            Provider ID if successful, None otherwise
        """
        try:
            if settings.DATABASE_TYPE == "mongodb":
                return await self._create_provider_mongodb(
                    provider_data, hashed_password, verification_token
                )
            else:
                return await self._create_provider_sql(
                    provider_data, hashed_password, verification_token
                )
                
        except Exception as e:
            logger.error(f"Error creating provider record: {e}")
            return None
    
    async def _create_provider_sql(
        self, 
        provider_data: ProviderRegistrationRequest, 
        hashed_password: str, 
        verification_token: str
    ) -> Optional[str]:
        """Create provider record in SQL database."""
        db = next(get_sql_db())
        try:
            provider_id = uuid.uuid4()
            
            provider = ProviderSQL(
                id=provider_id,
                first_name=provider_data.first_name.strip().title(),
                last_name=provider_data.last_name.strip().title(),
                email=provider_data.email.lower().strip(),
                phone_number=provider_data.phone_number,
                password_hash=hashed_password,
                specialization=provider_data.specialization,
                license_number=provider_data.license_number.upper().strip(),
                years_of_experience=provider_data.years_of_experience,
                clinic_address=provider_data.clinic_address.dict(),
                verification_token=verification_token,
                verification_status="pending",
                is_active=True
            )
            
            db.add(provider)
            db.commit()
            db.refresh(provider)
            
            return str(provider.id)
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating provider: {e}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating provider in SQL: {e}")
            return None
        finally:
            db.close()
    
    async def _create_provider_mongodb(
        self, 
        provider_data: ProviderRegistrationRequest, 
        hashed_password: str, 
        verification_token: str
    ) -> Optional[str]:
        """Create provider record in MongoDB."""
        try:
            db = get_mongodb()
            collection = db[ProviderMongo.get_collection_name()]
            
            provider_doc = ProviderMongo.create_document({
                "first_name": provider_data.first_name.strip().title(),
                "last_name": provider_data.last_name.strip().title(),
                "email": provider_data.email.lower().strip(),
                "phone_number": provider_data.phone_number,
                "password_hash": hashed_password,
                "specialization": provider_data.specialization,
                "license_number": provider_data.license_number.upper().strip(),
                "years_of_experience": provider_data.years_of_experience,
                "clinic_address": provider_data.clinic_address.dict(),
                "verification_token": verification_token,
            })
            
            result = await collection.insert_one(provider_doc)
            
            if result.inserted_id:
                return provider_doc["_id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating provider in MongoDB: {e}")
            return None
    
    async def _log_audit_event(
        self, 
        ip_address: str, 
        email: str, 
        action: str, 
        status: str, 
        details: Optional[str] = None
    ):
        """
        Log audit event for provider registration attempts.
        
        Args:
            ip_address: Client IP address
            email: Provider email
            action: Action performed
            status: Status of the action
            details: Additional details
        """
        try:
            audit_entry = AuditLog.create_audit_entry(
                ip_address, email, action, status, details
            )
            
            if settings.DATABASE_TYPE == "mongodb":
                db = get_mongodb()
                audit_collection = db["audit_logs"]
                await audit_collection.insert_one(audit_entry)
            else:
                db = next(get_sql_db())
                try:
                    audit_log = AuditLogSQL(
                        ip_address=ip_address,
                        email=email,
                        action=action,
                        status=status,
                        details=details
                    )
                    db.add(audit_log)
                    db.commit()
                finally:
                    db.close()
            
            logger.info(f"Audit log created: {action} - {status} for {email}")
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")


# Global provider service instance
provider_service = ProviderService()
