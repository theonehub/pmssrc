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
  Grid,
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
  CircularProgress
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import axios from '../../utils/axios';
//import { getCurrentUser } from '../../utils/auth';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import PageLayout from '../../layout/PageLayout';
import { styled } from '@mui/material/styles';

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

const LeaveManagement = () => {
  const [leaveBalance, setLeaveBalance] = useState({});
  const [leaves, setLeaves] = useState([]);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [leaveType, setLeaveType] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingLeave, setEditingLeave] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [leaveToDelete, setLeaveToDelete] = useState(null);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchLeaveBalance();
    fetchLeaves();
  }, []);

  const fetchLeaveBalance = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/leaves/leave-balance`);
      setLeaveBalance(response.data);
    } catch (error) {
      setAlert({
        open: true,
        message: 'Failed to fetch leave balance',
        severity: 'error'
      });
    }
  };

  const fetchLeaves = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/leaves/my-leaves`);
      setLeaves(response.data);
    } catch (error) {
      setAlert({
        open: true,
        message: 'Failed to fetch leave history',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

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
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        reason: reason
      };

      if (editingLeave) {
        await axios.put(`http://localhost:8000/leaves/${editingLeave._id}`, leaveData);
        setAlert({
          open: true,
          message: 'Leave request updated successfully',
          severity: 'success'
        });
      } else {
        await axios.post(`http://localhost:8000/leaves/apply`, leaveData);
        setAlert({
          open: true,
          message: 'Leave application submitted successfully',
          severity: 'success'
        });
      }
      
      fetchLeaveBalance();
      fetchLeaves();
      setShowModal(false);
      resetForm();
    } catch (error) {
      setAlert({
        open: true,
        message: error.response?.data?.detail || 'Failed to submit leave application',
        severity: 'error'
      });
    }
  };

  const handleEdit = (leave) => {
    setEditingLeave(leave);
    setLeaveType(leave.leave_name);
    setStartDate(new Date(leave.start_date));
    setEndDate(new Date(leave.end_date));
    setReason(leave.reason);
    setShowModal(true);
  };

  const handleDelete = (leave) => {
    setLeaveToDelete(leave);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/leaves/${leaveToDelete.leave_id}`);
      setAlert({
        open: true,
        message: 'Leave request deleted successfully',
        severity: 'success'
      });
      fetchLeaves();
      setShowDeleteConfirm(false);
    } catch (error) {
      setAlert({
        open: true,
        message: error.response?.data?.detail || 'Failed to delete leave request',
        severity: 'error'
      });
    }
  };

  const resetForm = () => {
    setEditingLeave(null);
    setStartDate(null);
    setEndDate(null);
    setLeaveType('');
    setReason('');
  };

  const canModifyLeave = (leave) => {
    const startDate = new Date(leave.start_date);
    const today = new Date();
    return startDate > today;
  };

  const getLeaveTypeColor = (type) => {
    const colors = {
      'casual_leave': 'primary.main',
      'sick_leave': 'warning.main',
      'earned_leave': 'success.main',
      'maternity_leave': 'info.main',
      'paternity_leave': 'secondary.main'
    };
    return colors[type] || 'grey.500';
  };

  const handleCloseAlert = () => {
    setAlert({ ...alert, open: false });
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
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {Object.entries(leaveBalance).map(([type, balance]) => (
            <Grid item xs={12} sm={6} md={4} key={type}>
              <Card 
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
                    {balance}
                  </Typography>
                  <Typography variant="body2">days remaining</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Leave History Table */}
        <Card>
          <CardContent>
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
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        <CircularProgress />
                      </TableCell>
                    </TableRow>
                  ) : leaves.length > 0 ? (
                    leaves.map((leave) => (
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
                <DatePicker
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
                <DatePicker
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
                  onChange={(e) => setLeaveType(e.target.value)}
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
                onChange={(e) => setReason(e.target.value)}
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