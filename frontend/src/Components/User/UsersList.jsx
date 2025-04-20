import React, { useState, useEffect } from 'react';
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
  Pagination,
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
  RadioGroup
} from '@mui/material';
import { 
  Add as AddIcon, 
  UploadFile as UploadFileIcon,
  Search as SearchIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon
} from '@mui/icons-material';
import axios from '../../utils/axios';
import { useNavigate } from 'react-router-dom';
import PageLayout from '../../layout/PageLayout';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ProtectedRoute from '../Common/ProtectedRoute';
import { Spinner } from 'react-bootstrap';
import { BsPlusCircle, BsFileEarmarkExcel, BsChevronLeft, BsChevronRight, BsSearch, BsCaretUpFill, BsCaretDownFill } from 'react-icons/bs';

function UsersList() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateUserModal, setShowCreateUserModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, [currentPage, pageSize]);

  // Sort function
  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Sort and filter users
  const getSortedAndFilteredUsers = () => {
    let filteredUsers = [...users];
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filteredUsers = filteredUsers.filter(user => 
        user.empId.toLowerCase().includes(searchLower) ||
        user.name.toLowerCase().includes(searchLower) ||
        user.email.toLowerCase().includes(searchLower) ||
        user.gender.toLowerCase().includes(searchLower) ||
        user.role.toLowerCase().includes(searchLower) ||
        user.mobile.includes(searchTerm)
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

  // Get sort icon
  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return null;
    }
    return sortConfig.direction === 'asc' ? <BsCaretUpFill /> : <BsCaretDownFill />;
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`/users?skip=${(currentPage - 1) * pageSize}&limit=${pageSize}`);
      setUsers(response.data.users);
      setTotalUsers(response.data.total);
    } catch (err) {
      setError(err.message || 'An error occurred while fetching users.');
      setAlert({
        open: true,
        message: err.message || 'Failed to fetch users',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    const userData = {
      empId: e.target.empId.value,
      name: e.target.name.value,
      email: e.target.email.value,
      gender: e.target.gender.value,
      dob: e.target.dob.value,
      doj: e.target.doj.value,
      mobile: e.target.mobile.value,
      managerId: e.target.managerId.value,
      password: e.target.password.value,
      role: e.target.role.value,
    };

    try {
      await axios.post('/users/create', userData);
      setAlert({
        open: true,
        message: 'User created successfully',
        severity: 'success'
      });
      setShowCreateUserModal(false);
      fetchUsers();
    } catch (error) {
      setAlert({
        open: true,
        message: error.response?.data?.detail || 'Failed to create user',
        severity: 'error'
      });
    }
  };

  const handleImport = async (e) => {
    e.preventDefault();
    if (!importFile) {
      setAlert({
        open: true,
        message: 'Please select a file to upload',
        severity: 'warning'
      });
      return;
    }

    setImporting(true);
    const formData = new FormData();
    formData.append('file', importFile);

    try {
      await axios.post('/users/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAlert({
        open: true,
        message: 'Users imported successfully',
        severity: 'success'
      });
      setShowImportModal(false);
      setImportFile(null);
      fetchUsers();
    } catch (error) {
      setAlert({
        open: true,
        message: error.response?.data?.detail || 'Failed to import users',
        severity: 'error'
      });
    } finally {
      setImporting(false);
    }
  };

  const handleCloseAlert = () => {
    setAlert({ ...alert, open: false });
  };

  // Calculate total pages
  const totalPages = Math.ceil(totalUsers / pageSize);

  // Generate page numbers
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <Pagination.Item
          key={i}
          active={i === currentPage}
          onClick={() => setCurrentPage(i)}
        >
          {i}
        </Pagination.Item>
      );
    }

    return pages;
  };

  return (
    <PageLayout title="Users Management">
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Users List</Typography>
          <Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowCreateUserModal(true)}
              sx={{ mr: 2 }}
            >
              Add User
            </Button>
            <Button
              variant="outlined"
              startIcon={<UploadFileIcon />}
              onClick={() => setShowImportModal(true)}
            >
              Import Users
            </Button>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <TextField
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ width: '300px' }}
          />
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Show</InputLabel>
            <Select
              value={pageSize}
              label="Show"
              onChange={(e) => {
                setPageSize(e.target.value);
                setCurrentPage(1);
              }}
            >
              {[5, 10, 20, 50, 100].map((size) => (
                <MenuItem key={size} value={size}>
                  {size}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ 
                '& .MuiTableCell-head': { 
                  backgroundColor: 'primary.main',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.875rem',
                  padding: '12px 16px'
                }
              }}>
                <TableCell>Employee ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Gender</TableCell>
                <TableCell>Mobile</TableCell>
                <TableCell>Date of Birth</TableCell>
                <TableCell>Date of Joining</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">Loading...</TableCell>
                </TableRow>
              ) : users.length > 0 ? (
                getSortedAndFilteredUsers().map((user) => (
                  <TableRow 
                    key={user.empId}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{user.empId}</TableCell>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          backgroundColor: getRoleBadgeColor(user.role),
                          color: 'white',
                          fontSize: '0.75rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {user.role}
                      </Box>
                    </TableCell>
                    <TableCell>{user.gender}</TableCell>
                    <TableCell>{user.mobile}</TableCell>
                    <TableCell>{new Date(user.dob).toLocaleDateString()}</TableCell>
                    <TableCell>{new Date(user.doj).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} align="center">No users found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={Math.ceil(totalUsers / pageSize)}
            page={currentPage}
            onChange={(event, value) => setCurrentPage(value)}
            color="primary"
          />
        </Box>

        {/* Create User Dialog */}
        <Dialog open={showCreateUserModal} onClose={() => setShowCreateUserModal(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create New User</DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleCreateUser} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Employee ID"
                name="empId"
                required
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Name"
                name="name"
                required
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                required
                sx={{ mb: 2 }}
              />
              <FormControl component="fieldset" sx={{ mb: 2 }}>
                <RadioGroup row name="gender">
                  <FormControlLabel value="male" control={<Radio />} label="Male" />
                  <FormControlLabel value="female" control={<Radio />} label="Female" />
                  <FormControlLabel value="other" control={<Radio />} label="Other" />
                </RadioGroup>
              </FormControl>
              <TextField
                fullWidth
                label="Date of Birth"
                name="dob"
                type="date"
                required
                sx={{ mb: 2 }}
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                fullWidth
                label="Date of Joining"
                name="doj"
                type="date"
                required
                sx={{ mb: 2 }}
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                fullWidth
                label="Mobile"
                name="mobile"
                required
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Manager ID"
                name="managerId"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Password"
                name="password"
                type="password"
                required
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Role</InputLabel>
                <Select name="role" label="Role" required>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="superadmin">Super Admin</MenuItem>
                </Select>
              </FormControl>
              <DialogActions>
                <Button onClick={() => setShowCreateUserModal(false)}>Cancel</Button>
                <Button type="submit" variant="contained">Create</Button>
              </DialogActions>
            </Box>
          </DialogContent>
        </Dialog>

        {/* Import Users Dialog */}
        <Dialog open={showImportModal} onClose={() => setShowImportModal(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Import Users</DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleImport} sx={{ mt: 2 }}>
              <input
                type="file"
                accept=".xlsx"
                onChange={(e) => setImportFile(e.target.files[0])}
                style={{ marginBottom: '16px' }}
              />
              <DialogActions>
                <Button onClick={() => setShowImportModal(false)}>Cancel</Button>
                <Button type="submit" variant="contained" disabled={!importFile || importing}>
                  {importing ? 'Importing...' : 'Import'}
                </Button>
              </DialogActions>
            </Box>
          </DialogContent>
        </Dialog>

        <Snackbar 
          open={alert.open} 
          autoHideDuration={6000} 
          onClose={handleCloseAlert}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleCloseAlert} 
            severity={alert.severity}
            sx={{ width: '100%' }}
          >
            {alert.message}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
}

// Helper function to get badge color based on role
const getRoleBadgeColor = (role) => {
  switch (role?.toLowerCase()) {
    case 'admin':
      return 'primary.main';
    case 'superadmin':
      return 'error.main';
    case 'manager':
      return 'info.main';
    case 'user':
      return 'success.main';
    default:
      return 'grey.500';
  }
};

export default UsersList;