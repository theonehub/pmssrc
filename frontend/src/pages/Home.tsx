import React, { useEffect, useState } from 'react';
import { get, post } from '../utils/apiClient';
import PageLayout from '../layout/PageLayout';
import {
  Typography,
  Paper,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  useTheme,
  Snackbar,
  Alert,
  AlertColor,
} from '@mui/material';
import {
  People as PeopleIcon,
  Work as HRIcon,
  AccountTree as LeadIcon,
  Person as UserIcon,
  Login as CheckInIcon,
  Logout as CheckOutIcon,
} from '@mui/icons-material';
import { DashboardStats } from '../types';

// Type definitions for component state
interface SnackbarState {
  open: boolean;
  message: string;
  severity: AlertColor;
}

interface DashboardCard {
  title: string;
  value: number;
  color: string;
  icon: React.ReactElement;
}

interface AttendanceStats {
  checkin_count: number;
  checkout_count: number;
}

const Home: React.FC = () => {
  const [usersStats, setUsersStats] = useState<Partial<DashboardStats>>({});
  const [attendanceStats, setAttendanceStats] = useState<
    Partial<AttendanceStats>
  >({});
  const [loading, setLoading] = useState<boolean>(true);
  const [attendanceLoading, setAttendanceLoading] = useState<boolean>(false);
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: '',
    severity: 'success',
  });
  const theme = useTheme();

  useEffect(() => {
    const fetchStats = async (): Promise<void> => {
      try {
        setLoading(true);

        // Fetch user statistics
        const usersResponse = await get<DashboardStats>('/users/stats');
        if (usersResponse.success && usersResponse.data) {
          setUsersStats(usersResponse.data);
        }

        // Fetch attendance statistics
        const attendanceResponse = await get<AttendanceStats>(
          '/attendance/stats/today'
        );
        if (attendanceResponse.success && attendanceResponse.data) {
          setAttendanceStats(attendanceResponse.data);
        }
      } catch (error) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Error fetching stats:', error);
        }
        setSnackbar({
          open: true,
          message: 'Failed to load dashboard data',
          severity: 'error',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleCheckIn = async (): Promise<void> => {
    try {
      setAttendanceLoading(true);
      const response = await post('/attendance/checkin');

      if (response.success) {
        setSnackbar({
          open: true,
          message: 'Check-in successful!',
          severity: 'success',
        });
      } else {
        throw new Error(response.error || 'Failed to check in');
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Check-in error:', error);
      }
      setSnackbar({
        open: true,
        message: error instanceof Error ? error.message : 'Failed to check in',
        severity: 'error',
      });
    } finally {
      setAttendanceLoading(false);
    }
  };

  const handleCheckOut = async (): Promise<void> => {
    try {
      setAttendanceLoading(true);
      const response = await post('/attendance/checkout');

      if (response.success) {
        setSnackbar({
          open: true,
          message: 'Check-out successful!',
          severity: 'success',
        });
      } else {
        throw new Error(response.error || 'Failed to check out');
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Check-out error:', error);
      }
      setSnackbar({
        open: true,
        message: error instanceof Error ? error.message : 'Failed to check out',
        severity: 'error',
      });
    } finally {
      setAttendanceLoading(false);
    }
  };

  const handleCloseSnackbar = (): void => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Dashboard card data
  const dashboardCards: DashboardCard[] = [
    {
      title: 'Total Users',
      value: usersStats.total_users || 0,
      color: theme.palette.primary.main,
      icon: <PeopleIcon fontSize='large' />,
    },
    {
      title: "Today's Check-Ins",
      value: attendanceStats.checkin_count || 0,
      color: theme.palette.success.main,
      icon: <CheckInIcon fontSize='large' />,
    },
    {
      title: "Today's Check-Outs",
      value: attendanceStats.checkout_count || 0,
      color: theme.palette.info.main,
      icon: <CheckOutIcon fontSize='large' />,
    },
    {
      title: 'HR',
      value: usersStats.hr || 0,
      color: theme.palette.warning.main,
      icon: <HRIcon fontSize='large' />,
    },
    {
      title: 'Leads',
      value: usersStats.lead || 0,
      color: theme.palette.secondary.main,
      icon: <LeadIcon fontSize='large' />,
    },
    {
      title: 'Users',
      value: usersStats.user || 0,
      color: theme.palette.grey[800],
      icon: <UserIcon fontSize='large' />,
    },
  ];

  return (
    <PageLayout title='Dashboard'>
      <Box sx={{ py: 3 }}>
        <Typography variant='h4' gutterBottom sx={{ mb: 4 }}>
          Overview
        </Typography>

        {/* Attendance Buttons */}
        <Paper
          elevation={3}
          sx={{
            p: 3,
            mb: 4,
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'center',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Typography variant='h6' sx={{ flexGrow: 1, mb: { xs: 2, sm: 0 } }}>
            Today's Attendance
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant='contained'
              color='primary'
              size='large'
              startIcon={<CheckInIcon />}
              onClick={handleCheckIn}
              disabled={attendanceLoading}
            >
              {attendanceLoading ? 'Checking In...' : 'Check In'}
            </Button>
            <Button
              variant='contained'
              color='secondary'
              size='large'
              startIcon={<CheckOutIcon />}
              onClick={handleCheckOut}
              disabled={attendanceLoading}
            >
              {attendanceLoading ? 'Checking Out...' : 'Check Out'}
            </Button>
          </Box>
        </Paper>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 3,
            }}
          >
            {dashboardCards.map((card, index) => (
              <Card key={`dashboard-card-${index}`} sx={{ height: '100%' }}>
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      mb: 2,
                    }}
                  >
                    <Typography variant='h6' component='div'>
                      {card.title}
                    </Typography>
                    <Box
                      sx={{
                        color: card.color,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: `${card.color}15`, // semi-transparent background
                        borderRadius: '50%',
                        width: 48,
                        height: 48,
                      }}
                    >
                      {card.icon}
                    </Box>
                  </Box>
                  <Typography
                    variant='h3'
                    component='div'
                    sx={{ fontWeight: 'bold' }}
                  >
                    {card.value}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          variant='filled'
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </PageLayout>
  );
};

export default Home;
