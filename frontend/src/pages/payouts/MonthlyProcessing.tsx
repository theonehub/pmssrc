import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';

/**
 * MonthlyProcessing Component - Redirects to admin payouts page
 * Simple redirect component with loading indicator
 */
const MonthlyProcessing: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to admin payouts page
    navigate('/payouts/admin');
  }, [navigate]);

  return (
    <Box 
      display="flex" 
      flexDirection="column" 
      alignItems="center" 
      justifyContent="center" 
      minHeight="50vh"
    >
      <CircularProgress />
      <Typography variant="body1" sx={{ mt: 2 }}>
        Redirecting to Salary Calculator...
      </Typography>
    </Box>
  );
};

export default MonthlyProcessing; 