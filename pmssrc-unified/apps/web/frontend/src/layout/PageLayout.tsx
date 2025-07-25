import React, { useState, useEffect } from 'react';
import {
  Box,
  useTheme,
  useMediaQuery,
  IconButton,
  Drawer,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import ChangePasswordDialog from '../components/Common/ChangePasswordDialog';
import { useAuth } from '../context/AuthContext';
import { organizationApi, Organization } from '../shared/api/organizationApi';

interface PageLayoutProps {
  title: string;
  children: React.ReactNode;
}

const PageLayout: React.FC<PageLayoutProps> = ({ title, children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth();
  const [sidebarWidth, setSidebarWidth] = useState<number>(280); // Default width
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] =
    useState<boolean>(false);
  const [isResizing, setIsResizing] = useState<boolean>(false);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [isPasswordDialogOpen, setIsPasswordDialogOpen] = useState<boolean>(false);

  // Store sidebar width in localStorage to persist between sessions
  useEffect(() => {
    const storedWidth = localStorage.getItem('sidebarWidth');
    const storedState = localStorage.getItem('sidebarOpen');

    if (storedWidth) {
      setSidebarWidth(parseInt(storedWidth));
    }

    if (storedState !== null) {
      setIsSidebarOpen(storedState === 'true');
    }
  }, []);

  // Fetch current organization data
  useEffect(() => {
    const fetchOrganization = async () => {
      if (!user) return;
      
      try {
        const orgData = await organizationApi.getCurrentOrganization();
        setOrganization(orgData);
      } catch (error: any) {
        console.error('Failed to fetch organization data:', error);
        // Don't show error to user, just continue without org data
      }
    };

    fetchOrganization();
  }, [user]);

  // Handle sidebar toggle for desktop
  const toggleSidebar = (): void => {
    const newState = !isSidebarOpen;
    setIsSidebarOpen(newState);
    localStorage.setItem('sidebarOpen', newState.toString());
  };

  // Handle mobile drawer toggle
  const toggleMobileDrawer = (): void => {
    setIsMobileSidebarOpen(!isMobileSidebarOpen);
  };

  // Handle password change dialog
  const handlePasswordChange = () => {
    setIsPasswordDialogOpen(true);
  };

  const handlePasswordDialogClose = () => {
    setIsPasswordDialogOpen(false);
  };

  // Handle resizing sidebar
  const handleMouseDown = (e: React.MouseEvent): void => {
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);

    // Add event listeners for mouse move and mouse up
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseMove = (e: MouseEvent): void => {
    if (isResizing) {
      const newWidth = e.clientX;
      if (newWidth >= 200 && newWidth <= 500) {
        setSidebarWidth(newWidth);
        document.body.style.cursor = 'ew-resize';
      }
    }
  };

  const handleMouseUp = (): void => {
    setIsResizing(false);
    document.body.style.cursor = '';
    localStorage.setItem('sidebarWidth', sidebarWidth.toString());

    // Remove event listeners when not resizing
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  const mainContentMargin = isMobile ? 0 : isSidebarOpen ? sidebarWidth : 0;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        position: 'relative',
        backgroundColor: theme.palette.background.default,
      }}
    >
      <Topbar
        title={title}
        onMenuClick={isMobile ? toggleMobileDrawer : toggleSidebar}
        organizationLogo={organization?.logo_url}
        organizationName={organization?.company_name}
        onPasswordChange={handlePasswordChange}
      />

      {/* Password Change Dialog */}
      <ChangePasswordDialog
        open={isPasswordDialogOpen}
        onClose={handlePasswordDialogClose}
      />

      <Box
        sx={{
          display: 'flex',
          flexGrow: 1,
          mt: '64px', // Add margin top equal to AppBar height
          height: 'calc(100vh - 64px)', // Subtract AppBar height from total height
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {/* Desktop Sidebar */}
        {!isMobile && (
          <Box
            sx={{
              width: isSidebarOpen ? `${sidebarWidth}px` : 0,
              flexShrink: 0,
              position: 'fixed',
              height: 'calc(100vh - 64px)',
              overflowY: 'auto',
              left: 0,
              top: '64px',
              zIndex: 1100,
              visibility: isSidebarOpen ? 'visible' : 'hidden',
              transition: !isResizing
                ? theme.transitions.create(['width', 'visibility'], {
                    easing: theme.transitions.easing.sharp,
                    duration: theme.transitions.duration.standard,
                  })
                : 'none',
              backgroundColor: theme.palette.background.paper,
            }}
          >
            <Sidebar />

            {/* Resize Handle */}
            {isSidebarOpen && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: '8px',
                  height: '100%',
                  cursor: 'ew-resize',
                  backgroundColor: isResizing
                    ? theme.palette.primary.main
                    : 'transparent',
                  '&:hover': {
                    backgroundColor: theme.palette.primary.light,
                  },
                  zIndex: 10000,
                }}
                onMouseDown={handleMouseDown}
              />
            )}
          </Box>
        )}

        {/* Mobile Drawer */}
        {isMobile && (
          <Drawer
            variant='temporary'
            open={isMobileSidebarOpen}
            onClose={toggleMobileDrawer}
            ModalProps={{ keepMounted: true }}
            sx={{
              '& .MuiDrawer-paper': {
                width: '280px',
                top: '64px',
                height: 'calc(100% - 64px)',
                backgroundColor: theme.palette.background.paper,
              },
              zIndex: theme.zIndex.drawer,
            }}
          >
            <Sidebar />
          </Drawer>
        )}

        {/* Toggle button */}
        {!isMobile && (
          <IconButton
            onClick={toggleSidebar}
            sx={{
              position: 'fixed',
              left: isSidebarOpen ? `${sidebarWidth - 12}px` : '12px',
              top: '72px',
              transform: isSidebarOpen ? 'none' : 'rotate(180deg)',
              zIndex: 1200,
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              boxShadow: '0 3px 5px rgba(0,0,0,0.1)',
              transition: theme.transitions.create(['left', 'transform'], {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.standard,
              }),
              '&:hover': {
                backgroundColor: theme.palette.action.hover,
              },
            }}
          >
            {isSidebarOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
        )}

        <Box
          component='main'
          sx={{
            flexGrow: 1,
            width: '100%',
            p: { xs: 2, sm: 3 },
            overflow: 'auto',
            ml: `${mainContentMargin}px`,
            backgroundColor: theme.palette.background.default,
            transition: theme.transitions.create('margin-left', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.standard,
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
