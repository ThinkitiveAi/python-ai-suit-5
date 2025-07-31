import React from 'react';
import { createRouter, createRoute, createRootRoute } from '@tanstack/react-router';
import { MantineProvider } from '@mantine/core';
import PatientLogin from './components/PatientLogin';
import ProviderRegistration from './components/ProviderRegistration';

const theme = {
  primaryColor: 'blue',
  colors: {
    blue: ['#eff6ff', '#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a'] as const,
    green: ['#ecfdf5', '#d1fae5', '#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#059669', '#047857', '#065f46', '#064e3b'] as const,
    teal: ['#f0fdfa', '#ccfbf1', '#99f6e4', '#5eead4', '#2dd4bf', '#14b8a6', '#0d9488', '#0f766e', '#115e59', '#134e4a'] as const,
  },
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
};

// Provider Login Component
const ProviderLogin: React.FC = () => {
  const [loginState, setLoginState] = React.useState({
    isLoading: false,
    error: null as string | null,
    success: false
  });

  const handleLogin = async (values: any) => {
    setLoginState({ isLoading: true, error: null, success: false });
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (values.credential === 'provider@medical.com' && values.password === 'password123') {
        setLoginState({ isLoading: false, error: null, success: true });
        setTimeout(() => {
          console.log('Redirecting to provider dashboard...');
        }, 1500);
      } else {
        setLoginState({ 
          isLoading: false, 
          error: 'Invalid credentials. Please check your email/phone and password.', 
          success: false 
        });
      }
    } catch (error) {
      setLoginState({ 
        isLoading: false, 
        error: 'Network error. Please check your connection and try again.', 
        success: false 
      });
    }
  };

  return (
    <div>Provider Login Component - Use existing component here</div>
  );
};

// Root route
const rootRoute = createRootRoute({
  component: () => (
    <MantineProvider theme={theme}>
      <div id="app">
        {/* Navigation can be added here */}
        <div id="content">
          {/* This is where child routes will render */}
        </div>
      </div>
    </MantineProvider>
  ),
});

// Auth routes
const authRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/auth',
  component: () => <div>Auth Layout</div>,
});

const patientLoginRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/patient-login',
  component: () => (
    <PatientLogin 
      onNavigateToRegistration={() => window.location.href = '/auth/patient-register'}
      onNavigateToProviderLogin={() => window.location.href = '/auth/provider-login'}
    />
  ),
});

const providerLoginRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/provider-login',
  component: ProviderLogin,
});

const providerRegisterRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/provider-register',
  component: () => (
    <ProviderRegistration 
      onNavigateToLogin={() => window.location.href = '/auth/provider-login'}
    />
  ),
});

// Create the route tree
const routeTree = rootRoute.addChildren([
  authRoute.addChildren([
    patientLoginRoute,
    providerLoginRoute,
    providerRegisterRoute,
  ]),
]);

// Create the router
export const router = createRouter({ routeTree }); 