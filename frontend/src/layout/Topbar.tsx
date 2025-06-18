import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  useTheme,
  IconButton,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';

// Define the props interface
interface TopbarProps {
  title?: string;
  onMenuClick: () => void;
}

const Topbar: React.FC<TopbarProps> = ({ title, onMenuClick }) => {
  const theme = useTheme();

  return (
    <AppBar
      position='fixed'
      elevation={0}
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderBottom: 'none',
        zIndex: theme.zIndex.drawer + 1,
        height: '64px',
        display: 'flex',
        justifyContent: 'center',
        boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Toolbar sx={{ minHeight: '64px !important' }}>
        <IconButton
          color='inherit'
          aria-label='toggle menu'
          edge='start'
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography
            variant='h6'
            noWrap
            component='div'
            sx={{
              fontWeight: 700,
              color: 'white',
              fontSize: '1.2rem',
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
