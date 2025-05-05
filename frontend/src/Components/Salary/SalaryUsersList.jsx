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
  FormLabel,
  Radio,
  RadioGroup,
  Grid,
  Input,
  
  Tooltip
} from '@mui/material';
import { 
  Add as AddIcon, 
  UploadFile as UploadFileIcon,
  Search as SearchIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import api from '../../utils/apiUtils';
import { useNavigate } from 'react-router-dom';
import PageLayout from '../../layout/PageLayout';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {BsCaretUpFill, BsCaretDownFill } from 'react-icons/bs';

function SalaryUsersList() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [userComponents, setUserComponents] = useState([]);
  const [components, setComponents] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedComponents, setSelectedComponents] = useState([{ componentId: '', minValue: '', maxValue: '' }]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showViewUserModal, setShowViewUserModal] = useState(false);
  const [showAssignComponentsModal, setShowAssignComponentsModal] = useState(false);
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
        user.emp_id.toLowerCase().includes(searchLower) ||
        user.name.toLowerCase().includes(searchLower) ||
        user.designation.toLowerCase().includes(searchLower) ||
        user.location.toLowerCase().includes(searchLower)
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
      const response = await api.get('/users', {
        params: {
          skip: (currentPage - 1) * pageSize,
          limit: pageSize
        }
      });
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
    
    try {
      await api.upload('/salary-components/assignments/import/with-file', importFile);
      setAlert({
        open: true,
        message: 'Salary components imported successfully',
        severity: 'success'
      });
      setShowImportModal(false);
      setImportFile(null);
      fetchUsers();
    } catch (error) {
      setAlert({
        open: true,
        message: error.response?.data?.detail || 'Failed to import salary components',
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

  const handleViewComponents = (empId) => {
    setShowViewUserModal(true);
    setSelectedUser(empId);
    fetchUserComponents(empId); 
  };

  const handleEditComponents = (empId) => {
    setShowAssignComponentsModal(true);
    setSelectedUser(empId);
    fetchComponents();
    fetchUserComponents(empId);
  };

  const handleCloseViewModal = () => {
    setShowViewUserModal(false);
    setUserComponents([]);
  };

  const handleCloseAssignModal = () => {
    setShowAssignComponentsModal(false);
    setSelectedComponents([{ componentId: '', minValue: '', maxValue: '' }]);
  };

  const fetchComponents = async () => {
    try {
      const response = await api.get('/salary-components');
      setComponents(response.data);
    } catch (error) {
      console.error('Error fetching components:', error); 
      toast.error('Failed to fetch components');
    }
  };

  const fetchUserComponents = async (empId) => {
    try {
      const response = await api.get(`/salary-components/assignments/${empId}`);
      setUserComponents(response.data);
      console.log(response.data);
    } catch (error) {
      console.error('Error fetching user components:', error);
      toast.error('Failed to fetch user components');
    }
  };

  const handleComponentChange = (index, field, value) => {
    const updated = [...selectedComponents];
    updated[index] = { ...updated[index], [field]: value };
    setSelectedComponents(updated);
  };

  const addComponentField = () => {
    setSelectedComponents([...selectedComponents, { componentId: '', minValue: '', maxValue: '' }]);
  };

  const availableComponents = (currentIndex) => {
    const used = selectedComponents.filter((_, i) => i !== currentIndex);
    return components.filter(c => !used.includes(c.sc_id));
  };

  const assignComponents = async () => {
    try {
      const componentsData = selectedComponents
        .filter(comp => comp.componentId) // Filter out any empty component IDs
        .map(comp => ({
          sc_id: comp.componentId,
          max_value: comp.maxValue ? parseFloat(comp.maxValue) : 0
        }));

      const response = await api.post(`/salary-components/assignments/${selectedUser}`, componentsData);
      
      setAlert({
        open: true,
        message: 'Components assigned successfully',
        severity: 'success'
      });
      
      setShowAssignComponentsModal(false);
      setSelectedComponents([{ componentId: '', maxValue: '' }]);
      // Refresh the user components list
      fetchUserComponents(selectedUser);
    } catch (error) { 
      const errorMessage = error.response?.data?.detail || 
                          (typeof error.response?.data === 'object' ? JSON.stringify(error.response?.data) : 'Failed to assign components');
      
      setAlert({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    }
  };

  // Update useEffect to prefill values when userComponents change
  useEffect(() => {
    if (showAssignComponentsModal && userComponents.length > 0) {
      const prefilledComponents = userComponents.map(comp => ({
        componentId: comp.sc_id,
        maxValue: comp.max_value.toString()
      }));
      setSelectedComponents(prefilledComponents);
    }
  }, [userComponents, showAssignComponentsModal]);

  const handleDeleteComponent = (index) => {
    const updatedComponents = [...selectedComponents];
    updatedComponents.splice(index, 1);
    // If no components left, add an empty one
    if (updatedComponents.length === 0) {
      updatedComponents.push({ componentId: '', maxValue: '' });
    }
    setSelectedComponents(updatedComponents);
  };

  return (
    <PageLayout title="User's Salary Components Management">
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Users List</Typography>
          <Box>
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
                <TableCell>Designation</TableCell>  
                <TableCell>Location</TableCell>
                <TableCell>Actions</TableCell>
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
                    key={user.emp_id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{user.emp_id}</TableCell>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.designation}</TableCell>
                    <TableCell>{user.location}</TableCell>
                    <TableCell>
                      <Tooltip title="View Components">
                        <IconButton
                          color="primary"
                          size="small"
                          onClick={() => handleViewComponents(user.emp_id)}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Components">
                        <IconButton
                          color="primary"
                          size="small"
                          onClick={() => handleEditComponents(user.emp_id)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
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

        {/* View User Components Dialog */}
        <Dialog 
          open={showViewUserModal} 
          onClose={handleCloseViewModal} 
          maxWidth="md" 
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">User Salary Components</Typography>
              <Button onClick={handleCloseViewModal}>Close</Button>
            </Box>
          </DialogTitle>
          <DialogContent>
            {userComponents.length > 0 ? (
              <>
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Component ID</TableCell>
                        <TableCell>Component Name</TableCell>
                        <TableCell>Component Type</TableCell>
                        <TableCell>Max Value</TableCell>
                        <TableCell>Component Description</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {userComponents.map((component) => (
                        <TableRow key={component.sc_id}>
                          <TableCell>{component.sc_id}</TableCell>
                          <TableCell>{component.name}</TableCell>
                          <TableCell>{component.type}</TableCell>
                          <TableCell>{component.max_value}</TableCell>
                          <TableCell>{component.description}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={() => {
                      handleCloseViewModal();
                      handleEditComponents(selectedUser);
                    }}
                  >
                    Edit Components
                  </Button>
                </Box>
              </>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  No Components Assigned
                </Typography>
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={() => {
                    handleCloseViewModal();
                    handleEditComponents(selectedUser);
                  }}
                >
                  Assign Components
                </Button>
              </Box>
            )}
          </DialogContent>
        </Dialog>
      
        {/* Assign Components Dialog */}  
        <Dialog 
          open={showAssignComponentsModal} 
          onClose={handleCloseAssignModal} 
          maxWidth="md" 
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">
                {userComponents.length > 0 ? 'Edit Components' : 'Assign Components'} for {selectedUser}
              </Typography>
              <Button onClick={handleCloseAssignModal}>Close</Button>
            </Box>
          </DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="normal">
              <FormLabel>Select Components and Set Values</FormLabel>
              {selectedComponents.map((selected, index) => (
                <Box key={index} mb={2} sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Select
                    value={selected.componentId}
                    onChange={(e) => handleComponentChange(index, 'componentId', e.target.value)}
                    displayEmpty
                    sx={{ flex: 2 }}
                  >
                    <MenuItem disabled value="">
                      Select component
                    </MenuItem>
                    {availableComponents(index).map((component) => (
                      <MenuItem key={component.sc_id} value={component.sc_id}>
                        {component.name}
                      </MenuItem>
                    ))}
                  </Select>
                  <TextField
                    label="Max Value"
                    type="number"
                    value={selected.maxValue}
                    onChange={(e) => handleComponentChange(index, 'maxValue', e.target.value)}
                    sx={{ flex: 1 }}
                  />
                  <IconButton
                    onClick={() => handleDeleteComponent(index)}
                    color="error"
                    sx={{ visibility: selectedComponents.length > 1 ? 'visible' : 'hidden' }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={addComponentField}
                  disabled={selectedComponents.length >= components.length}
                  startIcon={<AddIcon />}
                >
                  Add Another Component
                </Button>
                <Button
                  variant="contained"
                  onClick={assignComponents}
                  disabled={selectedComponents.some(comp => !comp.componentId || !comp.maxValue)}
                >
                  {userComponents.length > 0 ? 'Update Components' : 'Assign Components'}
                </Button>
              </Box>
            </FormControl>
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
            {typeof alert.message === 'string' ? alert.message : JSON.stringify(alert.message)}
          </Alert>
        </Snackbar>
      </Box>
    </PageLayout>
  );
};

export default SalaryUsersList;