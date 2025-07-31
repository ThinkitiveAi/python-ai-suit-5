import React from 'react';
import { createRootRoute, Link, Outlet } from '@tanstack/react-router';
import { MantineProvider } from '@mantine/core';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';

const theme = {
  primaryColor: 'blue',
  colors: {
    blue: ['#eff6ff', '#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e40af', '#1e3a8a'] as const,
    green: ['#ecfdf5', '#d1fae5', '#a7f3d0', '#6ee7b7', '#34d399', '#10b981', '#059669', '#047857', '#065f46', '#064e3b'] as const,
    teal: ['#f0fdfa', '#ccfbf1', '#99f6e4', '#5eead4', '#2dd4bf', '#14b8a6', '#0d9488', '#0f766e', '#115e59', '#134e4a'] as const,
  },
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
};

function RootComponent() {
  return (
    <MantineProvider theme={theme}>
      <div className="app">
        <Outlet />
      </div>
      <TanStackRouterDevtools />
    </MantineProvider>
  );
}

export const rootRoute = createRootRoute({
  component: RootComponent,
}); 