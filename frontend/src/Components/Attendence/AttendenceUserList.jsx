import React, { useState, useEffect } from 'react';
import axios from '../../utils/axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PageLayout from '../../layout/PageLayout';
import {
  Box,
  Button,
  Container,
  TextField,
  IconButton,
  InputAdornment,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination as MuiPagination,
  Tooltip
} from '@mui/material';
import {
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Search as SearchIcon,
  KeyboardArrowLeft as KeyboardArrowLeftIcon,
  KeyboardArrowRight as KeyboardArrowRightIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import AttendanceCalendar from './AttendanceCalendar';
import './AttendanceCalendar.css';

function AttendenceUserList() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [selectedEmpId, setSelectedEmpId] = useState(null);
  const [showCalendar, setShowCalendar] = useState(false);
  const [lwpData, setLwpData] = useState({});

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, [currentPage, pageSize]);

  useEffect(() => {
    if (users.length > 0) {
      fetchLWPData();
    }
  }, [users]);

  const fetchLWPData = async () => {
    try {
      const currentDate = new Date();
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();

      const lwpPromises = users.map(user =>
        axios.get(`/leaves/lwp/${user.empId}/${month}/${year}`)
      );

      const lwpResponses = await Promise.all(lwpPromises);
      const lwpMap = {};
      
      users.forEach((user, index) => {
        lwpMap[user.empId] = lwpResponses[index].data.lwp_days;
      });

      setLwpData(lwpMap);
    } catch (error) {
      console.error('Error fetching LWP data:', error);
      toast.error('Failed to fetch LWP data');
    }
  };

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
    return sortConfig.direction === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />;
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`/users?skip=${(currentPage - 1) * pageSize}&limit=${pageSize}`);
      setUsers(response.data.users);
      setTotalUsers(response.data.total);
    } catch (err) {
      setError(err.message || 'An error occurred while fetching users.');
      toast.error(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleViewAttendance = (empId) => {
    setSelectedEmpId(empId);
    setShowCalendar(true);
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Calculate total pages
  const totalPages = Math.ceil(totalUsers / pageSize);

  // Handle page change
  const handlePageChange = (event, newPage) => {
    setCurrentPage(newPage);
  };

  return (
    <PageLayout title="Users Management">
      <Container>
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" gutterBottom>
            Users List
          </Typography>

          {/* Search Box */}
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search users..."
              value={searchTerm}
              onChange={handleSearch}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {/* Page Size Selector */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                Show
              </Typography>
              <FormControl sx={{ minWidth: 80 }}>
                <Select
                  value={pageSize}
                  size="small"
                  onChange={(e) => {
                    setPageSize(Number(e.target.value));
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
              <Typography variant="body2" sx={{ ml: 2 }}>
                entries
              </Typography>
            </Box>
            <Typography variant="body2">
              Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers} entries
            </Typography>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : (
            <>
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
                      <TableCell onClick={() => requestSort('empId')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          Employee ID {getSortIcon('empId')}
                        </Box>
                      </TableCell>
                      <TableCell onClick={() => requestSort('name')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          Name {getSortIcon('name')}
                        </Box>
                      </TableCell>
                      <TableCell onClick={() => requestSort('email')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          Email {getSortIcon('email')}
                        </Box>
                      </TableCell>
                      <TableCell onClick={() => requestSort('doj')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          Date of Joining {getSortIcon('doj')}
                        </Box>
                      </TableCell>
                      <TableCell onClick={() => requestSort('mobile')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          Mobile {getSortIcon('mobile')}
                        </Box>
                      </TableCell>
                      <TableCell onClick={() => requestSort('lwp')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          LWP (Current Month) {getSortIcon('lwp')}
                          <Tooltip title="Leave Without Pay - Days absent without approved leave" arrow>
                            <IconButton size="small" sx={{ ml: 0.5, color: 'inherit' }}>
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                      <TableCell>
                        Action
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {getSortedAndFilteredUsers().map((user) => (
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
                        <TableCell>{user.doj}</TableCell>
                        <TableCell>{user.mobile}</TableCell>
                        <TableCell>
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            color: lwpData[user.empId] > 0 ? 'error.main' : 'success.main'
                          }}>
                            {lwpData[user.empId] || 0}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="contained" 
                            color="primary"
                            size="small"
                            onClick={() => handleViewAttendance(user.empId)}
                          >
                            View Attendance
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Pagination */}
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <MuiPagination 
                  count={totalPages}
                  page={currentPage}
                  onChange={handlePageChange}
                  color="primary"
                  showFirstButton
                  showLastButton
                />
              </Box>
            </>
          )}

          {/* Attendance Calendar Modal */}
          {selectedEmpId && (
            <AttendanceCalendar
              empId={selectedEmpId}
              show={showCalendar}
              onHide={() => setShowCalendar(false)}
            />
          )}
        </Box>
      </Container>
    </PageLayout>
  );
}

export default AttendenceUserList;