import React, { useState, useRef } from 'react';
import {
  Container,
  Paper,
  Title,
  Text,
  TextInput,
  PasswordInput,
  Button,
  Select,
  Checkbox,
  Stack,
  Group,
  Box,
  Center,
  Alert,
  Progress,
  Divider,
  Avatar,
  SimpleGrid,
  FileInput,
  Modal,
  Anchor,
  BackgroundImage,
  Tooltip,
  ActionIcon,
  Stepper,
  Card,
} from '@mantine/core';
import {
  IconUser,
  IconMail,
  IconPhone,
  IconLock,
  IconHeart,
  IconUpload,
  IconCheck,
  IconAlertCircle,
  IconEye,
  IconEyeOff,
  IconMapPin,
  IconCalendar,
  IconShieldCheck,
  IconInfoCircle,
  IconUserPlus,
  IconHome,
  IconEmergencyBed,
  IconChevronRight,
  IconChevronLeft,
} from '@tabler/icons-react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';

// Gender options with inclusive choices
const GENDER_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer-not-to-say', label: 'Prefer not to say' },
];

// Relationship options for emergency contact
const RELATIONSHIP_OPTIONS = [
  'Spouse/Partner',
  'Parent',
  'Child',
  'Sibling',
  'Grandparent',
  'Friend',
  'Guardian',
  'Other Family',
  'Caregiver',
  'Other',
];

// US States (can be expanded for international)
const US_STATES = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
  'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
  'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
  'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
  'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
  'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
  'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
  'Wisconsin', 'Wyoming'
];

// Validation schema
const patientRegistrationValidationSchema = Yup.object({
  // Personal Information
  firstName: Yup.string()
    .required('First name is required')
    .min(2, 'First name must be at least 2 characters')
    .max(50, 'First name must be less than 50 characters'),
  lastName: Yup.string()
    .required('Last name is required')
    .min(2, 'Last name must be at least 2 characters')
    .max(50, 'Last name must be less than 50 characters'),
  email: Yup.string()
    .required('Email address is required')
    .email('Please enter a valid email address'),
  phone: Yup.string()
    .required('Phone number is required')
    .matches(/^[\+]?[1-9][\d]{0,15}$/, 'Please enter a valid phone number'),
  dateOfBirth: Yup.date()
    .required('Date of birth is required')
    .max(new Date(), 'Date of birth cannot be in the future')
    .test('age', 'You must be at least 13 years old to register', function(value) {
      if (!value) return false;
      const today = new Date();
      const birthDate = new Date(value);
      const age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        return age - 1 >= 13;
      }
      return age >= 13;
    }),
  gender: Yup.string()
    .required('Please select your gender'),
  
  // Address Information
  streetAddress: Yup.string()
    .required('Street address is required'),
  city: Yup.string()
    .required('City is required'),
  state: Yup.string()
    .required('State is required'),
  zipCode: Yup.string()
    .required('ZIP code is required')
    .matches(/^\d{5}(-\d{4})?$/, 'Please enter a valid ZIP code'),
  
  // Emergency Contact
  emergencyContactName: Yup.string()
    .required('Emergency contact name is required'),
  emergencyRelationship: Yup.string()
    .required('Please specify your relationship to emergency contact'),
  emergencyPhone: Yup.string()
    .required('Emergency contact phone is required')
    .matches(/^[\+]?[1-9][\d]{0,15}$/, 'Please enter a valid phone number')
    .test('different-phone', 'Emergency contact phone must be different from your phone', function(value) {
      return value !== this.parent.phone;
    }),
  
  // Account Security
  password: Yup.string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, 
      'Password must contain uppercase, lowercase, number, and special character'),
  confirmPassword: Yup.string()
    .required('Please confirm your password')
    .oneOf([Yup.ref('password')], 'Passwords must match'),
  
  // Legal
  agreeToTerms: Yup.boolean()
    .oneOf([true], 'You must agree to the terms and conditions'),
  agreeToPrivacy: Yup.boolean()
    .oneOf([true], 'You must agree to the privacy policy'),
});

interface PatientRegistrationFormValues {
  // Personal Information
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: Date | null;
  gender: string;
  profilePhoto: File | null;
  
  // Address Information
  streetAddress: string;
  city: string;
  state: string;
  zipCode: string;
  
  // Emergency Contact
  emergencyContactName: string;
  emergencyRelationship: string;
  emergencyPhone: string;
  
  // Account Security
  password: string;
  confirmPassword: string;
  
  // Legal
  agreeToTerms: boolean;
  agreeToPrivacy: boolean;
}

interface PatientRegistrationState {
  isLoading: boolean;
  error: string | null;
  success: boolean;
  currentStep: number;
}

interface PatientRegistrationProps {
  onNavigateToLogin?: () => void;
}

const PatientRegistration: React.FC<PatientRegistrationProps> = ({ onNavigateToLogin }) => {
  const [registrationState, setRegistrationState] = useState<PatientRegistrationState>({
    isLoading: false,
    error: null,
    success: false,
    currentStep: 0,
  });
  
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [profilePhotoPreview, setProfilePhotoPreview] = useState<string | null>(null);
  const [savedData, setSavedData] = useState<Partial<PatientRegistrationFormValues>>({});

  const initialValues: PatientRegistrationFormValues = {
    firstName: savedData.firstName || '',
    lastName: savedData.lastName || '',
    email: savedData.email || '',
    phone: savedData.phone || '',
    dateOfBirth: savedData.dateOfBirth || null,
    gender: savedData.gender || '',
    profilePhoto: null,
    streetAddress: savedData.streetAddress || '',
    city: savedData.city || '',
    state: savedData.state || '',
    zipCode: savedData.zipCode || '',
    emergencyContactName: savedData.emergencyContactName || '',
    emergencyRelationship: savedData.emergencyRelationship || '',
    emergencyPhone: savedData.emergencyPhone || '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
    agreeToPrivacy: false,
  };

  const handleRegistration = async (values: PatientRegistrationFormValues) => {
    setRegistrationState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Mock registration logic - check for existing email
      if (values.email === 'existing@patient.com') {
        setRegistrationState(prev => ({
          ...prev,
          isLoading: false,
          error: 'An account with this email already exists. Please use a different email or try signing in.',
        }));
        return;
      }
      
      console.log('Patient registration data:', values);
      
      setRegistrationState({
        isLoading: false,
        error: null,
        success: true,
        currentStep: 4,
      });
    } catch (error) {
      setRegistrationState(prev => ({
        ...prev,
        isLoading: false,
        error: 'Registration failed. Please check your connection and try again.',
      }));
    }
  };

  const handlePhotoUpload = (file: File | null, setFieldValue: any) => {
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
      }
      
      setFieldValue('profilePhoto', file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setProfilePhotoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const getPasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (/[a-z]/.test(password)) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/\d/.test(password)) strength += 12.5;
    if (/[@$!%*?&]/.test(password)) strength += 12.5;
    return strength;
  };

  const getPasswordStrengthColor = (strength: number) => {
    if (strength < 50) return 'red';
    if (strength < 75) return 'yellow';
    return 'green';
  };

  const getProgressValue = (values: PatientRegistrationFormValues, currentStep: number) => {
    const stepProgress = (currentStep / 3) * 100;
    return Math.min(stepProgress, 100);
  };

  // Auto-save functionality
  const handleAutoSave = (values: PatientRegistrationFormValues) => {
    setSavedData(values);
    localStorage.setItem('patientRegistrationData', JSON.stringify(values));
  };

  // Format phone number as user types
  const formatPhoneNumber = (value: string) => {
    const phoneNumber = value.replace(/[^\d]/g, '');
    const phoneNumberLength = phoneNumber.length;
    
    if (phoneNumberLength < 4) return phoneNumber;
    if (phoneNumberLength < 7) {
      return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3)}`;
    }
    return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3, 6)}-${phoneNumber.slice(6, 10)}`;
  };

  return (
    <BackgroundImage
      src="data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23e8f5e8' fill-opacity='0.2'%3E%3Cpath d='M50 50c0-13.807-11.193-25-25-25s-25 11.193-25 25 11.193 25 25 25 25-11.193 25-25zm25 0c0-13.807-11.193-25-25-25s-25 11.193-25 25 11.193 25 25 25 25-11.193 25-25z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 50%, #fefce8 100%)',
      }}
    >
      <Container size="md" py={40}>
        <Center>
          <Paper
            shadow="lg"
            p={40}
            radius="xl"
            style={{
              width: '100%',
              maxWidth: 700,
              background: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
            }}
          >
            {/* Welcome Header */}
            <Stack align="center" mb={40}>
              <Box
                style={{
                  background: 'linear-gradient(135deg, #3b82f6 0%, #10b981 100%)',
                  borderRadius: '50%',
                  padding: 20,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)',
                }}
              >
                <IconHeart size={36} color="white" />
              </Box>
              <Title order={1} size="h1" fw={600} c="dark.8" ta="center">
                Welcome to Our Healthcare Family
              </Title>
              <Text size="lg" c="dimmed" ta="center" maw={500}>
                Create your patient account to access personalized healthcare services, 
                book appointments, and connect with your care team
              </Text>
            </Stack>

            {/* Success State */}
            {registrationState.success && (
              <Alert
                icon={<IconCheck size={18} />}
                title="Welcome to Our Healthcare Community!"
                color="teal"
                mb="xl"
                radius="lg"
                style={{
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                }}
              >
                <Stack gap="sm">
                  <Text size="sm">
                    🎉 Your account has been created successfully! We've sent a welcome email with next steps.
                  </Text>
                  <Text size="sm">
                    📧 Please check your email to verify your account and complete your setup.
                  </Text>
                  <Group mt="md">
                    <Button 
                      size="sm" 
                      variant="light" 
                      color="teal"
                      onClick={onNavigateToLogin}
                      leftSection={<IconUserPlus size={16} />}
                    >
                      Sign In Now
                    </Button>
                    <Button size="sm" variant="outline" color="teal">
                      Check Email
                    </Button>
                  </Group>
                </Stack>
              </Alert>
            )}

            {/* Error State */}
            {registrationState.error && (
              <Alert
                icon={<IconAlertCircle size={18} />}
                title="We Need Your Help"
                color="orange"
                mb="xl"
                radius="lg"
                style={{
                  backgroundColor: 'rgba(251, 146, 60, 0.1)',
                  border: '1px solid rgba(251, 146, 60, 0.2)',
                }}
              >
                <Stack gap="sm">
                  <Text size="sm">
                    {registrationState.error}
                  </Text>
                  <Group gap="xs">
                    <Anchor size="sm" c="orange.7" fw={500}>
                      Contact Support
                    </Anchor>
                    <Text size="sm" c="dimmed">•</Text>
                    <Anchor size="sm" c="orange.7" fw={500}>
                      Try Again
                    </Anchor>
                  </Group>
                </Stack>
              </Alert>
            )}

            {!registrationState.success && (
              <Formik
                initialValues={initialValues}
                validationSchema={patientRegistrationValidationSchema}
                onSubmit={handleRegistration}
              >
                {({ values, errors, touched, setFieldValue }) => {
                  const progressValue = getProgressValue(values, registrationState.currentStep);
                  const passwordStrength = getPasswordStrength(values.password);
                  
                  return (
                    <Form>
                      {/* Progress Indicator */}
                      <Box mb="xl">
                        <Group justify="space-between" mb="xs">
                          <Text size="sm" fw={500} c="dark.7">
                            Registration Progress
                          </Text>
                          <Text size="sm" c="dimmed">
                            {Math.round(progressValue)}% Complete
                          </Text>
                        </Group>
                        <Progress 
                          value={progressValue} 
                          color="teal" 
                          size="lg" 
                          radius="xl"
                          style={{
                            background: 'rgba(16, 185, 129, 0.1)',
                          }}
                        />
                        <Text size="xs" c="dimmed" mt="xs" ta="center">
                          Your progress is automatically saved as you go
                        </Text>
                      </Box>

                      <Stack gap="xl">
                        {/* Personal Information Section */}
                        <Card shadow="sm" padding="lg" radius="lg" withBorder>
                          <Group mb="md">
                            <IconUser size={24} color="#3b82f6" />
                            <Title order={2} size="h3" c="dark.7">
                              Tell Us About Yourself
                            </Title>
                          </Group>
                          
                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
                            <Field name="firstName">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="First Name"
                                  placeholder="Enter your first name"
                                  error={touched.firstName && errors.firstName}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#3b82f6',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                            
                            <Field name="lastName">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Last Name"
                                  placeholder="Enter your last name"
                                  error={touched.lastName && errors.lastName}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#3b82f6',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" mt="md">
                            <Field name="email">
                              {({ field }: any) => (
                                <Box>
                                  <Group gap="xs" mb="xs">
                                    <Text size="sm" fw={500} c="dark.7">
                                      Email Address
                                    </Text>
                                    <Tooltip
                                      label="We'll use this to send appointment reminders and health updates"
                                      position="top"
                                      withArrow
                                    >
                                      <ActionIcon variant="subtle" size="xs" color="gray">
                                        <IconInfoCircle size={14} />
                                      </ActionIcon>
                                    </Tooltip>
                                  </Group>
                                  <TextInput
                                    {...field}
                                    placeholder="your.email@example.com"
                                    leftSection={<IconMail size={18} />}
                                    error={touched.email && errors.email}
                                    disabled={registrationState.isLoading}
                                    size="lg"
                                    radius="lg"
                                    required
                                    styles={{
                                      input: {
                                        backgroundColor: '#fafafa',
                                        '&:focus': {
                                          backgroundColor: '#ffffff',
                                          borderColor: '#3b82f6',
                                        }
                                      }
                                    }}
                                  />
                                </Box>
                              )}
                            </Field>
                            
                            <Field name="phone">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Phone Number"
                                  placeholder="(555) 123-4567"
                                  leftSection={<IconPhone size={18} />}
                                  error={touched.phone && errors.phone}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  onChange={(event) => {
                                    const formatted = formatPhoneNumber(event.target.value);
                                    setFieldValue('phone', formatted);
                                  }}
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#3b82f6',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" mt="md">
                            <Field name="dateOfBirth">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Date of Birth"
                                  placeholder="MM/DD/YYYY"
                                  leftSection={<IconCalendar size={18} />}
                                  error={touched.dateOfBirth && errors.dateOfBirth}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  type="date"
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#3b82f6',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                            
                            <Field name="gender">
                              {({ field }: any) => (
                                <Select
                                  {...field}
                                  label="Gender"
                                  placeholder="Select your gender"
                                  data={GENDER_OPTIONS}
                                  error={touched.gender && errors.gender}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#3b82f6',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          {/* Profile Photo Upload */}
                          <Box mt="md">
                            <Text size="sm" fw={500} mb="xs" c="dark.7">
                              Profile Photo (Optional)
                            </Text>
                            <Group>
                              <Avatar
                                src={profilePhotoPreview}
                                size={80}
                                radius="lg"
                                style={{ 
                                  border: '2px dashed #cbd5e1',
                                  backgroundColor: '#f8fafc',
                                }}
                              >
                                <IconUser size={40} color="#94a3b8" />
                              </Avatar>
                              <FileInput
                                placeholder="Upload a friendly photo (Optional)"
                                accept="image/*"
                                leftSection={<IconUpload size={18} />}
                                onChange={(file) => handlePhotoUpload(file, setFieldValue)}
                                disabled={registrationState.isLoading}
                                style={{ flex: 1 }}
                                size="lg"
                                radius="lg"
                                styles={{
                                  input: {
                                    backgroundColor: '#fafafa',
                                    '&:focus': {
                                      backgroundColor: '#ffffff',
                                      borderColor: '#3b82f6',
                                    }
                                  }
                                }}
                              />
                            </Group>
                            <Text size="xs" c="dimmed" mt="xs">
                              📸 A friendly photo helps your care team recognize you. Max 5MB, JPG/PNG format.
                            </Text>
                          </Box>
                        </Card>

                        {/* Address Information Section */}
                        <Card shadow="sm" padding="lg" radius="lg" withBorder>
                          <Group mb="md">
                            <IconHome size={24} color="#10b981" />
                            <Title order={2} size="h3" c="dark.7">
                              Where Can We Reach You?
                            </Title>
                          </Group>
                          
                          <Field name="streetAddress">
                            {({ field }: any) => (
                              <TextInput
                                {...field}
                                label="Street Address"
                                placeholder="123 Main Street, Apt 4B"
                                leftSection={<IconMapPin size={18} />}
                                error={touched.streetAddress && errors.streetAddress}
                                disabled={registrationState.isLoading}
                                size="lg"
                                radius="lg"
                                required
                                mb="md"
                                styles={{
                                  input: {
                                    backgroundColor: '#fafafa',
                                    '&:focus': {
                                      backgroundColor: '#ffffff',
                                      borderColor: '#10b981',
                                    }
                                  }
                                }}
                              />
                            )}
                          </Field>

                          <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
                            <Field name="city">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="City"
                                  placeholder="Your city"
                                  error={touched.city && errors.city}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#10b981',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                            
                            <Field name="state">
                              {({ field }: any) => (
                                <Select
                                  {...field}
                                  label="State"
                                  placeholder="Select state"
                                  data={US_STATES}
                                  error={touched.state && errors.state}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  searchable
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#10b981',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                            
                            <Field name="zipCode">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="ZIP Code"
                                  placeholder="12345"
                                  error={touched.zipCode && errors.zipCode}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#10b981',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                          </SimpleGrid>
                        </Card>

                        {/* Emergency Contact Section */}
                        <Card shadow="sm" padding="lg" radius="lg" withBorder>
                          <Group mb="md">
                            <IconEmergencyBed size={24} color="#f59e0b" />
                            <Box>
                              <Title order={2} size="h3" c="dark.7">
                                Emergency Contact
                              </Title>
                              <Text size="sm" c="dimmed">
                                Someone we can contact in case of emergency
                              </Text>
                            </Box>
                          </Group>
                          
                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
                            <Field name="emergencyContactName">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Emergency Contact Name"
                                  placeholder="Full name of emergency contact"
                                  error={touched.emergencyContactName && errors.emergencyContactName}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#f59e0b',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                            
                            <Field name="emergencyRelationship">
                              {({ field }: any) => (
                                <Select
                                  {...field}
                                  label="Relationship"
                                  placeholder="Select relationship"
                                  data={RELATIONSHIP_OPTIONS}
                                  error={touched.emergencyRelationship && errors.emergencyRelationship}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#f59e0b',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          <Field name="emergencyPhone">
                            {({ field }: any) => (
                              <TextInput
                                {...field}
                                label="Emergency Contact Phone"
                                placeholder="(555) 987-6543"
                                leftSection={<IconPhone size={18} />}
                                error={touched.emergencyPhone && errors.emergencyPhone}
                                disabled={registrationState.isLoading}
                                size="lg"
                                radius="lg"
                                required
                                mt="md"
                                onChange={(event) => {
                                  const formatted = formatPhoneNumber(event.target.value);
                                  setFieldValue('emergencyPhone', formatted);
                                }}
                                styles={{
                                  input: {
                                    backgroundColor: '#fafafa',
                                    '&:focus': {
                                      backgroundColor: '#ffffff',
                                      borderColor: '#f59e0b',
                                    }
                                  }
                                }}
                              />
                            )}
                          </Field>
                        </Card>

                        {/* Account Security Section */}
                        <Card shadow="sm" padding="lg" radius="lg" withBorder>
                          <Group mb="md">
                            <IconShieldCheck size={24} color="#dc2626" />
                            <Box>
                              <Title order={2} size="h3" c="dark.7">
                                Secure Your Account
                              </Title>
                              <Text size="sm" c="dimmed">
                                Create a strong password to protect your health information
                              </Text>
                            </Box>
                          </Group>
                          
                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
                            <Field name="password">
                              {({ field }: any) => (
                                <Box>
                                  <PasswordInput
                                    {...field}
                                    label="Password"
                                    placeholder="Create a strong password"
                                    leftSection={<IconLock size={18} />}
                                    visibilityToggleIcon={({ reveal }) =>
                                      reveal ? <IconEyeOff size={18} /> : <IconEye size={18} />
                                    }
                                    error={touched.password && errors.password}
                                    disabled={registrationState.isLoading}
                                    size="lg"
                                    radius="lg"
                                    required
                                    styles={{
                                      input: {
                                        backgroundColor: '#fafafa',
                                        '&:focus': {
                                          backgroundColor: '#ffffff',
                                          borderColor: '#dc2626',
                                        }
                                      }
                                    }}
                                  />
                                  {values.password && (
                                    <Box mt="xs">
                                      <Group justify="space-between" mb="xs">
                                        <Text size="xs" c="dark.6">
                                          Password Strength
                                        </Text>
                                        <Text size="xs" c={getPasswordStrengthColor(passwordStrength)}>
                                          {passwordStrength < 50 ? 'Weak' : passwordStrength < 75 ? 'Good' : 'Strong'}
                                        </Text>
                                      </Group>
                                      <Progress
                                        value={passwordStrength}
                                        color={getPasswordStrengthColor(passwordStrength)}
                                        size="sm"
                                        radius="xl"
                                      />
                                      <Text size="xs" c="dimmed" mt="xs">
                                        💡 Include uppercase, lowercase, numbers, and symbols
                                      </Text>
                                    </Box>
                                  )}
                                </Box>
                              )}
                            </Field>
                            
                            <Field name="confirmPassword">
                              {({ field }: any) => (
                                <PasswordInput
                                  {...field}
                                  label="Confirm Password"
                                  placeholder="Re-enter your password"
                                  leftSection={<IconLock size={18} />}
                                  visibilityToggleIcon={({ reveal }) =>
                                    reveal ? <IconEyeOff size={18} /> : <IconEye size={18} />
                                  }
                                  error={touched.confirmPassword && errors.confirmPassword}
                                  disabled={registrationState.isLoading}
                                  size="lg"
                                  radius="lg"
                                  required
                                  styles={{
                                    input: {
                                      backgroundColor: '#fafafa',
                                      '&:focus': {
                                        backgroundColor: '#ffffff',
                                        borderColor: '#dc2626',
                                      }
                                    }
                                  }}
                                />
                              )}
                            </Field>
                          </SimpleGrid>
                        </Card>

                        {/* Legal Agreements */}
                        <Card shadow="sm" padding="lg" radius="lg" withBorder>
                          <Stack gap="md">
                            <Field name="agreeToTerms">
                              {({ field }: any) => (
                                <Checkbox
                                  {...field}
                                  checked={values.agreeToTerms}
                                  onChange={(event) => setFieldValue('agreeToTerms', event.currentTarget.checked)}
                                  label={
                                    <Text size="sm">
                                      I agree to the{' '}
                                      <Anchor
                                        size="sm"
                                        onClick={() => setShowTermsModal(true)}
                                        style={{ cursor: 'pointer' }}
                                      >
                                        Terms of Service
                                      </Anchor>
                                    </Text>
                                  }
                                  error={touched.agreeToTerms && errors.agreeToTerms}
                                  disabled={registrationState.isLoading}
                                  size="md"
                                  color="teal"
                                  required
                                />
                              )}
                            </Field>

                            <Field name="agreeToPrivacy">
                              {({ field }: any) => (
                                <Checkbox
                                  {...field}
                                  checked={values.agreeToPrivacy}
                                  onChange={(event) => setFieldValue('agreeToPrivacy', event.currentTarget.checked)}
                                  label={
                                    <Text size="sm">
                                      I agree to the{' '}
                                      <Anchor
                                        size="sm"
                                        onClick={() => setShowPrivacyModal(true)}
                                        style={{ cursor: 'pointer' }}
                                      >
                                        Privacy Policy
                                      </Anchor>
                                      {' '}and understand how my health information will be protected under HIPAA
                                    </Text>
                                  }
                                  error={touched.agreeToPrivacy && errors.agreeToPrivacy}
                                  disabled={registrationState.isLoading}
                                  size="md"
                                  color="teal"
                                  required
                                />
                              )}
                            </Field>
                          </Stack>
                        </Card>

                        {/* Submit Button */}
                        <Button
                          type="submit"
                          size="xl"
                          radius="xl"
                          fullWidth
                          loading={registrationState.isLoading}
                          gradient={{ from: 'blue.5', to: 'teal.5', deg: 135 }}
                          leftSection={registrationState.isLoading ? null : <IconHeart size={24} />}
                          styles={{
                            root: {
                              height: '64px',
                              fontSize: '18px',
                              fontWeight: 600,
                              boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)',
                              '&:hover': {
                                transform: registrationState.isLoading ? 'none' : 'translateY(-2px)',
                                boxShadow: registrationState.isLoading ? 'none' : '0 6px 24px rgba(59, 130, 246, 0.4)',
                              }
                            }
                          }}
                        >
                          {registrationState.isLoading ? 'Creating Your Account...' : '🎉 Create My Patient Account'}
                        </Button>

                        {/* Login Link */}
                        <Center>
                          <Text size="sm" c="dimmed" ta="center">
                            Already have an account?{' '}
                            <Anchor
                              c="blue.6"
                              fw={600}
                              onClick={onNavigateToLogin}
                              style={{ cursor: 'pointer' }}
                            >
                              Sign In Here
                            </Anchor>
                          </Text>
                        </Center>

                        {/* Security Assurance */}
                        <Center mt="lg">
                          <Group gap="xs">
                            <IconShieldCheck size={16} color="#10b981" />
                            <Text size="xs" c="dimmed" ta="center">
                              Your personal and health information is protected with bank-level security and HIPAA compliance
                            </Text>
                          </Group>
                        </Center>
                      </Stack>
                    </Form>
                  );
                }}
              </Formik>
            )}

            {/* Terms Modal */}
            <Modal
              opened={showTermsModal}
              onClose={() => setShowTermsModal(false)}
              title="Terms of Service"
              size="lg"
              radius="lg"
            >
              <Stack gap="md">
                <Text size="sm">
                  <strong>1. Healthcare Services</strong><br />
                  By creating an account, you agree to use our platform for legitimate healthcare purposes and provide accurate information.
                </Text>
                <Text size="sm">
                  <strong>2. Patient Responsibilities</strong><br />
                  You are responsible for keeping your account secure and providing accurate health information to your care providers.
                </Text>
                <Text size="sm">
                  <strong>3. Privacy Protection</strong><br />
                  Your health information is protected under HIPAA and will only be shared with authorized healthcare providers.
                </Text>
                <Text size="sm">
                  <strong>4. Account Security</strong><br />
                  You must keep your login credentials secure and notify us immediately of any unauthorized access.
                </Text>
                <Button onClick={() => setShowTermsModal(false)} fullWidth size="lg" radius="lg">
                  I Understand
                </Button>
              </Stack>
            </Modal>

            {/* Privacy Modal */}
            <Modal
              opened={showPrivacyModal}
              onClose={() => setShowPrivacyModal(false)}
              title="Privacy Policy & HIPAA Protection"
              size="lg"
              radius="lg"
            >
              <Stack gap="md">
                <Text size="sm">
                  <strong>🔒 Your Privacy is Our Priority</strong><br />
                  We are committed to protecting your personal and health information in accordance with HIPAA regulations.
                </Text>
                <Text size="sm">
                  <strong>📊 Information We Collect</strong><br />
                  We collect only the information necessary to provide you with quality healthcare services and improve your experience.
                </Text>
                <Text size="sm">
                  <strong>🏥 How We Use Your Information</strong><br />
                  Your information is used to facilitate healthcare services, appointment scheduling, and communication with your care team.
                </Text>
                <Text size="sm">
                  <strong>🛡️ Security Measures</strong><br />
                  We use industry-standard encryption and security measures to protect your data from unauthorized access.
                </Text>
                <Button onClick={() => setShowPrivacyModal(false)} fullWidth size="lg" radius="lg">
                  I Understand My Rights
                </Button>
              </Stack>
            </Modal>
          </Paper>
        </Center>
      </Container>
    </BackgroundImage>
  );
};

export default PatientRegistration; 