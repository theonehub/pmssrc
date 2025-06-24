import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  Divider,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  Cancel as CancelIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { useAuth } from '../../shared/hooks/useAuth';
import { salaryComponentApi } from '../../shared/api/salaryComponentApi';
import { organizationApi } from '../../shared/api/organizationApi';
import {
  GlobalSalaryComponent,
  ComponentAssignment,
  AssignComponentsRequest,
  RemoveComponentsRequest,
} from '../../shared/api/salaryComponentApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`assignment-tabpanel-${index}`}
      aria-labelledby={`assignment-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AssignComponents: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [organizationLoading, setOrganizationLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Data states
  const [globalComponents, setGlobalComponents] = useState<GlobalSalaryComponent[]>([]);
  const [organizationComponents, setOrganizationComponents] = useState<ComponentAssignment[]>([]);
  const [comparisonData, setComparisonData] = useState<{
    global_components: GlobalSalaryComponent[];
    organization_components: ComponentAssignment[];
    available_for_assignment: GlobalSalaryComponent[];
  } | null>(null);
  
  // Organization state
  const [currentOrganization, setCurrentOrganization] = useState<{
    org_id: string;
    hostname: string;
    company_name: string;
  } | null>(null);
  
  // UI states
  const [tabValue, setTabValue] = useState(0);
  const [selectedComponents, setSelectedComponents] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [componentTypeFilter, setComponentTypeFilter] = useState<string>('');
  const [assignmentDialogOpen, setAssignmentDialogOpen] = useState(false);
  const [assignmentNotes, setAssignmentNotes] = useState('');
  
  // Filters - memoized to prevent infinite re-renders
  const filters = useMemo(() => ({
    search_term: '',
    component_type: '',
    is_active: true,
    page: 1,
    page_size: 50,
  }), []);

  const loadCurrentOrganization = useCallback(async () => {
    if (!user?.hostname) return;
    
    try {
      setOrganizationLoading(true);
      const organization = await organizationApi.getOrganizationByHostname(user.hostname);
      setCurrentOrganization({
        org_id: organization.org_id,
        hostname: organization.hostname,
        company_name: organization.company_name,
      });
    } catch (err) {
      console.error('Error loading current organization:', err);
      setError('Failed to load current organization');
    } finally {
      setOrganizationLoading(false);
    }
  }, [user?.hostname]);

  const loadGlobalComponents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await salaryComponentApi.getGlobalSalaryComponents(filters);
      
      if (response.success) {
        setGlobalComponents(response.data);
      } else {
        setError(response.message || 'Failed to load global components');
      }
    } catch (err) {
      setError('Failed to load global components');
      console.error('Error loading global components:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const loadOrganizationComponents = useCallback(async () => {
    if (!currentOrganization?.org_id) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await salaryComponentApi.getOrganizationComponents(currentOrganization.org_id);
      
      if (response.success) {
        setOrganizationComponents(response.data);
      } else {
        setError(response.message || 'Failed to load organization components');
      }
    } catch (err) {
      setError('Failed to load organization components');
      console.error('Error loading organization components:', err);
    } finally {
      setLoading(false);
    }
  }, [currentOrganization?.org_id]);

  const loadComparisonData = useCallback(async () => {
    if (!currentOrganization?.org_id) return;
    
    try {
      const response = await salaryComponentApi.getComparisonData(currentOrganization.org_id);
      
      if (response.success) {
        setComparisonData(response.data);
      }
    } catch (err) {
      console.error('Error loading comparison data:', err);
    }
  }, [currentOrganization?.org_id]);

  useEffect(() => {
    if (user?.hostname) {
      loadCurrentOrganization();
    }
  }, [user?.hostname, loadCurrentOrganization]);

  useEffect(() => {
    if (user?.hostname) {
      loadGlobalComponents();
    }
  }, [user?.hostname, loadGlobalComponents]);

  useEffect(() => {
    if (currentOrganization?.org_id) {
      loadOrganizationComponents();
      loadComparisonData();
    }
  }, [currentOrganization?.org_id, loadOrganizationComponents, loadComparisonData]);

  const handleAssignComponents = async () => {
    if (selectedComponents.length === 0) {
      setError('Please select at least one component to assign');
      return;
    }

    if (!currentOrganization?.org_id) {
      setError('No organization selected');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const request: AssignComponentsRequest = {
        organization_id: currentOrganization.org_id,
        component_ids: selectedComponents,
        status: 'ACTIVE',
        notes: assignmentNotes,
      };

      const response = await salaryComponentApi.assignComponents(request);
      
      if (response.success) {
        setSuccess(`Successfully assigned ${selectedComponents.length} components to organization`);
        setSelectedComponents([]);
        setAssignmentNotes('');
        setAssignmentDialogOpen(false);
        
        // Reload data
        await Promise.all([
          loadOrganizationComponents(),
          loadComparisonData(),
        ]);
      } else {
        setError(response.message || 'Failed to assign components');
      }
    } catch (err) {
      setError('Failed to assign components');
      console.error('Error assigning components:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveComponents = async (componentIds: string[]) => {
    if (!currentOrganization?.org_id) {
      setError('No organization selected');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const request: RemoveComponentsRequest = {
        organization_id: currentOrganization.org_id,
        component_ids: componentIds,
        notes: 'Removed by superadmin',
      };

      const response = await salaryComponentApi.removeComponents(request);
      
      if (response.success) {
        setSuccess(`Successfully removed ${componentIds.length} components from organization`);
        
        // Reload data
        await Promise.all([
          loadOrganizationComponents(),
          loadComparisonData(),
        ]);
      } else {
        setError(response.message || 'Failed to remove components');
      }
    } catch (err) {
      setError('Failed to remove components');
      console.error('Error removing components:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredGlobalComponents = globalComponents.filter(component => {
    const matchesSearch = !searchTerm || 
      component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      component.code.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = !componentTypeFilter || component.component_type === componentTypeFilter;
    
    return matchesSearch && matchesType;
  });

  const availableForAssignment = comparisonData?.available_for_assignment || [];

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleComponentSelection = (componentId: string) => {
    setSelectedComponents(prev => 
      prev.includes(componentId) 
        ? prev.filter(id => id !== componentId)
        : [...prev, componentId]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'INACTIVE': return 'error';
      case 'PENDING': return 'warning';
      default: return 'default';
    }
  };

  if (!user?.role || user.role !== 'superadmin') {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Access denied. Only superadmin can assign salary components to organizations.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        <AssignmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Assign Salary Components
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Manage salary component assignments for organizations. Assign global components to specific organizations.
      </Typography>

      {/* Organization Information */}
      {organizationLoading ? (
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <CircularProgress size={20} sx={{ mr: 1 }} />
          <Typography variant="body2" color="text.secondary">
            Loading organization information...
          </Typography>
        </Box>
      ) : currentOrganization ? (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.50' }}>
          <Typography variant="h6" gutterBottom>
            Current Organization
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">
                <strong>Company:</strong> {currentOrganization.company_name}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">
                <strong>Hostname:</strong> {currentOrganization.hostname}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">
                <strong>Organization ID:</strong> {currentOrganization.org_id}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      ) : (
        <Alert severity="warning" sx={{ mb: 3 }}>
          No organization information available. Please ensure you are logged in with a valid organization.
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="assignment tabs">
            <Tab label="Global Components" disabled={!currentOrganization} />
            <Tab label="Organization Components" disabled={!currentOrganization} />
            <Tab label="Comparison View" disabled={!currentOrganization} />
          </Tabs>
        </Box>

        {!currentOrganization && !organizationLoading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Organization Information Required
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Please wait for organization information to load or contact support if the issue persists.
            </Typography>
          </Box>
        ) : (
          <>
            <TabPanel value={tabValue} index={0}>
              <Box sx={{ mb: 2 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Search Components"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      InputProps={{
                        startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <FormControl fullWidth>
                      <InputLabel>Component Type</InputLabel>
                      <Select
                        value={componentTypeFilter}
                        label="Component Type"
                        onChange={(e) => setComponentTypeFilter(e.target.value)}
                      >
                        <MenuItem value="">All Types</MenuItem>
                        <MenuItem value="EARNING">Earning</MenuItem>
                        <MenuItem value="DEDUCTION">Deduction</MenuItem>
                        <MenuItem value="REIMBURSEMENT">Reimbursement</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Button
                      variant="outlined"
                      startIcon={<SearchIcon />}
                      onClick={loadGlobalComponents}
                      disabled={loading}
                    >
                      Refresh
                    </Button>
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <Button
                      variant="contained"
                      startIcon={<AssignmentIcon />}
                      onClick={() => setAssignmentDialogOpen(true)}
                      disabled={selectedComponents.length === 0 || !currentOrganization}
                      fullWidth
                    >
                      Assign Selected ({selectedComponents.length})
                    </Button>
                  </Grid>
                </Grid>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <Grid container spacing={2}>
                  {filteredGlobalComponents.map((component) => (
                    <Grid item xs={12} md={6} lg={4} key={component.component_id}>
                      <Card 
                        variant={selectedComponents.includes(component.component_id) ? "elevation" : "outlined"}
                        sx={{ 
                          cursor: 'pointer',
                          border: selectedComponents.includes(component.component_id) ? 2 : 1,
                          borderColor: selectedComponents.includes(component.component_id) ? 'primary.main' : 'divider',
                        }}
                        onClick={() => handleComponentSelection(component.component_id)}
                      >
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Typography variant="h6" component="div">
                              {component.name}
                            </Typography>
                            <Checkbox
                              checked={selectedComponents.includes(component.component_id)}
                              onChange={() => handleComponentSelection(component.component_id)}
                              onClick={(e) => e.stopPropagation()}
                            />
                          </Box>
                          
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Code: {component.code}
                          </Typography>
                          
                          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                            <Chip 
                              label={component.component_type} 
                              size="small" 
                              color="primary" 
                              variant="outlined" 
                            />
                            <Chip 
                              label={component.value_type} 
                              size="small" 
                              color="secondary" 
                              variant="outlined" 
                            />
                            <Chip 
                              label={component.is_taxable ? 'Taxable' : 'Non-Taxable'} 
                              size="small" 
                              color={component.is_taxable ? 'error' : 'success'} 
                              variant="outlined" 
                            />
                          </Box>
                          
                          {component.description && (
                            <Typography variant="body2" color="text.secondary">
                              {component.description}
                            </Typography>
                          )}
                          
                          {component.formula && (
                            <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                              Formula: {component.formula}
                            </Typography>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <Typography variant="h6" gutterBottom>
                Components Assigned to: {currentOrganization?.company_name}
              </Typography>
              
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <List>
                  {organizationComponents.map((assignment) => (
                    <React.Fragment key={assignment.assignment_id}>
                      <ListItem>
                        <ListItemText
                          primary={assignment.component_name || assignment.component_id}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Code: {assignment.component_code || assignment.component_id}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                Assigned by: {assignment.assigned_by} on {new Date(assignment.assigned_at).toLocaleDateString()}
                              </Typography>
                              {assignment.notes && (
                                <Typography variant="body2" color="text.secondary">
                                  Notes: {assignment.notes}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                            <Chip 
                              label={assignment.status} 
                              color={getStatusColor(assignment.status) as any}
                              size="small"
                            />
                            <Tooltip title="Remove Component">
                              <IconButton
                                edge="end"
                                color="error"
                                onClick={() => handleRemoveComponents([assignment.component_id])}
                                disabled={loading}
                              >
                                <CancelIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              )}
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <Typography variant="h6" gutterBottom>
                Comparison: Global vs Organization Components
              </Typography>
              
              {comparisonData && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Available for Assignment ({availableForAssignment.length})
                        </Typography>
                        <List dense>
                          {availableForAssignment.map((component) => (
                            <ListItem key={component.component_id}>
                              <ListItemText
                                primary={component.name}
                                secondary={`${component.component_type} - ${component.value_type}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Currently Assigned ({organizationComponents.length})
                        </Typography>
                        <List dense>
                          {organizationComponents.map((assignment) => (
                            <ListItem key={assignment.assignment_id}>
                              <ListItemText
                                primary={assignment.component_name || assignment.component_id}
                                secondary={`Status: ${assignment.status}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              )}
            </TabPanel>
          </>
        )}
      </Paper>

      {/* Assignment Dialog */}
      <Dialog 
        open={assignmentDialogOpen} 
        onClose={() => setAssignmentDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Assign Components to Organization</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            You are about to assign {selectedComponents.length} components to organization: {currentOrganization?.company_name}
          </Typography>
          
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Assignment Notes (Optional)"
            value={assignmentNotes}
            onChange={(e) => setAssignmentNotes(e.target.value)}
            placeholder="Add any notes about this assignment..."
          />
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Selected Components:
            </Typography>
            <List dense>
              {selectedComponents.map((componentId) => {
                const component = globalComponents.find(c => c.component_id === componentId);
                return (
                  <ListItem key={componentId}>
                    <ListItemText
                      primary={component?.name || componentId}
                      secondary={component?.code || componentId}
                    />
                  </ListItem>
                );
              })}
            </List>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignmentDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleAssignComponents} 
            variant="contained" 
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <AssignmentIcon />}
          >
            {loading ? 'Assigning...' : 'Assign Components'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AssignComponents; 