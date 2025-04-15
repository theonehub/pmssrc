import React, { useEffect, useState } from 'react';
import { Container, Table, Button, Spinner } from 'react-bootstrap';
import axios from '../utils/axios';
import { toast } from 'react-toastify';
import PageLayout from '../layout/PageLayout';
import AssignReimbursementModal from './AssignReimbursementModal';

const ReimbursementAssignmentList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const fetchUsersWithAssignments = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/reimbursements/assignment/users-with-assignments');
      setUsers(res.data);
    } catch (err) {
      toast.error('Failed to load users and assignments');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUsersWithAssignments();
  }, []);

  const handleAssign = (user) => {
    setSelectedUser(user);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedUser(null);
    fetchUsersWithAssignments();
  };

  return (
    <PageLayout>
      <Container className="mt-4">
        <h4>Manage Reimbursement Assignments</h4>

        {loading ? (
          <Spinner animation="border" />
        ) : (
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
                      ? user.assigned_reimbursements.map((r) => r.name).join(', ')
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
        )}

        {showModal && selectedUser && (
          <AssignReimbursementModal user={selectedUser} onClose={handleCloseModal} />
        )}
      </Container>
    </PageLayout>
  );
};

export default ReimbursementAssignmentList;