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
  NumberInput,
  FileInput,
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
  Textarea,
  Modal,
  Anchor,
  BackgroundImage,
} from '@mantine/core';
import {
  IconUser,
  IconMail,
  IconPhone,
  IconLock,
  IconStethoscope,
  IconMedicalCross,
  IconUpload,
  IconCheck,
  IconAlertCircle,
  IconEye,
  IconEyeOff,
  IconBuilding,
  IconMapPin,
  IconCertificate,
  IconCalendar,
  IconFileText,
  IconShieldCheck,
} from '@tabler/icons-react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { providerAPI, ProviderRegistrationData } from '../services/api';

// Medical specializations
const MEDICAL_SPECIALIZATIONS = [
  'Anesthesiology',
  'Cardiology',
  'Dermatology',
  'Emergency Medicine',
  'Endocrinology',
  'Family Medicine',
  'Gastroenterology',
  'General Surgery',
  'Hematology',
  'Internal Medicine',
  'Nephrology',
  'Neurology',
  'Obstetrics & Gynecology',
  'Oncology',
  'Ophthalmology',
  'Orthopedics',
  'Otolaryngology',
  'Pathology',
  'Pediatrics',
  'Psychiatry',
  'Pulmonology',
  'Radiology',
  'Rheumatology',
  'Urology',
];

const PRACTICE_TYPES = [
  'Private Practice',
  'Hospital',
  'Clinic',
  'Medical Center',
  'Urgent Care',
  'Specialty Center',
  'Academic Medical Center',
  'Community Health Center',
];

const YEARS_EXPERIENCE = Array.from({ length: 50 }, (_, i) => ({
  value: (i + 1).toString(),
  label: i === 0 ? '1 year' : `${i + 1} years`,
}));

// Validation schema
const registrationValidationSchema = Yup.object({
  // Personal Information
  firstName: Yup.string()
    .required('First name is required')
    .min(2, 'First name must be at least 2 characters'),
  lastName: Yup.string()
    .required('Last name is required')
    .min(2, 'Last name must be at least 2 characters'),
  email: Yup.string()
    .required('Email is required')
    .email('Please enter a valid email address'),
  phone: Yup.string()
    .required('Phone number is required')
    .matches(/^[\+]?[1-9][\d]{0,15}$/, 'Please enter a valid phone number'),
  
  // Professional Information
  licenseNumber: Yup.string()
    .required('Medical license number is required')
    .min(5, 'License number must be at least 5 characters'),
  specialization: Yup.string()
    .required('Please select your specialization'),
  yearsExperience: Yup.string()
    .required('Please select your years of experience'),
  medicalDegree: Yup.string()
    .required('Medical degree/qualifications are required'),
  
  // Practice Information
  clinicName: Yup.string()
    .required('Clinic/Hospital name is required'),
  streetAddress: Yup.string()
    .required('Street address is required'),
  city: Yup.string()
    .required('City is required'),
  state: Yup.string()
    .required('State is required'),
  zipCode: Yup.string()
    .required('ZIP code is required')
    .matches(/^\d{5}(-\d{4})?$/, 'Please enter a valid ZIP code'),
  practiceType: Yup.string()
    .required('Please select your practice type'),
  
  // Account Security
  password: Yup.string()
    .required('Password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, 
      'Password must contain uppercase, lowercase, number, and special character'),
  confirmPassword: Yup.string()
    .required('Please confirm your password')
    .oneOf([Yup.ref('password')], 'Passwords must match'),
  
  // Terms and Conditions
  agreeToTerms: Yup.boolean()
    .oneOf([true], 'You must agree to the terms and conditions'),
});

interface RegistrationFormValues {
  // Personal Information
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  profilePhoto: File | null;
  
  // Professional Information
  licenseNumber: string;
  specialization: string;
  yearsExperience: string;
  medicalDegree: string;
  
  // Practice Information
  clinicName: string;
  streetAddress: string;
  city: string;
  state: string;
  zipCode: string;
  practiceType: string;
  
  // Account Security
  password: string;
  confirmPassword: string;
  
  // Terms
  agreeToTerms: boolean;
}

interface RegistrationState {
  isLoading: boolean;
  error: string | null;
  success: boolean;
  step: number;
}

interface ProviderRegistrationProps {
  onNavigateToLogin?: () => void;
}

const ProviderRegistration: React.FC<ProviderRegistrationProps> = ({ onNavigateToLogin }) => {
  const [registrationState, setRegistrationState] = useState<RegistrationState>({
    isLoading: false,
    error: null,
    success: false,
    step: 1,
  });
  
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [profilePhotoPreview, setProfilePhotoPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const initialValues: RegistrationFormValues = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    profilePhoto: null,
    licenseNumber: '',
    specialization: '',
    yearsExperience: '',
    medicalDegree: '',
    clinicName: '',
    streetAddress: '',
    city: '',
    state: '',
    zipCode: '',
    practiceType: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  };

  const handleRegistration = async (values: RegistrationFormValues) => {
    setRegistrationState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      // Map form values to API structure
      const apiData: ProviderRegistrationData = {
        first_name: values.firstName,
        last_name: values.lastName,
        email: values.email,
        phone_number: values.phone,
        password: values.password,
        confirm_password: values.confirmPassword,
        specialization: values.specialization,
        license_number: values.licenseNumber,
        years_of_experience: parseInt(values.yearsExperience, 10),
        clinic_address: {
          street: values.streetAddress,
          city: values.city,
          state: values.state,
          zip: values.zipCode,
        },
      };

      // Call the API
      const response = await providerAPI.register(apiData);
      
      console.log('Registration successful:', response);
      
      setRegistrationState({
        isLoading: false,
        error: null,
        success: true,
        step: 4,
      });
    } catch (error: any) {
      console.error('Registration error:', error);
      
      let errorMessage = 'Registration failed. Please check your connection and try again.';
      
      // Handle specific API errors
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.status === 400) {
        errorMessage = 'Invalid registration data. Please check your information and try again.';
      } else if (error.response?.status === 409) {
        errorMessage = 'An account with this email already exists. Please use a different email or try logging in.';
      } else if (error.response?.status === 422) {
        errorMessage = 'Please check your input data. Some fields may contain invalid information.';
      }
      
      setRegistrationState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
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

  const getProgressValue = (values: RegistrationFormValues) => {
    const fields = Object.keys(values).filter(key => key !== 'profilePhoto');
    const filledFields = fields.filter(key => {
      const value = values[key as keyof RegistrationFormValues];
      return value !== '' && value !== false && value !== null;
    });
    return (filledFields.length / fields.length) * 100;
  };

  return (
    <BackgroundImage
      src="data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23f1f5f9' fill-opacity='0.4'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container size="md" py={40}>
        <Center>
          <Paper
            shadow="xl"
            p={40}
            radius="lg"
            style={{
              width: '100%',
              maxWidth: 800,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
            }}
          >
            {/* Header Section */}
            <Stack align="center" mb={30}>
              <Box
                style={{
                  background: 'linear-gradient(135deg, #2563eb 0%, #059669 100%)',
                  borderRadius: '50%',
                  padding: 16,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <IconMedicalCross size={32} color="white" />
              </Box>
              <Title order={1} size="h2" fw={700} c="dark.8">
                Provider Registration
              </Title>
              <Text size="sm" c="dimmed" ta="center">
                Join our healthcare network and start helping patients
              </Text>
            </Stack>

            {/* Success State */}
            {registrationState.success && (
              <Alert
                icon={<IconCheck size={16} />}
                title="Registration Successful!"
                color="green"
                mb="md"
              >
                <Stack gap="xs">
                  <Text size="sm">
                    Thank you for registering! We've sent a verification email to your address.
                  </Text>
                  <Text size="sm">
                    Your account will be reviewed and approved within 24-48 hours.
                  </Text>
                  <Group mt="md">
                    <Button 
                      size="sm" 
                      variant="light" 
                      color="green"
                      onClick={onNavigateToLogin}
                    >
                      Go to Login
                    </Button>
                    <Button size="sm" variant="outline" color="green">
                      Check Email
                    </Button>
                  </Group>
                </Stack>
              </Alert>
            )}

            {/* Error State */}
            {registrationState.error && (
              <Alert
                icon={<IconAlertCircle size={16} />}
                title="Registration Failed"
                color="red"
                mb="md"
              >
                {registrationState.error}
              </Alert>
            )}

            {!registrationState.success && (
              <Formik
                initialValues={initialValues}
                validationSchema={registrationValidationSchema}
                onSubmit={handleRegistration}
              >
                {({ values, errors, touched, setFieldValue }) => {
                  const progressValue = getProgressValue(values);
                  const passwordStrength = getPasswordStrength(values.password);
                  
                  return (
                    <Form>
                      {/* Progress Bar */}
                      <Box mb="xl">
                        <Group justify="space-between" mb="xs">
                          <Text size="sm" fw={500}>Registration Progress</Text>
                          <Text size="sm" c="dimmed">{Math.round(progressValue)}% Complete</Text>
                        </Group>
                        <Progress value={progressValue} color="blue" size="sm" radius="xl" />
                      </Box>

                      <Stack gap="xl">
                        {/* Personal Information Section */}
                        <Box>
                          <Group mb="md">
                            <IconUser size={20} color="#2563eb" />
                            <Title order={3} size="h4" c="dark.7">Personal Information</Title>
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
                                  required
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
                                  required
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" mt="md">
                            <Field name="email">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Email Address"
                                  placeholder="Enter your email"
                                  leftSection={<IconMail size={18} />}
                                  error={touched.email && errors.email}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                            
                            <Field name="phone">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Phone Number"
                                  placeholder="Enter your phone number"
                                  leftSection={<IconPhone size={18} />}
                                  error={touched.phone && errors.phone}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          {/* Profile Photo Upload */}
                          <Box mt="md">
                            <Text size="sm" fw={500} mb="xs">Profile Photo (Optional)</Text>
                            <Group>
                              <Avatar
                                src={profilePhotoPreview}
                                size={80}
                                radius="md"
                                style={{ border: '2px dashed #ced4da' }}
                              >
                                <IconUser size={40} />
                              </Avatar>
                              <FileInput
                                placeholder="Upload profile photo (Max 5MB)"
                                accept="image/*"
                                leftSection={<IconUpload size={18} />}
                                onChange={(file) => handlePhotoUpload(file, setFieldValue)}
                                disabled={registrationState.isLoading}
                                style={{ flex: 1 }}
                              />
                            </Group>
                            <Text size="xs" c="dimmed" mt="xs">
                              Supported formats: JPG, PNG, GIF. Maximum size: 5MB
                            </Text>
                          </Box>
                        </Box>

                        <Divider />

                        {/* Professional Information Section */}
                        <Box>
                          <Group mb="md">
                            <IconStethoscope size={20} color="#059669" />
                            <Title order={3} size="h4" c="dark.7">Professional Information</Title>
                          </Group>
                          
                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
                            <Field name="licenseNumber">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Medical License Number"
                                  placeholder="Enter your license number"
                                  leftSection={<IconCertificate size={18} />}
                                  error={touched.licenseNumber && errors.licenseNumber}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                            
                            <Field name="specialization">
                              {({ field }: any) => (
                                <Select
                                  {...field}
                                  label="Specialization"
                                  placeholder="Select your specialization"
                                  data={MEDICAL_SPECIALIZATIONS}
                                  error={touched.specialization && errors.specialization}
                                  disabled={registrationState.isLoading}
                                  searchable
                                  required
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" mt="md">
                            <Field name="yearsExperience">
                              {({ field }: any) => (
                                <Select
                                  {...field}
                                  label="Years of Experience"
                                  placeholder="Select years of experience"
                                  data={YEARS_EXPERIENCE}
                                  leftSection={<IconCalendar size={18} />}
                                  error={touched.yearsExperience && errors.yearsExperience}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                            
                            <Field name="medicalDegree">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Medical Degree/Qualifications"
                                  placeholder="e.g., MD, DO, MBBS"
                                  leftSection={<IconFileText size={18} />}
                                  error={touched.medicalDegree && errors.medicalDegree}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                          </SimpleGrid>
                        </Box>

                        <Divider />

                        {/* Practice Information Section */}
                        <Box>
                          <Group mb="md">
                            <IconBuilding size={20} color="#7c3aed" />
                            <Title order={3} size="h4" c="dark.7">Practice Information</Title>
                          </Group>
                          
                          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
                            <Field name="clinicName">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="Clinic/Hospital Name"
                                  placeholder="Enter clinic or hospital name"
                                  leftSection={<IconBuilding size={18} />}
                                  error={touched.clinicName && errors.clinicName}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                            
                            <Field name="practiceType">
                              {({ field }: any) => (
                                <Select
                                  {...field}
                                  label="Practice Type"
                                  placeholder="Select practice type"
                                  data={PRACTICE_TYPES}
                                  error={touched.practiceType && errors.practiceType}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                          </SimpleGrid>

                          <Field name="streetAddress">
                            {({ field }: any) => (
                              <TextInput
                                {...field}
                                label="Street Address"
                                placeholder="Enter street address"
                                leftSection={<IconMapPin size={18} />}
                                error={touched.streetAddress && errors.streetAddress}
                                disabled={registrationState.isLoading}
                                mt="md"
                                required
                              />
                            )}
                          </Field>

                          <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md" mt="md">
                            <Field name="city">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="City"
                                  placeholder="Enter city"
                                  error={touched.city && errors.city}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                            
                            <Field name="state">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="State"
                                  placeholder="Enter state"
                                  error={touched.state && errors.state}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                            
                            <Field name="zipCode">
                              {({ field }: any) => (
                                <TextInput
                                  {...field}
                                  label="ZIP Code"
                                  placeholder="Enter ZIP code"
                                  error={touched.zipCode && errors.zipCode}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                          </SimpleGrid>
                        </Box>

                        <Divider />

                        {/* Account Security Section */}
                        <Box>
                          <Group mb="md">
                            <IconShieldCheck size={20} color="#dc2626" />
                            <Title order={3} size="h4" c="dark.7">Account Security</Title>
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
                                    required
                                  />
                                  {values.password && (
                                    <Box mt="xs">
                                      <Group justify="space-between" mb="xs">
                                        <Text size="xs">Password Strength</Text>
                                        <Text size="xs" c={getPasswordStrengthColor(passwordStrength)}>
                                          {passwordStrength < 50 ? 'Weak' : passwordStrength < 75 ? 'Medium' : 'Strong'}
                                        </Text>
                                      </Group>
                                      <Progress
                                        value={passwordStrength}
                                        color={getPasswordStrengthColor(passwordStrength)}
                                        size="xs"
                                      />
                                      <Text size="xs" c="dimmed" mt="xs">
                                        Must contain: uppercase, lowercase, number, and special character
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
                                  placeholder="Confirm your password"
                                  leftSection={<IconLock size={18} />}
                                  visibilityToggleIcon={({ reveal }) =>
                                    reveal ? <IconEyeOff size={18} /> : <IconEye size={18} />
                                  }
                                  error={touched.confirmPassword && errors.confirmPassword}
                                  disabled={registrationState.isLoading}
                                  required
                                />
                              )}
                            </Field>
                          </SimpleGrid>
                        </Box>

                        {/* Terms and Conditions */}
                        <Box>
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
                                      Terms and Conditions
                                    </Anchor>
                                    {' '}and{' '}
                                    <Anchor size="sm" style={{ cursor: 'pointer' }}>
                                      Privacy Policy
                                    </Anchor>
                                  </Text>
                                }
                                error={touched.agreeToTerms && errors.agreeToTerms}
                                disabled={registrationState.isLoading}
                                required
                              />
                            )}
                          </Field>
                        </Box>

                        {/* Submit Button */}
                        <Button
                          type="submit"
                          size="lg"
                          radius="md"
                          fullWidth
                          loading={registrationState.isLoading}
                          gradient={{ from: 'blue.6', to: 'green.6', deg: 135 }}
                          leftSection={<IconMedicalCross size={20} />}
                        >
                          {registrationState.isLoading ? 'Creating Account...' : 'Create Provider Account'}
                        </Button>

                        {/* Login Link */}
                        <Center>
                          <Text size="sm" c="dimmed">
                            Already have an account?{' '}
                            <Anchor
                              c="blue.6"
                              fw={500}
                              onClick={onNavigateToLogin}
                              style={{ cursor: 'pointer' }}
                            >
                              Sign In
                            </Anchor>
                          </Text>
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
              title="Terms and Conditions"
              size="lg"
            >
              <Stack gap="md">
                <Text size="sm">
                  <strong>1. Acceptance of Terms</strong><br />
                  By registering as a healthcare provider, you agree to comply with all applicable laws and regulations.
                </Text>
                <Text size="sm">
                  <strong>2. Professional Responsibility</strong><br />
                  You certify that all information provided is accurate and that you maintain valid medical licensure.
                </Text>
                <Text size="sm">
                  <strong>3. Patient Privacy</strong><br />
                  You agree to maintain strict confidentiality of all patient information in accordance with HIPAA regulations.
                </Text>
                <Text size="sm">
                  <strong>4. Account Security</strong><br />
                  You are responsible for maintaining the security of your account credentials.
                </Text>
                <Text size="sm">
                  <strong>5. Account Verification</strong><br />
                  Your account and medical license will be verified before activation. This process may take 24-48 hours.
                </Text>
                <Button onClick={() => setShowTermsModal(false)} fullWidth>
                  Close
                </Button>
              </Stack>
            </Modal>
          </Paper>
        </Center>
      </Container>
    </BackgroundImage>
  );
};

export default ProviderRegistration; 