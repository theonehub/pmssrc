import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  useTheme,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LockIcon from '@mui/icons-material/Lock';
import LogoutIcon from '@mui/icons-material/Logout';
import BusinessIcon from '@mui/icons-material/Business';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { normalizeFilePath } from '../shared/utils/apiUtils';
import { API_CONFIG } from '../shared/utils/constants';

// Define the props interface
interface TopbarProps {
  title?: string;
  onMenuClick: () => void;
  organizationLogo?: string | undefined;
  organizationName?: string | undefined;
  onPasswordChange?: () => void;
}

const Topbar: React.FC<TopbarProps> = ({ 
  title, 
  onMenuClick, 
  organizationLogo,
  organizationName,
  onPasswordChange 
}) => {
  const theme = useTheme();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handlePasswordChange = () => {
    handleMenuClose();
    if (onPasswordChange) {
      onPasswordChange();
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Generate user initials for avatar fallback
  const getUserInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  // Get user display name
  const getUserDisplayName = () => {
    if (!user) return 'User';
    return user.name || user.email || 'User';
  };

  return (
    <AppBar
      position='fixed'
      elevation={1}
      sx={{
        backgroundColor: theme.palette.background.paper,
        color: theme.palette.text.primary,
        borderBottom: `1px solid ${theme.palette.divider}`,
        zIndex: theme.zIndex.drawer + 1,
        height: '64px',
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <Toolbar sx={{ minHeight: '64px !important' }}>
        {/* Left side - Menu button and Organization Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            color='inherit'
            aria-label='toggle menu'
            edge='start'
            onClick={onMenuClick}
            sx={{ mr: 1 }}
          >
            <MenuIcon />
          </IconButton>
          
          {/* Organization Logo */}
          {organizationLogo ? (
            <Avatar
              src={organizationLogo.startsWith('http') ? organizationLogo : `${API_CONFIG.BASE_URL}/files/${normalizeFilePath(organizationLogo)}`}
              sx={{ 
                width: 40, 
                height: 40,
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              <BusinessIcon />
            </Avatar>
          ) : (
            <Avatar
              sx={{ 
                width: 40, 
                height: 40,
                backgroundColor: theme.palette.primary.main,
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              <BusinessIcon />
            </Avatar>
          )}
          
          {/* Organization Name */}
          {organizationName && (
            <Typography
              variant='subtitle2'
              sx={{
                color: theme.palette.text.secondary,
                fontWeight: 500,
                display: { xs: 'none', sm: 'block' },
              }}
            >
              {organizationName}
            </Typography>
          )}
        </Box>

        {/* Center - Page Title */}
        <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
          <Typography
            variant='h6'
            noWrap
            component='div'
            sx={{
              fontWeight: 600,
              color: theme.palette.primary.main,
            }}
          >
            {title || 'Dashboard'}
          </Typography>
        </Box>

        {/* Right side - User Info and Menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* User Name */}
          <Typography
            variant='body2'
            sx={{
              color: theme.palette.text.secondary,
              fontWeight: 500,
              display: { xs: 'none', md: 'block' },
            }}
          >
            {getUserDisplayName()}
          </Typography>

          {/* User Avatar */}
          <Tooltip title="User Menu">
            <IconButton
              onClick={handleMenuClick}
              sx={{ 
                p: 0.5,
                border: `1px solid ${theme.palette.divider}`,
                '&:hover': {
                  borderColor: theme.palette.primary.main,
                }
              }}
            >
              {user?.profile_picture ? (
                <Avatar
                  src={user.profile_picture}
                  sx={{ width: 32, height: 32 }}
                >
                  {getUserInitials(getUserDisplayName())}
                </Avatar>
              ) : (
                <Avatar
                  sx={{ 
                    width: 32, 
                    height: 32,
                    backgroundColor: theme.palette.primary.main,
                  }}
                >
                  {getUserInitials(getUserDisplayName())}
                </Avatar>
              )}
            </IconButton>
          </Tooltip>

          {/* User Menu */}
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 200,
                boxShadow: theme.shadows[8],
                border: `1px solid ${theme.palette.divider}`,
              }
            }}
          >
            {/* User Info Section */}
            <MenuItem disabled sx={{ opacity: 1 }}>
              <ListItemIcon>
                <AccountCircleIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={getUserDisplayName()}
                secondary={user?.email || user?.role || 'User'}
                primaryTypographyProps={{
                  variant: 'subtitle2',
                  fontWeight: 600,
                }}
                secondaryTypographyProps={{
                  variant: 'caption',
                }}
              />
            </MenuItem>
            
            <Divider />
            
            {/* Password Change Option */}
            <MenuItem onClick={handlePasswordChange}>
              <ListItemIcon>
                <LockIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Change Password" />
            </MenuItem>
            
            <Divider />
            
            {/* Logout Option */}
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Topbar;
