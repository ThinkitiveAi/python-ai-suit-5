import React from 'react';
import { createRoute, Outlet } from '@tanstack/react-router';
import { rootRoute } from './__root';
import { AppShell, Box, Button, Group } from '@mantine/core';
import { IconStethoscope, IconUser, IconHeart } from '@tabler/icons-react';

function AuthLayout() {
  return (
    <AppShell>
      <Outlet />
      
      {/* Quick Navigation - Floating Navigation Bar */}
      <Box
        style={{
          position: 'fixed',
          top: 20,
          right: 20,
          zIndex: 1000,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          borderRadius: '12px',
          padding: '8px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        }}
      >
        <Group gap="xs">
          <Button
            variant="light"
            size="sm"
            onClick={() => window.location.href = '/auth/patient-login'}
            leftSection={<IconHeart size={16} />}
            color="teal"
          >
            Patient
          </Button>
          <Button
            variant="light"
            size="sm"
            onClick={() => window.location.href = '/auth/provider-login'}
            leftSection={<IconStethoscope size={16} />}
            color="blue"
          >
            Provider
          </Button>
          <Button
            variant="light"
            size="sm"
            onClick={() => window.location.href = '/auth/provider-register'}
            leftSection={<IconUser size={16} />}
            color="green"
          >
            Register
          </Button>
        </Group>
      </Box>
    </AppShell>
  );
}

export const authRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/auth',
  component: AuthLayout,
}); 