import React, { useState } from 'react';
import {
  Container,
  Paper,
  Title,
  Text,
  TextInput,
  PasswordInput,
  Button,
  Checkbox,
  Anchor,
  Stack,
  Group,
  Box,
  Center,
  Alert,
  Divider,
  BackgroundImage,
  Tooltip,
  ActionIcon,
} from '@mantine/core';
import {
  IconMail,
  IconPhone,
  IconLock,
  IconEye,
  IconEyeOff,
  IconHeart,
  IconUser,
  IconAlertCircle,
  IconCheck,
  IconShieldCheck,
  IconQuestionMark,
  IconInfoCircle,
} from '@tabler/icons-react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';

// Validation schema for patient login
const patientLoginValidationSchema = Yup.object({
  credential: Yup.string()
    .required('Please enter your email or phone number')
    .test('email-or-phone', 'Please enter a valid email or phone number', function(value) {
      if (!value) return false;
      
      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      // Phone validation (basic international format)
      const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
      
      return emailRegex.test(value) || phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''));
    }),
  password: Yup.string()
    .required('Please enter your password')
    .min(6, 'Password should be at least 6 characters'),
  rememberMe: Yup.boolean()
});

interface PatientLoginFormValues {
  credential: string;
  password: string;
  rememberMe: boolean;
}

interface PatientLoginState {
  isLoading: boolean;
  error: string | null;
  success: boolean;
}

interface PatientLoginProps {
  onNavigateToRegistration?: () => void;
  onNavigateToProviderLogin?: () => void;
}

const PatientLogin: React.FC<PatientLoginProps> = ({ 
  onNavigateToRegistration, 
  onNavigateToProviderLogin 
}) => {
  const [loginState, setLoginState] = useState<PatientLoginState>({
    isLoading: false,
    error: null,
    success: false
  });

  const initialValues: PatientLoginFormValues = {
    credential: '',
    password: '',
    rememberMe: false
  };

  const handleLogin = async (values: PatientLoginFormValues) => {
    setLoginState({ isLoading: true, error: null, success: false });
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock authentication logic
      if (values.credential === 'patient@health.com' && values.password === 'patient123') {
        setLoginState({ isLoading: false, error: null, success: true });
        
        // Redirect to patient dashboard after success
        setTimeout(() => {
          console.log('Redirecting to patient dashboard...');
          // window.location.href = '/patient-dashboard';
        }, 1500);
      } else {
        // More gentle error messages for patients
        if (values.credential && values.password) {
          setLoginState({ 
            isLoading: false, 
            error: 'We couldn\'t find an account with those details. Please check your information and try again, or contact support if you need help.', 
            success: false 
          });
        } else {
          setLoginState({ 
            isLoading: false, 
            error: 'Please fill in all required fields to continue.', 
            success: false 
          });
        }
      }
    } catch (error) {
      setLoginState({ 
        isLoading: false, 
        error: 'We\'re having trouble connecting right now. Please check your internet connection and try again.', 
        success: false 
      });
    }
  };

  const getCredentialIcon = (value: string) => {
    if (!value) return <IconUser size={18} />;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value) ? <IconMail size={18} /> : <IconPhone size={18} />;
  };

  const getCredentialPlaceholder = (value: string) => {
    if (!value) return 'Enter your email or phone number';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value) ? 'example@email.com' : '+1 (555) 123-4567';
  };

  return (
    <BackgroundImage
      src="data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23e0f2fe' fill-opacity='0.3'%3E%3Cpath d='M40 40c0-11.046-8.954-20-20-20s-20 8.954-20 20 8.954 20 20 20 20-8.954 20-20zm20 0c0-11.046-8.954-20-20-20s-20 8.954-20 20 8.954 20 20 20 20-8.954 20-20z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #e0f7fa 0%, #f3e5f5 50%, #fff3e0 100%)',
      }}
    >
      <Container size="sm" py={60}>
        <Center>
          <Paper
            shadow="md"
            p={50}
            radius="xl"
            style={{
              width: '100%',
              maxWidth: 480,
              background: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            {/* Header Section */}
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
                Welcome Back
              </Title>
              <Text size="lg" c="dimmed" ta="center" maw={400}>
                Sign in to access your health records, appointments, and care team
              </Text>
            </Stack>

            {/* Success State */}
            {loginState.success && (
              <Alert
                icon={<IconCheck size={18} />}
                title="Welcome back!"
                color="teal"
                mb="xl"
                radius="md"
                style={{
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                }}
              >
                <Text size="sm">
                  You're successfully signed in. Taking you to your dashboard...
                </Text>
              </Alert>
            )}

            {/* Error State */}
            {loginState.error && (
              <Alert
                icon={<IconAlertCircle size={18} />}
                title="Having trouble signing in?"
                color="orange"
                mb="xl"
                radius="md"
                style={{
                  backgroundColor: 'rgba(251, 146, 60, 0.1)',
                  border: '1px solid rgba(251, 146, 60, 0.2)',
                }}
              >
                <Text size="sm" mb="sm">
                  {loginState.error}
                </Text>
                <Group gap="xs">
                  <Anchor size="sm" c="orange.7" fw={500}>
                    Reset Password
                  </Anchor>
                  <Text size="sm" c="dimmed">•</Text>
                  <Anchor size="sm" c="orange.7" fw={500}>
                    Contact Support
                  </Anchor>
                </Group>
              </Alert>
            )}

            {/* Login Form */}
            <Formik
              initialValues={initialValues}
              validationSchema={patientLoginValidationSchema}
              onSubmit={handleLogin}
            >
              {({ values, errors, touched, setFieldValue }) => (
                <Form>
                  <Stack gap="lg">
                    {/* Email/Phone Input */}
                    <Field name="credential">
                      {({ field }: any) => (
                        <Box>
                          <Group gap="xs" mb="xs">
                            <Text size="sm" fw={500} c="dark.7">
                              Email or Phone Number
                            </Text>
                            <Tooltip
                              label="You can use either your email address or phone number to sign in"
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
                            placeholder={getCredentialPlaceholder(values.credential)}
                            leftSection={getCredentialIcon(values.credential)}
                            error={touched.credential && errors.credential}
                            disabled={loginState.isLoading || loginState.success}
                            size="lg"
                            radius="lg"
                            styles={{
                              input: {
                                borderColor: touched.credential && errors.credential ? '#f59e0b' : '#e5e7eb',
                                backgroundColor: '#fafafa',
                                fontSize: '16px',
                                '&:focus': {
                                  borderColor: '#3b82f6',
                                  backgroundColor: '#ffffff',
                                },
                                '&::placeholder': {
                                  color: '#9ca3af',
                                }
                              }
                            }}
                          />
                          {touched.credential && !errors.credential && values.credential && (
                            <Text size="xs" c="teal.6" mt="xs">
                              ✓ {values.credential.includes('@') ? 'Valid email format' : 'Valid phone format'}
                            </Text>
                          )}
                        </Box>
                      )}
                    </Field>

                    {/* Password Input */}
                    <Field name="password">
                      {({ field }: any) => (
                        <Box>
                          <Group gap="xs" mb="xs">
                            <Text size="sm" fw={500} c="dark.7">
                              Password
                            </Text>
                            <Tooltip
                              label="Your password is encrypted and secure"
                              position="top"
                              withArrow
                            >
                              <ActionIcon variant="subtle" size="xs" color="gray">
                                <IconShieldCheck size={14} />
                              </ActionIcon>
                            </Tooltip>
                          </Group>
                          <PasswordInput
                            {...field}
                            placeholder="Enter your password"
                            leftSection={<IconLock size={18} />}
                            visibilityToggleIcon={({ reveal }) =>
                              reveal ? <IconEyeOff size={18} /> : <IconEye size={18} />
                            }
                            error={touched.password && errors.password}
                            disabled={loginState.isLoading || loginState.success}
                            size="lg"
                            radius="lg"
                            styles={{
                              input: {
                                borderColor: touched.password && errors.password ? '#f59e0b' : '#e5e7eb',
                                backgroundColor: '#fafafa',
                                fontSize: '16px',
                                '&:focus': {
                                  borderColor: '#3b82f6',
                                  backgroundColor: '#ffffff',
                                },
                                '&::placeholder': {
                                  color: '#9ca3af',
                                }
                              }
                            }}
                          />
                        </Box>
                      )}
                    </Field>

                    {/* Remember Me & Forgot Password */}
                    <Group justify="space-between" mt="xs">
                      <Field name="rememberMe">
                        {({ field }: any) => (
                          <Group gap="xs">
                            <Checkbox
                              {...field}
                              checked={values.rememberMe}
                              onChange={(event) => setFieldValue('rememberMe', event.currentTarget.checked)}
                              disabled={loginState.isLoading || loginState.success}
                              size="sm"
                              color="teal"
                            />
                            <Text size="sm" c="dark.6">
                              Keep me signed in
                            </Text>
                            <Tooltip
                              label="We'll remember you on this device for 30 days"
                              position="top"
                              withArrow
                            >
                              <ActionIcon variant="subtle" size="xs" color="gray">
                                <IconQuestionMark size={12} />
                              </ActionIcon>
                            </Tooltip>
                          </Group>
                        )}
                      </Field>
                      
                      <Anchor
                        size="sm"
                        c="blue.6"
                        fw={500}
                        onClick={() => console.log('Navigate to forgot password')}
                        style={{ cursor: 'pointer' }}
                      >
                        Forgot password?
                      </Anchor>
                    </Group>

                    {/* Login Button */}
                    <Button
                      type="submit"
                      size="xl"
                      radius="lg"
                      fullWidth
                      mt="lg"
                      loading={loginState.isLoading}
                      disabled={loginState.success}
                      gradient={{ from: 'blue.5', to: 'teal.5', deg: 135 }}
                      leftSection={loginState.success ? <IconCheck size={20} /> : <IconHeart size={20} />}
                      styles={{
                        root: {
                          height: '56px',
                          fontSize: '16px',
                          fontWeight: 600,
                          boxShadow: loginState.isLoading ? 'none' : '0 4px 16px rgba(59, 130, 246, 0.3)',
                          '&:hover': {
                            transform: loginState.isLoading ? 'none' : 'translateY(-1px)',
                            boxShadow: loginState.isLoading ? 'none' : '0 6px 20px rgba(59, 130, 246, 0.4)',
                          }
                        }
                      }}
                    >
                      {loginState.isLoading ? 'Signing you in...' : loginState.success ? 'Welcome back!' : 'Sign In to Your Account'}
                    </Button>

                    {/* Security Notice */}
                    <Center mt="md">
                      <Group gap="xs">
                        <IconShieldCheck size={16} color="#10b981" />
                        <Text size="xs" c="dimmed" ta="center">
                          Your information is protected with bank-level security
                        </Text>
                      </Group>
                    </Center>

                    {/* Divider */}
                    <Divider 
                      label="New to our healthcare platform?" 
                      labelPosition="center" 
                      my="xl"
                      color="gray.3"
                    />

                    {/* Registration and Provider Links */}
                    <Stack gap="md">
                      <Center>
                        <Text size="sm" c="dimmed" ta="center">
                          Don't have a patient account yet?{' '}
                          <Anchor
                            c="blue.6"
                            fw={600}
                            onClick={onNavigateToRegistration}
                            style={{ cursor: 'pointer' }}
                          >
                            Create Account
                          </Anchor>
                        </Text>
                      </Center>

                      <Center>
                        <Text size="sm" c="dimmed" ta="center">
                          Are you a healthcare provider?{' '}
                          <Anchor
                            c="teal.6"
                            fw={600}
                            onClick={onNavigateToProviderLogin}
                            style={{ cursor: 'pointer' }}
                          >
                            Provider Sign In
                          </Anchor>
                        </Text>
                      </Center>
                    </Stack>
                  </Stack>
                </Form>
              )}
            </Formik>

            {/* Support Section */}
            <Box mt="xl" pt="lg" style={{ borderTop: '1px solid #f3f4f6' }}>
              <Stack gap="sm">
                <Center>
                  <Text size="sm" fw={500} c="dark.6">
                    Need help signing in?
                  </Text>
                </Center>
                <Group justify="center" gap="xl">
                  <Anchor 
                    size="sm" 
                    c="gray.6" 
                    onClick={() => console.log('Navigate to help')}
                    style={{ cursor: 'pointer' }}
                  >
                    Help Center
                  </Anchor>
                  <Anchor 
                    size="sm" 
                    c="gray.6" 
                    onClick={() => console.log('Contact support')}
                    style={{ cursor: 'pointer' }}
                  >
                    Contact Support
                  </Anchor>
                  <Anchor 
                    size="sm" 
                    c="gray.6" 
                    onClick={() => console.log('Technical support')}
                    style={{ cursor: 'pointer' }}
                  >
                    Technical Issues
                  </Anchor>
                </Group>
              </Stack>
            </Box>

            {/* Footer Information */}
            <Center mt="lg">
              <Text size="xs" c="dimmed" ta="center" maw={400}>
                By signing in, you agree to our{' '}
                <Anchor size="xs" c="dimmed" td="underline">Terms of Service</Anchor>
                {' '}and{' '}
                <Anchor size="xs" c="dimmed" td="underline">Privacy Policy</Anchor>.
                Your health information is protected under HIPAA.
              </Text>
            </Center>
          </Paper>
        </Center>
      </Container>
    </BackgroundImage>
  );
};

export default PatientLogin; 