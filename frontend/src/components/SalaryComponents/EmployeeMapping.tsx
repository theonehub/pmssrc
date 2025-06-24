import React, { useState, useMemo } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Grid,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import DataTable from '../Common/UIComponents/DataTable';
import { 
  useEmployeeMappings, 
  useSalaryComponents 
} from '../../shared/hooks/useSalaryComponents';
import { 
  EmployeeSalaryMapping, 
  CreateEmployeeMappingRequest 
} from '../../shared/api/salaryComponentApi';

const EmployeeMapping: React.FC = () => {
  // State for filters and dialogs
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
  const [selectedComponentId, setSelectedComponentId] = useState<string>('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editMapping, setEditMapping] = useState<EmployeeSalaryMapping | null>(null);

  // Dialog form state
  const [formData, setFormData] = useState<CreateEmployeeMappingRequest>({
    employee_id: '',
    component_id: '',
    effective_from: new Date().toISOString().split('T')[0] as string,
  });

  // Get data using custom hooks
  const {
    mappings,
    isLoading,
    error,
    createMapping,
    updateMapping,
    isCreating,
    isUpdating,
    refetch,
  } = useEmployeeMappings(selectedEmployeeId, selectedComponentId);

  const { components } = useSalaryComponents({ is_active: true });

  // Table columns configuration
  const columns = useMemo(() => [
    {
      field: 'employee_name' as keyof EmployeeSalaryMapping,
      headerName: 'Employee',
      width: '20%',
      renderCell: (row: EmployeeSalaryMapping) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {row.employee_name || row.employee_id}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            ID: {row.employee_id}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'component_name' as keyof EmployeeSalaryMapping,
      headerName: 'Component',
      width: '20%',
      renderCell: (row: EmployeeSalaryMapping) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {row.component_name || row.component_id}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'fixed_amount' as keyof EmployeeSalaryMapping,
      headerName: 'Fixed Amount',
      width: '15%',
      renderCell: (row: EmployeeSalaryMapping) => (
        row.fixed_amount ? `₹${row.fixed_amount.toLocaleString()}` : '-'
      ),
    },
    {
      field: 'percentage_of_basic' as keyof EmployeeSalaryMapping,
      headerName: 'Percentage',
      width: '15%',
      renderCell: (row: EmployeeSalaryMapping) => (
        row.percentage_of_basic ? `${row.percentage_of_basic}%` : '-'
      ),
    },
    {
      field: 'effective_from' as keyof EmployeeSalaryMapping,
      headerName: 'Effective From',
      width: '12%',
      renderCell: (row: EmployeeSalaryMapping) => (
        new Date(row.effective_from).toLocaleDateString()
      ),
    },
    {
      field: 'is_active' as keyof EmployeeSalaryMapping,
      headerName: 'Status',
      width: '8%',
      renderCell: (row: EmployeeSalaryMapping) => (
        <Chip
          label={row.is_active ? 'Active' : 'Inactive'}
          color={row.is_active ? 'success' : 'default'}
          size="small"
        />
      ),
    },
  ], []);

  // Handle dialog actions
  const handleOpenDialog = (mapping?: EmployeeSalaryMapping) => {
    if (mapping) {
      setEditMapping(mapping);
      const newFormData: CreateEmployeeMappingRequest = {
        employee_id: mapping.employee_id,
        component_id: mapping.component_id,
        effective_from: mapping.effective_from,
      };
      
      if (mapping.fixed_amount !== undefined) {
        newFormData.fixed_amount = mapping.fixed_amount;
      }
      
      if (mapping.percentage_of_basic !== undefined) {
        newFormData.percentage_of_basic = mapping.percentage_of_basic;
      }
      
      if (mapping.effective_to) {
        newFormData.effective_to = mapping.effective_to;
      }
      
      setFormData(newFormData);
    } else {
      setEditMapping(null);
      setFormData({
        employee_id: '',
        component_id: '',
        effective_from: new Date().toISOString().split('T')[0] as string,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditMapping(null);
  };

  const handleSaveMapping = async () => {
    try {
      if (editMapping) {
        await updateMapping('mapping_id', formData); // Note: Real implementation needs mapping ID
      } else {
        await createMapping(formData);
      }
      handleCloseDialog();
    } catch (error) {
      // Error handled by hook
    }
  };

  // Render action buttons for each row
  const renderActions = (mapping: EmployeeSalaryMapping) => (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Tooltip title="Edit Mapping">
        <IconButton
          size="small"
          onClick={() => handleOpenDialog(mapping)}
        >
          <EditIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Employee Salary Mappings
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Mapping
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error.message || 'Failed to load employee mappings'}
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Employee ID"
              value={selectedEmployeeId}
              onChange={(e) => setSelectedEmployeeId(e.target.value)}
              placeholder="Filter by employee ID..."
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              select
              fullWidth
              label="Component"
              value={selectedComponentId}
              onChange={(e) => setSelectedComponentId(e.target.value)}
            >
              <MenuItem value="">All Components</MenuItem>
              {components.map((component) => (
                <MenuItem key={component.component_id} value={component.component_id}>
                  {component.name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="outlined"
              onClick={() => {
                setSelectedEmployeeId('');
                setSelectedComponentId('');
              }}
              fullWidth
              sx={{ height: 56 }}
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={mappings}
        loading={isLoading}
        emptyMessage="No employee mappings found"
        renderActions={renderActions}
      />

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editMapping ? 'Edit Employee Mapping' : 'Add Employee Mapping'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Employee ID"
                value={formData.employee_id}
                onChange={(e) => setFormData(prev => ({ ...prev, employee_id: e.target.value }))}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Salary Component"
                value={formData.component_id}
                onChange={(e) => setFormData(prev => ({ ...prev, component_id: e.target.value }))}
                required
              >
                {components.map((component) => (
                  <MenuItem key={component.component_id} value={component.component_id}>
                    {component.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Fixed Amount"
                type="number"
                value={formData.fixed_amount || ''}
                onChange={(e) => {
                  const newFormData = { ...formData };
                  if (e.target.value) {
                    newFormData.fixed_amount = parseFloat(e.target.value);
                  } else {
                    delete newFormData.fixed_amount;
                  }
                  setFormData(newFormData);
                }}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Percentage of Basic"
                type="number"
                value={formData.percentage_of_basic || ''}
                onChange={(e) => {
                  const newFormData = { ...formData };
                  if (e.target.value) {
                    newFormData.percentage_of_basic = parseFloat(e.target.value);
                  } else {
                    delete newFormData.percentage_of_basic;
                  }
                  setFormData(newFormData);
                }}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Effective From"
                type="date"
                value={formData.effective_from}
                onChange={(e) => setFormData(prev => ({ ...prev, effective_from: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Effective To (Optional)"
                type="date"
                value={formData.effective_to || ''}
                onChange={(e) => {
                  const newFormData = { ...formData };
                  if (e.target.value) {
                    newFormData.effective_to = e.target.value;
                  } else {
                    delete newFormData.effective_to;
                  }
                  setFormData(newFormData);
                }}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveMapping}
            variant="contained"
            disabled={isCreating || isUpdating || !formData.employee_id || !formData.component_id}
          >
            {(isCreating || isUpdating) 
              ? 'Saving...' 
              : (editMapping ? 'Update' : 'Create')
            }
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmployeeMapping; 