#!/usr/bin/env python3
"""
Test phone number validation directly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.validation_service import ValidationService

def test_phone_formats():
    """Test various phone number formats."""
    
    validation_service = ValidationService()
    
    # Test various phone number formats
    phone_numbers = [
        "+12345678901",           # E.164 format
        "+1 234 567 8901",        # With spaces
        "+1-234-567-8901",        # With dashes
        "+1 (234) 567-8901",      # US format with parentheses
        "+15551234567",           # Simple US format
        "+1 555 123 4567",        # US with spaces
        "15551234567",            # Without +
        "(555) 123-4567",         # US domestic format
        "555-123-4567",           # US domestic format
        "+44 20 7946 0958",       # UK format
        "+91 98765 43210",        # India format
    ]
    
    print("📞 Testing Phone Number Formats")
    print("=" * 50)
    
    for phone in phone_numbers:
        is_valid, message, formatted = validation_service.validate_phone_number(phone)
        status = "✅" if is_valid else "❌"
        print(f"{status} {phone:<20} -> {message}")
        if formatted:
            print(f"   Formatted: {formatted}")
        print()

if __name__ == "__main__":
    test_phone_formats()
