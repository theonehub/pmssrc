import React, { useState, useEffect } from 'react';
import { Paper, Container, Table, TableContainer, TableHead, TableBody, TableRow, TableCell, Box, Grid } from '@mui/material';
import { Modal, Form, Card, Button, Alert } from 'react-bootstrap';
import axios from '../../utils/axios';
//import { getCurrentUser } from '../../utils/auth';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import PageLayout from '../../layout/PageLayout';

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

  useEffect(() => {
    fetchLeaveBalance();
    fetchLeaves();
  }, []);

  const fetchLeaveBalance = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/leaves/leave-balance`);
      setLeaveBalance(response.data);
    } catch (error) {
      setError('Failed to fetch leave balance');
    }
  };

  const fetchLeaves = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/leaves/my-leaves`);
      setLeaves(response.data);
      setLoading(false);
    } catch (error) {
      setError('Failed to fetch leave history');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!startDate || !endDate || !leaveType) {
      setError('Please fill in all required fields');
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
        setSuccess('Leave request updated successfully');
      } else {
        await axios.post(`http://localhost:8000/leaves/apply`, leaveData);
        setSuccess('Leave application submitted successfully');
      }
      
      fetchLeaveBalance();
      fetchLeaves();
      setShowModal(false);
      resetForm();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit leave application');
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
      setSuccess('Leave request deleted successfully');
      fetchLeaves();
      setShowDeleteConfirm(false);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to delete leave request');
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
      'casual_leave': 'primary',
      'sick_leave': 'warning',
      'earned_leave': 'success',
      'maternity_leave': 'info',
      'paternity_leave': 'secondary'
    };
    return colors[type] || 'dark';
  };

  return (
    <PageLayout title="Leave Management">
      <Container fluid>
        {/* Header with Apply Button */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Leave Management</h2>
          <Button 
            variant="primary" 
            onClick={() => setShowModal(true)}
            className="d-flex align-items-center"
          >
            <i className="bi bi-plus-circle me-2"></i>
            Apply for Leave
          </Button>
        </div>

        {/* Leave Balance Tiles */}
        <Grid container spacing={2} className="mb-4">
          {Object.entries(leaveBalance).map(([type, balance]) => (
            <Grid item md={4} className="mb-3">
              <Card 
                bg={getLeaveTypeColor(type)}
                text="white"
                className="h-100"
              >
                <Card.Body className="d-flex flex-column align-items-center">
                  <Card.Title className="text-capitalize mb-3">
                    {type.replace('_', ' ')}
                  </Card.Title>
                  <Card.Text className="display-4 mb-0">
                    {balance}
                  </Card.Text>
                  <small>days remaining</small>
                </Card.Body>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Leave History */}
        <Card>
          <Card.Header>
            <h4>Leave History</h4>
          </Card.Header>
          <Card.Body>
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
                      <TableCell colSpan={5} align="center">Loading...</TableCell>
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
                      <TableCell colSpan={5} align="center">No leaves found</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Card.Body>
        </Card>

        {/* Leave Application Modal */}
        <Modal show={showModal} onHide={() => {
          setShowModal(false);
          resetForm();
        }} size="lg">
          <Modal.Header closeButton>
            <Modal.Title>{editingLeave ? 'Update Leave Request' : 'Apply for Leave'}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {error && <Alert variant="danger">{error}</Alert>}
            {success && <Alert variant="success">{success}</Alert>}
            <Form onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Leave Type</Form.Label>
                    <Form.Select
                      value={leaveType}
                      onChange={(e) => setLeaveType(e.target.value)}
                      required
                    >
                      <option value="">Select Leave Type</option>
                      {Object.keys(leaveBalance).map((type) => (
                        <option key={type} value={type}>
                          {type.replace('_', ' ')}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Grid>
                <Grid item md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Reason</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={2}
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                    />
                  </Form.Group>
                </Grid>
              </Grid>
              <Grid container spacing={2}>
                <Grid item md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Start Date</Form.Label>
                    <DatePicker
                      selected={startDate}
                      onChange={(date) => setStartDate(date)}
                      className="form-control"
                      dateFormat="yyyy-MM-dd"
                      minDate={new Date()}
                      required
                    />
                  </Form.Group>
                </Grid>
                <Grid item md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>End Date</Form.Label>
                    <DatePicker
                      selected={endDate}
                      onChange={(date) => setEndDate(date)}
                      className="form-control"
                      dateFormat="yyyy-MM-dd"
                      minDate={startDate || new Date()}
                      required
                    />
                  </Form.Group>
                </Grid>
              </Grid>
              <div className="d-flex justify-content-end gap-2">
                <Button variant="secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit">
                  Submit Leave Application
                </Button>
              </div>
            </Form>
          </Modal.Body>
        </Modal>

        {/* Delete Confirmation Modal */}
        <Modal show={showDeleteConfirm} onHide={() => setShowDeleteConfirm(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Confirm Delete</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            Are you sure you want to delete this leave request?
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowDeleteConfirm(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={confirmDelete}>
              Delete
            </Button>
          </Modal.Footer>
        </Modal>
      </Container>
    </PageLayout>
  );
};

export default LeaveManagement; 