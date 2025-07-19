import React, { useEffect, useState } from 'react';
import { get, post } from '../shared/api/baseApi';
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
  CurrencyRupee as RupeeIcon,
  Login as CheckInIcon,
  Logout as CheckOutIcon,
} from '@mui/icons-material';
import { DashboardStats } from '../shared/types';

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


const Home: React.FC = () => {
  const [dashboardStats, setDashboardStats] = useState<Partial<DashboardStats>>({});

  const [loading, setLoading] = useState<boolean>(true);
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

        // Fetch dashboard statistics using reporting service
        const dashboardResponse = await get<DashboardStats>('/v2/reporting/dashboard/analytics/statistics');
        if (dashboardResponse) {
          setDashboardStats(dashboardResponse);
        }
      } catch (error: any) {
        const backendMessage = error?.response?.data?.detail;
        setSnackbar({
          open: true,
          message: backendMessage || 'Failed to load dashboard data',
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
      setLoading(true);
      await post('/v2/attendance/checkin');

      // If we get a response without error, consider it successful
      setSnackbar({
        open: true,
        message: 'Check-in successful!',
        severity: 'success',
      });
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Check-in error:', error);
      }
      setSnackbar({
        open: true,
        message: backendMessage || 'Failed to check in',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async (): Promise<void> => {
    try {
      setLoading(true);
      await post('/v2/attendance/checkout');

      // If we get a response without error, consider it successful
      setSnackbar({
        open: true,
        message: 'Check-out successful!',
        severity: 'success',
      });
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Check-out error:', error);
      }
      setSnackbar({
        open: true,
        message: backendMessage || 'Failed to check out',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = (): void => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Dashboard card data
  const dashboardCards: DashboardCard[] = [
    {
      title: 'Total Users',
      value: dashboardStats.total_users || 0,
      color: theme.palette.primary.main,
      icon: <PeopleIcon fontSize='large' />,
    },
    {
      title: "Today's Check-Ins",
      value: dashboardStats.checkin_count || 0,
      color: theme.palette.success.main,
      icon: <CheckInIcon fontSize='large' />,
    },
    {
      title: "Today's Check-Outs",
      value: dashboardStats.checkout_count || 0,
      color: theme.palette.info.main,
      icon: <CheckOutIcon fontSize='large' />,
    },
    {
      title: 'Pending Reimbursements',
      value: dashboardStats.pending_reimbursements || 0,
      color: theme.palette.warning.main,
      icon: <RupeeIcon fontSize='large' />, 
    },
    {
      title: 'Pending Amount (₹)',
      value: dashboardStats.pending_reimbursements_amount || 0,
      color: theme.palette.warning.main,
      icon: <RupeeIcon fontSize='large' />, 
    },
    {
      title: 'Approved Reimbursements',
      value: dashboardStats.approved_reimbursements || 0,
      color: theme.palette.success.main,
      icon: <RupeeIcon fontSize='large' />, 
    },
    {
      title: 'Approved Amount (₹)',
      value: dashboardStats.approved_reimbursements_amount || 0,
      color: theme.palette.success.main,
      icon: <RupeeIcon fontSize='large' />, 
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
              disabled={loading}
            >
              {loading ? 'Checking In...' : 'Check In'}
            </Button>
            <Button
              variant='contained'
              color='secondary'
              size='large'
              startIcon={<CheckOutIcon />}
              onClick={handleCheckOut}
              disabled={loading}
            >
              {loading ? 'Checking Out...' : 'Check Out'}
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
