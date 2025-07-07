import React, { useState } from 'react';
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
  IconButton,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import { toast } from 'react-toastify';
import { useLeavesQuery } from '../../shared/hooks/useLeaves';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import Tooltip from '@mui/material/Tooltip';

// Define interfaces
interface Leave {
  id: string;
  leave_id: string;
  employee_id: string;
  emp_name: string;
  emp_email: string;
  employee_name: string;
  employee_email: string;
  leave_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  leave_count: number;
  status: string;
}

interface SelectedLeave extends Leave {
  action: 'approved' | 'rejected';
}

type StatusFilter = 'ALL' | 'pending' | 'approved' | 'rejected';
type StatusType = 'approved' | 'pending' | 'rejected';

const AllLeaves: React.FC = () => {
  const [selectedLeave, setSelectedLeave] = useState<SelectedLeave | null>(null);
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  // const [leaveStats, setLeaveStats] = useState<LeaveStats>({ total: 0, pending: 0 });

  // Use React Query for leaves
  const { data: leavesData, isLoading, error: leavesError, refetch } = useLeavesQuery();
  const leaves: Leave[] = Array.isArray(leavesData) ? leavesData : (leavesData?.data || []);

  React.useEffect(() => {
    if (leavesError) {
      toast.error(leavesError.message || 'Failed to fetch leaves');
    }
    // eslint-disable-next-line
  }, [leavesError]);

  const handleApproveReject = (leave: Leave, action: 'approved' | 'rejected'): void => {
    setSelectedLeave({ ...leave, action });
    setOpenDialog(true);
  };

  const handleConfirm = async (): Promise<void> => {
    if (!selectedLeave) return;

    try {
      await refetch();
      toast.success(`Leave ${selectedLeave.action} successfully`);
      setOpenDialog(false);
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Failed to update leave status:', error);
      }
      toast.error('Failed to update leave status');
    }
  };

  const getStatusColor = (status?: string): string => {
    switch (status?.toLowerCase() as StatusType) {
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

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const filteredLeaves = Array.isArray(leaves) ? leaves.filter((leave: Leave) => {
    const matchesStatus = statusFilter === 'ALL' || leave.status === statusFilter;
    const matchesSearch = searchTerm === '' || 
      (leave.employee_name || leave.emp_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (leave.employee_email || leave.emp_email || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (leave.leave_name || leave.leave_type || '').toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  }) : [];

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchTerm(event.target.value);
  };

  const handleStatusFilterChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setStatusFilter(event.target.value as StatusFilter);
  };

  const handleCloseDialog = (): void => {
    setOpenDialog(false);
    setSelectedLeave(null);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        All Leaves
      </Typography>
      
      {/* Statistics Cards */}
      <Box sx={{ display: 'flex', gap: 3, mb: 4 }}>
        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Leaves Applied
              </Typography>
              <Typography variant="h4" component="div">
                {Array.isArray(leaves) ? leaves.length : 0}
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Approval
              </Typography>
              <Typography variant="h4" component="div">
                {Array.isArray(leaves) ? leaves.filter((leave: Leave) => leave.status === 'pending').length : 0}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <TextField
            fullWidth
            label="Search"
            variant="outlined"
            value={searchTerm}
            onChange={handleSearchChange}
            placeholder="Search by name, email or leave type"
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <TextField
            fullWidth
            select
            label="Status"
            value={statusFilter}
            onChange={handleStatusFilterChange}
            SelectProps={{
              native: true,
            }}
          >
            <option value="ALL">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </TextField>
        </Box>
      </Box>

      {/* Leaves Table */}
      {isLoading ? (
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
              {filteredLeaves.length > 0 ? (
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
                    <TableCell>{leave.employee_id}</TableCell>
                    <TableCell>{leave.employee_name || leave.emp_name}</TableCell>
                    <TableCell>{leave.employee_email || leave.emp_email}</TableCell>
                    <TableCell>{leave.leave_name || leave.leave_type}</TableCell>
                    <TableCell>{formatDate(leave.start_date)}</TableCell>
                    <TableCell>{formatDate(leave.end_date)}</TableCell>
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
                          <Tooltip title="Approve Leave" placement="top" arrow>
                            <IconButton
                              color="success"
                              onClick={() => handleApproveReject(leave, 'approved')}
                              size="small"
                            >
                              <CheckCircleIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reject Leave" placement="top" arrow>
                            <IconButton
                              color="error"
                              onClick={() => handleApproveReject(leave, 'rejected')}
                              size="small"
                            >
                              <CancelIcon />
                            </IconButton>
                          </Tooltip>
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
                  <TableCell colSpan={9} align="center">No leaves found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Confirmation Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Confirm Action</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to {selectedLeave?.action} this leave application?
          </Typography>
          {selectedLeave && (
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" gutterBottom>
                <strong>Employee:</strong> {selectedLeave.employee_name || selectedLeave.emp_name}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Leave Type:</strong> {selectedLeave.leave_name || selectedLeave.leave_type}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Duration:</strong> {formatDate(selectedLeave.start_date)} to {formatDate(selectedLeave.end_date)}
              </Typography>
              <Typography variant="body2">
                <strong>Days:</strong> {selectedLeave.leave_count}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleConfirm} 
            color={selectedLeave?.action === 'approved' ? 'success' : 'error'}
            variant="contained"
          >
            {selectedLeave?.action === 'approved' ? 'Approve' : 'Reject'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AllLeaves; 