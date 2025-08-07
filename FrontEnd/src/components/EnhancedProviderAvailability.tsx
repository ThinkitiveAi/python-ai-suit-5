import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Paper,
  Title,
  Text,
  Button,
  Select,
  Stack,
  Group,
  Box,
  Center,
  Alert,
  Modal,
  Anchor,
  ActionIcon,
  Card,
  Badge,
  Tooltip,
  Menu,
  TextInput,
  Textarea,
  Checkbox,
  SimpleGrid,
  Timeline,
  ScrollArea,
  Divider,
  Switch,
  NumberInput,
  Tabs,
  Grid,
  Loader,
  Notification,
  Progress,
  RingProgress,
  Drawer,
  Kbd,
  Table,
  Pagination,
} from '@mantine/core';
import {
  IconCalendar,
  IconClock,
  IconStethoscope,
  IconPlus,
  IconEdit,
  IconTrash,
  IconCopy,
  IconSettings,
  IconChevronLeft,
  IconChevronRight,
  IconCalendarEvent,
  IconFilter,
  IconPrinter,
  IconDownload,
  IconRefresh,
  IconCheck,
  IconAlertTriangle,
  IconInfoCircle,
  IconX,
  IconDots,
  IconClockHour4,
  IconUserCheck,
  IconUserX,
  IconCalendarPlus,
  IconTemplate,
  IconRepeat,
  IconZoomIn,
  IconZoomOut,
  IconEye,
  IconEyeOff,
  IconBulb,
  IconHistory,
  IconDeviceFloppy,
  IconArrowBack,
  IconMenu2,
  IconGridDots,
  IconList,
  IconCalendarTime,
  IconClipboard,
  IconBrandGoogleFilled,
  IconUsers,
  IconUser,
  IconPhone,
  IconMail,
} from '@tabler/icons-react';
import { DatePicker, TimeInput } from '@mantine/dates';
import { notifications } from '@mantine/notifications';
import { useDisclosure } from '@mantine/hooks';
import { availabilityAPI, TimeSlot, Appointment, AvailabilityStats, AppointmentStats } from '../services/api';

// Types and Interfaces
interface AvailabilityFormData {
  date: Date | null;
  startTime: string;
  endTime: string;
  duration: number;
  status: 'available' | 'booked' | 'blocked' | 'tentative' | 'break';
  appointmentType: string;
  notes: string;
  isRecurring: boolean;
  recurringPattern: 'none' | 'daily' | 'weekly' | 'biweekly' | 'monthly';
  recurringEndDate: Date | null;
}

interface AppointmentFormData {
  availabilityId: string;
  patientId: string;
  appointmentDate: Date | null;
  startTime: string;
  endTime: string;
  appointmentType: string;
  reason: string;
  notes: string;
  patientNotes: string;
}

type CalendarView = 'month' | 'week' | 'day';

interface EnhancedProviderAvailabilityProps {
  providerId?: string;
  onClose?: () => void;
}

const EnhancedProviderAvailability: React.FC<EnhancedProviderAvailabilityProps> = ({ 
  providerId = 'provider-1', 
  onClose 
}) => {
  // State management
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [currentView, setCurrentView] = useState<CalendarView>('week');
  const [sidebarOpened, setSidebarOpened] = useState(true);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<AvailabilityStats>({
    totalSlots: 0,
    availableSlots: 0,
    bookedSlots: 0,
    blockedSlots: 0,
    utilizationRate: 0,
    averageBookingTime: 0,
  });
  const [appointmentStats, setAppointmentStats] = useState<AppointmentStats>({
    totalAppointments: 0,
    scheduledAppointments: 0,
    confirmedAppointments: 0,
    completedAppointments: 0,
    cancelledAppointments: 0,
    noShowAppointments: 0,
    completionRate: 0,
  });

  // Modal states
  const [addModalOpened, { open: openAddModal, close: closeAddModal }] = useDisclosure(false);
  const [editModalOpened, { open: openEditModal, close: closeEditModal }] = useDisclosure(false);
  const [appointmentModalOpened, { open: openAppointmentModal, close: closeAppointmentModal }] = useDisclosure(false);
  const [deleteModalOpened, { open: openDeleteModal, close: closeDeleteModal }] = useDisclosure(false);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);

  // Form states
  const [availabilityForm, setAvailabilityForm] = useState<AvailabilityFormData>({
    date: new Date(),
    startTime: '09:00',
    endTime: '10:00',
    duration: 60,
    status: 'available',
    appointmentType: '',
    notes: '',
    isRecurring: false,
    recurringPattern: 'none',
    recurringEndDate: null,
  });

  const [appointmentForm, setAppointmentForm] = useState<AppointmentFormData>({
    availabilityId: '',
    patientId: '',
    appointmentDate: new Date(),
    startTime: '09:00',
    endTime: '10:00',
    appointmentType: '',
    reason: '',
    notes: '',
    patientNotes: '',
  });

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, [providerId]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load availability slots
      const availabilityData = await availabilityAPI.getProviderAvailability(providerId);
      setTimeSlots(availabilityData);

      // Load appointments
      const appointmentData = await availabilityAPI.getProviderAppointments(providerId);
      setAppointments(appointmentData);

      // Load statistics
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30);
      const endDate = new Date();
      endDate.setDate(endDate.getDate() + 30);

      const availabilityStats = await availabilityAPI.getAvailabilityStats(
        providerId,
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );
      setStats(availabilityStats);

      const appointmentStatsData = await availabilityAPI.getAppointmentStats(
        providerId,
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );
      setAppointmentStats(appointmentStatsData);

    } catch (error) {
      console.error('Error loading data:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to load data',
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  // Utility functions
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatTime = (time: string) => {
    return time;
  };

  const getStatusBadge = (status: TimeSlot['status']) => {
    const statusConfig = {
      available: { color: 'green', label: 'Available' },
      booked: { color: 'blue', label: 'Booked' },
      blocked: { color: 'red', label: 'Blocked' },
      tentative: { color: 'yellow', label: 'Tentative' },
      break: { color: 'gray', label: 'Break' },
    };
    
    const config = statusConfig[status];
    return <Badge color={config.color} variant="light">{config.label}</Badge>;
  };

  const getAppointmentStatusBadge = (status: Appointment['status']) => {
    const statusConfig = {
      scheduled: { color: 'blue', label: 'Scheduled' },
      confirmed: { color: 'green', label: 'Confirmed' },
      cancelled: { color: 'red', label: 'Cancelled' },
      completed: { color: 'teal', label: 'Completed' },
      no_show: { color: 'orange', label: 'No Show' },
    };
    
    const config = statusConfig[status];
    return <Badge color={config.color} variant="light">{config.label}</Badge>;
  };

  // CRUD Operations for Availability
  const handleCreateAvailability = async () => {
    if (!availabilityForm.date) return;

    try {
      const newSlot = await availabilityAPI.createAvailability({
        providerId,
        date: availabilityForm.date.toISOString().split('T')[0],
        startTime: availabilityForm.startTime,
        endTime: availabilityForm.endTime,
        duration: availabilityForm.duration,
        status: availabilityForm.status,
        appointmentType: availabilityForm.appointmentType,
        notes: availabilityForm.notes,
        isRecurring: availabilityForm.isRecurring,
        recurringPattern: availabilityForm.recurringPattern,
        recurringEndDate: availabilityForm.recurringEndDate?.toISOString().split('T')[0],
      });

      setTimeSlots(prev => [...prev, newSlot]);
      closeAddModal();
      notifications.show({
        title: 'Success',
        message: 'Availability slot created successfully',
        color: 'green',
      });
    } catch (error) {
      console.error('Error creating availability:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to create availability slot',
        color: 'red',
      });
    }
  };

  const handleUpdateAvailability = async () => {
    if (!selectedSlot || !availabilityForm.date) return;

    try {
      const updatedSlot = await availabilityAPI.updateAvailability(selectedSlot.id, {
        date: availabilityForm.date.toISOString().split('T')[0],
        startTime: availabilityForm.startTime,
        endTime: availabilityForm.endTime,
        duration: availabilityForm.duration,
        status: availabilityForm.status,
        appointmentType: availabilityForm.appointmentType,
        notes: availabilityForm.notes,
        isRecurring: availabilityForm.isRecurring,
        recurringPattern: availabilityForm.recurringPattern,
        recurringEndDate: availabilityForm.recurringEndDate?.toISOString().split('T')[0],
      });

      setTimeSlots(prev => prev.map(slot => 
        slot.id === selectedSlot.id ? updatedSlot : slot
      ));
      closeEditModal();
      notifications.show({
        title: 'Success',
        message: 'Availability slot updated successfully',
        color: 'green',
      });
    } catch (error) {
      console.error('Error updating availability:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to update availability slot',
        color: 'red',
      });
    }
  };

  const handleDeleteAvailability = async () => {
    if (!selectedSlot) return;

    try {
      await availabilityAPI.deleteAvailability(selectedSlot.id);
      setTimeSlots(prev => prev.filter(slot => slot.id !== selectedSlot.id));
      closeDeleteModal();
      notifications.show({
        title: 'Success',
        message: 'Availability slot deleted successfully',
        color: 'green',
      });
    } catch (error) {
      console.error('Error deleting availability:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to delete availability slot',
        color: 'red',
      });
    }
  };

  // CRUD Operations for Appointments
  const handleCreateAppointment = async () => {
    if (!appointmentForm.appointmentDate) return;

    try {
      const newAppointment = await availabilityAPI.createAppointment({
        availabilityId: appointmentForm.availabilityId,
        patientId: appointmentForm.patientId,
        providerId,
        appointmentDate: appointmentForm.appointmentDate.toISOString().split('T')[0],
        startTime: appointmentForm.startTime,
        endTime: appointmentForm.endTime,
        appointmentType: appointmentForm.appointmentType,
        reason: appointmentForm.reason,
        notes: appointmentForm.notes,
        patientNotes: appointmentForm.patientNotes,
        status: 'scheduled',
      });

      setAppointments(prev => [...prev, newAppointment]);
      closeAppointmentModal();
      notifications.show({
        title: 'Success',
        message: 'Appointment created successfully',
        color: 'green',
      });
    } catch (error) {
      console.error('Error creating appointment:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to create appointment',
        color: 'red',
      });
    }
  };

  const handleUpdateAppointment = async () => {
    if (!selectedAppointment || !appointmentForm.appointmentDate) return;

    try {
      const updatedAppointment = await availabilityAPI.updateAppointment(selectedAppointment.id, {
        appointmentDate: appointmentForm.appointmentDate.toISOString().split('T')[0],
        startTime: appointmentForm.startTime,
        endTime: appointmentForm.endTime,
        appointmentType: appointmentForm.appointmentType,
        reason: appointmentForm.reason,
        notes: appointmentForm.notes,
        patientNotes: appointmentForm.patientNotes,
      });

      setAppointments(prev => prev.map(apt => 
        apt.id === selectedAppointment.id ? updatedAppointment : apt
      ));
      closeAppointmentModal();
      notifications.show({
        title: 'Success',
        message: 'Appointment updated successfully',
        color: 'green',
      });
    } catch (error) {
      console.error('Error updating appointment:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to update appointment',
        color: 'red',
      });
    }
  };

  const handleDeleteAppointment = async () => {
    if (!selectedAppointment) return;

    try {
      await availabilityAPI.deleteAppointment(selectedAppointment.id);
      setAppointments(prev => prev.filter(apt => apt.id !== selectedAppointment.id));
      closeDeleteModal();
      notifications.show({
        title: 'Success',
        message: 'Appointment deleted successfully',
        color: 'green',
      });
    } catch (error) {
      console.error('Error deleting appointment:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to delete appointment',
        color: 'red',
      });
    }
  };

  // Event handlers
  const handleAddSlot = () => {
    setAvailabilityForm({
      date: new Date(),
      startTime: '09:00',
      endTime: '10:00',
      duration: 60,
      status: 'available',
      appointmentType: '',
      notes: '',
      isRecurring: false,
      recurringPattern: 'none',
      recurringEndDate: null,
    });
    openAddModal();
  };

  const handleEditSlot = (slot: TimeSlot) => {
    setSelectedSlot(slot);
    setAvailabilityForm({
      date: new Date(slot.date),
      startTime: slot.startTime,
      endTime: slot.endTime,
      duration: slot.duration,
      status: slot.status,
      appointmentType: slot.appointmentType || '',
      notes: slot.notes || '',
      isRecurring: slot.isRecurring || false,
      recurringPattern: slot.recurringPattern || 'none',
      recurringEndDate: slot.recurringEndDate ? new Date(slot.recurringEndDate) : null,
    });
    openEditModal();
  };

  const handleDeleteSlot = (slot: TimeSlot) => {
    setSelectedSlot(slot);
    openDeleteModal();
  };

  const handleCreateAppointmentFromSlot = (slot: TimeSlot) => {
    setSelectedSlot(slot);
    setAppointmentForm({
      availabilityId: slot.id,
      patientId: '',
      appointmentDate: new Date(slot.date),
      startTime: slot.startTime,
      endTime: slot.endTime,
      appointmentType: slot.appointmentType || '',
      reason: '',
      notes: '',
      patientNotes: '',
    });
    openAppointmentModal();
  };

  const handleEditAppointment = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setAppointmentForm({
      availabilityId: appointment.availabilityId,
      patientId: appointment.patientId,
      appointmentDate: new Date(appointment.appointmentDate),
      startTime: appointment.startTime,
      endTime: appointment.endTime,
      appointmentType: appointment.appointmentType,
      reason: appointment.reason || '',
      notes: appointment.notes || '',
      patientNotes: appointment.patientNotes || '',
    });
    openAppointmentModal();
  };

  const handleDeleteAppointmentFromList = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    openDeleteModal();
  };

  const toggleSidebar = () => setSidebarOpened(!sidebarOpened);

  // Get slots for current view
  const getViewSlots = () => {
    const startOfWeek = new Date(selectedDate);
    startOfWeek.setDate(selectedDate.getDate() - selectedDate.getDay());
    
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6);

    return timeSlots.filter(slot => {
      const slotDate = new Date(slot.date);
      
      if (currentView === 'day') {
        return slotDate.toDateString() === selectedDate.toDateString();
      } else if (currentView === 'week') {
        return slotDate >= startOfWeek && slotDate <= endOfWeek;
      } else {
        return slotDate.getMonth() === selectedDate.getMonth() && 
               slotDate.getFullYear() === selectedDate.getFullYear();
      }
    });
  };

  const viewSlots = getViewSlots();

  return (
    <Box px={20} py={20} style={{ width: '100%' }}>
      {/* Header */}
      <Paper shadow="sm" p="md" radius="lg" mb="lg">
        <Group justify="space-between">
          <Group>
            <ActionIcon
              variant="subtle"
              size="lg"
              onClick={toggleSidebar}
              color="blue"
            >
              <IconMenu2 size={20} />
            </ActionIcon>
            <Box>
              <Title order={2} c="dark.8">
                <Group gap="xs">
                  <IconCalendarTime size={28} color="#8b5cf6" />
                  Enhanced Provider Availability Management
                </Group>
              </Title>
              <Text size="sm" c="dimmed">
                Dr. Sarah Johnson • Cardiologist • {formatDate(selectedDate)}
              </Text>
            </Box>
          </Group>
          
          <Group>
            <Button
              leftSection={<IconPlus size={16} />}
              onClick={handleAddSlot}
              style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)',
              }}
            >
              Add Availability
            </Button>
            <Button
              variant="light"
              leftSection={<IconRefresh size={16} />}
              onClick={loadData}
              loading={loading}
            >
              Refresh
            </Button>
          </Group>
        </Group>
      </Paper>

      <Grid>
        {/* Sidebar */}
        <Grid.Col span={{ base: 12, md: sidebarOpened ? 3 : 0 }}>
          {sidebarOpened && (
            <Stack gap="md">
              {/* Statistics */}
              <Card shadow="sm" padding="lg" radius="lg">
                <Stack gap="md">
                  <Text fw={600} size="sm">Availability Statistics</Text>
                  
                  <Center>
                    <RingProgress
                      size={120}
                      thickness={8}
                      sections={[
                        { value: stats.utilizationRate, color: '#8b5cf6' },
                        { value: 100 - stats.utilizationRate, color: '#e2e8f0' },
                      ]}
                      label={
                        <Center>
                          <div style={{ textAlign: 'center' }}>
                            <Text size="xs" c="dimmed">Utilization</Text>
                            <Text fw={700} size="lg">{stats.utilizationRate.toFixed(1)}%</Text>
                          </div>
                        </Center>
                      }
                    />
                  </Center>
                  
                  <SimpleGrid cols={2} spacing="xs">
                    <Box ta="center">
                      <Text size="lg" fw={700} c="green">{stats.availableSlots}</Text>
                      <Text size="xs" c="dimmed">Available</Text>
                    </Box>
                    <Box ta="center">
                      <Text size="lg" fw={700} c="blue">{stats.bookedSlots}</Text>
                      <Text size="xs" c="dimmed">Booked</Text>
                    </Box>
                  </SimpleGrid>
                </Stack>
              </Card>

              {/* Appointment Statistics */}
              <Card shadow="sm" padding="lg" radius="lg">
                <Stack gap="md">
                  <Text fw={600} size="sm">Appointment Statistics</Text>
                  
                  <SimpleGrid cols={2} spacing="xs">
                    <Box ta="center">
                      <Text size="lg" fw={700} c="teal">{appointmentStats.totalAppointments}</Text>
                      <Text size="xs" c="dimmed">Total</Text>
                    </Box>
                    <Box ta="center">
                      <Text size="lg" fw={700} c="green">{appointmentStats.completionRate.toFixed(1)}%</Text>
                      <Text size="xs" c="dimmed">Completion</Text>
                    </Box>
                  </SimpleGrid>
                </Stack>
              </Card>
            </Stack>
          )}
        </Grid.Col>

        {/* Main Content */}
        <Grid.Col span={{ base: 12, md: sidebarOpened ? 9 : 12 }}>
          <Tabs defaultValue="availability">
            <Tabs.List>
              <Tabs.Tab value="availability" leftSection={<IconCalendar size={16} />}>
                Availability Slots
              </Tabs.Tab>
              <Tabs.Tab value="appointments" leftSection={<IconUsers size={16} />}>
                Appointments
              </Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="availability" pt="md">
              <Stack gap="md">
                {/* Availability Slots Table */}
                <Paper shadow="sm" p="md" radius="lg">
                  <Group justify="space-between" mb="md">
                    <Title order={3} size="h4">Availability Slots</Title>
                    <Badge variant="light" color="blue">
                      {timeSlots.length} slots
                    </Badge>
                  </Group>

                  <ScrollArea>
                    <Table>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>Date</Table.Th>
                          <Table.Th>Time</Table.Th>
                          <Table.Th>Duration</Table.Th>
                          <Table.Th>Status</Table.Th>
                          <Table.Th>Type</Table.Th>
                          <Table.Th>Actions</Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {timeSlots.map((slot) => (
                          <Table.Tr key={slot.id}>
                            <Table.Td>{formatDate(new Date(slot.date))}</Table.Td>
                            <Table.Td>{formatTime(slot.startTime)} - {formatTime(slot.endTime)}</Table.Td>
                            <Table.Td>{slot.duration} min</Table.Td>
                            <Table.Td>{getStatusBadge(slot.status)}</Table.Td>
                            <Table.Td>{slot.appointmentType || '-'}</Table.Td>
                            <Table.Td>
                              <Group gap="xs">
                                <ActionIcon
                                  size="sm"
                                  variant="light"
                                  color="blue"
                                  onClick={() => handleEditSlot(slot)}
                                >
                                  <IconEdit size={14} />
                                </ActionIcon>
                                <ActionIcon
                                  size="sm"
                                  variant="light"
                                  color="red"
                                  onClick={() => handleDeleteSlot(slot)}
                                >
                                  <IconTrash size={14} />
                                </ActionIcon>
                                {slot.status === 'available' && (
                                  <ActionIcon
                                    size="sm"
                                    variant="light"
                                    color="green"
                                    onClick={() => handleCreateAppointmentFromSlot(slot)}
                                  >
                                    <IconCalendarPlus size={14} />
                                  </ActionIcon>
                                )}
                              </Group>
                            </Table.Td>
                          </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                  </ScrollArea>
                </Paper>
              </Stack>
            </Tabs.Panel>

            <Tabs.Panel value="appointments" pt="md">
              <Stack gap="md">
                {/* Appointments Table */}
                <Paper shadow="sm" p="md" radius="lg">
                  <Group justify="space-between" mb="md">
                    <Title order={3} size="h4">Appointments</Title>
                    <Badge variant="light" color="teal">
                      {appointments.length} appointments
                    </Badge>
                  </Group>

                  <ScrollArea>
                    <Table>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>Date</Table.Th>
                          <Table.Th>Time</Table.Th>
                          <Table.Th>Patient</Table.Th>
                          <Table.Th>Type</Table.Th>
                          <Table.Th>Status</Table.Th>
                          <Table.Th>Actions</Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {appointments.map((appointment) => (
                          <Table.Tr key={appointment.id}>
                            <Table.Td>{formatDate(new Date(appointment.appointmentDate))}</Table.Td>
                            <Table.Td>{formatTime(appointment.startTime)} - {formatTime(appointment.endTime)}</Table.Td>
                            <Table.Td>{appointment.patientId}</Table.Td>
                            <Table.Td>{appointment.appointmentType}</Table.Td>
                            <Table.Td>{getAppointmentStatusBadge(appointment.status)}</Table.Td>
                            <Table.Td>
                              <Group gap="xs">
                                <ActionIcon
                                  size="sm"
                                  variant="light"
                                  color="blue"
                                  onClick={() => handleEditAppointment(appointment)}
                                >
                                  <IconEdit size={14} />
                                </ActionIcon>
                                <ActionIcon
                                  size="sm"
                                  variant="light"
                                  color="red"
                                  onClick={() => handleDeleteAppointmentFromList(appointment)}
                                >
                                  <IconTrash size={14} />
                                </ActionIcon>
                              </Group>
                            </Table.Td>
                          </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                  </ScrollArea>
                </Paper>
              </Stack>
            </Tabs.Panel>
          </Tabs>
        </Grid.Col>
      </Grid>

      {/* Add/Edit Availability Modal */}
      <Modal
        opened={addModalOpened || editModalOpened}
        onClose={closeAddModal}
        title={addModalOpened ? "Add Availability Slot" : "Edit Availability Slot"}
        size="lg"
      >
        <Stack gap="md">
          <DatePicker
            label="Date"
            placeholder="Select date"
            value={availabilityForm.date}
            onChange={(date) => setAvailabilityForm(prev => ({ ...prev, date }))}
            required
          />
          
          <Group grow>
            <TimeInput
              label="Start Time"
              value={availabilityForm.startTime}
              onChange={(event) => setAvailabilityForm(prev => ({ 
                ...prev, 
                startTime: event.currentTarget.value 
              }))}
              required
            />
            <TimeInput
              label="End Time"
              value={availabilityForm.endTime}
              onChange={(event) => setAvailabilityForm(prev => ({ 
                ...prev, 
                endTime: event.currentTarget.value 
              }))}
              required
            />
          </Group>

          <NumberInput
            label="Duration (minutes)"
            value={availabilityForm.duration}
            onChange={(value) => setAvailabilityForm(prev => ({ 
              ...prev, 
              duration: value || 60 
            }))}
            min={15}
            max={480}
            required
          />

          <Select
            label="Status"
            value={availabilityForm.status}
            onChange={(value) => setAvailabilityForm(prev => ({ 
              ...prev, 
              status: value as any 
            }))}
            data={[
              { value: 'available', label: 'Available' },
              { value: 'blocked', label: 'Blocked' },
              { value: 'tentative', label: 'Tentative' },
              { value: 'break', label: 'Break' },
            ]}
            required
          />

          <TextInput
            label="Appointment Type"
            value={availabilityForm.appointmentType}
            onChange={(event) => setAvailabilityForm(prev => ({ 
              ...prev, 
              appointmentType: event.currentTarget.value 
            }))}
            placeholder="e.g., Consultation, Follow-up"
          />

          <Textarea
            label="Notes"
            value={availabilityForm.notes}
            onChange={(event) => setAvailabilityForm(prev => ({ 
              ...prev, 
              notes: event.currentTarget.value 
            }))}
            placeholder="Additional notes..."
          />

          <Checkbox
            label="Recurring"
            checked={availabilityForm.isRecurring}
            onChange={(event) => setAvailabilityForm(prev => ({ 
              ...prev, 
              isRecurring: event.currentTarget.checked 
            }))}
          />

          {availabilityForm.isRecurring && (
            <>
              <Select
                label="Recurring Pattern"
                value={availabilityForm.recurringPattern}
                onChange={(value) => setAvailabilityForm(prev => ({ 
                  ...prev, 
                  recurringPattern: value as any 
                }))}
                data={[
                  { value: 'daily', label: 'Daily' },
                  { value: 'weekly', label: 'Weekly' },
                  { value: 'biweekly', label: 'Bi-weekly' },
                  { value: 'monthly', label: 'Monthly' },
                ]}
              />
              <DatePicker
                label="End Date"
                placeholder="Select end date"
                value={availabilityForm.recurringEndDate}
                onChange={(date) => setAvailabilityForm(prev => ({ ...prev, recurringEndDate: date }))}
              />
            </>
          )}

          <Group justify="flex-end" mt="md">
            <Button variant="light" onClick={closeAddModal}>
              Cancel
            </Button>
            <Button
              onClick={addModalOpened ? handleCreateAvailability : handleUpdateAvailability}
              style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)',
              }}
            >
              {addModalOpened ? 'Create' : 'Update'}
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Add/Edit Appointment Modal */}
      <Modal
        opened={appointmentModalOpened}
        onClose={closeAppointmentModal}
        title={selectedAppointment ? "Edit Appointment" : "Create Appointment"}
        size="lg"
      >
        <Stack gap="md">
          <TextInput
            label="Patient ID"
            value={appointmentForm.patientId}
            onChange={(event) => setAppointmentForm(prev => ({ 
              ...prev, 
              patientId: event.currentTarget.value 
            }))}
            required
          />

          <DatePicker
            label="Appointment Date"
            placeholder="Select date"
            value={appointmentForm.appointmentDate}
            onChange={(date) => setAppointmentForm(prev => ({ ...prev, appointmentDate: date }))}
            required
          />
          
          <Group grow>
            <TimeInput
              label="Start Time"
              value={appointmentForm.startTime}
              onChange={(event) => setAppointmentForm(prev => ({ 
                ...prev, 
                startTime: event.currentTarget.value 
              }))}
              required
            />
            <TimeInput
              label="End Time"
              value={appointmentForm.endTime}
              onChange={(event) => setAppointmentForm(prev => ({ 
                ...prev, 
                endTime: event.currentTarget.value 
              }))}
              required
            />
          </Group>

          <TextInput
            label="Appointment Type"
            value={appointmentForm.appointmentType}
            onChange={(event) => setAppointmentForm(prev => ({ 
              ...prev, 
              appointmentType: event.currentTarget.value 
            }))}
            placeholder="e.g., Consultation, Follow-up"
            required
          />

          <Textarea
            label="Reason"
            value={appointmentForm.reason}
            onChange={(event) => setAppointmentForm(prev => ({ 
              ...prev, 
              reason: event.currentTarget.value 
            }))}
            placeholder="Reason for appointment..."
          />

          <Textarea
            label="Provider Notes"
            value={appointmentForm.notes}
            onChange={(event) => setAppointmentForm(prev => ({ 
              ...prev, 
              notes: event.currentTarget.value 
            }))}
            placeholder="Provider notes..."
          />

          <Textarea
            label="Patient Notes"
            value={appointmentForm.patientNotes}
            onChange={(event) => setAppointmentForm(prev => ({ 
              ...prev, 
              patientNotes: event.currentTarget.value 
            }))}
            placeholder="Patient notes..."
          />

          <Group justify="flex-end" mt="md">
            <Button variant="light" onClick={closeAppointmentModal}>
              Cancel
            </Button>
            <Button
              onClick={selectedAppointment ? handleUpdateAppointment : handleCreateAppointment}
              style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)',
              }}
            >
              {selectedAppointment ? 'Update' : 'Create'}
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        opened={deleteModalOpened}
        onClose={closeDeleteModal}
        title="Confirm Delete"
        size="sm"
      >
        <Stack gap="md">
          <Text>
            Are you sure you want to delete this {selectedAppointment ? 'appointment' : 'availability slot'}?
            This action cannot be undone.
          </Text>
          
          <Group justify="flex-end" mt="md">
            <Button variant="light" onClick={closeDeleteModal}>
              Cancel
            </Button>
            <Button
              color="red"
              onClick={selectedAppointment ? handleDeleteAppointment : handleDeleteAvailability}
            >
              Delete
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Box>
  );
};

export default EnhancedProviderAvailability; 