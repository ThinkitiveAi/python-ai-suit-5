import React from 'react';
import { createRoute } from '@tanstack/react-router';
import { authRoute } from '../auth';
import PatientRegistration from '../../components/PatientRegistration';

function PatientRegistrationPage() {
  return (
    <PatientRegistration 
      onNavigateToLogin={() => window.location.href = '/auth/patient-login'}
    />
  );
}

export const patientRegisterRoute = createRoute({
  getParentRoute: () => authRoute,
  path: '/patient-register',
  component: PatientRegistrationPage,
}); 