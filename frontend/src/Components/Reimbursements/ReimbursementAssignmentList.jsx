import React, { useEffect, useState } from 'react';
import {
  Button,
  Container,
  Table,
  Alert,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Box,
  Pagination,
  Grid,
  TextField,
  Select,
  MenuItem,
  Typography
} from '@mui/material';
import { Modal, Spinner } from 'react-bootstrap';
import axios from '../../utils/axios';
import { toast } from 'react-toastify';
import PageLayout from '../../layout/PageLayout';
import AssignReimbursementModal from './AssignReimbursementModal';
import { Paper } from '@mui/material';

const ReimbursementAssignmentList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchUsersWithAssignments = async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * pageSize;
      const res = await axios.get(`/reimbursements/assignment/all?skip=${skip}&limit=${pageSize}&search=${searchQuery}`);
      setUsers(res.data.data);
      setTotalUsers(res.data.total);
    } catch (err) {
      console.error('Error fetching users:', err);
      toast.error('Failed to load users and assignments');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUsersWithAssignments();
  }, [currentPage, pageSize, searchQuery]);

  const handleAssign = (user) => {
    setSelectedUser(user);
    setShowModal(true);
  };

  const handleDelete = (user) => {
    console.log("Delete requested for not implemented yet");
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedUser(null);
    fetchUsersWithAssignments();
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1); // Reset to first page on new search
    fetchUsersWithAssignments();
  };

  const totalPages = Math.ceil(totalUsers / pageSize);

  return (
    <PageLayout>
      <Container className="mt-4">
        <Typography variant="h4" gutterBottom>Manage Reimbursement Assignments</Typography>

        {/* Search and Page Size Controls */}
        <Grid container spacing={2} className="mb-3">
          <Grid item md={6}>
            <form onSubmit={handleSearch}>
              <TextField
                fullWidth
                variant="outlined"
                label="Search by name or email"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </Grid>
          <Grid item md={6} sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
            <Typography variant="body1" sx={{ mr: 2 }}>Show</Typography>
            <Select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              sx={{ width: 'auto' }}
            >
              <MenuItem value={5}>5</MenuItem>
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={20}>20</MenuItem>
              <MenuItem value={50}>50</MenuItem>
            </Select>
            <Typography variant="body1" sx={{ ml: 2 }}>entries</Typography>
          </Grid>
        </Grid>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <Spinner animation="border" variant="primary" />
          </Box>
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
                    <TableCell>Employee</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((user) => (
                    <TableRow 
                      key={user.id}
                      sx={{ 
                        '&:hover': { 
                          backgroundColor: 'action.hover',
                          cursor: 'pointer'
                        }
                      }}
                    >
                      <TableCell>{user.name}</TableCell>
                      <TableCell>{user.type_name}</TableCell>
                      <TableCell>{user.amount}</TableCell>
                      <TableCell>
                        <Box
                          component="span"
                          sx={{
                            display: 'inline-block',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            backgroundColor: user.is_active ? 'success.main' : 'error.main',
                            color: 'white',
                            fontSize: '0.75rem',
                            fontWeight: 'bold'
                          }}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button
                            variant="contained"
                            color="primary"
                            size="small"
                            onClick={() => handleAssign(user)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="contained"
                            color="error"
                            size="small"
                            onClick={() => handleDelete(user)}
                          >
                            Delete
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3 }}>
              <Typography variant="body2">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers} entries
              </Typography>
              <Pagination>
                <Pagination.First onClick={() => setCurrentPage(1)} disabled={currentPage === 1} />
                <Pagination.Prev onClick={() => setCurrentPage(currentPage - 1)} disabled={currentPage === 1} />
                {[...Array(totalPages)].map((_, i) => (
                  <Pagination.Item
                    key={i + 1}
                    active={currentPage === i + 1}
                    onClick={() => setCurrentPage(i + 1)}
                  >
                    {i + 1}
                  </Pagination.Item>
                ))}
                <Pagination.Next onClick={() => setCurrentPage(currentPage + 1)} disabled={currentPage === totalPages} />
                <Pagination.Last onClick={() => setCurrentPage(totalPages)} disabled={currentPage === totalPages} />
              </Pagination>
            </Box>
          </>
        )}

        {showModal && selectedUser && (
          <AssignReimbursementModal
            show={showModal}
            onClose={handleCloseModal}
            userId={selectedUser.id}
            userName={selectedUser.name}
          />
        )}
      </Container>
    </PageLayout>
  );
};

export default ReimbursementAssignmentList;