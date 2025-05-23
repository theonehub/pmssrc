import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  TextField,
  InputAdornment,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Radio,
  RadioGroup,
  Grid,
  Input,
  Card,
  CardContent,
  Skeleton,
  Tooltip,
  Fade,
  Chip,
  CircularProgress,
  TablePagination,
  Avatar,
  TableSortLabel
} from '@mui/material';
import { 
  Add as AddIcon, 
  UploadFile as UploadFileIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  People as PeopleIcon,
  Person as PersonIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import api from '../../utils/apiUtils';
import { useNavigate } from 'react-router-dom';
import PageLayout from '../../layout/PageLayout';
import ProtectedRoute from '../Common/ProtectedRoute';

function UsersList() {
  const navigate = useNavigate();
  
  // State management
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [alert, setAlert] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);

  // Memoized fetch function
  const fetchUsers = useCallback(async (showRefreshLoader = false) => {
    if (showRefreshLoader) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const response = await api.get('/users', {
        skip: page * rowsPerPage,
        limit: rowsPerPage
      });
      
      setUsers(response.data.users || []);
      setTotalUsers(response.data.total || 0);
    } catch (error) {
      console.error('Error fetching users:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to fetch users';
      showAlert(errorMessage, 'error');
      setUsers([]);
      setTotalUsers(0);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [page, rowsPerPage]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Helper functions
  const showAlert = (message, severity = 'success') => {
    setAlert({ open: true, message, severity });
  };

  const handleCloseAlert = () => {
    setAlert(prev => ({ ...prev, open: false }));
  };

  // Sort and filter functionality
  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortedAndFilteredUsers = () => {
    let filteredUsers = [...users];
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filteredUsers = filteredUsers.filter(user => 
        user.emp_id?.toLowerCase().includes(searchLower) ||
        user.name?.toLowerCase().includes(searchLower) ||
        user.email?.toLowerCase().includes(searchLower) ||
        user.gender?.toLowerCase().includes(searchLower) ||
        user.role?.toLowerCase().includes(searchLower) ||
        user.mobile?.includes(searchTerm)
      );
    }

    // Apply sorting
    if (sortConfig.key) {
      filteredUsers.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        // Special handling for dates
        if (sortConfig.key === 'dob' || sortConfig.key === 'doj') {
          aValue = new Date(aValue);
          bValue = new Date(bValue);
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }

    return filteredUsers;
  };

  // Event handlers


  const handleImport = async (e) => {
    e.preventDefault();
    if (!importFile) {
      showAlert('Please select a file to upload', 'warning');
      return;
    }

    setImporting(true);
    
    try {
      await api.upload('/users/import/with-file', importFile);
      showAlert('Users imported successfully', 'success');
      setShowImportModal(false);
      setImportFile(null);
      fetchUsers();
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to import users';
      showAlert(errorMessage, 'error');
    } finally {
      setImporting(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/users/template', {}, { responseType: 'blob' });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'user_import_template.xlsx');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      showAlert('Failed to download template', 'error');
    }
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = () => {
    fetchUsers(true);
  };

  // Render helpers
  const renderTableSkeleton = () => (
    Array.from({ length: rowsPerPage }).map((_, index) => (
      <TableRow key={index}>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton /></TableCell>
        <TableCell><Skeleton width={120} /></TableCell>
      </TableRow>
    ))
  );

  const renderEmptyState = () => (
    <TableRow>
      <TableCell colSpan={8} align="center" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center' }}>
          <PeopleIcon 
            sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} 
          />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No users found' : 'No users yet'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {searchTerm 
              ? `No users match "${searchTerm}"`
              : 'Get started by adding your first user'
            }
          </Typography>
          {!searchTerm && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/users/add')}
            >
              Add User
            </Button>
          )}
        </Box>
      </TableCell>
    </TableRow>
  );

  const getRoleBadgeColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'admin': return 'error';
      case 'manager': return 'warning';
      case 'hr': return 'info';
      case 'employee': return 'success';
      default: return 'default';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const filteredUsers = getSortedAndFilteredUsers();

  return (
    <PageLayout>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Card elevation={1} sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Typography variant="h4" color="primary" gutterBottom>
                  Users Management
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage user accounts and permissions
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                  <Tooltip title="Refresh">
                    <IconButton 
                      onClick={handleRefresh}
                      disabled={refreshing}
                      color="primary"
                    >
                      <RefreshIcon />
                    </IconButton>
                  </Tooltip>
                  <Button
                    variant="outlined"
                    startIcon={<UploadFileIcon />}
                    onClick={() => setShowImportModal(true)}
                    size="large"
                  >
                    Import
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/users/add')}
                    size="large"
                  >
                    Add User
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Search and Controls */}
        <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Search users"
                variant="outlined"
                value={searchTerm}
                onChange={handleSearchChange}
                placeholder="Search by ID, name, email, role, or mobile..."
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {loading ? 'Loading...' : `${filteredUsers.length} user${filteredUsers.length !== 1 ? 's' : ''}`}
                </Typography>
                {refreshing && <CircularProgress size={16} />}
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Table */}
        <Paper elevation={1}>
          <TableContainer>
            <Table stickyHeader>
              <TableHead>
                <TableRow sx={{ 
                  '& .MuiTableCell-head': { 
                    backgroundColor: 'primary.main',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '0.875rem'
                  }
                }}>
                  <TableCell>
                    <TableSortLabel
                      active={sortConfig.key === 'emp_id'}
                      direction={sortConfig.direction}
                      onClick={() => requestSort('emp_id')}
                      sx={{ color: 'inherit', '&:hover': { color: 'inherit' } }}
                    >
                      Employee ID
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortConfig.key === 'name'}
                      direction={sortConfig.direction}
                      onClick={() => requestSort('name')}
                      sx={{ color: 'inherit', '&:hover': { color: 'inherit' } }}
                    >
                      Name
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Gender</TableCell>
                  <TableCell>Mobile</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortConfig.key === 'doj'}
                      direction={sortConfig.direction}
                      onClick={() => requestSort('doj')}
                      sx={{ color: 'inherit', '&:hover': { color: 'inherit' } }}
                    >
                      Joining Date
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  renderTableSkeleton()
                ) : filteredUsers.length > 0 ? (
                  filteredUsers.map((user) => (
                    <Fade in key={user.emp_id} timeout={300}>
                      <TableRow 
                        hover
                        sx={{ 
                          '&:hover': { 
                            backgroundColor: 'action.hover' 
                          }
                        }}
                      >
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {user.emp_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Avatar 
                              sx={{ 
                                width: 32, 
                                height: 32, 
                                fontSize: '0.875rem',
                                bgcolor: 'primary.main'
                              }}
                            >
                              {getInitials(user.name)}
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle2" fontWeight="medium">
                                {user.name}
                              </Typography>
                              {user.designation && (
                                <Typography variant="caption" color="text.secondary">
                                  {user.designation}
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {user.email}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={user.role}
                            color={getRoleBadgeColor(user.role)}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {user.gender}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {user.mobile}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(user.doj)}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => navigate(`/users/emp/${user.emp_id}`)}
                              >
                                <VisibilityIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Edit User">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => navigate(`/users/emp/${user.emp_id}/edit`)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    </Fade>
                  ))
                ) : (
                  renderEmptyState()
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          {totalUsers > 0 && (
            <TablePagination
              component="div"
              count={totalUsers}
              page={page}
              onPageChange={handlePageChange}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={handleRowsPerPageChange}
              rowsPerPageOptions={[5, 10, 25, 50]}
              showFirstButton
              showLastButton
            />
          )}
        </Paper>



        {/* Import Modal */}
        <Dialog
          open={showImportModal}
          onClose={() => setShowImportModal(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            Import Users
          </DialogTitle>
          <DialogContent>
            <form onSubmit={handleImport}>
              <Box sx={{ mb: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownloadTemplate}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Download Template
                </Button>
              </Box>
              <Input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={(e) => setImportFile(e.target.files[0])}
                fullWidth
              />
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
                <Button onClick={() => setShowImportModal(false)}>
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  variant="contained"
                  disabled={importing || !importFile}
                >
                  {importing ? 'Importing...' : 'Import'}
                </Button>
              </Box>
            </form>
          </DialogContent>
        </Dialog>

        {/* Toast Notifications */}
        <Snackbar 
          open={alert.open} 
          autoHideDuration={6000} 
          onClose={handleCloseAlert}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={handleCloseAlert} 
            severity={alert.severity}
            sx={{ width: '100%' }}
            variant="filled"
          >
            {alert.message}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
}

export default UsersList;