import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Paper,
  Alert,
  CircularProgress,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
} from '@mui/material';
import {
  Download as DownloadIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as PreviewIcon,
  GetApp as ExportIcon,
} from '@mui/icons-material';
// import { DatePicker } from '@mui/x-date-pickers/DatePicker';
// import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
// import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { 
  useEmployeePreviewQuery,
  useEmployeeExportMutation
} from '../../shared/hooks/useEmployeeExport';
import { EmployeeExportFilters, EmployeeExportField } from '../../shared/types/api';

// Available fields for export
const AVAILABLE_FIELDS: EmployeeExportField[] = [
  { key: 'employee_id', label: 'Employee ID', category: 'Basic' },
  { key: 'name', label: 'Full Name', category: 'Basic' },
  { key: 'email', label: 'Email', category: 'Basic' },
  { key: 'mobile', label: 'Mobile Number', category: 'Basic' },
  { key: 'department', label: 'Department', category: 'Employment' },
  { key: 'designation', label: 'Designation', category: 'Employment' },
  { key: 'role', label: 'Role', category: 'Employment' },
  { key: 'location', label: 'Location', category: 'Employment' },
  { key: 'manager_id', label: 'Manager ID', category: 'Employment' },
  { key: 'date_of_joining', label: 'Date of Joining', category: 'Dates' },
  { key: 'date_of_leaving', label: 'Date of Leaving', category: 'Dates' },
  { key: 'date_of_birth', label: 'Date of Birth', category: 'Personal' },
  { key: 'gender', label: 'Gender', category: 'Personal' },
  { key: 'pan_number', label: 'PAN Number', category: 'Documents' },
  { key: 'aadhar_number', label: 'Aadhar Number', category: 'Documents' },
  { key: 'uan_number', label: 'UAN Number', category: 'Documents' },
  { key: 'esi_number', label: 'ESI Number', category: 'Documents' },
  { key: 'bank_account_number', label: 'Bank Account Number', category: 'Banking' },
  { key: 'bank_name', label: 'Bank Name', category: 'Banking' },
  { key: 'ifsc_code', label: 'IFSC Code', category: 'Banking' },
  { key: 'account_holder_name', label: 'Account Holder Name', category: 'Banking' },
  { key: 'status', label: 'Status', category: 'System' },
  { key: 'is_active', label: 'Is Active', category: 'System' },
  { key: 'created_at', label: 'Created Date', category: 'System' },
  { key: 'updated_at', label: 'Updated Date', category: 'System' },
];

// Default selected fields
const DEFAULT_SELECTED_FIELDS = [
  'employee_id',
  'name',
  'email',
  'mobile',
  'department',
  'designation',
  'date_of_joining',
  'status'
];

interface SnackbarState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

const DownloadCenter: React.FC = () => {
  // State for filters
  const [filters, setFilters] = useState<EmployeeExportFilters>({
    include_inactive: false,
    include_deleted: false,
  });

  // State for date filters
  const [dateOfJoiningFrom, setDateOfJoiningFrom] = useState<string>('');
  const [dateOfJoiningTo, setDateOfJoiningTo] = useState<string>('');
  const [dateOfLeavingFrom, setDateOfLeavingFrom] = useState<string>('');
  const [dateOfLeavingTo, setDateOfLeavingTo] = useState<string>('');
  const [dateOfBirthFrom, setDateOfBirthFrom] = useState<string>('');
  const [dateOfBirthTo, setDateOfBirthTo] = useState<string>('');

  // State for field selection
  const [selectedFields, setSelectedFields] = useState<string[]>(DEFAULT_SELECTED_FIELDS);

  // State for export format
  const [exportFormat, setExportFormat] = useState<'csv' | 'excel'>('excel');

  // State for preview dialog
  const [previewOpen, setPreviewOpen] = useState(false);
  const [enablePreview, setEnablePreview] = useState(false);

  // Snackbar state
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: '',
    severity: 'info',
  });

  // Export mutation for direct async handling
  const exportMutation = useEmployeeExportMutation();

  // Group fields by category
  const fieldsByCategory = AVAILABLE_FIELDS.reduce((acc, field) => {
    if (!acc[field.category]) {
      acc[field.category] = [];
    }
    acc[field.category]!.push(field);
    return acc;
  }, {} as Record<string, EmployeeExportField[]>);

  // Handle filter changes
  const handleFilterChange = (key: keyof EmployeeExportFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // Handle field selection
  const handleFieldToggle = (fieldKey: string) => {
    setSelectedFields(prev =>
      prev.includes(fieldKey)
        ? prev.filter(f => f !== fieldKey)
        : [...prev, fieldKey]
    );
  };

  // Handle category selection
  const handleCategoryToggle = (category: string) => {
    const categoryFields = fieldsByCategory[category]?.map(f => f.key) || [];
    const allSelected = categoryFields.every(field => selectedFields.includes(field));
    
    if (allSelected) {
      // Deselect all fields in this category
      setSelectedFields(prev => prev.filter(field => !categoryFields.includes(field)));
    } else {
      // Select all fields in this category
      setSelectedFields(prev => [
        ...prev.filter(field => !categoryFields.includes(field)),
        ...categoryFields,
      ]);
    }
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      include_inactive: false,
      include_deleted: false,
    });
    setDateOfJoiningFrom('');
    setDateOfJoiningTo('');
    setDateOfLeavingFrom('');
    setDateOfLeavingTo('');
    setDateOfBirthFrom('');
    setDateOfBirthTo('');
  };

  // Build complete filters object
  const buildCompleteFilters = (): EmployeeExportFilters => {
    const completeFilters: EmployeeExportFilters = { ...filters };

    if (dateOfJoiningFrom) {
      completeFilters.date_of_joining_from = dateOfJoiningFrom;
    }
    if (dateOfJoiningTo) {
      completeFilters.date_of_joining_to = dateOfJoiningTo;
    }
    if (dateOfLeavingFrom) {
      completeFilters.date_of_leaving_from = dateOfLeavingFrom;
    }
    if (dateOfLeavingTo) {
      completeFilters.date_of_leaving_to = dateOfLeavingTo;
    }
    if (dateOfBirthFrom) {
      completeFilters.date_of_birth_from = dateOfBirthFrom;
    }
    if (dateOfBirthTo) {
      completeFilters.date_of_birth_to = dateOfBirthTo;
    }

    return completeFilters;
  };

  // Build preview request
  const previewRequest = {
    filters: buildCompleteFilters(),
    fields: selectedFields,
    limit: 10,
  };
  
  // Preview query - only enabled when user clicks preview
  const previewQuery = useEmployeePreviewQuery(previewRequest, enablePreview && selectedFields.length > 0);

  // Handle preview
  const handlePreview = () => {
    if (selectedFields.length === 0) {
      setSnackbar({
        open: true,
        message: 'Please select at least one field to preview',
        severity: 'warning',
      });
      return;
    }

    // Enable the preview query which will automatically fetch data
    setEnablePreview(true);
    setPreviewOpen(true);
  };

  // Handle export
  const handleExport = () => {
    if (selectedFields.length === 0) {
      setSnackbar({
        open: true,
        message: 'Please select at least one field to export',
        severity: 'warning',
      });
      return;
    }

    const completeFilters = buildCompleteFilters();
    
    // Use the React Query mutation with proper Promise handling
    exportMutation.mutate({
      filters: completeFilters,
      fields: selectedFields,
      format: exportFormat,
    }, {
      onSuccess: (blob: Blob) => {
        // Download the file
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `employee_list_${new Date().toISOString().split('T')[0]}.${exportFormat === 'excel' ? 'xlsx' : 'csv'}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        setSnackbar({
          open: true,
          message: 'Employee list exported successfully',
          severity: 'success',
        });
      },
      onError: () => {
        setSnackbar({
          open: true,
          message: 'Failed to export employee list',
          severity: 'error',
        });
      }
    });
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
        {/* Header */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h4" color="primary" gutterBottom>
                  Download Center
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Export employee data with customizable filters and field selection
                </Typography>
              </Box>
              <DownloadIcon sx={{ fontSize: 48, color: 'primary.main', opacity: 0.3 }} />
            </Box>
          </CardContent>
        </Card>

        <Grid container spacing={3}>
          {/* Filters Section */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <FilterIcon />
                  Filters
                </Typography>

                <Grid container spacing={3}>
                  {/* Basic Filters */}
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Department</InputLabel>
                      <Select
                        value={filters.department || ''}
                        onChange={(e) => handleFilterChange('department', e.target.value || undefined)}
                        label="Department"
                      >
                        <MenuItem value="">All Departments</MenuItem>
                        <MenuItem value="Engineering">Engineering</MenuItem>
                        <MenuItem value="HR">HR</MenuItem>
                        <MenuItem value="Finance">Finance</MenuItem>
                        <MenuItem value="Marketing">Marketing</MenuItem>
                        <MenuItem value="Sales">Sales</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Role</InputLabel>
                      <Select
                        value={filters.role || ''}
                        onChange={(e) => handleFilterChange('role', e.target.value || undefined)}
                        label="Role"
                      >
                        <MenuItem value="">All Roles</MenuItem>
                        <MenuItem value="user">User</MenuItem>
                        <MenuItem value="manager">Manager</MenuItem>
                        <MenuItem value="admin">Admin</MenuItem>
                        <MenuItem value="superadmin">Super Admin</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Location</InputLabel>
                      <Select
                        value={filters.location || ''}
                        onChange={(e) => handleFilterChange('location', e.target.value || undefined)}
                        label="Location"
                      >
                        <MenuItem value="">All Locations</MenuItem>
                        <MenuItem value="Bangalore">Bangalore</MenuItem>
                        <MenuItem value="Mumbai">Mumbai</MenuItem>
                        <MenuItem value="Delhi">Delhi</MenuItem>
                        <MenuItem value="Hyderabad">Hyderabad</MenuItem>
                        <MenuItem value="Chennai">Chennai</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Search"
                      placeholder="Search by name, email, or employee ID"
                      value={filters.search || ''}
                      onChange={(e) => handleFilterChange('search', e.target.value || undefined)}
                    />
                  </Grid>

                  {/* Date Filters */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Date of Joining
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="From Date"
                          type="date"
                          value={dateOfJoiningFrom}
                          onChange={(e) => setDateOfJoiningFrom(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="To Date"
                          type="date"
                          value={dateOfJoiningTo}
                          onChange={(e) => setDateOfJoiningTo(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                    </Grid>
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Date of Leaving
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="From Date"
                          type="date"
                          value={dateOfLeavingFrom}
                          onChange={(e) => setDateOfLeavingFrom(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="To Date"
                          type="date"
                          value={dateOfLeavingTo}
                          onChange={(e) => setDateOfLeavingTo(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                    </Grid>
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Date of Birth
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="From Date"
                          type="date"
                          value={dateOfBirthFrom}
                          onChange={(e) => setDateOfBirthFrom(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="To Date"
                          type="date"
                          value={dateOfBirthTo}
                          onChange={(e) => setDateOfBirthTo(e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                    </Grid>
                  </Grid>

                  {/* Status Filters */}
                  <Grid item xs={12}>
                    <FormGroup>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={filters.include_inactive || false}
                            onChange={(e) => handleFilterChange('include_inactive', e.target.checked)}
                          />
                        }
                        label="Include Inactive Employees"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={filters.include_deleted || false}
                            onChange={(e) => handleFilterChange('include_deleted', e.target.checked)}
                          />
                        }
                        label="Include Deleted Employees"
                      />
                    </FormGroup>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<ClearIcon />}
                    onClick={clearFilters}
                  >
                    Clear Filters
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Export Options */}
          <Grid item xs={12} md={4}>
            <Stack spacing={3}>
              {/* Export Format */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Export Format
                  </Typography>
                  <FormControl fullWidth>
                    <InputLabel>Format</InputLabel>
                    <Select
                      value={exportFormat}
                      onChange={(e) => setExportFormat(e.target.value as 'csv' | 'excel')}
                      label="Format"
                    >
                      <MenuItem value="excel">Excel (.xlsx)</MenuItem>
                      <MenuItem value="csv">CSV (.csv)</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Actions
                  </Typography>
                  <Stack spacing={2}>
                    <Button
                      variant="outlined"
                      startIcon={<PreviewIcon />}
                      onClick={handlePreview}
                      disabled={previewQuery.isFetching || selectedFields.length === 0}
                      fullWidth
                    >
                      {previewQuery.isFetching ? (
                        <>
                          <CircularProgress size={20} sx={{ mr: 1 }} />
                          Loading...
                        </>
                      ) : (
                        'Preview Data'
                      )}
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<ExportIcon />}
                      onClick={handleExport}
                      disabled={exportMutation.isPending || selectedFields.length === 0}
                      fullWidth
                      size="large"
                    >
                      {exportMutation.isPending ? (
                        <>
                          <CircularProgress size={20} sx={{ mr: 1 }} />
                          Exporting...
                        </>
                      ) : (
                        'Export Data'
                      )}
                    </Button>
                  </Stack>
                  
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                    Note: Preview shows basic employee fields only. Personal details, banking info, and date filters are applied during export.
                  </Typography>
                  
                  {selectedFields.length === 0 && (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      Please select at least one field to export
                    </Alert>
                  )}
                  
                  {(exportMutation.error || previewQuery.error) && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {exportMutation.error?.message || previewQuery.error?.message || 'An error occurred'}
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Stack>
          </Grid>

          {/* Field Selection */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Select Fields to Export ({selectedFields.length} selected)
                </Typography>

                {Object.entries(fieldsByCategory).map(([category, fields]) => {
                  const categoryFields = fields.map(f => f.key);
                  const allSelected = categoryFields.every(field => selectedFields.includes(field));
                  const someSelected = categoryFields.some(field => selectedFields.includes(field));

                  return (
                    <Accordion key={category} defaultExpanded={category === 'Basic'}>
                      <AccordionSummary
                        expandIcon={<ExpandMoreIcon />}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={allSelected}
                              indeterminate={someSelected && !allSelected}
                              onChange={() => handleCategoryToggle(category)}
                              onClick={(e) => e.stopPropagation()}
                            />
                          }
                          label={
                            <Typography variant="subtitle1" fontWeight="medium">
                              {category} ({categoryFields.filter(field => selectedFields.includes(field)).length}/{categoryFields.length})
                            </Typography>
                          }
                          onClick={(e) => e.stopPropagation()}
                        />
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={1}>
                          {fields.map((field) => (
                            <Grid item xs={12} sm={6} md={4} key={field.key}>
                              <FormControlLabel
                                control={
                                  <Checkbox
                                    checked={selectedFields.includes(field.key)}
                                    onChange={() => handleFieldToggle(field.key)}
                                    size="small"
                                  />
                                }
                                label={
                                  <Typography variant="body2">
                                    {field.label}
                                  </Typography>
                                }
                              />
                            </Grid>
                          ))}
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  );
                })}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Preview Dialog */}
        <Dialog
          open={previewOpen}
          onClose={() => {
            setPreviewOpen(false);
            setEnablePreview(false); // Disable query when dialog closes
          }}
          maxWidth="lg"
          fullWidth
        >
          <DialogTitle>
            Data Preview (First 10 records)
            {previewQuery.isFetching && (
              <CircularProgress size={20} sx={{ ml: 2 }} />
            )}
          </DialogTitle>
          <DialogContent>
            {previewQuery.isFetching ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading preview...</Typography>
              </Box>
            ) : previewQuery.error ? (
              <Alert severity="error">
                Failed to load preview: {previewQuery.error.message}
              </Alert>
            ) : previewQuery.data && previewQuery.data.length > 0 ? (
              <Box sx={{ overflow: 'auto' }}>
                <Paper variant="outlined">
                  <Box sx={{ p: 2, minWidth: 600 }}>
                    {previewQuery.data.map((row, index) => (
                      <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Record {index + 1}
                        </Typography>
                        <Grid container spacing={2}>
                          {selectedFields.map((field) => (
                            <Grid item xs={12} sm={6} md={4} key={field}>
                              <Typography variant="caption" color="text.secondary">
                                {AVAILABLE_FIELDS.find(f => f.key === field)?.label || field}:
                              </Typography>
                              <Typography variant="body2">
                                {row[field] || 'N/A'}
                              </Typography>
                            </Grid>
                          ))}
                        </Grid>
                      </Box>
                    ))}
                  </Box>
                </Paper>
              </Box>
            ) : (
              <Typography>No data available for preview</Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setPreviewOpen(false);
              setEnablePreview(false);
            }}>
              Close
            </Button>
            {previewQuery.data && previewQuery.data.length > 0 && (
              <Button 
                variant="contained" 
                onClick={handleExport}
                disabled={exportMutation.isPending}
                startIcon={exportMutation.isPending ? <CircularProgress size={16} /> : <ExportIcon />}
              >
                {exportMutation.isPending ? 'Exporting...' : 'Export All Data'}
              </Button>
            )}
          </DialogActions>
        </Dialog>

        {/* Snackbar */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
            severity={snackbar.severity}
            variant="filled"
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    );
};

export default DownloadCenter; 