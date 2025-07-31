import React, { useState } from 'react';
import {
  Group,
  Text,
  Box,
  ActionIcon,
  Menu,
  Avatar,
  Indicator,
  Divider,
  UnstyledButton,
  Paper,
} from '@mantine/core';
import {
  IconDashboard,
  IconCalendarTime,
  IconUsers,
  IconMessageCircle,
  IconReceipt,
  IconArrowsExchange,
  IconChartBar,
  IconSettings,
  IconBell,
  IconMail,
  IconChevronDown,
  IconLogout,
  IconUser,
} from '@tabler/icons-react';
import { useNavigate, useLocation } from '@tanstack/react-router';

interface NavbarProps {
  onTabChange?: (tab: string) => void;
  activeTab?: string;
}

const Navbar: React.FC<NavbarProps> = ({ onTabChange, activeTab = 'patients' }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [hoveredTab, setHoveredTab] = useState<string | null>(null);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: IconDashboard, path: '/provider/dashboard' },
    { id: 'scheduling', label: 'Scheduling', icon: IconCalendarTime, path: '/provider/availability' },
    { id: 'patients', label: 'Patients', icon: IconUsers, path: '/provider/patients' },
    { id: 'communications', label: 'Communications', icon: IconMessageCircle, path: '/provider/communications' },
    { id: 'billing', label: 'Billing', icon: IconReceipt, path: '/provider/billing' },
    { id: 'referral', label: 'Referral', icon: IconArrowsExchange, path: '/provider/referral' },
    { id: 'reports', label: 'Reports', icon: IconChartBar, path: '/provider/reports' },
    { id: 'settings', label: 'Settings', icon: IconSettings, path: '/provider/settings' },
  ];

  const handleTabClick = (tabId: string, path: string) => {
    if (onTabChange) {
      onTabChange(tabId);
    }
    navigate({ to: path });
  };

  const isActiveTab = (tabId: string) => {
    return activeTab === tabId || location.pathname.includes(tabId);
  };

  return (
    <Paper
      shadow="sm"
      style={{
        backgroundColor: '#233853',
        borderRadius: '0px 0px 4px 4px',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
      }}
    >
      <Group
        justify="space-between"
        align="center"
        px={16}
        style={{ height: 40 }}
      >
        {/* Logo */}
        <Group gap={6}>
          <Text
            size="sm"
            fw={500}
            c="white"
            style={{ fontFamily: 'Roboto, sans-serif' }}
          >
            Sample EMR
          </Text>
        </Group>

        {/* Navigation Items */}
        <Group gap={12} style={{ flex: 1 }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = isActiveTab(item.id);
            const isHovered = hoveredTab === item.id;

            return (
              <Box key={item.id} style={{ position: 'relative' }}>
                <UnstyledButton
                  onClick={() => handleTabClick(item.id, item.path)}
                  onMouseEnter={() => setHoveredTab(item.id)}
                  onMouseLeave={() => setHoveredTab(null)}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 4,
                    padding: '0 8px',
                    minHeight: isActive ? 14 : 'auto',
                    transition: 'all 0.2s ease',
                    opacity: isHovered ? 0.8 : 1,
                  }}
                >
                  <Group gap={8} justify="center" align="center" style={{ padding: '0 4px' }}>
                    <Text
                      size="sm"
                      c="white"
                      fw={400}
                      style={{
                        fontFamily: 'Roboto, sans-serif',
                        fontSize: 14,
                        lineHeight: '1em',
                        textAlign: 'center',
                      }}
                    >
                      {item.label}
                    </Text>
                  </Group>
                  
                  {/* Active indicator */}
                  {isActive && (
                    <Box
                      style={{
                        width: '100%',
                        height: 3,
                        backgroundColor: '#ffffff',
                        borderRadius: '2px 2px 0px 0px',
                        position: 'absolute',
                        bottom: -4,
                      }}
                    />
                  )}
                </UnstyledButton>
              </Box>
            );
          })}
        </Group>

        {/* Right Side Icons */}
        <Group gap={10}>
          {/* Search Icon */}
          <ActionIcon variant="subtle" color="white" size="sm">
            <Box style={{ width: 17.49, height: 17.49 }}>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path
                  d="M12.5 11h-.79l-.28-.27A6.471 6.471 0 0 0 13 6.5 6.5 6.5 0 1 0 6.5 13c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L17.49 16l-4.99-5zm-6 0C4.01 11 2 8.99 2 6.5S4.01 2 6.5 2 11 4.01 11 6.5 8.99 11 6.5 11z"
                  fill="white"
                />
              </svg>
            </Box>
          </ActionIcon>

          <Divider orientation="vertical" size="sm" color="rgba(255, 255, 255, 0.3)" />

          {/* Chat/Messages Icon with notification */}
          <Indicator
            inline
            label=""
            size={8}
            color="red"
            position="top-end"
            offset={2}
          >
            <ActionIcon variant="subtle" color="white" size="sm">
              <IconMessageCircle size={20} />
            </ActionIcon>
          </Indicator>

          <Divider orientation="vertical" size="sm" color="rgba(255, 255, 255, 0.3)" />

          {/* Notifications Icon */}
          <ActionIcon variant="subtle" color="white" size="sm">
            <IconBell size={20} />
          </ActionIcon>

          <Divider orientation="vertical" size="sm" color="rgba(255, 255, 255, 0.3)" />

          {/* User Profile Dropdown */}
          <Menu shadow="md" width={200} position="bottom-end">
            <Menu.Target>
              <Group gap={12} style={{ cursor: 'pointer' }}>
                <Avatar
                  size={20}
                  src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&h=100&fit=crop&crop=face"
                  style={{ border: '1px solid white' }}
                />
                <ActionIcon variant="subtle" color="white" size="sm">
                  <IconChevronDown size={16} opacity={0.87} />
                </ActionIcon>
              </Group>
            </Menu.Target>

            <Menu.Dropdown>
              <Menu.Label>Dr. Sarah Johnson</Menu.Label>
              <Menu.Item leftSection={<IconUser size={14} />}>
                Profile
              </Menu.Item>
              <Menu.Item leftSection={<IconSettings size={14} />}>
                Account Settings
              </Menu.Item>
              <Menu.Divider />
              <Menu.Item
                leftSection={<IconLogout size={14} />}
                color="red"
                onClick={() => navigate({ to: '/auth/provider-login' })}
              >
                Logout
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Group>
      </Group>
    </Paper>
  );
};

export default Navbar; 