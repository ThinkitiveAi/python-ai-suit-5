# Healthcare Management System - Frontend

A modern, responsive healthcare management system built with React, TypeScript, and Mantine UI. This frontend application provides separate interfaces for healthcare providers and patients, with comprehensive authentication, registration, and dashboard functionality.

## 🚀 Features

### For Healthcare Providers
- **Secure Registration & Login** - Complete provider onboarding with license verification
- **Professional Dashboard** - Comprehensive provider management interface
- **Patient Management** - View and manage patient records
- **Appointment Scheduling** - Manage availability and appointments
- **Communication Tools** - Secure messaging with patients
- **Billing & Reports** - Financial management and reporting tools
- **Referral System** - Manage patient referrals

### For Patients
- **Easy Registration & Login** - Simple patient onboarding process
- **Personal Dashboard** - Access to medical records and appointments
- **Provider Search** - Find and connect with healthcare providers
- **Appointment Booking** - Schedule appointments with providers
- **Secure Messaging** - Communicate with healthcare providers

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development
- **Mantine UI** - Modern React components library
- **TanStack Router** - Type-safe routing
- **Formik + Yup** - Form handling and validation
- **Axios** - HTTP client for API communication
- **Tabler Icons** - Beautiful icon set

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (version 16.0 or higher)
- **npm** (version 7.0 or higher) or **yarn**
- **Git**

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd FrontEnd
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Start the Development Server
```bash
npm start
# or
yarn start
```

The application will be available at `http://localhost:3000`

### 4. Build for Production
```bash
npm run build
# or
yarn build
```

## 🌐 API Configuration

The frontend is configured to work with a backend API at:
```
Base URL: http://192.168.0.201:8000
```

### API Endpoints Used:
- `POST /api/v1/provider/register` - Provider registration
- `POST /api/v1/provider/login` - Provider authentication

The application includes automatic fallback to dummy data when the API is not available.

## 🔑 Test Credentials

### Provider Login
Use these credentials to test provider functionality:

**Email Login:**
- Email: `provider@medical.com`
- Password: `password123`

**Phone Login:**
- Phone: `+15551234567`
- Password: `password123`

### Patient Login
Use these credentials to test patient functionality:

**Email Login:**
- Email: `patient@healthcare.com`
- Password: `patient123`

**Phone Login:**
- Phone: `+15559876543`
- Password: `patient123`

## 🎯 Usage

### Provider Registration
1. Navigate to the Provider Registration page
2. Fill in all required fields:
   - **Personal Information**: Name, email, phone
   - **Professional Information**: License number, specialization, experience
   - **Practice Information**: Clinic details and address
   - **Account Security**: Strong password
3. Accept terms and conditions
4. Submit registration

### Provider Login
1. Go to Provider Login page
2. Enter email/phone and password
3. Use "Remember me" for persistent sessions
4. Access the provider dashboard

### Patient Registration & Login
1. Navigate to Patient Login/Registration
2. Complete the registration process or login with existing credentials
3. Access patient dashboard and features

## 🏗️ Project Structure

```
src/
├── components/           # Reusable React components
│   ├── PatientLogin.tsx
│   ├── PatientRegistration.tsx
│   ├── ProviderRegistration.tsx
│   └── ProviderLayout.tsx
├── services/            # API services and utilities
│   └── api.ts          # Axios configuration and API calls
├── App.tsx             # Main application component with routing
└── index.tsx           # Application entry point
```

## 🔒 Security Features

- **Input Validation** - Comprehensive form validation using Yup
- **Password Strength** - Real-time password strength indicator
- **Secure Authentication** - JWT token-based authentication
- **HTTPS Ready** - Production-ready security configurations
- **Error Handling** - Comprehensive error handling for API failures

## 🎨 UI/UX Features

- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Dark/Light Theme** - Automatic theme detection and switching
- **Loading States** - Smooth loading indicators for better UX
- **Form Progress** - Visual progress indicators for multi-step forms
- **Accessibility** - WCAG compliant components and navigation
- **Modern Animations** - Smooth transitions and micro-interactions

## 🧪 Development Features

- **TypeScript** - Full type safety throughout the application
- **Hot Reload** - Instant updates during development
- **ESLint + Prettier** - Code quality and formatting
- **Component Testing** - Ready for unit and integration tests
- **API Mocking** - Automatic fallback to dummy data during development

## 🚀 Deployment

### Environment Variables
Create a `.env` file in the root directory:
```env
REACT_APP_API_BASE_URL=http://192.168.0.201:8000
REACT_APP_ENVIRONMENT=production
```

### Build Commands
```bash
# Development build
npm run build:dev

# Production build
npm run build

# Serve production build locally
npm run serve
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 API Integration Status

- ✅ Provider Registration - Fully integrated
- ✅ Provider Login - Fully integrated
- 🔄 Patient Registration - In development
- 🔄 Patient Login - In development
- 🔄 Dashboard APIs - Planned
- 🔄 Appointment APIs - Planned

---

**Note**: This frontend application includes intelligent fallback mechanisms. When the backend API is not available, it automatically uses dummy credentials and mock responses to ensure continuous development and testing capabilities. 