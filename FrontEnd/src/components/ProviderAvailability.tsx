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
  BackgroundImage,
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
} from '@tabler/icons-react';
import { DatePicker, TimeInput } from '@mantine/dates';
import { notifications } from '@mantine/notifications';
import { useDisclosure } from '@mantine/hooks';

// Types and Interfaces
interface TimeSlot {
  id: string;
  date: Date;
  startTime: string;
  endTime: string;
  duration: number; // in minutes
  status: 'available' | 'booked' | 'blocked' | 'tentative' | 'break';
  appointmentType?: string;
  patientName?: string;
  notes?: string;
  isRecurring?: boolean;
  recurringPattern?: 'weekly' | 'biweekly' | 'monthly';
}

interface AvailabilityTemplate {
  id: string;
  name: string;
  description: string;
  timeSlots: Omit<TimeSlot, 'id' | 'date'>[];
  isDefault: boolean;
}

interface ProviderStats {
  totalSlots: number;
  availableSlots: number;
  bookedSlots: number;
  utilizationRate: number;
  averageBookingTime: number;
}

type CalendarView = 'month' | 'week' | 'day';

const APPOINTMENT_TYPES = [
  'General Consultation',
  'Follow-up',
  'Emergency',
  'Routine Checkup',
  'Specialist Consultation',
  'Procedure',
  'Telemedicine',
];

const DURATION_OPTIONS = [
  { value: '15', label: '15 minutes' },
  { value: '30', label: '30 minutes' },
  { value: '45', label: '45 minutes' },
  { value: '60', label: '1 hour' },
  { value: '90', label: '1.5 hours' },
  { value: '120', label: '2 hours' },
];

const STATUS_COLORS = {
  available: '#10b981',
  booked: '#3b82f6',
  blocked: '#ef4444',
  tentative: '#f59e0b',
  break: '#6b7280',
};

interface ProviderAvailabilityProps {
  providerId?: string;
  onClose?: () => void;
}

const ProviderAvailability: React.FC<ProviderAvailabilityProps> = ({ 
  providerId = 'provider-1', 
  onClose 
}) => {
  // State Management
  const [currentView, setCurrentView] = useState<CalendarView>('week');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [templates, setTemplates] = useState<AvailabilityTemplate[]>([]);
  const [selectedSlots, setSelectedSlots] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState<ProviderStats>({
    totalSlots: 0,
    availableSlots: 0,
    bookedSlots: 0,
    utilizationRate: 0,
    averageBookingTime: 0,
  });

  // Modal and Form States
  const [addModalOpened, { open: openAddModal, close: closeAddModal }] = useDisclosure(false);
  const [editModalOpened, { open: openEditModal, close: closeEditModal }] = useDisclosure(false);
  const [templateModalOpened, { open: openTemplateModal, close: closeTemplateModal }] = useDisclosure(false);
  const [settingsOpened, { open: openSettings, close: closeSettings }] = useDisclosure(false);
  const [sidebarOpened, { toggle: toggleSidebar }] = useDisclosure(true);

  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [bulkEditMode, setBulkEditMode] = useState(false);
  const [showConflicts, setShowConflicts] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  // Form States
  const [formData, setFormData] = useState({
    date: new Date(),
    startTime: '09:00',
    endTime: '17:00',
    duration: 30,
    appointmentType: 'General Consultation',
    notes: '',
    isRecurring: false,
    recurringPattern: 'weekly' as 'weekly' | 'biweekly' | 'monthly',
    breakDuration: 15,
  });

  // Mock Data Generation
  const generateMockData = useCallback(() => {
    const mockSlots: TimeSlot[] = [];
    const today = new Date();
    
    for (let i = 0; i < 14; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      
      // Skip weekends for this example
      if (date.getDay() === 0 || date.getDay() === 6) continue;
      
      const slots = [
        {
          id: `slot-${i}-1`,
          date,
          startTime: '09:00',
          endTime: '09:30',
          duration: 30,
          status: Math.random() > 0.7 ? 'booked' : 'available',
          appointmentType: 'General Consultation',
          patientName: Math.random() > 0.7 ? 'John Doe' : undefined,
        },
        {
          id: `slot-${i}-2`,
          date,
          startTime: '10:00',
          endTime: '10:30',
          duration: 30,
          status: Math.random() > 0.6 ? 'booked' : 'available',
          appointmentType: 'Follow-up',
          patientName: Math.random() > 0.6 ? 'Jane Smith' : undefined,
        },
        {
          id: `slot-${i}-3`,
          date,
          startTime: '11:00',
          endTime: '11:30',
          duration: 30,
          status: Math.random() > 0.8 ? 'tentative' : 'available',
          appointmentType: 'Routine Checkup',
        },
        {
          id: `slot-${i}-4`,
          date,
          startTime: '14:00',
          endTime: '14:30',
          duration: 30,
          status: 'break',
          notes: 'Lunch break',
        },
        {
          id: `slot-${i}-5`,
          date,
          startTime: '15:00',
          endTime: '15:30',
          duration: 30,
          status: Math.random() > 0.5 ? 'booked' : 'available',
          appointmentType: 'Specialist Consultation',
          patientName: Math.random() > 0.5 ? 'Mike Johnson' : undefined,
        },
      ] as TimeSlot[];
      
      mockSlots.push(...slots);
    }
    
    setTimeSlots(mockSlots);
    
    // Calculate stats
    const total = mockSlots.length;
    const available = mockSlots.filter(slot => slot.status === 'available').length;
    const booked = mockSlots.filter(slot => slot.status === 'booked').length;
    
    setStats({
      totalSlots: total,
      availableSlots: available,
      bookedSlots: booked,
      utilizationRate: Math.round((booked / total) * 100),
      averageBookingTime: 32,
    });
  }, []);

  // Mock Templates
  const generateMockTemplates = useCallback(() => {
    const mockTemplates: AvailabilityTemplate[] = [
      {
        id: 'template-1',
        name: 'Standard Weekday',
        description: 'Regular 9-5 schedule with lunch break',
        isDefault: true,
        timeSlots: [
          { startTime: '09:00', endTime: '12:00', duration: 30, status: 'available', appointmentType: 'General Consultation' },
          { startTime: '12:00', endTime: '13:00', duration: 60, status: 'break', notes: 'Lunch break' },
          { startTime: '13:00', endTime: '17:00', duration: 30, status: 'available', appointmentType: 'General Consultation' },
        ],
      },
      {
        id: 'template-2',
        name: 'Half Day Morning',
        description: 'Morning appointments only',
        isDefault: false,
        timeSlots: [
          { startTime: '08:00', endTime: '12:00', duration: 30, status: 'available', appointmentType: 'General Consultation' },
        ],
      },
      {
        id: 'template-3',
        name: 'Extended Hours',
        description: 'Early morning and evening availability',
        isDefault: false,
        timeSlots: [
          { startTime: '07:00', endTime: '09:00', duration: 30, status: 'available', appointmentType: 'Early Consultation' },
          { startTime: '09:00', endTime: '17:00', duration: 30, status: 'available', appointmentType: 'General Consultation' },
          { startTime: '17:00', endTime: '19:00', duration: 30, status: 'available', appointmentType: 'Evening Consultation' },
        ],
      },
    ];
    
    setTemplates(mockTemplates);
  }, []);

  useEffect(() => {
    generateMockData();
    generateMockTemplates();
  }, [generateMockData, generateMockTemplates]);

  // Helper Functions
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const formatTime = (time: string) => {
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const getStatusBadge = (status: TimeSlot['status']) => {
    const colors = {
      available: 'green',
      booked: 'blue',
      blocked: 'red',
      tentative: 'yellow',
      break: 'gray',
    };

    const labels = {
      available: 'Available',
      booked: 'Booked',
      blocked: 'Blocked',
      tentative: 'Tentative',
      break: 'Break',
    };

    return (
      <Badge color={colors[status]} variant="light" size="sm">
        {labels[status]}
      </Badge>
    );
  };

  const handleAddSlot = () => {
    const newSlot: TimeSlot = {
      id: `slot-${Date.now()}`,
      date: formData.date,
      startTime: formData.startTime,
      endTime: formData.endTime,
      duration: formData.duration,
      status: 'available',
      appointmentType: formData.appointmentType,
      notes: formData.notes,
      isRecurring: formData.isRecurring,
      recurringPattern: formData.recurringPattern,
    };

    setTimeSlots(prev => [...prev, newSlot]);
    closeAddModal();
    
    notifications.show({
      title: 'Availability Added',
      message: 'New time slot has been added successfully',
      color: 'green',
      icon: <IconCheck size={16} />,
    });
  };

  const handleEditSlot = () => {
    if (!selectedSlot) return;

    setTimeSlots(prev => prev.map(slot => 
      slot.id === selectedSlot.id 
        ? { ...slot, ...formData }
        : slot
    ));
    
    closeEditModal();
    setSelectedSlot(null);
    
    notifications.show({
      title: 'Availability Updated',
      message: 'Time slot has been updated successfully',
      color: 'blue',
      icon: <IconCheck size={16} />,
    });
  };

  const handleDeleteSlot = (slotId: string) => {
    setTimeSlots(prev => prev.filter(slot => slot.id !== slotId));
    
    notifications.show({
      title: 'Availability Removed',
      message: 'Time slot has been removed successfully',
      color: 'red',
      icon: <IconTrash size={16} />,
    });
  };

  const handleBulkAction = (action: 'delete' | 'block' | 'unblock') => {
    if (selectedSlots.length === 0) return;

    switch (action) {
      case 'delete':
        setTimeSlots(prev => prev.filter(slot => !selectedSlots.includes(slot.id)));
        notifications.show({
          title: 'Bulk Delete Complete',
          message: `${selectedSlots.length} slots removed`,
          color: 'red',
        });
        break;
      case 'block':
        setTimeSlots(prev => prev.map(slot => 
          selectedSlots.includes(slot.id) 
            ? { ...slot, status: 'blocked' as const }
            : slot
        ));
        notifications.show({
          title: 'Slots Blocked',
          message: `${selectedSlots.length} slots blocked`,
          color: 'orange',
        });
        break;
      case 'unblock':
        setTimeSlots(prev => prev.map(slot => 
          selectedSlots.includes(slot.id) 
            ? { ...slot, status: 'available' as const }
            : slot
        ));
        notifications.show({
          title: 'Slots Unblocked',
          message: `${selectedSlots.length} slots made available`,
          color: 'green',
        });
        break;
    }

    setSelectedSlots([]);
    setBulkEditMode(false);
  };

  const applyTemplate = (template: AvailabilityTemplate) => {
    const newSlots: TimeSlot[] = template.timeSlots.map((templateSlot, index) => ({
      id: `template-${template.id}-${Date.now()}-${index}`,
      date: formData.date,
      ...templateSlot,
    }));

    setTimeSlots(prev => [...prev, ...newSlots]);
    closeTemplateModal();
    
    notifications.show({
      title: 'Template Applied',
      message: `${template.name} template applied successfully`,
      color: 'green',
      icon: <IconTemplate size={16} />,
    });
  };

  // Calendar Navigation
  const navigateDate = (direction: 'prev' | 'next' | 'today') => {
    const newDate = new Date(selectedDate);
    
    switch (direction) {
      case 'prev':
        if (currentView === 'month') {
          newDate.setMonth(newDate.getMonth() - 1);
        } else if (currentView === 'week') {
          newDate.setDate(newDate.getDate() - 7);
        } else {
          newDate.setDate(newDate.getDate() - 1);
        }
        break;
      case 'next':
        if (currentView === 'month') {
          newDate.setMonth(newDate.getMonth() + 1);
        } else if (currentView === 'week') {
          newDate.setDate(newDate.getDate() + 7);
        } else {
          newDate.setDate(newDate.getDate() + 1);
        }
        break;
      case 'today':
        setSelectedDate(new Date());
        return;
    }
    
    setSelectedDate(newDate);
  };

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
                  <IconCalendarTime size={28} color="#3b82f6" />
                  Provider Availability Management
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
              onClick={openAddModal}
              gradient={{ from: 'blue.5', to: 'blue.7' }}
            >
              Add Availability
            </Button>
            <Button
              variant="light"
              leftSection={<IconTemplate size={16} />}
              onClick={openTemplateModal}
            >
              Templates
            </Button>
            <ActionIcon
              variant="light"
              size="lg"
              onClick={openSettings}
              color="gray"
            >
              <IconSettings size={18} />
            </ActionIcon>
          </Group>
        </Group>
      </Paper>

        <Grid>
          {/* Sidebar */}
          <Grid.Col span={{ base: 12, md: sidebarOpened ? 3 : 0 }}>
            {sidebarOpened && (
              <Stack gap="md">
                {/* Calendar Navigation */}
                <Card shadow="sm" padding="lg" radius="lg">
                  <Stack gap="md">
                    <Group justify="space-between">
                      <Text fw={600} size="sm">Calendar Navigation</Text>
                      <Group gap="xs">
                        <ActionIcon
                          variant="subtle"
                          size="sm"
                          onClick={() => navigateDate('prev')}
                        >
                          <IconChevronLeft size={14} />
                        </ActionIcon>
                        <ActionIcon
                          variant="subtle"
                          size="sm"
                          onClick={() => navigateDate('today')}
                        >
                          <IconCalendarEvent size={14} />
                        </ActionIcon>
                        <ActionIcon
                          variant="subtle"
                          size="sm"
                          onClick={() => navigateDate('next')}
                        >
                          <IconChevronRight size={14} />
                        </ActionIcon>
                      </Group>
                    </Group>
                    
                    <TextInput
                      type="date"
                      value={selectedDate.toISOString().split('T')[0]}
                      onChange={(event) => {
                        const newDate = new Date(event.currentTarget.value);
                        if (!isNaN(newDate.getTime())) {
                          setSelectedDate(newDate);
                        }
                      }}
                      size="sm"
                    />
                    
                    <Group justify="center">
                      <Button.Group>
                        <Button
                          variant={currentView === 'day' ? 'filled' : 'light'}
                          size="xs"
                          onClick={() => setCurrentView('day')}
                        >
                          Day
                        </Button>
                        <Button
                          variant={currentView === 'week' ? 'filled' : 'light'}
                          size="xs"
                          onClick={() => setCurrentView('week')}
                        >
                          Week
                        </Button>
                        <Button
                          variant={currentView === 'month' ? 'filled' : 'light'}
                          size="xs"
                          onClick={() => setCurrentView('month')}
                        >
                          Month
                        </Button>
                      </Button.Group>
                    </Group>
                  </Stack>
                </Card>

                {/* Statistics */}
                <Card shadow="sm" padding="lg" radius="lg">
                  <Stack gap="md">
                    <Text fw={600} size="sm">Availability Statistics</Text>
                    
                    <Center>
                      <RingProgress
                        size={120}
                        thickness={8}
                        sections={[
                          { value: (stats.bookedSlots / stats.totalSlots) * 100, color: 'blue' },
                          { value: (stats.availableSlots / stats.totalSlots) * 100, color: 'green' },
                        ]}
                        label={
                          <Center>
                            <div style={{ textAlign: 'center' }}>
                              <Text size="xs" c="dimmed">Utilization</Text>
                              <Text fw={700} size="lg">{stats.utilizationRate}%</Text>
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

                {/* Legend */}
                <Card shadow="sm" padding="lg" radius="lg">
                  <Stack gap="md">
                    <Text fw={600} size="sm">Status Legend</Text>
                    
                    <Stack gap="xs">
                      {Object.entries(STATUS_COLORS).map(([status, color]) => (
                        <Group key={status} gap="xs">
                          <Box
                            w={12}
                            h={12}
                            style={{
                              backgroundColor: color,
                              borderRadius: 2,
                            }}
                          />
                          <Text size="xs" tt="capitalize">{status}</Text>
                        </Group>
                      ))}
                    </Stack>
                  </Stack>
                </Card>

                {/* Quick Actions */}
                <Card shadow="sm" padding="lg" radius="lg">
                  <Stack gap="md">
                    <Text fw={600} size="sm">Quick Actions</Text>
                    
                    <Stack gap="xs">
                      <Button
                        variant="light"
                        size="xs"
                        leftSection={<IconRefresh size={14} />}
                        onClick={generateMockData}
                        fullWidth
                      >
                        Refresh Data
                      </Button>
                      <Button
                        variant="light"
                        size="xs"
                        leftSection={<IconPrinter size={14} />}
                        fullWidth
                      >
                        Print Schedule
                      </Button>
                      <Button
                        variant="light"
                        size="xs"
                        leftSection={<IconDownload size={14} />}
                        fullWidth
                      >
                        Export Data
                      </Button>
                    </Stack>
                  </Stack>
                </Card>
              </Stack>
            )}
          </Grid.Col>

          {/* Main Content */}
          <Grid.Col span={{ base: 12, md: sidebarOpened ? 9 : 12 }}>
            <Stack gap="md">
              {/* View Controls */}
              <Paper shadow="sm" p="md" radius="lg">
                <Group justify="space-between">
                  <Group>
                    <Text fw={600}>
                      {currentView === 'day' && `Day View - ${formatDate(selectedDate)}`}
                      {currentView === 'week' && `Week View - Week of ${formatDate(selectedDate)}`}
                      {currentView === 'month' && `Month View - ${selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}`}
                    </Text>
                    <Badge variant="light" color="blue">
                      {viewSlots.length} slots
                    </Badge>
                  </Group>
                  
                  <Group>
                    {bulkEditMode && (
                      <Group gap="xs">
                        <Badge variant="light" color="orange">
                          {selectedSlots.length} selected
                        </Badge>
                        <Button
                          size="xs"
                          variant="light"
                          color="red"
                          onClick={() => handleBulkAction('delete')}
                          disabled={selectedSlots.length === 0}
                        >
                          Delete
                        </Button>
                        <Button
                          size="xs"
                          variant="light"
                          color="orange"
                          onClick={() => handleBulkAction('block')}
                          disabled={selectedSlots.length === 0}
                        >
                          Block
                        </Button>
                        <Button
                          size="xs"
                          variant="light"
                          color="green"
                          onClick={() => handleBulkAction('unblock')}
                          disabled={selectedSlots.length === 0}
                        >
                          Unblock
                        </Button>
                      </Group>
                    )}
                    
                    <Switch
                      label="Bulk Edit"
                      checked={bulkEditMode}
                      onChange={(event) => {
                        setBulkEditMode(event.currentTarget.checked);
                        setSelectedSlots([]);
                      }}
                      size="sm"
                    />
                    
                    <Menu shadow="md" width={200}>
                      <Menu.Target>
                        <ActionIcon variant="light" color="gray">
                          <IconDots size={16} />
                        </ActionIcon>
                      </Menu.Target>
                      <Menu.Dropdown>
                        <Menu.Item leftSection={<IconFilter size={14} />}>
                          Filter Slots
                        </Menu.Item>
                        <Menu.Item leftSection={<IconEye size={14} />}>
                          Show Conflicts
                        </Menu.Item>
                        <Menu.Item leftSection={<IconZoomIn size={14} />}>
                          Zoom In
                        </Menu.Item>
                        <Menu.Item leftSection={<IconZoomOut size={14} />}>
                          Zoom Out
                        </Menu.Item>
                      </Menu.Dropdown>
                    </Menu>
                  </Group>
                </Group>
              </Paper>

              {/* Calendar Content */}
              <Paper shadow="sm" p="lg" radius="lg" style={{ minHeight: 600 }}>
                {isLoading ? (
                  <Center h={400}>
                    <Stack align="center" gap="md">
                      <Loader size="lg" />
                      <Text size="sm" c="dimmed">Loading availability data...</Text>
                    </Stack>
                  </Center>
                ) : (
                  <ScrollArea h={500}>
                    {currentView === 'day' && (
                      <Stack gap="xs">
                        {viewSlots.length === 0 ? (
                          <Center h={300}>
                            <Stack align="center" gap="md">
                              <IconCalendar size={48} color="#cbd5e1" />
                              <Text size="sm" c="dimmed">No availability set for this day</Text>
                              <Button
                                variant="light"
                                leftSection={<IconPlus size={16} />}
                                onClick={openAddModal}
                              >
                                Add Availability
                              </Button>
                            </Stack>
                          </Center>
                        ) : (
                          viewSlots
                            .sort((a, b) => a.startTime.localeCompare(b.startTime))
                            .map((slot) => (
                              <Card
                                key={slot.id}
                                shadow="xs"
                                padding="md"
                                radius="md"
                                withBorder
                                style={{
                                  borderLeft: `4px solid ${STATUS_COLORS[slot.status]}`,
                                  cursor: bulkEditMode ? 'pointer' : 'default',
                                  backgroundColor: selectedSlots.includes(slot.id) ? '#f1f5f9' : undefined,
                                }}
                                onClick={() => {
                                  if (bulkEditMode) {
                                    setSelectedSlots(prev => 
                                      prev.includes(slot.id)
                                        ? prev.filter(id => id !== slot.id)
                                        : [...prev, slot.id]
                                    );
                                  }
                                }}
                              >
                                <Group justify="space-between">
                                  <Group>
                                    {bulkEditMode && (
                                      <Checkbox
                                        checked={selectedSlots.includes(slot.id)}
                                        onChange={() => {}}
                                        size="sm"
                                      />
                                    )}
                                    <Box>
                                      <Group gap="xs" mb="xs">
                                        <Text fw={600} size="sm">
                                          {formatTime(slot.startTime)} - {formatTime(slot.endTime)}
                                        </Text>
                                        {getStatusBadge(slot.status)}
                                        <Badge variant="outline" size="xs">
                                          {slot.duration}min
                                        </Badge>
                                      </Group>
                                      <Text size="xs" c="dimmed">
                                        {slot.appointmentType}
                                        {slot.patientName && ` • ${slot.patientName}`}
                                        {slot.notes && ` • ${slot.notes}`}
                                      </Text>
                                    </Box>
                                  </Group>
                                  
                                  {!bulkEditMode && (
                                    <Menu shadow="md" width={150}>
                                      <Menu.Target>
                                        <ActionIcon variant="subtle" size="sm">
                                          <IconDots size={14} />
                                        </ActionIcon>
                                      </Menu.Target>
                                      <Menu.Dropdown>
                                        <Menu.Item
                                          leftSection={<IconEdit size={14} />}
                                          onClick={() => {
                                            setSelectedSlot(slot);
                                            setFormData({
                                              date: slot.date,
                                              startTime: slot.startTime,
                                              endTime: slot.endTime,
                                              duration: slot.duration,
                                              appointmentType: slot.appointmentType || 'General Consultation',
                                              notes: slot.notes || '',
                                              isRecurring: slot.isRecurring || false,
                                              recurringPattern: slot.recurringPattern || 'weekly',
                                              breakDuration: 15,
                                            });
                                            openEditModal();
                                          }}
                                        >
                                          Edit
                                        </Menu.Item>
                                        <Menu.Item
                                          leftSection={<IconCopy size={14} />}
                                          onClick={() => {
                                            const newSlot = {
                                              ...slot,
                                              id: `copy-${Date.now()}`,
                                            };
                                            setTimeSlots(prev => [...prev, newSlot]);
                                            notifications.show({
                                              title: 'Slot Copied',
                                              message: 'Time slot has been duplicated',
                                              color: 'blue',
                                            });
                                          }}
                                        >
                                          Duplicate
                                        </Menu.Item>
                                        <Menu.Divider />
                                        <Menu.Item
                                          leftSection={<IconTrash size={14} />}
                                          color="red"
                                          onClick={() => handleDeleteSlot(slot.id)}
                                        >
                                          Delete
                                        </Menu.Item>
                                      </Menu.Dropdown>
                                    </Menu>
                                  )}
                                </Group>
                              </Card>
                            ))
                        )}
                      </Stack>
                    )}

                    {currentView === 'week' && (
                      <SimpleGrid cols={7} spacing="xs">
                        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, dayIndex) => {
                          const dayDate = new Date(selectedDate);
                          dayDate.setDate(selectedDate.getDate() - selectedDate.getDay() + dayIndex);
                          const daySlots = viewSlots.filter(slot => 
                            new Date(slot.date).toDateString() === dayDate.toDateString()
                          );

                          return (
                            <Card key={day} shadow="xs" padding="sm" radius="md" withBorder>
                              <Stack gap="xs">
                                <Text fw={600} size="sm" ta="center">
                                  {day}
                                </Text>
                                <Text size="xs" c="dimmed" ta="center">
                                  {dayDate.getDate()}
                                </Text>
                                <Divider />
                                <Stack gap={4}>
                                  {daySlots.length === 0 ? (
                                    <Text size="xs" c="dimmed" ta="center">
                                      No slots
                                    </Text>
                                  ) : (
                                    daySlots
                                      .sort((a, b) => a.startTime.localeCompare(b.startTime))
                                      .slice(0, 4)
                                      .map((slot) => (
                                        <Box
                                          key={slot.id}
                                          p={4}
                                          style={{
                                            backgroundColor: STATUS_COLORS[slot.status],
                                            borderRadius: 4,
                                            cursor: 'pointer',
                                          }}
                                          onClick={() => {
                                            setSelectedSlot(slot);
                                            setFormData({
                                              date: slot.date,
                                              startTime: slot.startTime,
                                              endTime: slot.endTime,
                                              duration: slot.duration,
                                              appointmentType: slot.appointmentType || 'General Consultation',
                                              notes: slot.notes || '',
                                              isRecurring: slot.isRecurring || false,
                                              recurringPattern: slot.recurringPattern || 'weekly',
                                              breakDuration: 15,
                                            });
                                            openEditModal();
                                          }}
                                        >
                                          <Text size="xs" c="white" fw={500}>
                                            {formatTime(slot.startTime)}
                                          </Text>
                                          {slot.patientName && (
                                            <Text size="xs" c="white" opacity={0.8}>
                                              {slot.patientName}
                                            </Text>
                                          )}
                                        </Box>
                                      ))
                                  )}
                                  {daySlots.length > 4 && (
                                    <Text size="xs" c="dimmed" ta="center">
                                      +{daySlots.length - 4} more
                                    </Text>
                                  )}
                                </Stack>
                              </Stack>
                            </Card>
                          );
                        })}
                      </SimpleGrid>
                    )}

                    {currentView === 'month' && (
                      <Box>
                        <SimpleGrid cols={7} spacing="xs" mb="md">
                          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                            <Text key={day} fw={600} size="sm" ta="center" c="dimmed">
                              {day}
                            </Text>
                          ))}
                        </SimpleGrid>
                        
                        <SimpleGrid cols={7} spacing="xs">
                          {Array.from({ length: 42 }, (_, index) => {
                            const firstDay = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1);
                            const startDate = new Date(firstDay);
                            startDate.setDate(startDate.getDate() - firstDay.getDay() + index);
                            
                            const daySlots = viewSlots.filter(slot => 
                              new Date(slot.date).toDateString() === startDate.toDateString()
                            );
                            
                            const isCurrentMonth = startDate.getMonth() === selectedDate.getMonth();
                            const isToday = startDate.toDateString() === new Date().toDateString();

                            return (
                              <Card
                                key={index}
                                shadow="xs"
                                padding="xs"
                                radius="md"
                                withBorder
                                style={{
                                  minHeight: 80,
                                  opacity: isCurrentMonth ? 1 : 0.3,
                                  backgroundColor: isToday ? '#f0f9ff' : undefined,
                                }}
                              >
                                <Stack gap={2}>
                                  <Text
                                    size="xs"
                                    fw={isToday ? 600 : 400}
                                    c={isToday ? 'blue' : 'dark'}
                                  >
                                    {startDate.getDate()}
                                  </Text>
                                  
                                  {daySlots.slice(0, 2).map((slot) => (
                                    <Box
                                      key={slot.id}
                                      style={{
                                        width: '100%',
                                        height: 4,
                                        backgroundColor: STATUS_COLORS[slot.status],
                                        borderRadius: 2,
                                      }}
                                    />
                                  ))}
                                  
                                  {daySlots.length > 2 && (
                                    <Text size="xs" c="dimmed">
                                      +{daySlots.length - 2}
                                    </Text>
                                  )}
                                </Stack>
                              </Card>
                            );
                          })}
                        </SimpleGrid>
                      </Box>
                    )}
                  </ScrollArea>
                )}
              </Paper>
            </Stack>
          </Grid.Col>
        </Grid>

        {/* Add Availability Modal */}
        <Modal
          opened={addModalOpened}
          onClose={closeAddModal}
          title="Add Availability"
          size="lg"
          radius="lg"
        >
          <Stack gap="md">
            <SimpleGrid cols={2} spacing="md">
              <TextInput
                type="date"
                label="Date"
                value={formData.date.toISOString().split('T')[0]}
                onChange={(event) => {
                  const newDate = new Date(event.currentTarget.value);
                  if (!isNaN(newDate.getTime())) {
                    setFormData(prev => ({ ...prev, date: newDate }));
                  }
                }}
                required
              />
              <Select
                label="Appointment Type"
                data={APPOINTMENT_TYPES}
                value={formData.appointmentType}
                onChange={(value) => value && setFormData(prev => ({ ...prev, appointmentType: value }))}
                required
              />
            </SimpleGrid>

            <SimpleGrid cols={3} spacing="md">
              <TimeInput
                label="Start Time"
                value={formData.startTime}
                onChange={(event) => setFormData(prev => ({ ...prev, startTime: event.currentTarget.value }))}
                required
              />
              <TimeInput
                label="End Time"
                value={formData.endTime}
                onChange={(event) => setFormData(prev => ({ ...prev, endTime: event.currentTarget.value }))}
                required
              />
              <Select
                label="Duration per Slot"
                data={DURATION_OPTIONS}
                value={formData.duration.toString()}
                onChange={(value) => value && setFormData(prev => ({ ...prev, duration: parseInt(value) }))}
                required
              />
            </SimpleGrid>

            <Textarea
              label="Notes (Optional)"
              placeholder="Add any notes about this availability..."
              value={formData.notes}
              onChange={(event) => setFormData(prev => ({ ...prev, notes: event.currentTarget.value }))}
              rows={3}
            />

            <Card withBorder padding="md" radius="md">
              <Stack gap="md">
                <Checkbox
                  label="Make this recurring"
                  checked={formData.isRecurring}
                  onChange={(event) => setFormData(prev => ({ ...prev, isRecurring: event.currentTarget.checked }))}
                />
                
                {formData.isRecurring && (
                  <Select
                    label="Recurring Pattern"
                    data={[
                      { value: 'weekly', label: 'Weekly' },
                      { value: 'biweekly', label: 'Bi-weekly' },
                      { value: 'monthly', label: 'Monthly' },
                    ]}
                    value={formData.recurringPattern}
                    onChange={(value) => value && setFormData(prev => ({ ...prev, recurringPattern: value as 'weekly' | 'biweekly' | 'monthly' }))}
                  />
                )}
              </Stack>
            </Card>

            <Group justify="flex-end" mt="md">
              <Button variant="light" onClick={closeAddModal}>
                Cancel
              </Button>
              <Button onClick={handleAddSlot} leftSection={<IconCheck size={16} />}>
                Add Availability
              </Button>
            </Group>
          </Stack>
        </Modal>

        {/* Edit Availability Modal */}
        <Modal
          opened={editModalOpened}
          onClose={closeEditModal}
          title="Edit Availability"
          size="lg"
          radius="lg"
        >
          <Stack gap="md">
            <SimpleGrid cols={2} spacing="md">
              <TextInput
                type="date"
                label="Date"
                value={formData.date.toISOString().split('T')[0]}
                onChange={(event) => {
                  const newDate = new Date(event.currentTarget.value);
                  if (!isNaN(newDate.getTime())) {
                    setFormData(prev => ({ ...prev, date: newDate }));
                  }
                }}
                required
              />
              <Select
                label="Appointment Type"
                data={APPOINTMENT_TYPES}
                value={formData.appointmentType}
                onChange={(value) => value && setFormData(prev => ({ ...prev, appointmentType: value }))}
                required
              />
            </SimpleGrid>

            <SimpleGrid cols={3} spacing="md">
              <TimeInput
                label="Start Time"
                value={formData.startTime}
                onChange={(event) => setFormData(prev => ({ ...prev, startTime: event.currentTarget.value }))}
                required
              />
              <TimeInput
                label="End Time"
                value={formData.endTime}
                onChange={(event) => setFormData(prev => ({ ...prev, endTime: event.currentTarget.value }))}
                required
              />
              <Select
                label="Duration per Slot"
                data={DURATION_OPTIONS}
                value={formData.duration.toString()}
                onChange={(value) => value && setFormData(prev => ({ ...prev, duration: parseInt(value) }))}
                required
              />
            </SimpleGrid>

            <Textarea
              label="Notes (Optional)"
              placeholder="Add any notes about this availability..."
              value={formData.notes}
              onChange={(event) => setFormData(prev => ({ ...prev, notes: event.currentTarget.value }))}
              rows={3}
            />

            <Group justify="flex-end" mt="md">
              <Button variant="light" onClick={closeEditModal}>
                Cancel
              </Button>
              <Button onClick={handleEditSlot} leftSection={<IconCheck size={16} />}>
                Update Availability
              </Button>
            </Group>
          </Stack>
        </Modal>

        {/* Templates Modal */}
        <Modal
          opened={templateModalOpened}
          onClose={closeTemplateModal}
          title="Availability Templates"
          size="lg"
          radius="lg"
        >
          <Stack gap="md">
            <Text size="sm" c="dimmed">
              Apply pre-configured availability templates to quickly set up your schedule.
            </Text>

            <TextInput
              type="date"
              label="Apply to Date"
              value={formData.date.toISOString().split('T')[0]}
              onChange={(event) => {
                const newDate = new Date(event.currentTarget.value);
                if (!isNaN(newDate.getTime())) {
                  setFormData(prev => ({ ...prev, date: newDate }));
                }
              }}
              required
            />

            <Stack gap="sm">
              {templates.map((template) => (
                <Card key={template.id} shadow="xs" padding="md" radius="md" withBorder>
                  <Group justify="space-between">
                    <Box>
                      <Group gap="xs" mb="xs">
                        <Text fw={600} size="sm">{template.name}</Text>
                        {template.isDefault && (
                          <Badge variant="light" color="blue" size="xs">
                            Default
                          </Badge>
                        )}
                      </Group>
                      <Text size="xs" c="dimmed" mb="sm">
                        {template.description}
                      </Text>
                      <Group gap="xs">
                        <Text size="xs" c="dimmed">
                          {template.timeSlots.length} time slots
                        </Text>
                        <Text size="xs" c="dimmed">•</Text>
                        <Text size="xs" c="dimmed">
                          {template.timeSlots.filter(slot => slot.status === 'available').length} available
                        </Text>
                      </Group>
                    </Box>
                    <Button
                      size="xs"
                      variant="light"
                      onClick={() => applyTemplate(template)}
                    >
                      Apply
                    </Button>
                  </Group>
                </Card>
              ))}
            </Stack>

            <Group justify="flex-end" mt="md">
              <Button variant="light" onClick={closeTemplateModal}>
                Close
              </Button>
            </Group>
          </Stack>
        </Modal>

        {/* Settings Drawer */}
        <Drawer
          opened={settingsOpened}
          onClose={closeSettings}
          title="Availability Settings"
          position="right"
          size="md"
        >
          <Stack gap="md">
            <Card shadow="xs" padding="md" radius="md" withBorder>
              <Stack gap="md">
                <Text fw={600} size="sm">General Settings</Text>
                
                <Switch
                  label="Auto-save changes"
                  description="Automatically save availability changes"
                  checked={autoSave}
                  onChange={(event) => setAutoSave(event.currentTarget.checked)}
                />
                
                <Switch
                  label="Show conflicts"
                  description="Highlight scheduling conflicts"
                  checked={showConflicts}
                  onChange={(event) => setShowConflicts(event.currentTarget.checked)}
                />
                
                <NumberInput
                  label="Default appointment duration"
                  description="Default duration for new appointments (minutes)"
                  value={formData.duration}
                  onChange={(value) => setFormData(prev => ({ ...prev, duration: Number(value) || 30 }))}
                  min={15}
                  max={240}
                  step={15}
                />
              </Stack>
            </Card>

            <Card shadow="xs" padding="md" radius="md" withBorder>
              <Stack gap="md">
                <Text fw={600} size="sm">Notification Settings</Text>
                
                <Switch
                  label="New booking notifications"
                  description="Get notified when patients book appointments"
                  defaultChecked
                />
                
                <Switch
                  label="Cancellation notifications"
                  description="Get notified when appointments are cancelled"
                  defaultChecked
                />
                
                <Switch
                  label="Daily schedule summary"
                  description="Receive daily email with schedule overview"
                  defaultChecked
                />
              </Stack>
            </Card>

            <Card shadow="xs" padding="md" radius="md" withBorder>
              <Stack gap="md">
                <Text fw={600} size="sm">Calendar Integration</Text>
                
                <Button variant="light" fullWidth leftSection={<IconBrandGoogleFilled size={16} />}>
                  Sync with Google Calendar
                </Button>
                
                <Button variant="light" fullWidth leftSection={<IconCalendar size={16} />}>
                  Sync with Outlook
                </Button>
                
                <Button variant="light" fullWidth leftSection={<IconCalendar size={16} />}>
                  Export to iCal
                </Button>
              </Stack>
            </Card>

            <Group justify="flex-end" mt="md">
              <Button variant="light" onClick={closeSettings}>
                Close
              </Button>
              <Button leftSection={<IconDeviceFloppy size={16} />}>
                Save Settings
              </Button>
            </Group>
          </Stack>
        </Drawer>
      </Box>
  );
};

export default ProviderAvailability; 