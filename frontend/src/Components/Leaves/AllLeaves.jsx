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
  Chip,
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

  useEffect(() => {
    fetchLeaves();
  }, []);

  const fetchLeaves = async () => {
    try {
      const response = await axios.get('http://localhost:8000/leaves/all');
      setLeaves(response.data);
    } catch (error) {
      toast.error('Failed to fetch leaves');
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
    switch (status) {
      case 'APPROVED':
        return 'success';
      case 'REJECTED':
        return 'error';
      case 'PENDING':
        return 'warning';
      default:
        return 'default';
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
                <option value="PENDING">Pending</option>
                <option value="APPROVED">Approved</option>
                <option value="REJECTED">Rejected</option>
              </TextField>
            </Grid>
          </Grid>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
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
                {filteredLeaves.map((leave) => (
                  <TableRow key={leave.id}>
                    <TableCell>{leave.employee_name}</TableCell>
                    <TableCell>{leave.employee_email}</TableCell>
                    <TableCell>{leave.leave_name}</TableCell>
                    <TableCell>{leave.start_date}</TableCell>
                    <TableCell>{leave.end_date}</TableCell>
                    <TableCell>{leave.leave_count}</TableCell>
                    <TableCell>
                      <Chip
                        label={leave.status}
                        color={getStatusColor(leave.status)}
                      />
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
                ))}
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