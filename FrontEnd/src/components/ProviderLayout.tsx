import React, { useState } from 'react';
import { Box, Container } from '@mantine/core';
import Navbar from './Navbar';
import ProviderAvailability from './ProviderAvailability';

interface ProviderLayoutProps {
  children?: React.ReactNode;
  activeTab?: string;
}

const ProviderLayout: React.FC<ProviderLayoutProps> = ({ 
  children, 
  activeTab = 'scheduling' 
}) => {
  const [currentTab, setCurrentTab] = useState(activeTab);

  const handleTabChange = (tab: string) => {
    setCurrentTab(tab);
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'scheduling':
        return <ProviderAvailability />;
      case 'dashboard':
        return (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Dashboard</h2>
              <p>Dashboard content will be implemented here</p>
            </Box>
          </Container>
        );
      case 'patients':
        return (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Patients</h2>
              <p>Patient management content will be implemented here</p>
            </Box>
          </Container>
        );
      case 'communications':
        return (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Communications</h2>
              <p>Communications content will be implemented here</p>
            </Box>
          </Container>
        );
      case 'billing':
        return (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Billing</h2>
              <p>Billing content will be implemented here</p>
            </Box>
          </Container>
        );
      case 'referral':
        return (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Referral</h2>
              <p>Referral content will be implemented here</p>
            </Box>
          </Container>
        );
      case 'reports':
        return (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Reports</h2>
              <p>Reports content will be implemented here</p>
            </Box>
          </Container>
        );
      case 'settings':
        return (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Settings</h2>
              <p>Settings content will be implemented here</p>
            </Box>
          </Container>
        );
      default:
        return children || (
          <Container size="xl" py={40}>
            <Box ta="center">
              <h2>Welcome to Sample EMR</h2>
              <p>Select a tab from the navigation to get started</p>
            </Box>
          </Container>
        );
    }
  };

  return (
    <Box style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      <Navbar 
        onTabChange={handleTabChange} 
        activeTab={currentTab} 
      />
      <Box style={{ minHeight: 'calc(100vh - 40px)' }}>
        {renderContent()}
      </Box>
    </Box>
  );
};

export default ProviderLayout; 