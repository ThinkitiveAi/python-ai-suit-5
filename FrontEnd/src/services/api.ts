import axios from 'axios';

// Base URL for the API
const BASE_URL = 'http://192.168.0.201:8000';

// Dummy credentials for testing
export const DUMMY_CREDENTIALS = {
  provider: {
    email: 'provider@medical.com',
    phone: '+15551234567',
    password: 'password123'
  },
  patient: {
    email: 'patient@healthcare.com',
    phone: '+15559876543',
    password: 'patient123'
  }
};

// Create axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'accept': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Types for API requests and responses
export interface ClinicAddress {
  street: string;
  city: string;
  state: string;
  zip: string;
}

export interface ProviderRegistrationData {
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  password: string;
  confirm_password: string;
  specialization: string;
  license_number: string;
  years_of_experience: number;
  clinic_address: ClinicAddress;
}

export interface ProviderRegistrationResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  specialization: string;
  license_number: string;
  years_of_experience: number;
  clinic_address: ClinicAddress;
  created_at: string;
}

export interface ProviderLoginData {
  identifier: string; // email or phone (changed from credential)
  password: string;
  remember_me?: boolean; // added remember_me field
}

export interface ProviderLoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    specialization: string;
    license_number: string;
  };
}

// API functions
export const providerAPI = {
  register: async (data: ProviderRegistrationData): Promise<ProviderRegistrationResponse> => {
    try {
      const response = await api.post('/api/v1/provider/register', data);
      return response.data;
    } catch (error: any) {
      // If API is not available and using dummy data, return mock response
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy registration response');
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        return {
          id: 'dummy-provider-' + Date.now(),
          email: data.email,
          first_name: data.first_name,
          last_name: data.last_name,
          specialization: data.specialization,
          license_number: data.license_number,
          years_of_experience: data.years_of_experience,
          clinic_address: data.clinic_address,
          created_at: new Date().toISOString(),
        };
      }
      throw error;
    }
  },
  
  login: async (data: ProviderLoginData): Promise<ProviderLoginResponse> => {
    try {
      // Use the correct auth endpoint from the curl command
      const response = await api.post('/api/v1/auth/login', data);
      return response.data;
    } catch (error: any) {
      // If API is not available, check dummy credentials
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, checking dummy credentials');
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Check if credentials match dummy credentials (using identifier instead of credential)
        const isDummyEmail = data.identifier === DUMMY_CREDENTIALS.provider.email && 
                            data.password === DUMMY_CREDENTIALS.provider.password;
        const isDummyPhone = data.identifier === DUMMY_CREDENTIALS.provider.phone && 
                            data.password === DUMMY_CREDENTIALS.provider.password;
        
        if (isDummyEmail || isDummyPhone) {
          return {
            access_token: 'dummy-jwt-token-' + Date.now(),
            token_type: 'Bearer',
            expires_in: 3600,
            user: {
              id: 'dummy-provider-123',
              email: DUMMY_CREDENTIALS.provider.email,
              first_name: 'Dr. John',
              last_name: 'Smith',
              specialization: 'Cardiology',
              license_number: 'MD123456',
            },
          };
        } else {
          // Invalid dummy credentials
          const loginError = new Error('Invalid credentials');
          (loginError as any).response = {
            status: 401,
            data: { detail: 'Invalid credentials. Please check your email/phone and password.' }
          };
          throw loginError;
        }
      }
      throw error;
    }
  },
};

export default api; 