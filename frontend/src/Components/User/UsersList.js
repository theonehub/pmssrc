import React, { useState, useEffect } from 'react';
import axios from '../../utils/axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PageLayout from '../../layout/PageLayout';
import { Button, Table, Spinner, Modal, Form, Pagination, Dropdown } from 'react-bootstrap';
import { BsPlusCircle, BsFileEarmarkExcel, BsChevronLeft, BsChevronRight } from 'react-icons/bs';

function UsersList() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, [currentPage, pageSize]);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`/users?skip=${(currentPage - 1) * pageSize}&limit=${pageSize}`);
      setUsers(response.data.users);
      setTotalUsers(response.data.total);
    } catch (err) {
      setError(err.message || 'An error occurred while fetching users.');
      toast.error(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (e) => {
    e.preventDefault();
    if (!importFile) {
      toast.warning('Please select a file to upload');
      return;
    }

    setImporting(true);
    const formData = new FormData();
    formData.append('file', importFile);

    try {
      const response = await axios.post('/users/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      toast.success('Users imported successfully');
      setShowImportModal(false);
      setImportFile(null);
      fetchUsers(); // Refresh the user list
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to import users');
    } finally {
      setImporting(false);
    }
  };

  const handleFileChange = (e) => {
    setImportFile(e.target.files[0]);
  };

  // Calculate total pages
  const totalPages = Math.ceil(totalUsers / pageSize);

  // Generate page numbers
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <Pagination.Item
          key={i}
          active={i === currentPage}
          onClick={() => setCurrentPage(i)}
        >
          {i}
        </Pagination.Item>
      );
    }

    return pages;
  };

  return (
    <PageLayout title="Users Management">
      <div className="container-fluid">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h4>Users List</h4>
          <div>
            <Button
              variant="success"
              className="me-2"
              onClick={() => navigate('/register')}
            >
              <BsPlusCircle className="me-2" />
              Add User
            </Button>
            <Button
              variant="primary"
              onClick={() => setShowImportModal(true)}
            >
              <BsFileEarmarkExcel className="me-2" />
              Import Users
            </Button>
          </div>
        </div>

        {/* Page Size Selector */}
        <div className="d-flex justify-content-between align-items-center mb-3">
          <div className="d-flex align-items-center">
            <span className="me-2">Show</span>
            <Dropdown>
              <Dropdown.Toggle variant="outline-secondary" size="sm">
                {pageSize}
              </Dropdown.Toggle>
              <Dropdown.Menu>
                {[5, 10, 20, 50, 100].map((size) => (
                  <Dropdown.Item
                    key={size}
                    onClick={() => {
                      setPageSize(size);
                      setCurrentPage(1);
                    }}
                  >
                    {size}
                  </Dropdown.Item>
                ))}
              </Dropdown.Menu>
            </Dropdown>
            <span className="ms-2">entries</span>
          </div>
          <div>
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers} entries
          </div>
        </div>

        {loading ? (
          <div className="text-center">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : error ? (
          <div className="alert alert-danger">{error}</div>
        ) : (
          <>
            <div className="table-responsive">
              <Table striped bordered hover className="align-middle">
                <thead className="table-dark">
                  <tr>
                    <th>Emp ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Gender</th>
                    <th>Date of Birth</th>
                    <th>Date of Joining</th>
                    <th>Mobile</th>
                    <th>Username</th>
                    <th>Role</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user._id}>
                      <td>{user.empId}</td>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td>{user.gender}</td>
                      <td>{new Date(user.dob).toLocaleDateString()}</td>
                      <td>{new Date(user.doj).toLocaleDateString()}</td>
                      <td>{user.mobile}</td>
                      <td>{user.username || '-'}</td>
                      <td>
                        <span className={`badge bg-${getRoleBadgeColor(user.role)}`}>
                          {user.role}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>

            {/* Pagination */}
            <div className="d-flex justify-content-center mt-4">
              <Pagination>
                <Pagination.First
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                />
                <Pagination.Prev
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                />
                {getPageNumbers()}
                <Pagination.Next
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                />
                <Pagination.Last
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                />
              </Pagination>
            </div>
          </>
        )}

        {/* Import Modal */}
        <Modal show={showImportModal} onHide={() => setShowImportModal(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Import Users from Excel</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form onSubmit={handleImport}>
              <Form.Group className="mb-3">
                <Form.Label>Select Excel File (.xlsx)</Form.Label>
                <Form.Control
                  type="file"
                  accept=".xlsx"
                  onChange={handleFileChange}
                  required
                />
                <Form.Text className="text-muted">
                  Please ensure the Excel file follows the required format.
                </Form.Text>
              </Form.Group>
              <div className="d-flex justify-content-end">
                <Button
                  variant="secondary"
                  className="me-2"
                  onClick={() => setShowImportModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={importing}
                >
                  {importing ? (
                    <>
                      <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        className="me-2"
                      />
                      Importing...
                    </>
                  ) : (
                    'Import'
                  )}
                </Button>
              </div>
            </Form>
          </Modal.Body>
        </Modal>
      </div>
    </PageLayout>
  );
}

// Helper function to get badge color based on role
const getRoleBadgeColor = (role) => {
  switch (role?.toLowerCase()) {
    case 'admin':
      return 'primary';
    case 'superadmin':
      return 'danger';
    case 'hr':
      return 'info';
    case 'lead':
      return 'warning';
    case 'user':
      return 'success';
    default:
      return 'secondary';
  }
};

export default UsersList;