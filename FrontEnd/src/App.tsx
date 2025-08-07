import React from "react";
import {
  RouterProvider,
  createRouter,
  createRoute,
  createRootRoute,
  Outlet,
  useNavigate,
  useLocation,
} from "@tanstack/react-router";
import {
  MantineProvider,
  AppShell,
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
  Loader,
  Alert,
  Divider,
  BackgroundImage,
} from "@mantine/core";
import {
  IconMail,
  IconPhone,
  IconLock,
  IconEye,
  IconEyeOff,
  IconStethoscope,
  IconMedicalCross,
  IconUser,
  IconAlertCircle,
  IconCheck,
  IconHeart,
  IconCalendarTime,
  IconBolt,
} from "@tabler/icons-react";
import { Formik, Form, Field } from "formik";
import * as Yup from "yup";
import PatientLogin from "./components/PatientLogin";
import ProviderRegistration from "./components/ProviderRegistration";
import PatientRegistration from "./components/PatientRegistration";
import ProviderLayout from "./components/ProviderLayout";
import ThemeDemo from "./components/ThemeDemo";
import EnhancedProviderAvailability from "./components/EnhancedProviderAvailability";
import { providerAPI, ProviderLoginData } from "./services/api";

const theme = {
  primaryColor: "violet",
  colors: {
    // Modern Violet - Fresh and modern primary color
    violet: [
      "#f5f3ff",
      "#ede9fe", 
      "#ddd6fe",
      "#c4b5fd",
      "#a78bfa",
      "#8b5cf6",
      "#7c3aed",
      "#6d28d9",
      "#5b21b6",
      "#4c1d95"
    ] as const,
    // Soft Mint - Calming and fresh secondary
    mint: [
      "#f0fdfa",
      "#ccfbf1",
      "#99f6e4",
      "#5eead4",
      "#2dd4bf",
      "#14b8a6",
      "#0d9488",
      "#0f766e",
      "#115e59",
      "#134e4a"
    ] as const,
    // Warm Coral - Energetic and welcoming
    coral: [
      "#fff7ed",
      "#ffedd5",
      "#fed7aa",
      "#fdba74",
      "#fb923c",
      "#f97316",
      "#ea580c",
      "#c2410c",
      "#9a3412",
      "#7c2d12"
    ] as const,
    // Cool Slate - Professional and neutral
    slate: [
      "#f8fafc",
      "#f1f5f9",
      "#e2e8f0",
      "#cbd5e1",
      "#94a3b8",
      "#64748b",
      "#475569",
      "#334155",
      "#1e293b",
      "#0f172a"
    ] as const,
    // Deep Purple - Rich and sophisticated
    purple: [
      "#faf5ff",
      "#f3e8ff",
      "#e9d5ff",
      "#d8b4fe",
      "#c084fc",
      "#a855f7",
      "#9333ea",
      "#7c3aed",
      "#6b21a8",
      "#581c87"
    ] as const,
  },
  fontFamily: "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
  },
  spacing: {
    xs: '0.5rem',
    sm: '0.75rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
  },
  radius: {
    xs: '0.25rem',
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
  shadows: {
    xs: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    sm: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
};

// Validation schema
const loginValidationSchema = Yup.object({
  identifier: Yup.string() // changed from credential
    .required("Email or phone number is required")
    .test(
      "email-or-phone",
      "Please enter a valid email or phone number",
      function (value) {
        if (!value) return false;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;

        return (
          emailRegex.test(value) ||
          phoneRegex.test(value.replace(/[\s\-\(\)]/g, ""))
        );
      }
    ),
  password: Yup.string()
    .required("Password is required")
    .min(6, "Password must be at least 6 characters"),
  rememberMe: Yup.boolean(),
});

// Provider Login Component
const ProviderLoginComponent: React.FC = () => {
  const navigate = useNavigate();
  const [loginState, setLoginState] = React.useState({
    isLoading: false,
    error: null as string | null,
    success: false,
  });

  const initialValues = {
    identifier: "", // changed from credential
    password: "",
    rememberMe: false,
  };

  const handleProviderLogin = async (values: any) => {
    setLoginState({ isLoading: true, error: null, success: false });

    try {
      // Map form values to API structure
      const loginData: ProviderLoginData = {
        identifier: values.identifier, // changed from credential
        password: values.password,
        remember_me: values.rememberMe, // added remember_me field
      };

      // Call the API
      const response = await providerAPI.login(loginData);
      
      console.log('Login successful:', response);
      
      // Store the token (you might want to use a proper state management solution)
      localStorage.setItem('provider_token', response.access_token);
      localStorage.setItem('provider_user', JSON.stringify(response.user));
      
      setLoginState({ isLoading: false, error: null, success: true });
      setTimeout(() => {
        // Navigate to dashboard
        navigate({ to: "/provider/dashboard" });
      }, 1500);
    } catch (error: any) {
      console.error('Login error:', error);
      
      let errorMessage = "Network error. Please check your connection and try again.";
      
      // Handle specific API errors
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.status === 401) {
        errorMessage = "Invalid credentials. Please check your email/phone and password.";
      } else if (error.response?.status === 400) {
        errorMessage = "Invalid login data. Please check your information and try again.";
      } else if (error.response?.status === 404) {
        errorMessage = "Account not found. Please check your credentials or register first.";
      }
      
      setLoginState({
        isLoading: false,
        error: errorMessage,
        success: false,
      });
    }
  };

  const getCredentialIcon = (value: string) => {
    if (!value) return <IconUser size={18} />;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value) ? (
      <IconMail size={18} />
    ) : (
      <IconPhone size={18} />
    );
  };

  return (
    <BackgroundImage
      src="data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23f1f5f9' fill-opacity='0.4'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <Container size="sm" py={80}>
        <Center>
          <Paper
            shadow="xl"
            p={40}
            radius="lg"
            style={{
              width: "100%",
              maxWidth: 450,
              background: "rgba(255, 255, 255, 0.95)",
              backdropFilter: "blur(10px)",
            }}
          >
            {/* Header Section */}
            <Stack align="center" mb={30}>
              <Box
                style={{
                  background:
                    "linear-gradient(135deg, #2563eb 0%, #059669 100%)",
                  borderRadius: "50%",
                  padding: 16,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <IconStethoscope size={32} color="white" />
              </Box>
              <Title order={1} size="h2" fw={700} c="dark.8">
                Provider Login
              </Title>
              <Text size="sm" c="dimmed" ta="center">
                Secure access to your healthcare dashboard
              </Text>
            </Stack>

            {/* Success State */}
            {loginState.success && (
              <Alert
                icon={<IconCheck size={16} />}
                title="Login Successful!"
                color="green"
                mb="md"
              >
                Redirecting to your dashboard...
              </Alert>
            )}

            {/* Error State */}
            {loginState.error && (
              <Alert
                icon={<IconAlertCircle size={16} />}
                title="Login Failed"
                color="red"
                mb="md"
              >
                {loginState.error}
              </Alert>
            )}

            {/* Login Form */}
            <Formik
              initialValues={initialValues}
              validationSchema={loginValidationSchema}
              onSubmit={handleProviderLogin}
            >
              {({ values, errors, touched, setFieldValue }) => (
                <Form>
                  <Stack gap="md">
                    {/* Email/Phone Input */}
                    <Field name="identifier">
                      {({ field }: any) => (
                        <TextInput
                          {...field}
                          label="Email or Phone Number"
                          placeholder="Enter your email or phone number"
                          leftSection={getCredentialIcon(values.identifier)}
                          error={touched.identifier && errors.identifier}
                          disabled={loginState.isLoading || loginState.success}
                          size="md"
                          radius="md"
                        />
                      )}
                    </Field>

                    {/* Password Input */}
                    <Field name="password">
                      {({ field }: any) => (
                        <PasswordInput
                          {...field}
                          label="Password"
                          placeholder="Enter your password"
                          leftSection={<IconLock size={18} />}
                          visibilityToggleIcon={({ reveal }) =>
                            reveal ? (
                              <IconEyeOff size={18} />
                            ) : (
                              <IconEye size={18} />
                            )
                          }
                          error={touched.password && errors.password}
                          disabled={loginState.isLoading || loginState.success}
                          size="md"
                          radius="md"
                        />
                      )}
                    </Field>

                    {/* Remember Me & Forgot Password */}
                    <Group justify="space-between" mt="xs">
                      <Field name="rememberMe">
                        {({ field }: any) => (
                          <Checkbox
                            {...field}
                            checked={values.rememberMe}
                            onChange={(event) =>
                              setFieldValue(
                                "rememberMe",
                                event.currentTarget.checked
                              )
                            }
                            label="Remember me"
                            disabled={
                              loginState.isLoading || loginState.success
                            }
                            size="sm"
                          />
                        )}
                      </Field>
                      <Anchor
                        size="sm"
                        c="blue.6"
                        onClick={() =>
                          console.log("Navigate to forgot password")
                        }
                        style={{ cursor: "pointer" }}
                      >
                        Forgot password?
                      </Anchor>
                    </Group>

                    {/* Login Button */}
                    <Button
                      type="submit"
                      size="md"
                      radius="md"
                      fullWidth
                      mt="md"
                      loading={loginState.isLoading}
                      disabled={loginState.success}
                      gradient={{ from: "blue.6", to: "blue.8", deg: 135 }}
                      leftSection={
                        loginState.isLoading ? (
                          <Loader size={18} />
                        ) : (
                          <IconMedicalCross size={18} />
                        )
                      }
                    >
                      {loginState.isLoading ? "Signing In..." : "Sign In"}
                    </Button>

                    {/* Divider */}
                    <Divider
                      label="New to our platform?"
                      labelPosition="center"
                      my="lg"
                    />

                    {/* Registration and Patient Links */}
                    <Stack gap="md">
                      <Center>
                        <Text size="sm" c="dimmed">
                          Don't have a provider account?{" "}
                          <Anchor
                            c="blue.6"
                            fw={500}
                            onClick={() =>
                              navigate({ to: "/auth/provider-register" })
                            }
                            style={{ cursor: "pointer" }}
                          >
                            Register as Provider
                          </Anchor>
                        </Text>
                      </Center>

                      <Center>
                        <Text size="sm" c="dimmed">
                          Are you a patient?{" "}
                          <Anchor
                            c="teal.6"
                            fw={500}
                            onClick={() =>
                              navigate({ to: "/auth/patient-login" })
                            }
                            style={{ cursor: "pointer" }}
                          >
                            Patient Sign In
                          </Anchor>
                        </Text>
                      </Center>
                    </Stack>
                  </Stack>
                </Form>
              )}
            </Formik>

            {/* Footer Links */}
            <Group justify="center" mt="xl" gap="xl">
              <Anchor
                size="xs"
                c="dimmed"
                onClick={() => console.log("Navigate to support")}
              >
                Support
              </Anchor>
              <Anchor
                size="xs"
                c="dimmed"
                onClick={() => console.log("Navigate to privacy")}
              >
                Privacy Policy
              </Anchor>
              <Anchor
                size="xs"
                c="dimmed"
                onClick={() => console.log("Navigate to terms")}
              >
                Terms of Service
              </Anchor>
            </Group>
          </Paper>
        </Center>
      </Container>
    </BackgroundImage>
  );
};

// Root route
const rootRoute = createRootRoute({
  component: () => (
    <MantineProvider theme={theme}>
      <AppShell>
        <Outlet />

        {/* Quick Navigation - Floating Navigation Bar */}
        <Box
          style={{
            position: "fixed",
            top: 20,
            right: 20,
            zIndex: 1000,
            background: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(10px)",
            borderRadius: "12px",
            padding: "8px",
            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.1)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
          }}
        >
          <NavigationButtons />
        </Box>
      </AppShell>
    </MantineProvider>
  ),
});

// Navigation component
const NavigationButtons: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Check if we're on provider routes
  const isProviderRoute = location.pathname.startsWith("/provider");
  // Check if we're on auth routes
  const isAuthRoute = location.pathname.startsWith("/auth");

  // Only render navigation buttons on auth routes
  if (!isAuthRoute) {
    return null;
  }

  return (
    <Group gap="xs">
      {/* Always show Patient and Provider login buttons */}
      <Button
        variant="light"
        size="sm"
        onClick={() => navigate({ to: "/auth/patient-login" })}
        leftSection={<IconHeart size={16} />}
        color="teal"
      >
        Patient
      </Button>
      <Button
        variant="light"
        size="sm"
        onClick={() => navigate({ to: "/auth/provider-login" })}
        leftSection={<IconStethoscope size={16} />}
        color="blue"
      >
        Provider
      </Button>
      <Button
        variant="light"
        size="sm"
        onClick={() => navigate({ to: "/theme-demo" })}
        leftSection={<IconBolt size={16} />}
        style={{
          background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
          color: 'white',
          border: 'none',
        }}
      >
        Theme Demo
      </Button>
    </Group>
  );
};

// Auth routes
const authRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/auth",
  component: () => <Outlet />,
});

// Provider routes
const providerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/provider",
  component: () => <Outlet />,
});

// Index route - redirect to patient login
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: () => {
    const navigate = useNavigate();
    React.useEffect(() => {
      navigate({ to: "/auth/patient-login" });
    }, [navigate]);
    return <div>Redirecting...</div>;
  },
});

const patientLoginRoute = createRoute({
  getParentRoute: () => authRoute,
  path: "/patient-login",
  component: () => {
    const navigate = useNavigate();
    return (
      <PatientLogin
        onNavigateToRegistration={() =>
          navigate({ to: "/auth/patient-register" })
        }
        onNavigateToProviderLogin={() =>
          navigate({ to: "/auth/provider-login" })
        }
      />
    );
  },
});

const patientRegisterRoute = createRoute({
  getParentRoute: () => authRoute,
  path: "/patient-register",
  component: () => {
    const navigate = useNavigate();
    return (
      <PatientRegistration
        onNavigateToLogin={() => navigate({ to: "/auth/patient-login" })}
      />
    );
  },
});

const providerLoginRoute = createRoute({
  getParentRoute: () => authRoute,
  path: "/provider-login",
  component: ProviderLoginComponent,
});

const providerRegisterRoute = createRoute({
  getParentRoute: () => authRoute,
  path: "/provider-register",
  component: () => {
    const navigate = useNavigate();
    return (
      <ProviderRegistration
        onNavigateToLogin={() => navigate({ to: "/auth/provider-login" })}
      />
    );
  },
});

const providerAvailabilityRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/availability",
  component: () => {
    return <ProviderLayout activeTab="scheduling" />;
  },
});

const enhancedAvailabilityRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/enhanced-availability",
  component: () => {
    return <EnhancedProviderAvailability />;
  },
});

const providerDashboardRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/dashboard",
  component: () => {
    return <ProviderLayout activeTab="dashboard" />;
  },
});

const providerPatientsRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/patients",
  component: () => {
    return <ProviderLayout activeTab="patients" />;
  },
});

const providerCommunicationsRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/communications",
  component: () => {
    return <ProviderLayout activeTab="communications" />;
  },
});

const providerBillingRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/billing",
  component: () => {
    return <ProviderLayout activeTab="billing" />;
  },
});

const providerReferralRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/referral",
  component: () => {
    return <ProviderLayout activeTab="referral" />;
  },
});

const providerReportsRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/reports",
  component: () => {
    return <ProviderLayout activeTab="reports" />;
  },
});

const providerSettingsRoute = createRoute({
  getParentRoute: () => providerRoute,
  path: "/settings",
  component: () => {
    return <ProviderLayout activeTab="settings" />;
  },
});

// Theme demo route
const themeDemoRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/theme-demo",
  component: ThemeDemo,
});

// Create the route tree
const routeTree = rootRoute.addChildren([
  indexRoute,
  themeDemoRoute,
  authRoute.addChildren([
    patientLoginRoute,
    patientRegisterRoute,
    providerLoginRoute,
    providerRegisterRoute,
  ]),
  providerRoute.addChildren([
    providerAvailabilityRoute,
    enhancedAvailabilityRoute,
    providerDashboardRoute,
    providerPatientsRoute,
    providerCommunicationsRoute,
    providerBillingRoute,
    providerReferralRoute,
    providerReportsRoute,
    providerSettingsRoute,
  ]),
]);

// Create the router
const router = createRouter({ routeTree });

// Declare the router instance for TypeScript
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

// Main App component
const HealthcareApp: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default HealthcareApp;
