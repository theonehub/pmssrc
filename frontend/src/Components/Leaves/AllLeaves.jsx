import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Typography,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
} from '@mui/material';
import { toast } from 'react-toastify';
import axios from '../../utils/axios';
import Sidebar from '../../layout/Sidebar';
import Topbar from '../../layout/Topbar';

const AllLeaves = () => {
  const [leaves, setLeaves] = useState([]);
  const [selectedLeave, setSelectedLeave] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaves();
  }, []);

  const fetchLeaves = async () => {
    try {
      const response = await axios.get('http://localhost:8000/leaves/all');
      setLeaves(response.data);
    } catch (error) {
      toast.error('Failed to fetch leaves');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveReject = (leave, action) => {
    setSelectedLeave({ ...leave, action });
    setOpenDialog(true);
  };

  const handleConfirm = async () => {
    try {
      await axios.put(`http://localhost:8000/leaves/${selectedLeave.leave_id}/status?status=${selectedLeave.action}`);
      toast.success(`Leave ${selectedLeave.action} successfully`);
      fetchLeaves();
      setOpenDialog(false);
    } catch (error) {
      toast.error('Failed to update leave status');
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'success.main';
      case 'pending':
        return 'warning.main';
      case 'rejected':
        return 'error.main';
      default:
        return 'grey.500';
    }
  };

  const filteredLeaves = leaves.filter(leave => {
    const matchesStatus = statusFilter === 'ALL' || leave.status === statusFilter;
    const matchesSearch = searchTerm === '' || 
      leave.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      leave.employee_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      leave.leave_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <Box sx={{ display: 'flex' }}>
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Topbar />
        <Box sx={{ mt: 2 }}>
          <Typography variant="h4" gutterBottom>
            All Leaves
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Search"
                variant="outlined"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name, email or leave type"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                SelectProps={{
                  native: true,
                }}
              >
                <option value="ALL">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </TextField>
            </Grid>
          </Grid>

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
                  <TableCell>Employee</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Leave Type</TableCell>
                  <TableCell>Start Date</TableCell>
                  <TableCell>End Date</TableCell>
                  <TableCell>Days</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">Loading...</TableCell>
                  </TableRow>
                ) : leaves.length > 0 ? (
                  filteredLeaves.map((leave) => (
                    <TableRow 
                      key={leave.id}
                      sx={{ 
                        '&:hover': { 
                          backgroundColor: 'action.hover',
                          cursor: 'pointer'
                        }
                      }}
                    >
                      <TableCell>{leave.emp_id}</TableCell>
                      <TableCell>{leave.employee_name}</TableCell>
                      <TableCell>{leave.employee_email}</TableCell>
                      <TableCell>{leave.leave_name}</TableCell>
                      <TableCell>{leave.start_date}</TableCell>
                      <TableCell>{leave.end_date}</TableCell>
                      <TableCell>{leave.leave_count}</TableCell>
                      <TableCell>
                        <Box
                          component="span"
                          sx={{
                            display: 'inline-block',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            backgroundColor: getStatusColor(leave.status),
                            color: 'white',
                            fontSize: '0.75rem',
                            fontWeight: 'bold'
                          }}
                        >
                          {leave.status}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {leave.status && leave.status.toUpperCase() === 'PENDING' ? (
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button
                              variant="contained"
                              color="success"
                              size="small"
                              onClick={() => handleApproveReject(leave, 'approved')}
                            >
                              Approve
                            </Button>
                            <Button
                              variant="contained"
                              color="error"
                              size="small"
                              onClick={() => handleApproveReject(leave, 'rejected')}
                            >
                              Reject
                            </Button>
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            No actions available
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} align="center">No leaves found</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
            <DialogTitle>Confirm Action</DialogTitle>
            <DialogContent>
              Are you sure you want to {selectedLeave?.action} this leave?
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
              <Button onClick={handleConfirm} color="primary">
                Confirm
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
      </Box>
    </Box>
  );
};

export default AllLeaves; 