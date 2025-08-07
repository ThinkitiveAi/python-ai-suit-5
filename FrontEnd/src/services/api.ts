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

// Availability and Appointment Types
export interface TimeSlot {
  id: string;
  date: string;
  startTime: string;
  endTime: string;
  duration: number;
  status: 'available' | 'booked' | 'blocked' | 'tentative' | 'break';
  appointmentType?: string;
  notes?: string;
  isRecurring?: boolean;
  recurringPattern?: 'none' | 'daily' | 'weekly' | 'biweekly' | 'monthly';
  recurringEndDate?: string;
}

export interface Appointment {
  id: string;
  availabilityId: string;
  patientId: string;
  providerId: string;
  appointmentDate: string;
  startTime: string;
  endTime: string;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed' | 'no_show';
  appointmentType: string;
  reason?: string;
  notes?: string;
  patientNotes?: string;
}

export interface AvailabilityStats {
  totalSlots: number;
  availableSlots: number;
  bookedSlots: number;
  blockedSlots: number;
  utilizationRate: number;
  averageBookingTime?: number;
}

export interface AppointmentStats {
  totalAppointments: number;
  scheduledAppointments: number;
  confirmedAppointments: number;
  completedAppointments: number;
  cancelledAppointments: number;
  noShowAppointments: number;
  completionRate: number;
}

// Availability and Appointment API functions
export const availabilityAPI = {
  // Availability CRUD operations
  createAvailability: async (data: Omit<TimeSlot, 'id'> & { providerId: string }): Promise<TimeSlot> => {
    try {
      const response = await api.post('/api/v1/providers/availability/slots', data);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy availability response');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
          id: 'dummy-availability-' + Date.now(),
          date: data.date,
          startTime: data.startTime,
          endTime: data.endTime,
          duration: data.duration,
          status: data.status,
          appointmentType: data.appointmentType,
          notes: data.notes,
          isRecurring: data.isRecurring,
          recurringPattern: data.recurringPattern,
          recurringEndDate: data.recurringEndDate,
        };
      }
      throw error;
    }
  },

  getAvailability: async (availabilityId: string): Promise<TimeSlot | null> => {
    try {
      const response = await api.get(`/api/v1/providers/availability/slots/${availabilityId}`);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, returning null');
        return null;
      }
      throw error;
    }
  },

  getProviderAvailability: async (
    providerId?: string,
    startDate?: string,
    endDate?: string,
    statusFilter?: string
  ): Promise<TimeSlot[]> => {
    try {
      const params = new URLSearchParams();
      if (providerId) params.append('provider_id', providerId);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (statusFilter) params.append('status_filter', statusFilter);

      const response = await api.get(`/api/v1/providers/availability/slots?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy availability data');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Return dummy availability data
        return [
          {
            id: 'dummy-1',
            date: '2024-01-15',
            startTime: '09:00',
            endTime: '10:00',
            duration: 60,
            status: 'available',
            appointmentType: 'Consultation',
          },
          {
            id: 'dummy-2',
            date: '2024-01-15',
            startTime: '10:00',
            endTime: '11:00',
            duration: 60,
            status: 'booked',
            appointmentType: 'Follow-up',
          },
        ];
      }
      throw error;
    }
  },

  updateAvailability: async (availabilityId: string, data: Partial<TimeSlot>): Promise<TimeSlot> => {
    try {
      const response = await api.put(`/api/v1/providers/availability/slots/${availabilityId}`, data);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy update response');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
          id: availabilityId,
          date: data.date || '2024-01-15',
          startTime: data.startTime || '09:00',
          endTime: data.endTime || '10:00',
          duration: data.duration || 60,
          status: data.status || 'available',
          appointmentType: data.appointmentType,
          notes: data.notes,
        };
      }
      throw error;
    }
  },

  deleteAvailability: async (availabilityId: string): Promise<boolean> => {
    try {
      await api.delete(`/api/v1/providers/availability/slots/${availabilityId}`);
      return true;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy delete response');
        await new Promise(resolve => setTimeout(resolve, 1000));
        return true;
      }
      throw error;
    }
  },

  // Appointment CRUD operations
  createAppointment: async (data: Omit<Appointment, 'id'>): Promise<Appointment> => {
    try {
      const response = await api.post('/api/v1/providers/availability/appointments', data);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy appointment response');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
          id: 'dummy-appointment-' + Date.now(),
          availabilityId: data.availabilityId,
          patientId: data.patientId,
          providerId: data.providerId,
          appointmentDate: data.appointmentDate,
          startTime: data.startTime,
          endTime: data.endTime,
          status: data.status,
          appointmentType: data.appointmentType,
          reason: data.reason,
          notes: data.notes,
          patientNotes: data.patientNotes,
        };
      }
      throw error;
    }
  },

  getAppointment: async (appointmentId: string): Promise<Appointment | null> => {
    try {
      const response = await api.get(`/api/v1/providers/availability/appointments/${appointmentId}`);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, returning null');
        return null;
      }
      throw error;
    }
  },

  getProviderAppointments: async (
    providerId?: string,
    startDate?: string,
    endDate?: string,
    statusFilter?: string
  ): Promise<Appointment[]> => {
    try {
      const params = new URLSearchParams();
      if (providerId) params.append('provider_id', providerId);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (statusFilter) params.append('status_filter', statusFilter);

      const response = await api.get(`/api/v1/providers/availability/appointments?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy appointment data');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return [
          {
            id: 'dummy-apt-1',
            availabilityId: 'dummy-1',
            patientId: 'patient-123',
            providerId: 'provider-123',
            appointmentDate: '2024-01-15',
            startTime: '10:00',
            endTime: '11:00',
            status: 'confirmed',
            appointmentType: 'Follow-up',
            reason: 'Regular checkup',
          },
        ];
      }
      throw error;
    }
  },

  updateAppointment: async (appointmentId: string, data: Partial<Appointment>): Promise<Appointment> => {
    try {
      const response = await api.put(`/api/v1/providers/availability/appointments/${appointmentId}`, data);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy update response');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
          id: appointmentId,
          availabilityId: data.availabilityId || 'dummy-1',
          patientId: data.patientId || 'patient-123',
          providerId: data.providerId || 'provider-123',
          appointmentDate: data.appointmentDate || '2024-01-15',
          startTime: data.startTime || '10:00',
          endTime: data.endTime || '11:00',
          status: data.status || 'confirmed',
          appointmentType: data.appointmentType || 'Follow-up',
          reason: data.reason,
          notes: data.notes,
          patientNotes: data.patientNotes,
        };
      }
      throw error;
    }
  },

  deleteAppointment: async (appointmentId: string): Promise<boolean> => {
    try {
      await api.delete(`/api/v1/providers/availability/appointments/${appointmentId}`);
      return true;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy delete response');
        await new Promise(resolve => setTimeout(resolve, 1000));
        return true;
      }
      throw error;
    }
  },

  // Statistics
  getAvailabilityStats: async (
    providerId?: string,
    startDate?: string,
    endDate?: string
  ): Promise<AvailabilityStats> => {
    try {
      const params = new URLSearchParams();
      if (providerId) params.append('provider_id', providerId);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await api.get(`/api/v1/providers/availability/stats/availability?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy stats');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
          totalSlots: 20,
          availableSlots: 12,
          bookedSlots: 6,
          blockedSlots: 2,
          utilizationRate: 30.0,
          averageBookingTime: 45.5,
        };
      }
      throw error;
    }
  },

  getAppointmentStats: async (
    providerId?: string,
    startDate?: string,
    endDate?: string
  ): Promise<AppointmentStats> => {
    try {
      const params = new URLSearchParams();
      if (providerId) params.append('provider_id', providerId);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await api.get(`/api/v1/providers/availability/stats/appointments?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
        console.log('API not available, using dummy stats');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return {
          totalAppointments: 15,
          scheduledAppointments: 3,
          confirmedAppointments: 8,
          completedAppointments: 3,
          cancelledAppointments: 1,
          noShowAppointments: 0,
          completionRate: 20.0,
        };
      }
      throw error;
    }
  },
};

export default api; 