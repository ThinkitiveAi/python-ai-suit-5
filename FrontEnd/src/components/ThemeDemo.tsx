import React from 'react';
import {
  Container,
  Paper,
  Title,
  Text,
  Button,
  Stack,
  Group,
  Box,
  Center,
  Card,
  Badge,
  Divider,
  TextInput,
  PasswordInput,
  Checkbox,
  Alert,
} from '@mantine/core';
import {
  IconHeart,
  IconUser,
  IconMail,
  IconLock,
  IconCheck,
  IconAlertCircle,
  IconStar,
  IconShield,
  IconBolt,
} from '@tabler/icons-react';

const ThemeDemo: React.FC = () => {
  return (
    <Box
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #c084fc 100%)',
        padding: '2rem 0',
      }}
    >
      <Container size="lg">
        <Stack gap="xl">
          {/* Header */}
          <Center>
            <Stack align="center" gap="md">
              <Box
                style={{
                  background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                  borderRadius: '50%',
                  padding: 24,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 8px 32px rgba(139, 92, 246, 0.4)',
                }}
              >
                                 <IconBolt size={48} color="white" />
              </Box>
              <Title 
                order={1} 
                size="3rem" 
                fw={700} 
                c="white" 
                ta="center"
                style={{
                  textShadow: '0 4px 8px rgba(0,0,0,0.2)',
                  letterSpacing: '-0.02em',
                }}
              >
                New Theme Preview
              </Title>
              <Text 
                size="xl" 
                c="white" 
                ta="center" 
                opacity={0.9}
                style={{ maxWidth: 600 }}
              >
                Experience our refreshed design with modern violet gradients, enhanced typography, and improved user experience
              </Text>
            </Stack>
          </Center>

          {/* Color Palette Showcase */}
          <Paper
            shadow="xl"
            p={40}
            radius="xl"
            style={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            <Title order={2} size="2rem" fw={600} mb="xl" ta="center">
              Color Palette
            </Title>
            <Group gap="lg" justify="center" wrap="wrap">
              {/* Primary Violet */}
              <Card p="md" radius="lg" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
                <Stack gap="xs" align="center">
                  <Text c="white" fw={600}>Primary Violet</Text>
                  <Text c="white" size="sm">#8b5cf6</Text>
                </Stack>
              </Card>

              {/* Secondary Mint */}
              <Card p="md" radius="lg" style={{ background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)' }}>
                <Stack gap="xs" align="center">
                  <Text c="white" fw={600}>Secondary Mint</Text>
                  <Text c="white" size="sm">#14b8a6</Text>
                </Stack>
              </Card>

              {/* Accent Coral */}
              <Card p="md" radius="lg" style={{ background: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)' }}>
                <Stack gap="xs" align="center">
                  <Text c="white" fw={600}>Accent Coral</Text>
                  <Text c="white" size="sm">#f97316</Text>
                </Stack>
              </Card>

              {/* Neutral Slate */}
              <Card p="md" radius="lg" style={{ background: 'linear-gradient(135deg, #64748b 0%, #475569 100%)' }}>
                <Stack gap="xs" align="center">
                  <Text c="white" fw={600}>Neutral Slate</Text>
                  <Text c="white" size="sm">#64748b</Text>
                </Stack>
              </Card>
            </Group>
          </Paper>

          {/* Component Showcase */}
          <Paper
            shadow="xl"
            p={40}
            radius="xl"
            style={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            <Title order={2} size="2rem" fw={600} mb="xl" ta="center">
              Modern Components
            </Title>
            
            <Stack gap="xl">
              {/* Buttons */}
              <Box>
                <Title order={3} size="1.5rem" fw={600} mb="md">
                  Buttons
                </Title>
                <Group gap="md" wrap="wrap">
                  <Button 
                    size="lg"
                    style={{
                      background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                      boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)',
                    }}
                  >
                    Primary Action
                  </Button>
                  <Button 
                    variant="outline" 
                    size="lg"
                    style={{
                      borderColor: '#8b5cf6',
                      color: '#8b5cf6',
                    }}
                  >
                    Secondary Action
                  </Button>
                  <Button 
                    variant="light" 
                    size="lg"
                    style={{
                      background: 'rgba(139, 92, 246, 0.1)',
                      color: '#8b5cf6',
                    }}
                  >
                    Light Variant
                  </Button>
                </Group>
              </Box>

              <Divider />

              {/* Form Elements */}
              <Box>
                <Title order={3} size="1.5rem" fw={600} mb="md">
                  Form Elements
                </Title>
                <Stack gap="md" style={{ maxWidth: 400 }}>
                  <TextInput
                    placeholder="Enter your email"
                    leftSection={<IconMail size={16} />}
                    size="md"
                    radius="md"
                  />
                  <PasswordInput
                    placeholder="Enter your password"
                    leftSection={<IconLock size={16} />}
                    size="md"
                    radius="md"
                  />
                  <Checkbox label="Remember me" />
                </Stack>
              </Box>

              <Divider />

              {/* Alerts */}
              <Box>
                <Title order={3} size="1.5rem" fw={600} mb="md">
                  Alerts & Notifications
                </Title>
                <Stack gap="md">
                  <Alert
                    icon={<IconCheck size={18} />}
                    title="Success!"
                    color="teal"
                    radius="md"
                    style={{
                      backgroundColor: 'rgba(16, 185, 129, 0.1)',
                      border: '1px solid rgba(16, 185, 129, 0.2)',
                    }}
                  >
                    Your action was completed successfully.
                  </Alert>
                  <Alert
                    icon={<IconAlertCircle size={18} />}
                    title="Information"
                    color="blue"
                    radius="md"
                    style={{
                      backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      border: '1px solid rgba(59, 130, 246, 0.2)',
                    }}
                  >
                    Here's some important information for you.
                  </Alert>
                </Stack>
              </Box>

              <Divider />

              {/* Cards */}
              <Box>
                <Title order={3} size="1.5rem" fw={600} mb="md">
                  Cards & Content
                </Title>
                <Group gap="lg" wrap="wrap">
                  <Card p="lg" radius="lg" style={{ minWidth: 280 }}>
                    <Stack gap="md">
                      <Box
                        style={{
                          background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                          borderRadius: '50%',
                          width: 48,
                          height: 48,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <IconHeart size={24} color="white" />
                      </Box>
                      <Title order={4} size="1.25rem" fw={600}>
                        Feature Card
                      </Title>
                      <Text c="dimmed" size="sm">
                        This is an example of our new card design with improved spacing and typography.
                      </Text>
                      <Group gap="xs">
                        <Badge color="violet" variant="light">New</Badge>
                        <Badge color="mint" variant="light">Featured</Badge>
                      </Group>
                    </Stack>
                  </Card>

                  <Card p="lg" radius="lg" style={{ minWidth: 280 }}>
                    <Stack gap="md">
                      <Box
                        style={{
                          background: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
                          borderRadius: '50%',
                          width: 48,
                          height: 48,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <IconShield size={24} color="white" />
                      </Box>
                      <Title order={4} size="1.25rem" fw={600}>
                        Security First
                      </Title>
                      <Text c="dimmed" size="sm">
                        Built with security and privacy in mind, ensuring your data is always protected.
                      </Text>
                      <Group gap="xs">
                        <Badge color="mint" variant="light">Secure</Badge>
                        <Badge color="coral" variant="light">Trusted</Badge>
                      </Group>
                    </Stack>
                  </Card>
                </Group>
              </Box>
            </Stack>
          </Paper>

          {/* Call to Action */}
          <Center>
            <Paper
              shadow="xl"
              p={40}
              radius="xl"
              style={{
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                textAlign: 'center',
                maxWidth: 600,
              }}
            >
              <Stack gap="lg" align="center">
                <Title order={2} size="2rem" fw={600}>
                  Ready to Experience the New Design?
                </Title>
                <Text size="lg" c="dimmed">
                  The updated theme brings a fresh, modern look with improved accessibility and user experience.
                </Text>
                <Group gap="md">
                  <Button 
                    size="lg"
                    style={{
                      background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                      boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)',
                    }}
                  >
                    Get Started
                  </Button>
                  <Button 
                    variant="outline" 
                    size="lg"
                    style={{
                      borderColor: '#8b5cf6',
                      color: '#8b5cf6',
                    }}
                  >
                    Learn More
                  </Button>
                </Group>
              </Stack>
            </Paper>
          </Center>
        </Stack>
      </Container>
    </Box>
  );
};

export default ThemeDemo; 