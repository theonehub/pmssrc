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
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Snackbar,
  Alert,
  CircularProgress,
  SelectChangeEvent,
  // Chip,
  // Grid,
  // Fab,
  // Divider
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useLeavesQuery } from '../../shared/hooks/useLeaves';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import PageLayout from '../../layout/PageLayout';
import { styled } from '@mui/material/styles';
import { LeaveRequest, LeaveBalanceData, AlertState } from '../../shared/types';
import { apiClient } from '../../shared/api';

// Add custom styled components
const StyledDatePicker = styled(DatePicker)`
  width: 100%;
  
  .react-datepicker-wrapper {
    width: 100%;
  }

  .react-datepicker-popper {
    z-index: 9999;
  }

  .react-datepicker {
    font-size: 1rem;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }

  .react-datepicker__header {
    background-color: #1976d2;
    color: white;
    border-radius: 8px 8px 0 0;
  }

  .react-datepicker__current-month {
    color: white;
    font-weight: 500;
  }

  .react-datepicker__day-name {
    color: white;
  }

  .react-datepicker__day--selected {
    background-color: #1976d2;
  }
`;

const LeaveManagement: React.FC = () => {
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalanceData>({});
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [leaveType, setLeaveType] = useState<string>('');
  const [reason, setReason] = useState<string>('');
  const [showModal, setShowModal] = useState<boolean>(false);
  const [editingLeave, setEditingLeave] = useState<LeaveRequest | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  // const [loading, setLoading] = useState<boolean>(false);
  const [alert, setAlert] = useState<AlertState>({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  // Use React Query for leaves
  const { data: leavesData, isLoading: isLeavesLoading, error: leavesError, refetch } = useLeavesQuery();
  const leaves = Array.isArray(leavesData) ? leavesData : (leavesData?.data || []);

  React.useEffect(() => {
    if (leavesError) {
      setAlert({
        open: true,
        message: leavesError.message || 'Failed to fetch leave history',
        severity: 'error',
      });
    }
    // eslint-disable-next-line
  }, [leavesError]);

  const fetchLeaveBalance = async (): Promise<void> => {
    try {
      const response = await apiClient.get('/api/v2/leaves/leave-balance');
      setLeaveBalance(response.data);
    } catch (error: any) {
      setAlert({
        open: true,
        message: 'Failed to fetch leave balance',
        severity: 'error'
      });
    }
  };  

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();

    if (!startDate || !endDate || !leaveType) {
      setAlert({
        open: true,
        message: 'Please fill in all required fields',
        severity: 'warning'
      });
      return;
    }

    try {
      // Format dates to YYYY-MM-DD without timezone issues
      const formatDate = (date: Date): string => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };

      const leaveData = {
        leave_name: leaveType,
        start_date: formatDate(startDate),
        end_date: formatDate(endDate),
        reason
      };

      if (editingLeave) {
        await apiClient.put(`/api/v2/leaves/${editingLeave._id}`, leaveData);
        setAlert({
          open: true,
          message: 'Leave request updated successfully',
          severity: 'success'
        });
      } else {
        await apiClient.post('/api/v2/leaves/apply', leaveData);
        setAlert({
          open: true,
          message: 'Leave application submitted successfully',
          severity: 'success'
        });
      }
      
      fetchLeaveBalance();
      refetch();
      setShowModal(false);
      resetForm();
    } catch (error: any) {
      setAlert({
        open: true,
        message: error.response?.data?.detail || 'Failed to submit leave application',
        severity: 'error'
      });
    }
  };

  // Note: Edit and delete functionality can be added later if needed
  // const handleEdit = (leave: LeaveRequest): void => {
  //   setEditingLeave(leave);
  //   setLeaveType(leave.leave_name);
  //   setStartDate(new Date(leave.start_date));
  //   setEndDate(new Date(leave.end_date));
  //   setReason(leave.reason);
  //   setShowModal(true);
  // };

  // const handleDelete = (leave: LeaveRequest): void => {
  //   setLeaveToDelete(leave);
  //   setShowDeleteConfirm(true);
  // };

  const confirmDelete = async (): Promise<void> => {
    // Note: Delete functionality can be implemented later if needed
    setShowDeleteConfirm(false);
  };

  const resetForm = (): void => {
    setEditingLeave(null);
    setStartDate(null);
    setEndDate(null);
    setLeaveType('');
    setReason('');
  };

  // const canModifyLeave = (leave: LeaveRequest): boolean => {
  //   const startDate = new Date(leave.start_date);
  //   const today = new Date();
  //   return startDate > today;
  // };

  const getLeaveTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      'casual_leave': 'primary.main',
      'sick_leave': 'warning.main',
      'earned_leave': 'success.main',
      'maternity_leave': 'info.main',
      'paternity_leave': 'secondary.main'
    };
    return colors[type] || 'grey.500';
  };

  const handleCloseAlert = (): void => {
    setAlert({ ...alert, open: false });
  };

  const handleLeaveTypeChange = (e: SelectChangeEvent<string>): void => {
    setLeaveType(e.target.value);
  };

  const handleReasonChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setReason(e.target.value);
  };

  return (
    <PageLayout title="Leave Management">
      <Box sx={{ p: 3 }}>
        {/* Header with Apply Button */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Leave Management</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setShowModal(true)}
          >
            Apply for Leave
          </Button>
        </Box>

        {/* Leave Balance Cards */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, 
          gap: 2, 
          mb: 4 
        }}>
          {Object.entries(leaveBalance).map(([type, balance]) => (
            <Card 
              key={type}
              sx={{ 
                bgcolor: getLeaveTypeColor(type),
                color: 'white',
                height: '100%'
              }}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h6" sx={{ mb: 1, textTransform: 'capitalize' }}>
                  {type.replace('_', ' ')}
                </Typography>
                <Typography variant="h3" sx={{ mb: 1 }}>
                  {String(balance)}
                </Typography>
                <Typography variant="body2">days remaining</Typography>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Leave History Table */}
        <Card>
          <CardContent>
            {isLeavesLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
                <CircularProgress color="primary" />
              </Box>
            ) : (
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
                      <TableCell>Leave Type</TableCell>
                      <TableCell>Start Date</TableCell>
                      <TableCell>End Date</TableCell>
                      <TableCell>Used Days</TableCell>
                      <TableCell>Reason</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {isLeavesLoading ? (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          <CircularProgress />
                        </TableCell>
                      </TableRow>
                    ) : leaves.length > 0 ? (
                      leaves.map((leave: LeaveRequest) => (
                        <TableRow 
                          key={leave.id}
                          sx={{ 
                            '&:hover': { 
                              backgroundColor: 'action.hover',
                              cursor: 'pointer'
                            }
                          }}
                        >
                          <TableCell>{leave.leave_name}</TableCell>
                          <TableCell>{leave.start_date}</TableCell>
                          <TableCell>{leave.end_date}</TableCell>
                          <TableCell>{leave.leave_count}</TableCell>
                          <TableCell>{leave.reason}</TableCell>
                          <TableCell>
                            <Box
                              component="span"
                              sx={{
                                display: 'inline-block',
                                padding: '4px 8px',
                                borderRadius: '4px',
                                backgroundColor: leave.status === 'approved' ? 'success.main' : 'error.main',
                                color: 'white',
                                fontSize: '0.75rem',
                                fontWeight: 'bold'
                              }}
                            >
                              {leave.status.toUpperCase()}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={6} align="center">No leaves found</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Leave Application Dialog */}
        <Dialog 
          open={showModal} 
          onClose={() => {
            setShowModal(false);
            resetForm();
          }}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            {editingLeave ? 'Update Leave Request' : 'Apply for Leave'}
          </DialogTitle>
          <DialogContent>
            <Box 
              component="form" 
              onSubmit={handleSubmit} 
              sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                gap: 2, 
                mt: 2 
              }}
            >
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <StyledDatePicker
                  label="Start Date"
                  value={startDate}
                  onChange={(date) => setStartDate(date)}
                  slotProps={{ 
                    textField: { 
                      fullWidth: true, 
                      required: true 
                    } 
                  }}
                  minDate={new Date()}
                />
              </LocalizationProvider>

              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <StyledDatePicker
                  label="End Date"
                  value={endDate}
                  onChange={(date) => setEndDate(date)}
                  slotProps={{ 
                    textField: { 
                      fullWidth: true, 
                      required: true 
                    } 
                  }}
                  minDate={startDate || new Date()}
                />
              </LocalizationProvider>

              <FormControl fullWidth>
                <InputLabel id="leave-type-label">Leave Type</InputLabel>
                <Select
                  labelId="leave-type-label"
                  value={leaveType}
                  onChange={handleLeaveTypeChange}
                  label="Leave Type"
                  required
                >
                  <MenuItem value="">Select Leave Type</MenuItem>
                  {Object.keys(leaveBalance).map((type) => (
                    <MenuItem key={type} value={type}>
                      {type.replace('_', ' ')}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label="Reason"
                value={reason}
                onChange={handleReasonChange}
                fullWidth
                multiline
                rows={3}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button 
              onClick={() => {
                setShowModal(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleSubmit} 
              variant="contained" 
              disabled={!leaveType || !startDate || !endDate}
            >
              {editingLeave ? 'Update' : 'Submit'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={showDeleteConfirm}
          onClose={() => setShowDeleteConfirm(false)}
        >
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            Are you sure you want to delete this leave request?
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowDeleteConfirm(false)}>
              Cancel
            </Button>
            <Button onClick={confirmDelete} color="error">
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Alert Snackbar */}
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
};

export default LeaveManagement; 