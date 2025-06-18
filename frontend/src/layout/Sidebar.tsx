import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  Typography,
  useMediaQuery,
  Collapse,
} from '@mui/material';
import {
  Home as HomeIcon,
  People as PeopleIcon,
  CalendarToday as CalendarIcon,
  CalendarMonth as CalendarMonthIcon,
  Wallet as WalletIcon,
  EventBusy as EventBusyIcon,
  PersonAdd as PersonAddIcon,
  Receipt as ReceiptIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Business as BusinessIcon,
  CurrencyRupee as CurrencyRupeeIcon,
  CalculateOutlined as CalculateIcon,
  AccountBalance as AccountBalanceIcon,
  RequestPage as RequestPageIcon,
  Assessment as AssessmentIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';
import { getUserRole } from '../shared/utils/auth';
import { removeToken } from '../shared/utils/auth';
import { useCalculator } from '../context/CalculatorContext';
import { UserRole } from '../shared/types';

// Type definitions for menu structure
interface MenuItem {
  title: string;
  icon: React.ReactElement;
  path?: string;
  action?: string;
  roles: UserRole[];
}

interface MenuCategory {
  id: string;
  title: string;
  icon: React.ReactElement;
  items: MenuItem[];
}

interface ExpandedState {
  [key: string]: boolean;
}

const Sidebar: React.FC = () => {
  const role = getUserRole();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { openCalculator } = useCalculator();

  // State to track which menu categories are expanded
  const [expanded, setExpanded] = useState<ExpandedState>({
    home: false,
    organisation: false,
    leaves: false,
    payouts: false,
    reimbursements: false,
    taxation: false,
    reporting: false,
    settings: false,
  });

  // Toggle category expansion
  const toggleExpand = (category: string): void => {
    setExpanded(prev => ({
      ...prev,
      [category]: !prev[category],
    }));
  };

  // Menu structure with categories
  const menuCategories: MenuCategory[] = [
    {
      id: 'home',
      title: 'Home',
      icon: <HomeIcon />,
      items: [
        {
          title: 'Home',
          icon: <HomeIcon />,
          path: '/home',
          roles: ['manager', 'admin', 'superadmin', 'user'],
        },
      ],
    },
    {
      id: 'organisation',
      title: 'Organisation',
      icon: <BusinessIcon />,
      items: [
        {
          title: 'Organisations',
          icon: <BusinessIcon />,
          path: '/organisations',
          roles: ['superadmin'],
        },
        {
          title: 'Team',
          icon: <PeopleIcon />,
          path: '/users',
          roles: ['manager', 'admin', 'superadmin'],
        },
      ],
    },
    {
      id: 'leaves',
      title: 'Leaves & Attendance',
      icon: <CalendarIcon />,
      items: [
        {
          title: 'Public Holidays',
          icon: <CalendarIcon />,
          path: '/public-holidays',
          roles: ['manager', 'admin', 'superadmin'],
        },
        {
          title: 'Company Leaves',
          icon: <CalendarMonthIcon />,
          path: '/company-leaves',
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'Attendance',
          icon: <PeopleIcon />,
          path: '/attendance',
          roles: ['manager', 'admin', 'superadmin'],
        },
        {
          title: 'Leaves Approval',
          icon: <PeopleIcon />,
          path: '/all-leaves',
          roles: ['manager', 'admin', 'superadmin'],
        },
        {
          title: 'Leave Management',
          icon: <CalendarIcon />,
          path: '/leaves',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
        {
          title: 'LWP Management',
          icon: <EventBusyIcon />,
          path: '/lwp',
          roles: ['admin', 'superadmin'],
        },
      ],
    },
    {
      id: 'payouts',
      title: 'Payouts & Salary',
      icon: <AccountBalanceIcon />,
      items: [
        {
          title: 'My Salary Details',
          icon: <WalletIcon />,
          path: '/payouts/my-salary',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
        {
          title: 'My Payslips',
          icon: <RequestPageIcon />,
          path: '/payouts/my-payslips',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
        {
          title: 'Salary Calculator',
          icon: <CalculateIcon />,
          path: '/payouts/admin',
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'Monthly Processing',
          icon: <AssessmentIcon />,
          path: '/payouts/monthly',
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'Payout Reports',
          icon: <AssessmentIcon />,
          path: '/payouts/reports',
          roles: ['manager', 'admin', 'superadmin'],
        },
      ],
    },
    {
      id: 'taxation',
      title: 'Income Tax',
      icon: <CurrencyRupeeIcon />,
      items: [
        {
          title: 'Tax Dashboard',
          icon: <CurrencyRupeeIcon />,
          path: '/taxation',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
        {
          title: 'Employee Tax Selection',
          icon: <PeopleIcon />,
          path: '/taxation/employee-selection',
          roles: ['admin', 'superadmin'],
        },
      ],
    },
    {
      id: 'reimbursements',
      title: 'Reimbursements',
      icon: <ReceiptIcon />,
      items: [
        {
          title: 'Reimbursements Types',
          icon: <PersonAddIcon />,
          path: '/reimbursement-types',
          roles: ['superadmin'],
        },
        {
          title: 'My Reimbursements',
          icon: <ReceiptIcon />,
          path: '/my-reimbursements',
          roles: ['user', 'superadmin'],
        },
        {
          title: 'Reimbursement Approvals',
          icon: <ReceiptIcon />,
          path: '/reimbursement-approvals',
          roles: ['manager', 'admin', 'superadmin'],
        },
      ],
    },
    {
      id: 'reporting',
      title: 'Reports & Analytics',
      icon: <AssessmentIcon />,
      items: [
        {
          title: 'Dashboard Analytics',
          icon: <AssessmentIcon />,
          path: '/reporting',
          roles: ['manager', 'admin', 'superadmin'],
        },
      ],
    },
    {
      id: 'settings',
      title: 'Settings',
      icon: <SettingsIcon />,
      items: [
        {
          title: 'Project Attributes',
          icon: <SettingsIcon />,
          path: '/attributes',
          roles: ['superadmin'],
        },
        {
          title: 'Calculator',
          icon: <CalculateIcon />,
          action: 'calculator',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
      ],
    },
  ];

  // Helper function to check if a category has any visible items for the current user
  const hasVisibleItems = (category: MenuCategory): boolean => {
    if (!role) return false;
    return category.items.some(item => item.roles.includes(role));
  };

  // Handle menu item click
  const handleMenuItemClick = (item: MenuItem): void => {
    if (item.action === 'calculator') {
      openCalculator();
    } else if (item.path) {
      navigate(item.path);
    }
  };

  // Handle logout
  const handleLogout = (): void => {
    removeToken();
    navigate('/login');
  };

  // Don't render sidebar if user has no role
  if (!role) {
    return null;
  }

  return (
    <Box
      sx={{
        width: isMobile ? '100%' : 280,
        height: '100%',
        background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
        borderRight: '1px solid rgba(0, 0, 0, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        minHeight: '100vh',
        overflow: 'hidden',
        zIndex: 1300, // Ensure sidebar is above overlays
      }}
    >
      <Box 
        sx={{ 
          p: 3, 
          textAlign: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)'
        }}
      >
        <Typography variant='h6' fontWeight={700}>
          📋 PMS Dashboard
        </Typography>
      </Box>

      <List
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          backgroundColor: 'transparent',
          px: 1,
          py: 2,
        }}
      >
        {menuCategories.map(
          category =>
            // Only show categories with items the user has access to
            hasVisibleItems(category) && (
              <React.Fragment key={category.id}>
                <ListItemButton
                  onClick={() => toggleExpand(category.id)}
                  sx={{
                    backgroundColor: 'rgba(255, 255, 255, 0.7)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: 3,
                    mb: 1,
                    mx: 1,
                    boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.06)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      transform: 'translateY(-1px)',
                      boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)',
                    },
                    transition: 'all 0.2s ease-in-out',
                  }}
                >
                  <ListItemIcon 
                    sx={{ 
                      color: theme.palette.primary.main,
                      minWidth: 40,
                    }}
                  >
                    {category.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={category.title}
                    primaryTypographyProps={{
                      fontWeight: 600,
                      color: theme.palette.primary.dark,
                      fontSize: '0.95rem',
                    }}
                  />
                  <Box sx={{ color: theme.palette.primary.main }}>
                    {expanded[category.id] ? <ExpandLess /> : <ExpandMore />}
                  </Box>
                </ListItemButton>

                <Collapse
                  in={expanded[category.id] || false}
                  timeout='auto'
                  unmountOnExit
                >
                  <List component='div' disablePadding>
                    {category.items.map(
                      item =>
                        item.roles.includes(role) && (
                          <ListItem
                            key={item.path || item.action || item.title}
                            disablePadding
                          >
                            <ListItemButton
                              onClick={() => handleMenuItemClick(item)}
                              sx={{
                                ml: 2,
                                mr: 1,
                                mb: 0.5,
                                borderRadius: 2,
                                backgroundColor: 'rgba(255, 255, 255, 0.4)',
                                '&:hover': {
                                  backgroundColor: 'rgba(102, 126, 234, 0.08)',
                                  transform: 'translateX(4px)',
                                  boxShadow: '0px 2px 6px rgba(0, 0, 0, 0.08)',
                                },
                                transition: 'all 0.2s ease-in-out',
                              }}
                            >
                              <ListItemIcon
                                sx={{ 
                                  color: theme.palette.text.secondary,
                                  minWidth: 36,
                                }}
                              >
                                {item.icon}
                              </ListItemIcon>
                              <ListItemText
                                primary={item.title}
                                primaryTypographyProps={{
                                  color: theme.palette.text.primary,
                                  variant: 'body2',
                                  fontWeight: 500,
                                  fontSize: '0.875rem',
                                }}
                              />
                            </ListItemButton>
                          </ListItem>
                        )
                    )}
                  </List>
                </Collapse>
              </React.Fragment>
            )
        )}
      </List>

      <Box 
        sx={{ 
          backgroundColor: 'transparent',
          p: 1,
        }}
      >
        <ListItem disablePadding>
          <ListItemButton
            onClick={handleLogout}
            sx={{
              borderRadius: 3,
              backgroundColor: 'rgba(211, 47, 47, 0.1)',
              border: '1px solid rgba(211, 47, 47, 0.2)',
              '&:hover': {
                backgroundColor: 'rgba(211, 47, 47, 0.15)',
                transform: 'translateY(-1px)',
                boxShadow: '0px 4px 12px rgba(211, 47, 47, 0.2)',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          >
            <ListItemIcon sx={{ color: theme.palette.error.main }}>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText
              primary='Logout'
              primaryTypographyProps={{
                color: theme.palette.error.main,
                variant: 'body1',
                fontWeight: 600,
              }}
            />
          </ListItemButton>
        </ListItem>
      </Box>
    </Box>
  );
};

export default Sidebar;
