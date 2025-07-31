import React from 'react';
import { createRoute } from '@tanstack/react-router';
import { authRoute } from '../auth';
import PatientLogin from '../../components/PatientLogin';

function PatientLoginPage() {
  return (
    <PatientLogin 
      onNavigateToRegistration={() => console.log('Navigate to patient registration')}
      onNavigateToProviderLogin={() => window.location.href = '/auth/provider-login'}
    />
  );
}

export const patientLoginRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/patient-login',
  component: PatientLoginPage,
}); 