import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Grid,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
} from '@mui/material';
import {
  Extension as ExtensionIcon,
  Info as InfoIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { usePlugins } from '../../hooks/usePlugins';
import { PluginConfigRuntime } from '../../shared/types/plugin';

const PluginManager: React.FC = () => {
  const { plugins, loading, error, refreshPlugins } = usePlugins();
  const [selectedPlugin, setSelectedPlugin] = useState<PluginConfigRuntime | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const handlePluginToggle = async (pluginId: string, enabled: boolean) => {
    try {
      // In a real implementation, this would call an API to enable/disable the plugin
      console.log(`${enabled ? 'Enabling' : 'Disabling'} plugin: ${pluginId}`);
      
      // Update localStorage for demonstration
      const storedPlugins = JSON.parse(localStorage.getItem('pms_plugins') || '[]');
      const updatedPlugins = storedPlugins.map((plugin: any) =>
        plugin.id === pluginId ? { ...plugin, enabled } : plugin
      );
      localStorage.setItem('pms_plugins', JSON.stringify(updatedPlugins));
      
      // Refresh plugins
      await refreshPlugins();
    } catch (error) {
      console.error('Failed to toggle plugin:', error);
    }
  };

  const handleViewDetails = (plugin: PluginConfigRuntime) => {
    setSelectedPlugin(plugin);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedPlugin(null);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading plugins...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading plugins: {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Plugin Manager
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Manage and configure plugins for your application. Enabled plugins will appear in the sidebar menu.
      </Typography>

      <Grid container spacing={3}>
        {plugins.map((plugin) => (
          <Grid item xs={12} md={6} lg={4} key={plugin.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" alignItems="center" mb={2}>
                  <ExtensionIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6" component="div">
                    {plugin.name}
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {plugin.description || 'No description available'}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Chip 
                    label={`v${plugin.version}`} 
                    size="small" 
                    variant="outlined" 
                    sx={{ mr: 1 }}
                  />
                  <Chip 
                    label={plugin.enabled ? 'Enabled' : 'Disabled'}
                    size="small"
                    color={plugin.enabled ? 'success' : 'default'}
                  />
                </Box>

                <Typography variant="body2" sx={{ mb: 1 }}>
                  Menu Categories: {plugin.menuCategories.length}
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={plugin.enabled}
                      onChange={(e) => handlePluginToggle(plugin.id, e.target.checked)}
                      color="primary"
                    />
                  }
                  label={plugin.enabled ? 'Enabled' : 'Disabled'}
                  sx={{ mb: 2 }}
                />

                <Box>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<InfoIcon />}
                    onClick={() => handleViewDetails(plugin)}
                    fullWidth
                  >
                    View Details
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {plugins.length === 0 && (
        <Box textAlign="center" sx={{ mt: 4 }}>
          <ExtensionIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No plugins found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Install plugins to extend your application functionality
          </Typography>
        </Box>
      )}

      {/* Plugin Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Plugin Details: {selectedPlugin?.name}
        </DialogTitle>
        <DialogContent>
          {selectedPlugin && (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                {selectedPlugin.description}
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Information
                </Typography>
                <Typography variant="body2">ID: {selectedPlugin.id}</Typography>
                <Typography variant="body2">Version: {selectedPlugin.version}</Typography>
                <Typography variant="body2">
                  Status: {selectedPlugin.enabled ? 'Enabled' : 'Disabled'}
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Menu Categories
                </Typography>
                <List dense>
                  {selectedPlugin.menuCategories.map((category) => (
                    <ListItem key={category.id}>
                      <ListItemIcon>{category.icon}</ListItemIcon>
                      <ListItemText
                        primary={category.title}
                        secondary={`${category.items.length} menu items`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>

              {selectedPlugin.permissions && selectedPlugin.permissions.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Required Permissions
                  </Typography>
                  <Box>
                    {selectedPlugin.permissions.map((permission) => (
                      <Chip
                        key={permission}
                        label={permission}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {selectedPlugin.dependencies && selectedPlugin.dependencies.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Dependencies
                  </Typography>
                  <Box>
                    {selectedPlugin.dependencies.map((dependency) => (
                      <Chip
                        key={dependency}
                        label={dependency}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PluginManager; 