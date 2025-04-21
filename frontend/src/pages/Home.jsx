import React, { useEffect, useState } from 'react';
import axios from '../utils/axios';
import { getToken } from '../utils/auth';
import PageLayout from '../layout/PageLayout';
import { 
  Typography, 
  Grid, 
  Paper, 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CircularProgress, 
  useTheme,
  Snackbar,
  Alert
} from '@mui/material';
import {
  People as PeopleIcon,
  Work as HRIcon,
  AccountTree as LeadIcon,
  Person as UserIcon,
  Login as CheckInIcon,
  Logout as CheckOutIcon
} from '@mui/icons-material';

function Home() {
  const [usersStats, setUsersStats] = useState({});
  const [attendanceStats, setAttendanceStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [attendanceLoading, setAttendanceLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const theme = useTheme();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const res = await axios.get('/users/stats', {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setUsersStats(res.data);
        const res2 = await axios.get('/attendance/stats/today', {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setAttendanceStats(res2.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
        setSnackbar({
          open: true,
          message: 'Failed to load dashboard data',
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const handleCheckIn = async () => {
    try {
      setAttendanceLoading(true);
      await axios.post('/attendance/checkin');
      setSnackbar({
        open: true,
        message: 'Check-in successful!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Check-in error:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to check in',
        severity: 'error'
      });
    } finally {
      setAttendanceLoading(false);
    }
  };

  const handleCheckOut = async () => {
    try {
      setAttendanceLoading(true);
      await axios.post('/attendance/checkout');
      setSnackbar({
        open: true,
        message: 'Check-out successful!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Check-out error:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.message || 'Failed to check out',
        severity: 'error'
      });
    } finally {
      setAttendanceLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Dashboard card data
  const dashboardCards = [
    { title: 'Total Users', value: usersStats.total_users || 0, color: theme.palette.primary.main, icon: <PeopleIcon fontSize="large" /> },
    { title: 'Today\'s Check-Ins', value: attendanceStats.checkin_count || 0, color: theme.palette.success.main, icon: <CheckInIcon fontSize="large" /> },
    { title: 'Today\'s Check-Outs', value: attendanceStats.checkout_count || 0, color: theme.palette.info.main, icon: <CheckInIcon fontSize="large" /> },
    { title: 'HR', value: usersStats.hr || 0, color: theme.palette.warning.main, icon: <HRIcon fontSize="large" /> },
    { title: 'Leads', value: usersStats.lead || 0, color: theme.palette.secondary.main, icon: <LeadIcon fontSize="large" /> },
    { title: 'Users', value: usersStats.user || 0, color: theme.palette.grey[800], icon: <UserIcon fontSize="large" /> }
  ];

  return (
    <PageLayout title="Dashboard">
      <Box sx={{ py: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
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
            gap: 2
          }}
        >
          <Typography variant="h6" sx={{ flexGrow: 1, mb: { xs: 2, sm: 0 } }}>
            Today's Attendance
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button 
              variant="contained" 
              color="primary" 
              size="large"
              startIcon={<CheckInIcon />}
              onClick={handleCheckIn}
              disabled={attendanceLoading}
            >
              Check In
            </Button>
            <Button 
              variant="contained" 
              color="secondary" 
              size="large"
              startIcon={<CheckOutIcon />}
              onClick={handleCheckOut}
              disabled={attendanceLoading}
            >
              Check Out
            </Button>
          </Box>
        </Paper>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {dashboardCards.map((card, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      mb: 2
                    }}>
                      <Typography variant="h6" component="div">
                        {card.title}
                      </Typography>
                      <Box sx={{ 
                        color: card.color,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: `${card.color}15`, // semi-transparent background
                        borderRadius: '50%',
                        width: 48,
                        height: 48
                      }}>
                        {card.icon}
                      </Box>
                    </Box>
                    <Typography variant="h3" component="div" sx={{ fontWeight: 'bold' }}>
                      {card.value}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
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
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </PageLayout>
  );
}

export default Home; 