// src/layout/Topbar.js
import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Box,
  useTheme,
  useMediaQuery,
  IconButton
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';

const Topbar = ({ title, onMenuClick }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <AppBar 
      position="fixed" 
      elevation={1}
      sx={{
        backgroundColor: theme.palette.background.paper,
        color: theme.palette.text.primary,
        borderBottom: `1px solid ${theme.palette.divider}`,
        zIndex: theme.zIndex.drawer + 1,
        height: '64px',
        display: 'flex',
        justifyContent: 'center'
      }}
    >
      <Toolbar sx={{ minHeight: '64px !important' }}>
        {isMobile && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onMenuClick}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        <Box sx={{ flexGrow: 1 }}>
          <Typography 
            variant="h6" 
            noWrap 
            component="div"
            sx={{
              fontWeight: 600,
              color: theme.palette.primary.main
            }}
          >
            {title || 'Dashboard'}
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Topbar;
