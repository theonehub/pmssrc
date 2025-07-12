import React, { useState } from 'react';
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
  useMediaQuery,
  Collapse,
} from '@mui/material';
import {
  Home as HomeIcon,
  People as PeopleIcon,
  CalendarToday as CalendarIcon,
  CalendarMonth as CalendarMonthIcon,
  EventBusy as EventBusyIcon,
  PersonAdd as PersonAddIcon,
  Receipt as ReceiptIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Business as BusinessIcon,
  CurrencyRupee as CurrencyRupeeIcon,
  CalculateOutlined as CalculateIcon,
  Assessment as AssessmentIcon,
  Savings as SavingsIcon,
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
          roles: ['manager'],
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
      id: 'taxation',
      title: 'Income Tax',
      icon: <CurrencyRupeeIcon />,
      items: [
        {
          title: 'My Salary Components',
          icon: <CurrencyRupeeIcon />,
          path: '/my-salary',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
        {
          title: 'My Salary History',
          icon: <ReceiptIcon />,
          path: '/my-salary-history',
          roles: ['user', 'manager', 'admin', 'superadmin'],
        },
        {
          title: 'Component Management',
          icon: <SettingsIcon />,
          path: '/taxation/component-management',
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'Processed Salaries',
          icon: <ReceiptIcon />,
          path: '/taxation/processed-salaries',
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'TDS Report',
          icon: <AssessmentIcon />,
          path: '/taxation/tds-report',
          roles: ['admin', 'superadmin'],
        },
        {
          title: 'PF Report',
          icon: <SavingsIcon />,
          path: '/taxation/pf-report',
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
        backgroundColor: theme.palette.background.paper,
        borderRight: `1px solid ${theme.palette.divider}`,
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        minHeight: '100vh',
        overflow: 'hidden',
        zIndex: 1300, // Ensure sidebar is above overlays
      }}
    >
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant='h6' color='primary'>
          📋 Menu
        </Typography>
      </Box>
      <Divider />

      <List
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          backgroundColor: theme.palette.background.paper,
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
                    backgroundColor: theme.palette.action.selected,
                    mb: 0.5,
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover,
                    },
                  }}
                >
                  <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                    {category.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={category.title}
                    primaryTypographyProps={{
                      fontWeight: 'bold',
                      color: theme.palette.primary.main,
                    }}
                  />
                  {expanded[category.id] ? <ExpandLess /> : <ExpandMore />}
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
                                pl: 4,
                                '&:hover': {
                                  backgroundColor: theme.palette.action.hover,
                                },
                              }}
                            >
                              <ListItemIcon
                                sx={{ color: theme.palette.text.secondary }}
                              >
                                {item.icon}
                              </ListItemIcon>
                              <ListItemText
                                primary={item.title}
                                primaryTypographyProps={{
                                  color: theme.palette.text.primary,
                                  variant: 'body2',
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

      <Divider />

      <Box sx={{ backgroundColor: theme.palette.background.paper }}>
        <ListItem disablePadding>
          <ListItemButton
            onClick={handleLogout}
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
              primary='Logout'
              primaryTypographyProps={{
                color: theme.palette.error.main,
                variant: 'body1',
              }}
            />
          </ListItemButton>
        </ListItem>
      </Box>
    </Box>
  );
};

export default Sidebar;
