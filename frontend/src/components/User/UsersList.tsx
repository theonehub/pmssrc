import React, { useState } from 'react';
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
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  Card,
  CardContent,
  Skeleton,
  Tooltip,
  Fade,
  Chip,
  CircularProgress,
  TablePagination,
  Avatar,
  TableSortLabel,
  AlertColor,
  DialogActions,
} from '@mui/material';
import { 
  Add as AddIcon, 
  UploadFile as UploadFileIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  People as PeopleIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useUsersQuery } from '../../shared/hooks/useUsers';
import { User, SortConfig, AlertState, UserRole } from '../../shared/types';
import dataService from '../../shared/services/dataService';

const UsersList: React.FC = () => {
  const navigate = useNavigate();
  
  // State management with proper typing
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const [showImportModal, setShowImportModal] = useState<boolean>(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importing, setImporting] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: null, direction: 'asc' });
  const [alert, setAlert] = useState<AlertState>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  // Pagination state
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);

  // Use React Query for users
  const {
    data: usersData,
    isLoading,
    error: queryError,
    refetch
  } = useUsersQuery({ skip: page * rowsPerPage, limit: rowsPerPage });

  const users = Array.isArray(usersData) ? usersData : (usersData as any)?.users || [];
  const totalUsers = Array.isArray(usersData) ? usersData.length : (usersData as any)?.total || 0;

  // Show error from query
  React.useEffect(() => {
    if (queryError) {
      showAlert(queryError.message || 'Failed to fetch users', 'error');
    }
    // eslint-disable-next-line
  }, [queryError]);

  // Helper functions
  const showAlert = (message: string, severity: AlertColor = 'success'): void => {
    setAlert({ open: true, message, severity });
  };

  const handleCloseAlert = (): void => {
    setAlert(prev => ({ ...prev, open: false }));
  };

  // Sort and filter functionality
  const requestSort = (key: keyof User): void => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortedAndFilteredUsers = (): User[] => {
    let filteredUsers = [...users];
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filteredUsers = filteredUsers.filter(user => 
        user.employee_id?.toLowerCase().includes(searchLower) ||
        user.name?.toLowerCase().includes(searchLower) ||
        user.email?.toLowerCase().includes(searchLower) ||
        user.personal_details?.gender?.toLowerCase().includes(searchLower) ||
        user.role?.toLowerCase().includes(searchLower) ||
        user.personal_details?.mobile?.includes(searchTerm)
      );
    }

    // Apply sorting
    if (sortConfig.key) {
      filteredUsers.sort((a, b) => {
        let aValue: any = a[sortConfig.key!];
        let bValue: any = b[sortConfig.key!];

        // Special handling for dates
        if (sortConfig.key === 'date_of_birth' || sortConfig.key === 'date_of_joining') {
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
  const handleImport = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!importFile) {
      showAlert('Please select a file to upload', 'warning');
      return;
    }

    setImporting(true);
    
    try {
      await dataService.importUsers(importFile);
      showAlert('Users imported successfully', 'success');
      setShowImportModal(false);
      setImportFile(null);
      refetch();
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      showAlert(backendMessage || 'Failed to import users', 'error');
    } finally {
      setImporting(false);
    }
  };

  const handleDownloadTemplate = async (): Promise<void> => {
    try {
      const blob = await dataService.downloadUserTemplate();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'users_template.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      showAlert('Template downloaded successfully', 'success');
    } catch (error: any) {
      const backendMessage = error?.response?.data?.detail;
      showAlert(backendMessage || 'Failed to download template', 'error');
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handlePageChange = (_event: unknown, newPage: number): void => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = (): void => {
    setRefreshing(true);
    refetch().finally(() => setRefreshing(false));
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0] || null;
    setImportFile(file);
  };

  // Render helpers
  const renderTableSkeleton = (): React.ReactElement[] => (
    Array.from({ length: rowsPerPage }).map((_, index) => (
      <TableRow key={`skeleton-${index}`}>
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

  const renderEmptyState = (): React.ReactElement => (
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

  const getRoleBadgeColor = (role: UserRole): 'error' | 'warning' | 'info' | 'success' | 'default' => {
    switch (role?.toLowerCase()) {
      case 'admin': return 'error';
      case 'manager': return 'warning';
      case 'hr': return 'info';
      case 'user': return 'success';
      default: return 'default';
    }
  };

  const formatGender = (gender: string | undefined): string => {
    if (!gender) return 'N/A';
    switch (gender.toLowerCase()) {
      case 'male': return 'Male';
      case 'female': return 'Female';
      case 'other': return 'Other';
      case 'prefer_not_to_say': return 'Prefer not to say';
      default: return gender;
    }
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getInitials = (name: string): string => {
    if (!name) return 'U';
    return name.split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const filteredUsers = getSortedAndFilteredUsers();

  return (
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Manage user accounts and permissions
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
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
              >
                IMPORT
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/users/add')}
              >
                ADD USER
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Search and Controls */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <TextField
            sx={{ minWidth: 300, flexGrow: 1, maxWidth: 500 }}
            label="Search users"
            variant="outlined"
            size="small"
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {isLoading ? 'Loading...' : `${filteredUsers.length} user${filteredUsers.length !== 1 ? 's' : ''}`}
            </Typography>
            {refreshing && <CircularProgress size={16} />}
          </Box>
        </Box>
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
                    active={sortConfig.key === 'employee_id'}
                    direction={sortConfig.direction}
                    onClick={() => requestSort('employee_id')}
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
                    active={sortConfig.key === 'date_of_joining'}
                    direction={sortConfig.direction}
                    onClick={() => requestSort('date_of_joining')}
                    sx={{ color: 'inherit', '&:hover': { color: 'inherit' } }}
                  >
                    Joining Date
                  </TableSortLabel>
                </TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                renderTableSkeleton()
              ) : filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <Fade in key={user.employee_id} timeout={300}>
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
                          {user.employee_id}
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
                          {formatGender(user.gender)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {user.mobile}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {user.date_of_joining ? formatDate(user.date_of_joining) : 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => navigate(`/users/emp/${user.employee_id}`)}
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => navigate(`/users/emp/${user.employee_id}/edit`)}
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
        <DialogTitle>Import Users</DialogTitle>
        <form onSubmit={handleImport}>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Upload a CSV file to import multiple users at once.
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
              <Button
                variant="outlined"
                onClick={handleDownloadTemplate}
                startIcon={<DownloadIcon />}
              >
                Download Template
              </Button>
            </Box>

            <Box sx={{ mt: 3 }}>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                style={{ display: 'none' }}
                id="csv-upload"
              />
              <label htmlFor="csv-upload">
                <Button
                  variant="outlined"
                  component="span"
                  fullWidth
                  startIcon={<UploadFileIcon />}
                  sx={{ py: 2 }}
                >
                  {importFile ? importFile.name : 'Choose CSV File'}
                </Button>
              </label>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowImportModal(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={!importFile || importing}
              startIcon={importing ? <CircularProgress size={20} /> : <UploadFileIcon />}
            >
              {importing ? 'Importing...' : 'Import'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Alert */}
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
  );
};

export default UsersList; 