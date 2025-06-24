import React, { useState, useMemo } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Chip,
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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Functions as FunctionsIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import DataTable from '../Common/UIComponents/DataTable';
import { useSalaryComponents } from '../../shared/hooks/useSalaryComponents';
import { SalaryComponent, SalaryComponentFilters } from '../../shared/api/salaryComponentApi';

interface Column {
  field: keyof SalaryComponent | 'category';
  headerName: string;
  renderCell?: (row: SalaryComponent) => React.ReactNode;
  width?: number | string;
}

const SalaryComponentsList: React.FC = () => {
  const navigate = useNavigate();
  
  // State for filters
  const [filters, setFilters] = useState<SalaryComponentFilters>({
    page: 1,
    limit: 10,
  });
  const [showFilters, setShowFilters] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedComponent, setSelectedComponent] = useState<SalaryComponent | null>(null);

  // Get data using custom hook
  const {
    components,
    total,
    isLoading,
    error,
    deleteComponent,
    isDeleting,
    refetch,
  } = useSalaryComponents(filters);

  // Component type colors
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'EARNING':
        return 'success';
      case 'DEDUCTION':
        return 'error';
      case 'REIMBURSEMENT':
        return 'info';
      default:
        return 'default';
    }
  };

  // Category colors
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'BASIC':
        return 'primary';
      case 'ALLOWANCE':
        return 'secondary';
      case 'BONUS':
        return 'success';
      case 'DEDUCTION':
        return 'error';
      case 'REIMBURSEMENT':
        return 'info';
      default:
        return 'default';
    }
  };

  // Table columns configuration
  const columns: Column[] = useMemo(() => [
    {
      field: 'name',
      headerName: 'Component Name',
      width: '25%',
    },
    {
      field: 'component_type',
      headerName: 'Type',
      width: '15%',
      renderCell: (row) => (
        <Chip
          label={row.component_type}
          color={getTypeColor(row.component_type) as any}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'category',
      headerName: 'Category',
      width: '15%',
      renderCell: (row) => {
        const category = row.category || row.component_type; // Fallback to component_type if category is not set
        return (
          <Chip
            label={category}
            color={getCategoryColor(category) as any}
            size="small"
          />
        );
      },
    },
    {
      field: 'is_taxable',
      headerName: 'Taxable',
      width: '10%',
      renderCell: (row) => (
        <Chip
          label={row.is_taxable ? 'Yes' : 'No'}
          color={row.is_taxable ? 'warning' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'value_type',
      headerName: 'Type',
      width: '10%',
      renderCell: (row) => (
        <Chip
          label={row.value_type === 'FIXED' ? 'Fixed' : 'Formula'}
          color={row.value_type === 'FIXED' ? 'info' : 'secondary'}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'is_active',
      headerName: 'Status',
      width: '10%',
      renderCell: (row) => (
        <Chip
          label={row.is_active ? 'Active' : 'Inactive'}
          color={row.is_active ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'description',
      headerName: 'Description',
      width: '15%',
      renderCell: (row) => (
        <Tooltip title={row.description || ''}>
          <Typography
            variant="body2"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: 150,
            }}
          >
            {row.description || '-'}
          </Typography>
        </Tooltip>
      ),
    },
  ], []);

  // Handle filter changes
  const handleFilterChange = (field: keyof SalaryComponentFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
      page: 1, // Reset to first page when filters change
    }));
  };

  // Handle pagination
  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  // Handle delete component
  const handleDeleteClick = (component: SalaryComponent) => {
    setSelectedComponent(component);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (selectedComponent) {
      try {
        await deleteComponent(selectedComponent.component_id);
        setDeleteDialogOpen(false);
        setSelectedComponent(null);
      } catch (error) {
        // Error is handled by the hook
      }
    }
  };

  // Render action buttons for each row
  const renderActions = (component: SalaryComponent) => (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Tooltip title="Edit Component">
        <IconButton
          size="small"
          onClick={() => navigate(`/salary-components/edit/${component.component_id}`)}
        >
          <EditIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      
      {component.value_type !== 'FIXED' && (
        <Tooltip title="Formula Builder">
          <IconButton
            size="small"
            onClick={() => navigate(`/salary-components/formula-builder?component=${component.component_id}`)}
          >
            <FunctionsIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      )}
      
      <Tooltip title="Delete Component">
        <IconButton
          size="small"
          color="error"
          onClick={() => handleDeleteClick(component)}
          disabled={isDeleting}
        >
          <DeleteIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Box>
  );

  const totalPages = Math.ceil(total / (filters.limit || 10));

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Salary Components
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filters
          </Button>
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
            onClick={() => navigate('/salary-components/create')}
          >
            Create Component
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error.message || 'Failed to load salary components'}
        </Alert>
      )}

      {/* Filters */}
      {showFilters && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search"
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Component name..."
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                select
                fullWidth
                label="Type"
                value={filters.component_type || ''}
                onChange={(e) => handleFilterChange('component_type', e.target.value || undefined)}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="EARNING">Earning</MenuItem>
                <MenuItem value="DEDUCTION">Deduction</MenuItem>
                <MenuItem value="REIMBURSEMENT">Reimbursement</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                select
                fullWidth
                label="Category"
                value={filters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
              >
                <MenuItem value="">All Categories</MenuItem>
                <MenuItem value="BASIC">Basic</MenuItem>
                <MenuItem value="ALLOWANCE">Allowance</MenuItem>
                <MenuItem value="BONUS">Bonus</MenuItem>
                <MenuItem value="DEDUCTION">Deduction</MenuItem>
                <MenuItem value="REIMBURSEMENT">Reimbursement</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                select
                fullWidth
                label="Taxable"
                value={filters.is_taxable?.toString() || ''}
                onChange={(e) => handleFilterChange('is_taxable', e.target.value ? e.target.value === 'true' : undefined)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="true">Taxable</MenuItem>
                <MenuItem value="false">Non-Taxable</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                select
                fullWidth
                label="Status"
                value={filters.is_active?.toString() || ''}
                onChange={(e) => handleFilterChange('is_active', e.target.value ? e.target.value === 'true' : undefined)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="true">Active</MenuItem>
                <MenuItem value="false">Inactive</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={components}
        loading={isLoading}
        emptyMessage="No salary components found"
        renderActions={renderActions}
        page={filters.page || 1}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Salary Component</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the component "{selectedComponent?.name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={isDeleting}
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SalaryComponentsList; 