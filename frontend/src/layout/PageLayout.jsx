// src/layout/PageLayout.js
import React from 'react';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const PageLayout = ({ title, children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      minHeight: '100vh',
      backgroundColor: theme.palette.background.default
    }}>
      <Topbar title={title} />
      
      <Box sx={{ 
        display: 'flex', 
        flexGrow: 1,
        mt: '64px', // Add margin top equal to AppBar height
        height: 'calc(100vh - 64px)', // Subtract AppBar height from total height
        overflow: 'hidden'
      }}>
        {!isMobile && <Sidebar />}
        <Box 
          component="main"
          sx={{ 
            flexGrow: 1,
            p: 3,
            overflow: 'auto',
            backgroundColor: theme.palette.background.paper,
            transition: theme.transitions.create('margin', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default PageLayout;
