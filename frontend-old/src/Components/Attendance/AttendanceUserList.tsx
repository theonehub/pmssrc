import React, { useState, useEffect, useCallback } from 'react';
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
  Pagination as MuiPagination,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import {
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Search as SearchIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import AttendanceCalendar from './AttendanceCalendar';
import { apiGet } from '../../utils/apiUtils';
import { 
  User, 
  UsersListResponse, 
  LWPData, 
  AttendanceUserListSortConfig 
} from '../../types';
import './AttendanceCalendar.css';

const AttendanceUserList: React.FC = () => {
  
  // State management with proper typing
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortConfig, setSortConfig] = useState<AttendanceUserListSortConfig>({ 
    key: null, 
    direction: 'asc' 
  });
  const [selectedEmpId, setSelectedEmpId] = useState<string | null>(null);
  const [showCalendar, setShowCalendar] = useState<boolean>(false);
  const [lwpData, setLwpData] = useState<LWPData>({});

  // Pagination state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [totalUsers, setTotalUsers] = useState<number>(0);

  const fetchUsers = useCallback(async (): Promise<void> => {
    try {
      const response = await apiGet('/api/v2/users', {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize
      });
      
      const data = response.data as UsersListResponse;
      setUsers(data.users || []);
      setTotalUsers(data.total || 0);
      setError(null);
    } catch (err: any) {
      const errorMessage = err.message || 'An error occurred while fetching users.';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize]);

  const fetchLWPData = useCallback(async (): Promise<void> => {
    try {
      const currentDate = new Date();
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();

      const lwpPromises = users.map(user =>
        apiGet(`/api/v2/employee-leave/lwp/${user.employee_id}/${month}/${year}`)
      );

      const lwpResponses = await Promise.all(lwpPromises);
      const lwpMap: LWPData = {};
      
      users.forEach((user, index) => {
        lwpMap[user.employee_id || ''] = lwpResponses[index]?.data?.lwp_days || 0;
      });

      setLwpData(lwpMap);
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching LWP data:', error);
      }
      toast.error('Failed to fetch LWP data');
    }
  }, [users]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  useEffect(() => {
    if (users.length > 0) {
      fetchLWPData();
    }
  }, [fetchLWPData, users.length]);

  // Sort function
  const requestSort = (key: keyof User | 'lwp'): void => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Sort and filter users
  const getSortedAndFilteredUsers = (): User[] => {
    let filteredUsers = [...users];
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filteredUsers = filteredUsers.filter(user => 
        user.employee_id?.toLowerCase().includes(searchLower) ||
        user.name.toLowerCase().includes(searchLower) ||
        user.email.toLowerCase().includes(searchLower) ||
        user.mobile.includes(searchTerm)
      );
    }

    // Apply sorting
    if (sortConfig.key) {
      filteredUsers.sort((a, b) => {
        let aValue: any;
        let bValue: any;

        if (sortConfig.key === 'lwp') {
          aValue = lwpData[a.employee_id || ''] || 0;
          bValue = lwpData[b.employee_id || ''] || 0;
        } else {
          aValue = a[sortConfig.key!];
          bValue = b[sortConfig.key!];
        }

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

  // Get sort icon
  const getSortIcon = (columnKey: keyof User | 'lwp'): React.ReactElement | null => {
    if (sortConfig.key !== columnKey) {
      return null;
    }
    return sortConfig.direction === 'asc' ? 
      <ArrowUpwardIcon fontSize="small" /> : 
      <ArrowDownwardIcon fontSize="small" />;
  };

  const handleViewAttendance = (empId: string): void => {
    setSelectedEmpId(empId);
    setShowCalendar(true);
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(e.target.value);
  };

  const handlePageSizeChange = (e: SelectChangeEvent<number>): void => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  // Calculate total pages
  const totalPages = Math.ceil(totalUsers / pageSize);

  // Handle page change
  const handlePageChange = (_event: React.ChangeEvent<unknown>, newPage: number): void => {
    setCurrentPage(newPage);
  };

  const handleCloseCalendar = (): void => {
    setShowCalendar(false);
    setSelectedEmpId(null);
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
                  onChange={handlePageSizeChange}
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
                      <TableCell onClick={() => requestSort('employee_id')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          Employee ID {getSortIcon('employee_id')}
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
                      <TableCell onClick={() => requestSort('date_of_joining')} sx={{ cursor: 'pointer' }}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          Date of Joining {getSortIcon('date_of_joining')}
                        </Typography>
                      </TableCell>
                      <TableCell onClick={() => requestSort('mobile')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          Mobile {getSortIcon('mobile')}
                        </Box>
                      </TableCell>
                      <TableCell onClick={() => requestSort('lwp')} sx={{ cursor: 'pointer' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          LWP (Current Month) {getSortIcon('lwp')}
                          <Tooltip 
                            title="Leave Without Pay - Days absent without approved leave" 
                            placement="top"
                            arrow
                          >
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
                        key={user.employee_id}
                        sx={{ 
                          '&:hover': { 
                            backgroundColor: 'action.hover',
                            cursor: 'pointer'
                          }
                        }}
                      >
                        <TableCell>{user.employee_id}</TableCell>
                        <TableCell>{user.name}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>{user.date_of_joining}</TableCell>
                        <TableCell>{user.mobile}</TableCell>
                        <TableCell>
                          <Box sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            color: (lwpData[user.employee_id || ''] || 0) > 0 ? 'error.main' : 'success.main'
                          }}>
                            {lwpData[user.employee_id || ''] || 0}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="contained" 
                            color="primary"
                            size="small"
                            onClick={() => handleViewAttendance(user.employee_id || '')}
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
              employee_id={selectedEmpId}
              show={showCalendar}
              onHide={handleCloseCalendar}
            />
          )}
        </Box>
      </Container>
    </PageLayout>
  );
};

export default AttendanceUserList; 