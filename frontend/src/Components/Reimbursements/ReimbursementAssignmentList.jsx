import React, { useEffect, useState } from 'react';
import { Container, Table, Button, Spinner, Pagination, Form, Row, Col } from 'react-bootstrap';
import axios from '../../utils/axios';
import { toast } from 'react-toastify';
import PageLayout from '../../layout/PageLayout';
import AssignReimbursementModal from './AssignReimbursementModal';

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
        <h4>Manage Reimbursement Assignments</h4>

        {/* Search and Page Size Controls */}
        <Row className="mb-3">
          <Col md={6}>
            <Form onSubmit={handleSearch}>
              <Form.Control
                type="text"
                placeholder="Search by name or email"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </Form>
          </Col>
          <Col md={6} className="d-flex justify-content-end align-items-center">
            <span className="me-2">Show</span>
            <Form.Select
              style={{ width: 'auto' }}
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </Form.Select>
            <span className="ms-2">entries</span>
          </Col>
        </Row>

        {loading ? (
          <div className="text-center py-5">
            <Spinner animation="border" variant="primary" />
          </div>
        ) : (
          <>
            <Table bordered hover>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Assigned Reimbursements</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>
                      {user.assigned_reimbursements?.length > 0
                        ? user.assigned_reimbursements.map((r) => (
                            <div key={r.type_id}>
                              {r.name}
                              {r.monthly_limit && ` (Limit: ${r.monthly_limit})`}
                              {r.required_docs && ' (Docs Required)'}
                            </div>
                          ))
                        : 'None Assigned'}
                    </td>
                    <td>
                      <Button size="sm" onClick={() => handleAssign(user)}>
                        {user.assigned_reimbursements?.length > 0 ? 'Edit' : 'Assign'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>

            {/* Pagination */}
            <div className="d-flex justify-content-between align-items-center">
              <div>
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers} entries
              </div>
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
            </div>
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