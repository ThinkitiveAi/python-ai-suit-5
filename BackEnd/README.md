# Provider Registration Backend API

A secure and robust FastAPI backend for healthcare provider registration with comprehensive validation, security measures, and audit logging.

## 🚀 Features

### Security & Validation
- **Password Security**: bcrypt hashing with 12+ salt rounds
- **Input Validation**: Comprehensive validation using Pydantic
- **Rate Limiting**: 5 registration attempts per IP per hour
- **Input Sanitization**: Protection against injection attacks
- **Email Verification**: Secure token-based email verification
- **Audit Logging**: Complete audit trail of registration attempts

### Data Validation
- **Email Validation**: Format validation and disposable email detection
- **Phone Number Validation**: International phone number validation
- **Password Strength**: Enforced strong password requirements
- **License Number**: Alphanumeric license number validation
- **Specialization**: Validation against predefined medical specializations
- **Address Validation**: Comprehensive clinic address validation

### Database Support
- **SQL Databases**: SQLite, PostgreSQL, MySQL
- **NoSQL Database**: MongoDB
- **Async Support**: Asynchronous database operations
- **Migration Ready**: Alembic integration for database migrations

## 📁 Project Structure

```
BackEnd/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
│
├── api/v1/endpoints/
│   └── provider.py                 # Provider registration endpoints
│
├── core/
│   ├── config.py                   # Application configuration
│   └── security.py                # Security utilities
│
├── db/
│   ├── database.py                 # Database connection setup
│   └── models/
│       └── provider.py             # Provider database models
│
├── schemas/
│   └── provider.py                 # Pydantic request/response schemas
│
├── services/
│   ├── provider_service.py         # Provider business logic
│   ├── email_service.py            # Email sending service
│   └── validation_service.py       # Validation logic
│
├── middlewares/
│   └── rate_limiting.py            # Rate limiting middleware
│
├── utils/
│   ├── password_utils.py           # Password utilities
│   └── email_utils.py              # Email utilities
│
└── tests/
    ├── unit/
    │   ├── test_validation.py       # Validation tests
    │   └── test_password_utils.py   # Password utility tests
    └── integration/
        └── test_provider_registration.py  # Integration tests
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL/MySQL (optional, SQLite is default)
- MongoDB (optional)

### 1. Install Dependencies

```bash
cd BackEnd
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the BackEnd directory:

```env
# Application Settings
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production
APP_NAME=Provider Registration API
APP_VERSION=1.0.0

# Database Configuration
DATABASE_TYPE=sqlite  # sqlite, postgresql, mysql, mongodb
DATABASE_URL=sqlite:///./providers.db

# For PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost/provider_db

# For MySQL
# DATABASE_URL=mysql://username:password@localhost/provider_db

# For MongoDB (optional, can be used alongside SQL)
# MONGODB_URL=mongodb://localhost:27017

# Security Settings
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=3600

# Email Configuration (for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
FROM_EMAIL=noreply@yourcompany.com

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### 3. Database Setup

For SQLite (default):
```bash
# Database will be created automatically
```

For PostgreSQL:
```bash
# Create database
createdb provider_db

# Install PostgreSQL adapter
pip install psycopg2-binary
```

For MySQL:
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE provider_db;"

# Install MySQL adapter
pip install PyMySQL
```

For MongoDB:
```bash
# Install MongoDB driver
pip install motor

# MongoDB will create collections automatically
```

## 🚀 Running the Application

### Development Server

```bash
cd BackEnd
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs` (development only)
- **ReDoc**: `http://localhost:8000/redoc` (development only)

## 📚 API Endpoints

### Provider Registration

#### POST `/api/v1/provider/register`

Register a new healthcare provider.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "specialization": "Cardiology",
  "license_number": "MD123456",
  "years_of_experience": 10,
  "clinic_address": {
    "street": "123 Medical Center Drive",
    "city": "New York",
    "state": "NY",
    "zip": "10001"
  }
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Provider registered successfully. Please check your email for verification instructions.",
  "data": {
    "provider_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "verification_status": "pending"
  }
}
```

### Utility Endpoints

#### GET `/api/v1/provider/specializations`
Get list of allowed medical specializations.

#### GET `/api/v1/provider/password-requirements`
Get password requirements for client-side validation.

#### GET `/api/v1/provider/health`
Health check endpoint for monitoring.

#### GET `/health`
Application health check.

#### GET `/`
API information and available endpoints.

## 🔒 Security Features

### Password Requirements
- Minimum 8 characters, maximum 128 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*(),.?":{}|<>)
- No repeated characters (more than 2 consecutive)
- No common sequences (123, abc, qwe, etc.)

### Rate Limiting
- Maximum 5 registration attempts per IP per hour
- Automatic IP blocking for repeated violations
- Rate limit headers in responses

### Input Validation
- Email format validation and disposable email detection
- International phone number validation
- Medical license number format validation
- Specialization validation against predefined list
- Comprehensive address validation

### Security Headers
- X-RateLimit-Limit
- X-RateLimit-Remaining
- X-RateLimit-Reset
- Retry-After (when rate limited)

## 🧪 Testing

### Run Unit Tests

```bash
cd BackEnd
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Run All Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html
```

## 📊 Monitoring & Logging

### Audit Logging
All registration attempts are logged with:
- Timestamp
- IP address
- Email address
- Action performed
- Status (success/failure)
- Additional details

### Application Logging
- Structured logging with timestamps
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging
- Error tracking with stack traces

### Health Monitoring
- `/health` endpoint for application health
- `/api/v1/provider/health` for service-specific health
- Database connection monitoring
- Email service status monitoring

## 🚀 Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t provider-registration-api .
docker run -p 8000:8000 provider-registration-api
```

### Production Considerations

1. **Environment Variables**: Use proper environment variables for production
2. **Database**: Use PostgreSQL or MySQL for production
3. **Redis**: Replace in-memory rate limiting with Redis
4. **Email Service**: Configure proper SMTP settings
5. **Monitoring**: Add application monitoring (Prometheus, Grafana)
6. **Load Balancer**: Use nginx or similar for load balancing
7. **SSL/TLS**: Enable HTTPS in production
8. **Secrets Management**: Use proper secrets management (AWS Secrets Manager, etc.)

## 🔧 Configuration

### Allowed Specializations
The following medical specializations are currently supported:
- Cardiology
- Neurology
- Orthopedics
- Pediatrics
- Dermatology
- Psychiatry
- Radiology
- Anesthesiology
- Emergency Medicine
- Internal Medicine
- Surgery
- Obstetrics and Gynecology

### Database Configuration
The application supports multiple database types:
- **SQLite**: For development and testing
- **PostgreSQL**: Recommended for production
- **MySQL**: Alternative production database
- **MongoDB**: Optional NoSQL support

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database URL in environment variables
   - Ensure database server is running
   - Verify credentials and permissions

2. **Email Sending Issues**
   - Check SMTP configuration
   - Verify email credentials
   - Check firewall settings

3. **Rate Limiting Issues**
   - Clear rate limit history for testing
   - Adjust rate limit settings in config
   - Consider using Redis for production

4. **Validation Errors**
   - Check input data format
   - Verify specialization is in allowed list
   - Ensure password meets requirements

### Debug Mode
Enable debug mode by setting `DEBUG=True` in environment variables for detailed error messages and automatic API documentation.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test files for usage examples
