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
import { useLeavesQuery, useLeaveBalanceQuery } from '../../shared/hooks/useLeaves';
import { LeaveRequest, AlertState } from '../../shared/types';
import { apiClient } from '../../shared/api';

// Add custom styled components for consistent styling

const LeaveManagement: React.FC = () => {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
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

  // Use React Query for leaves and leave balance
  const { data: leavesData, isLoading: isLeavesLoading, error: leavesError, refetch } = useLeavesQuery();
  const { data: leaveBalance, isLoading: isBalanceLoading, error: balanceError, refetch: refetchBalance } = useLeaveBalanceQuery();
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

  React.useEffect(() => {
    if (balanceError) {
      setAlert({
        open: true,
        message: balanceError.message || 'Failed to fetch leave balance',
        severity: 'error',
      });
    }
    // eslint-disable-next-line
  }, [balanceError]);

  

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
      const leaveData = {
        leave_name: leaveType,
        start_date: startDate,
        end_date: endDate,
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
      
      refetchBalance();
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
    setStartDate('');
    setEndDate('');
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
      'Casual Leave': 'primary.main',
      'Sick Leave': 'warning.main',
      'Earned Leave': 'success.main',
      'Maternity Leave': 'info.main',
      'Paternity Leave': 'secondary.main',
      // Fallback for old format
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
    <Box>
      {/* Header */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h4" color="primary" gutterBottom>
                Leave Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Apply for leaves and track your leave history
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowModal(true)}
            >
              APPLY FOR LEAVE
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Leave Balance Cards */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Leave Balance</Typography>
        {isBalanceLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress color="primary" />
          </Box>
        ) : leaveBalance && Object.keys(leaveBalance).length > 0 ? (
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, 
            gap: 2
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
                    {type}
                  </Typography>
                  <Typography variant="h3" sx={{ mb: 1 }}>
                    {String(balance)}
                  </Typography>
                  <Typography variant="body2">days remaining</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Typography variant="body1" color="text.secondary">
              No leave balance data available
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Leave History Table */}
      <Paper elevation={1}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Leave History</Typography>
        </Box>
        {isLeavesLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <CircularProgress color="primary" />
          </Box>
        ) : (
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
                      key={leave.leave_id || leave.id}
                      sx={{ 
                        '&:hover': { 
                          backgroundColor: 'action.hover',
                          cursor: 'pointer'
                        }
                      }}
                    >
                      <TableCell>{leave.leave_type}</TableCell>
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
      </Paper>

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
            <TextField
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
              inputProps={{
                min: new Date().toISOString().split('T')[0] // Today's date as minimum
              }}
            />

            <TextField
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
              inputProps={{
                min: startDate || new Date().toISOString().split('T')[0] // Start date or today as minimum
              }}
            />

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
                {leaveBalance && Object.keys(leaveBalance).map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
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
  );
};

export default LeaveManagement; 