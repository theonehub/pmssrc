import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Divider,
  useTheme,
  Typography,
  useMediaQuery
} from '@mui/material';
import {
  Home as HomeIcon,
  People as PeopleIcon,
  CalendarToday as CalendarIcon,
  CalendarMonth as CalendarMonthIcon,
  Wallet as WalletIcon,
  Edit as EditIcon,
  EventBusy as EventBusyIcon,
  PersonAdd as PersonAddIcon,
  Receipt as ReceiptIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Business as BusinessIcon
} from '@mui/icons-material';
import { getUserRole } from '../utils/auth';

const Sidebar = () => {
  const role = getUserRole();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const menuItems = [
    {
      title: 'Home',
      icon: <HomeIcon />,
      path: '/home',
      roles: ['manager', 'admin', 'superadmin', 'user']
    },
    {
      title: 'Organisations',
      icon: <BusinessIcon />,
      path: '/organisations',
      roles: ['superadmin']
    },
    {
      title: 'Team',
      icon: <PeopleIcon />,
      path: '/users',
      roles: ['manager', 'admin', 'superadmin']
    },
    {
      title: 'Public Holidays',
      icon: <CalendarIcon />,
      path: '/public-holidays',
      roles: ['manager', 'admin', 'superadmin']
    },
    {
      title: 'Company Leaves',
      icon: <CalendarMonthIcon />,
      path: '/company-leaves',
      roles: ['admin', 'superadmin']
    },
    {
      title: 'Attendance',
      icon: <PeopleIcon />,
      path: '/attendance',
      roles: ['manager', 'admin', 'superadmin']
    },
    {
      title: 'Leaves Approval',
      icon: <PeopleIcon />,
      path: '/all-leaves',
      roles: ['manager', 'admin', 'superadmin']
    },
    {
      title: 'Salary Components',
      icon: <WalletIcon />,
      path: '/salary-components',
      roles: ['admin', 'superadmin', 'hr']
    },
    {
      title: 'Salary Users List',
      icon: <WalletIcon />,
      path: '/salary-users-list',
      roles: ['admin', 'superadmin', 'hr']
    },
    {
      title: 'Salary Declaration',
      icon: <EditIcon />,
      path: '/salary-declaration',
      roles: ['admin', 'superadmin', 'hr', 'manager']
    },
    {
      title: 'LWP Management',
      icon: <EventBusyIcon />,
      path: '/lwp',
      roles: ['admin', 'superadmin']
    },
    {
      title: 'Reimbursements Types',
      icon: <PersonAddIcon />,
      path: '/reimbursement-types',
      roles: ['superadmin']
    },
    {
      title: 'My Reimbursements',
      icon: <ReceiptIcon />,
      path: '/my-reimbursements',
      roles: ['user', 'superadmin']
    },
    {
      title: 'Reimbursement Approvals',
      icon: <ReceiptIcon />,
      path: '/reimbursement-approvals',
      roles: ['manager', 'admin', 'superadmin']
    },
    {
      title: 'Project Attributes',
      icon: <SettingsIcon />,
      path: '/attributes',
      roles: ['superadmin']
    },
    {
      title: 'Leave Management',
      icon: <CalendarIcon />,
      path: '/leaves',
      roles: ['user', 'manager', 'admin', 'superadmin']
    }
  ];

  return (
    <Box
      sx={{
        width: isMobile ? '100%' : 280,
        height: '100%',
        backgroundColor: theme.palette.background.paper,
        borderRight: `1px solid ${theme.palette.divider}`,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="primary">
          📋 Menu
        </Typography>
      </Box>
      <Divider />
      <List sx={{ flexGrow: 1 }}>
        {menuItems.map((item) => {
          if (item.roles.includes(role)) {
            return (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  onClick={() => navigate(item.path)}
                  sx={{
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover,
                    },
                  }}
                >
                  <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.title}
                    primaryTypographyProps={{
                      color: theme.palette.text.primary,
                      variant: 'body1'
                    }}
                  />
                </ListItemButton>
              </ListItem>
            );
          }
          return null;
        })}
      </List>
      <Divider />
      <ListItem disablePadding>
        <ListItemButton
          onClick={() => {
            localStorage.removeItem('token');
            navigate('/login');
          }}
          sx={{
            '&:hover': {
              backgroundColor: theme.palette.error.light,
            },
          }}
        >
          <ListItemIcon sx={{ color: theme.palette.error.main }}>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Logout"
            primaryTypographyProps={{
              color: theme.palette.error.main,
              variant: 'body1'
            }}
          />
        </ListItemButton>
      </ListItem>
    </Box>
  );
};

export default Sidebar;
