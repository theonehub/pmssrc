import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Alert,
  Grid,
  Paper,
} from '@mui/material';
import { 
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon 
} from '@mui/icons-material';

const PluginDemo: React.FC = () => {
  const initializePlugins = () => {
    // Initialize demo plugins
    const plugins = [
      {
        id: 'analytics-plugin',
        name: 'Advanced Analytics',
        version: '1.0.0',
        description: 'Advanced analytics and reporting features',
        enabled: true,
        menuCategories: [
          {
            id: 'analytics',
            title: 'Advanced Analytics',
            icon: 'AnalyticsIcon',
            priority: 10,
            items: [
              {
                title: 'Performance Dashboard',
                icon: 'TrendingUpIcon',
                path: '/performance-dashboard',
                roles: ['manager', 'admin', 'superadmin'],
              },
              {
                title: 'Revenue Analytics',
                icon: 'PieChartIcon',
                path: '/revenue-analytics',
                roles: ['admin', 'superadmin'],
              },
            ],
          },
        ],
        permissions: ['analytics.read'],
      },
      {
        id: 'inventory-plugin',
        name: 'Inventory Management',
        version: '2.1.0',
        description: 'Complete inventory management system',
        enabled: false,
        menuCategories: [
          {
            id: 'inventory',
            title: 'Inventory',
            icon: 'InventoryIcon',
            priority: 5,
            items: [
              {
                title: 'Product Catalog',
                icon: 'CategoryIcon',
                path: '/product-catalog',
                roles: ['manager', 'admin', 'superadmin'],
              },
              {
                title: 'Stock Management',
                icon: 'InventoryIcon',
                path: '/stock-management',
                roles: ['admin', 'superadmin'],
              },
            ],
          },
        ],
        permissions: ['inventory.read', 'inventory.write'],
      },
    ];

    localStorage.setItem('pms_plugins', JSON.stringify(plugins));
    alert('Demo plugins initialized! Check the sidebar to see the "Advanced Analytics" menu (Inventory is disabled).');
    window.location.reload();
  };

  const enableInventoryPlugin = () => {
    const plugins = JSON.parse(localStorage.getItem('pms_plugins') || '[]');
    const updatedPlugins = plugins.map((plugin: any) =>
      plugin.id === 'inventory-plugin' ? { ...plugin, enabled: true } : plugin
    );
    localStorage.setItem('pms_plugins', JSON.stringify(updatedPlugins));
    alert('Inventory plugin enabled! Refresh the page to see it in the sidebar.');
    window.location.reload();
  };

  const disableAnalyticsPlugin = () => {
    const plugins = JSON.parse(localStorage.getItem('pms_plugins') || '[]');
    const updatedPlugins = plugins.map((plugin: any) =>
      plugin.id === 'analytics-plugin' ? { ...plugin, enabled: false } : plugin
    );
    localStorage.setItem('pms_plugins', JSON.stringify(updatedPlugins));
    alert('Analytics plugin disabled! Refresh the page to see it removed from sidebar.');
    window.location.reload();
  };

  const clearPlugins = () => {
    localStorage.removeItem('pms_plugins');
    alert('All plugins cleared! Refresh the page to see the default sidebar.');
    window.location.reload();
  };

  const getCurrentPlugins = () => {
    const plugins = localStorage.getItem('pms_plugins');
    return plugins ? JSON.parse(plugins) : [];
  };

  const currentPlugins = getCurrentPlugins();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Plugin System Demo
      </Typography>
      
      <Typography variant="body1" paragraph>
        This demo shows how the plugin system works. Plugins that are enabled will appear in the sidebar menu,
        while disabled plugins won't be shown.
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>How it works:</strong>
          <br />
          1. Plugins are stored in localStorage for this demo
          <br />
          2. When enabled, plugins automatically appear in the sidebar
          <br />
          3. When disabled, plugins are hidden from the sidebar
          <br />
          4. Plugin menu items respect user role permissions
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Demo Controls
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={initializePlugins}
                  fullWidth
                >
                  Initialize Demo Plugins
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<PlayIcon />}
                  onClick={enableInventoryPlugin}
                  fullWidth
                  disabled={!currentPlugins.some((p: any) => p.id === 'inventory-plugin')}
                >
                  Enable Inventory Plugin
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<StopIcon />}
                  onClick={disableAnalyticsPlugin}
                  fullWidth
                  disabled={!currentPlugins.some((p: any) => p.id === 'analytics-plugin')}
                >
                  Disable Analytics Plugin
                </Button>
                
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<RefreshIcon />}
                  onClick={clearPlugins}
                  fullWidth
                >
                  Clear All Plugins
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Plugin Status
              </Typography>
              
              {currentPlugins.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No plugins found. Click "Initialize Demo Plugins" to get started.
                </Typography>
              ) : (
                <Box>
                  {currentPlugins.map((plugin: any) => (
                    <Paper key={plugin.id} elevation={1} sx={{ p: 2, mb: 1 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {plugin.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Status: {plugin.enabled ? '✅ Enabled' : '❌ Disabled'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Menu Categories: {plugin.menuCategories.length}
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Browser Console Commands
        </Typography>
        <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
          <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace' }}>
{`// Available console commands:
pluginDemo.init()                    // Initialize plugins
pluginDemo.enable('plugin-id')       // Enable a plugin
pluginDemo.disable('plugin-id')      // Disable a plugin
pluginDemo.list()                    // List all plugins
pluginDemo.clear()                   // Clear all plugins
pluginDemo.showInstructions()        // Show detailed instructions`}
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
};

export default PluginDemo; 