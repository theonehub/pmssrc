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
  Collapse
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
  Business as BusinessIcon,
  CurrencyRupee as CurrencyRupeeIcon,
  CalculateOutlined as CalculateIcon,
  AccountBalance as AccountBalanceIcon,
  Payment as PaymentIcon,
  RequestPage as RequestPageIcon,
  Assessment as AssessmentIcon,
  ExpandLess,
  ExpandMore
} from '@mui/icons-material';
import { getUserRole } from '../utils/auth';

const Sidebar = () => {
  const role = getUserRole();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // State to track which menu categories are expanded
  const [expanded, setExpanded] = useState({
    home: false,
    organization: false,
    leaves: false,
    payouts: false,
    reimbursements: false,
    taxation: false,
    settings: false
  });

  // Toggle category expansion
  const toggleExpand = (category) => {
    console.log('Sidebar: Before toggle -', category, ':', expanded);
    setExpanded((prev) => {
      const newExpanded = { ...prev, [category]: !prev[category] };
      console.log('Sidebar: After toggle -', category, ':', newExpanded);
      return newExpanded;
    });
  };

  // Menu structure with categories
  const menuCategories = [
    {
      id: 'home',
      title: 'Home',
      icon: <HomeIcon />,
      items: [
        {
          title: 'Home',
          icon: <HomeIcon />,
          path: '/home',
          roles: ['manager', 'admin', 'superadmin', 'user']
        }
      ]
    },
    {
      id: 'organization',
      title: 'Organization',
      icon: <BusinessIcon />,
      items: [
        {
          title: 'Organizations',
          icon: <BusinessIcon />,
          path: '/organisations',
          roles: ['superadmin']
        },
        {
          title: 'Team',
          icon: <PeopleIcon />,
          path: '/users',
          roles: ['manager', 'admin', 'superadmin']
        }
      ]
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
          title: 'Leave Management',
          icon: <CalendarIcon />,
          path: '/leaves',
          roles: ['user', 'manager', 'admin', 'superadmin']
        },
        {
          title: 'LWP Management',
          icon: <EventBusyIcon />,
          path: '/lwp',
          roles: ['admin', 'superadmin']
        }
      ]
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
          roles: ['user', 'manager', 'admin', 'superadmin']
        },
        {
          title: 'My Payslips',
          icon: <RequestPageIcon />,
          path: '/payouts/my-payslips',
          roles: ['user', 'manager', 'admin', 'superadmin']
        },
        {
          title: 'Salary Calculator',
          icon: <CalculateIcon />,
          path: '/payouts/admin',
          roles: ['admin', 'superadmin']
        },
        {
          title: 'Monthly Processing',
          icon: <AssessmentIcon />,
          path: '/payouts/monthly',
          roles: ['admin', 'superadmin']
        },
        {
          title: 'Payout Reports',
          icon: <AssessmentIcon />,
          path: '/payouts/reports',
          roles: ['manager', 'admin', 'superadmin']
        }
      ]
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
          roles: ['user', 'manager', 'admin', 'superadmin']
        },
        {
          title: 'Tax Declaration',
          icon: <CalculateIcon />,
          path: '/taxation/declaration',
          roles: ['user', 'manager', 'admin', 'superadmin']
        },
        {
          title: 'Employee Tax Selection',
          icon: <PeopleIcon />,
          path: '/taxation/employee-selection',
          roles: ['admin', 'superadmin']
        }
      ]
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
        }
      ]
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
          roles: ['superadmin']
        }
      ]
    }
  ];

  // Helper function to check if any item in a category has the required role
  const hasCategoryAccess = (category) => {
    return category.items.some(item => item.roles.includes(role));
  };

  // Helper function to check if a category has any visible items for the current user
  const hasVisibleItems = (category) => {
    return category.items.filter(item => item.roles.includes(role)).length > 0;
  };

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
        zIndex: 1300 // Ensure sidebar is above overlays
      }}
    >
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="primary">
          📋 Menu
        </Typography>
      </Box>
      <Divider />
      <List sx={{ 
        flexGrow: 1,
        overflowY: 'auto',
        backgroundColor: theme.palette.background.paper,
      }}>
        {menuCategories.map((category) => (
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
                    color: theme.palette.primary.main
                  }}
                />
                {expanded[category.id] ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>

              <Collapse in={expanded[category.id]} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  {category.items.map((item) => (
                    item.roles.includes(role) && (
                      <ListItem key={item.path} disablePadding>
                        <ListItemButton
                          onClick={() => navigate(item.path)}
                          sx={{
                            pl: 4,
                            '&:hover': {
                              backgroundColor: theme.palette.action.hover,
                            },
                          }}
                        >
                          <ListItemIcon sx={{ color: theme.palette.text.secondary }}>
                            {item.icon}
                          </ListItemIcon>
                          <ListItemText 
                            primary={item.title}
                            primaryTypographyProps={{
                              color: theme.palette.text.primary,
                              variant: 'body2'
                            }}
                          />
                        </ListItemButton>
                      </ListItem>
                    )
                  ))}
                </List>
              </Collapse>
            </React.Fragment>
          )
        ))}
      </List>
      <Divider />
      <Box sx={{ backgroundColor: theme.palette.background.paper }}>
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
    </Box>
  );
};

export default Sidebar;
