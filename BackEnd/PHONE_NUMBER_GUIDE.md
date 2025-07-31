# Phone Number Format Guide

## ✅ **Valid Phone Number Formats**

The API accepts international phone numbers in various formats. Here are examples of **valid** formats:

### US Numbers:
- `+12345678901` (E.164 format)
- `+1 234 567 8901` (with spaces)
- `+1-234-567-8901` (with dashes)
- `+1 (234) 567-8901` (with parentheses)

### International Numbers:
- `+44 20 7946 0958` (UK)
- `+91 98765 43210` (India)
- `+49 30 12345678` (Germany)
- `+33 1 42 86 83 26` (France)

## ❌ **Invalid Phone Number Formats**

### Common Issues:
1. **555 Numbers**: `+15551234567` - Reserved for fictional use
2. **Missing Country Code**: `(555) 123-4567` - Must include country code
3. **Invalid Formats**: Numbers that don't conform to international standards

## 🧪 **Testing Phone Numbers**

### For Testing Purposes, Use:
```json
{
  "phone_number": "+12345678901"
}
```

### Real-World Examples:
```json
{
  "phone_number": "+1 234 567 8901"  // US format with spaces
}
```

```json
{
  "phone_number": "+44 20 7946 0958"  // UK format
}
```

## 🔍 **Validation Rules**

The system validates phone numbers using the `phonenumbers` library and checks:

1. **Format Validity**: Must be a valid international phone number
2. **Number Type**: Must be mobile, landline, or fixed-line-or-mobile
3. **Country Code**: Must include a valid country code
4. **Length**: Must meet international standards for the country

## 💡 **Tips**

- Always include the country code (e.g., `+1` for US)
- Avoid using 555 numbers (they're reserved for fictional use)
- The system will automatically format valid numbers to E.164 format
- Both mobile and landline numbers are accepted

## 🚀 **Quick Test**

You can test phone number validation using our test script:

```bash
python3 test_phone.py
```

This will show you which formats are accepted and how they're formatted internally.
