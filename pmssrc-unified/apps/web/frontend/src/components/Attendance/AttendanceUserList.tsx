import React, { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {
  Box,
  Button,
  TextField,
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
  FormControl,
  Select,
  MenuItem,
  Pagination as MuiPagination,
  Tooltip,
  SelectChangeEvent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Search as SearchIcon,
  Info as InfoIcon,
  Visibility,
  PlaylistAddCheck
} from '@mui/icons-material';
import AttendanceCalendar from './AttendanceCalendar';
import { useUsersQuery } from '../../shared/hooks/useUsers';
import { User } from '../../shared/api/userApi';
import { 
  AttendanceUserListSortConfig,
  LWPData,
  SortKey
} from '../../shared/types';
import './AttendanceCalendar.css';
import { Card, CardContent } from '@mui/material';
import apiClient from '../../shared/utils/apiClient';

interface BulkForm {
  startDate: string;
  startTime: string;
  endDate: string;
  endTime: string;
}

// Utility to convert YYYY-MM-DD to DD-MM-YYYY
function toDDMMYYYY(dateStr: string): string {
  if (!dateStr) return '';
  const [yyyy, mm, dd] = dateStr.split('-');
  return `${dd}-${mm}-${yyyy}`;
}

const AttendanceUserList: React.FC = () => {
  
  // State management with proper typing
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortConfig, setSortConfig] = useState<AttendanceUserListSortConfig>({ 
    key: 'name', 
    direction: 'asc' 
  });
  const [selectedEmpId, setSelectedEmpId] = useState<string | null>(null);
  const [showCalendar, setShowCalendar] = useState<boolean>(false);
  const [lwpData, setLwpData] = useState<LWPData>({});
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [bulkDialogEmployeeId, setBulkDialogEmployeeId] = useState<string | null>(null);
  const [bulkForm, setBulkForm] = useState<BulkForm>({
    startDate: '',
    startTime: '',
    endDate: '',
    endTime: '',
  });
  const [bulkFormErrors, setBulkFormErrors] = useState<Record<string, string>>({});
  const [bulkDialogLoading, setBulkDialogLoading] = useState(false);

  // Pagination state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  // Use React Query for users
  const { data: usersData, isLoading, error: usersError } = useUsersQuery({ skip: (currentPage - 1) * pageSize, limit: pageSize });
  const users = React.useMemo(() => 
    Array.isArray(usersData) ? usersData : (usersData as any)?.users || [], 
    [usersData]
  );
  const totalUsers = React.useMemo(() => 
    Array.isArray(usersData) ? usersData.length : (usersData as any)?.total || 0, 
    [usersData]
  );

  const fetchLWPData = React.useCallback(async () => {
    try {
      const currentDate = new Date();
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();

      // Use relative path to ensure correct backend port is used
      const lwpPromises = users.map((user: User) =>
        fetch(`/v2/employee-leave/lwp/${user.employee_id}/${month}/${year}`)
          .then(res => res.json())
      );

      const lwpResponses = await Promise.all(lwpPromises);
      const lwpMap: LWPData = {};
      
      users.forEach((user: User, index: number) => {
        lwpMap[user.employee_id || ''] = lwpResponses[index]?.lwp_days || 0;
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

  React.useEffect(() => {
    if (users.length > 0) {
      fetchLWPData();
    }
  }, [fetchLWPData, users]);

  // Sort functionality
  const requestSort = (key: SortKey): void => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Get sort icon
  const getSortIcon = (columnKey: SortKey): React.ReactElement | null => {
    if (sortConfig.key !== columnKey) {
      return null;
    }
    return sortConfig.direction === 'asc' ? 
      <ArrowUpwardIcon fontSize="small" /> : 
      <ArrowDownwardIcon fontSize="small" />;
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
        user.personal_details?.mobile?.includes(searchTerm)
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
        } else if (sortConfig.key === 'personal_details.mobile') {
          aValue = a.personal_details?.mobile || '';
          bValue = b.personal_details?.mobile || '';
        } else {
          aValue = a[sortConfig.key];
          bValue = b[sortConfig.key];
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

  const handleViewAttendance = (empId: string): void => {
    setSelectedEmpId(empId);
    setShowCalendar(true);
  };

  const handleBulkAttendance = (employeeId: string) => {
    setBulkDialogEmployeeId(employeeId);
    setBulkDialogOpen(true);
    setBulkForm({ startDate: '', startTime: '', endDate: '', endTime: '' });
    setBulkFormErrors({});
  };

  const handleBulkDialogClose = () => {
    setBulkDialogOpen(false);
    setBulkDialogEmployeeId(null);
    setBulkForm({ startDate: '', startTime: '', endDate: '', endTime: '' });
    setBulkFormErrors({});
  };

  const handleBulkFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setBulkForm((prev) => ({ ...prev, [name]: value }));
    setBulkFormErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const validateBulkForm = () => {
    const errors: Record<string, string> = {};
    if (!bulkForm.startDate) errors.startDate = 'Start date required';
    if (!bulkForm.startTime) errors.startTime = 'Start time required';
    if (!bulkForm.endDate) errors.endDate = 'End date required';
    if (!bulkForm.endTime) errors.endTime = 'End time required';
    setBulkFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleBulkDialogSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateBulkForm()) return;
    if (!bulkDialogEmployeeId) return;
    setBulkDialogLoading(true);
    try {
      const startDateFormatted = toDDMMYYYY(bulkForm.startDate);
      const endDateFormatted = toDDMMYYYY(bulkForm.endDate);
      const url = `/v2/attendance/bulk/checkin/checkout/${bulkDialogEmployeeId}/start/${startDateFormatted}/${bulkForm.startTime}/end/${endDateFormatted}/${bulkForm.endTime}`;
      await apiClient.post(url);
      toast.success('Bulk attendance entry successful');
      setBulkDialogOpen(false);
    } catch (error: any) {
      toast.error(
        error?.response?.data?.detail ||
        error?.message ||
        'Bulk attendance entry failed'
      );
    } finally {
      setBulkDialogLoading(false);
    }
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
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h4" color="primary" gutterBottom>
                Users Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage user attendance and LWP tracking
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Search and Filters */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2">
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
              <Typography variant="body2">
                entries
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              Showing {Math.min((currentPage - 1) * pageSize + 1, totalUsers)} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers} entries
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Error Alert */}
      {usersError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {usersError.message || 'Failed to load users'}
        </Alert>
      )}

      {/* Users Table */}
      <Paper elevation={1}>
        <TableContainer>
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
                <TableCell>
                  <Button
                    color="inherit"
                    onClick={() => requestSort('employee_id')}
                    endIcon={getSortIcon('employee_id')}
                    sx={{ color: 'white', textTransform: 'none' }}
                  >
                    Employee ID
                  </Button>
                </TableCell>
                <TableCell>
                  <Button
                    color="inherit"
                    onClick={() => requestSort('name')}
                    endIcon={getSortIcon('name')}
                    sx={{ color: 'white', textTransform: 'none' }}
                  >
                    Name
                  </Button>
                </TableCell>
                <TableCell>
                  <Button
                    color="inherit"
                    onClick={() => requestSort('email')}
                    endIcon={getSortIcon('email')}
                    sx={{ color: 'white', textTransform: 'none' }}
                  >
                    Email
                  </Button>
                </TableCell>
                <TableCell>
                  <Button
                    color="inherit"
                    onClick={() => requestSort('personal_details.mobile')}
                    endIcon={getSortIcon('personal_details.mobile')}
                    sx={{ color: 'white', textTransform: 'none' }}
                  >
                    Mobile
                  </Button>
                </TableCell>
                <TableCell>
                  <Button
                    color="inherit"
                    onClick={() => requestSort('department')}
                    endIcon={getSortIcon('department')}
                    sx={{ color: 'white', textTransform: 'none' }}
                  >
                    Department
                  </Button>
                </TableCell>
                <TableCell>
                  <Button
                    color="inherit"
                    onClick={() => requestSort('lwp')}
                    endIcon={getSortIcon('lwp')}
                    sx={{ color: 'white', textTransform: 'none' }}
                  >
                    LWP Days
                    <Tooltip title="Leave Without Pay days for current month" placement="top">
                      <InfoIcon sx={{ ml: 1, fontSize: '1rem' }} />
                    </Tooltip>
                  </Button>
                </TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                Array.from({ length: pageSize }).map((_, index) => (
                  <TableRow key={index}>
                    <TableCell><CircularProgress size={20} /></TableCell>
                    <TableCell><CircularProgress size={20} /></TableCell>
                    <TableCell><CircularProgress size={20} /></TableCell>
                    <TableCell><CircularProgress size={20} /></TableCell>
                    <TableCell><CircularProgress size={20} /></TableCell>
                    <TableCell><CircularProgress size={20} /></TableCell>
                    <TableCell><CircularProgress size={20} /></TableCell>
                  </TableRow>
                ))
              ) : getSortedAndFilteredUsers().length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      No users found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                getSortedAndFilteredUsers().map((user) => (
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
                    <TableCell>{user.personal_details?.mobile || 'N/A'}</TableCell>
                    <TableCell>{user.department || 'N/A'}</TableCell>
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        color={((lwpData[user.employee_id || ''] ?? 0) > 0) ? 'error' : 'text.primary'}
                        fontWeight={((lwpData[user.employee_id || ''] ?? 0) > 0) ? 'bold' : 'normal'}
                      >
                        {lwpData[user.employee_id || ''] ?? 0}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Attendance">
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleViewAttendance(user.employee_id || '')}
                          sx={{ mr: 1 }}
                        >
                          <Visibility />
                        </Button>
                      </Tooltip>
                      <Tooltip title="Bulk Attendance">
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleBulkAttendance(user.employee_id || '')}
                        >
                          <PlaylistAddCheck />
                        </Button>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3, pb: 2 }}>
          <MuiPagination
            count={totalPages}
            page={currentPage}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Box>
      </Paper>

      {/* Attendance Calendar Modal */}
      {showCalendar && selectedEmpId && (
        <AttendanceCalendar
          employee_id={selectedEmpId}
          show={showCalendar}
          onHide={handleCloseCalendar}
        />
      )}

      <Dialog open={bulkDialogOpen} onClose={handleBulkDialogClose} maxWidth="xs" fullWidth>
        <DialogTitle>Bulk Attendance Entry</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Start Date"
              name="startDate"
              type="date"
              value={bulkForm.startDate}
              onChange={handleBulkFormChange}
              InputLabelProps={{ shrink: true }}
              error={!!bulkFormErrors.startDate}
              helperText={bulkFormErrors.startDate}
              required
            />
            <TextField
              label="Start Time"
              name="startTime"
              type="time"
              value={bulkForm.startTime}
              onChange={handleBulkFormChange}
              InputLabelProps={{ shrink: true }}
              error={!!bulkFormErrors.startTime}
              helperText={bulkFormErrors.startTime}
              required
            />
            <TextField
              label="End Date"
              name="endDate"
              type="date"
              value={bulkForm.endDate}
              onChange={handleBulkFormChange}
              InputLabelProps={{ shrink: true }}
              error={!!bulkFormErrors.endDate}
              helperText={bulkFormErrors.endDate}
              required
            />
            <TextField
              label="End Time"
              name="endTime"
              type="time"
              value={bulkForm.endTime}
              onChange={handleBulkFormChange}
              InputLabelProps={{ shrink: true }}
              error={!!bulkFormErrors.endTime}
              helperText={bulkFormErrors.endTime}
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleBulkDialogClose}>Cancel</Button>
          <Button onClick={handleBulkDialogSubmit} variant="contained" disabled={bulkDialogLoading}>
            {bulkDialogLoading ? <CircularProgress size={22} /> : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AttendanceUserList; 