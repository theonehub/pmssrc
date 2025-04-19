import React, { useState, useEffect } from 'react';
import axios from '../../utils/axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PageLayout from '../../layout/PageLayout';
import ProtectedRoute from '../Common/ProtectedRoute';
import { Button, Table, Spinner, Modal, Form, Pagination, Dropdown, InputGroup } from 'react-bootstrap';
import { BsPlusCircle, BsFileEarmarkExcel, BsChevronLeft, BsChevronRight, BsSearch, BsCaretUpFill, BsCaretDownFill } from 'react-icons/bs';

function UsersList() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateUserModal, setShowCreateUserModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalUsers, setTotalUsers] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, [currentPage, pageSize]);

  // Sort function
  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Sort and filter users
  const getSortedAndFilteredUsers = () => {
    let filteredUsers = [...users];
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filteredUsers = filteredUsers.filter(user => 
        user.empId.toLowerCase().includes(searchLower) ||
        user.name.toLowerCase().includes(searchLower) ||
        user.email.toLowerCase().includes(searchLower) ||
        user.gender.toLowerCase().includes(searchLower) ||
        user.role.toLowerCase().includes(searchLower) ||
        user.mobile.includes(searchTerm)
      );
    }

    // Apply sorting
    if (sortConfig.key) {
      filteredUsers.sort((a, b) => {
        let aValue = a[sortConfig.key];
        let bValue = b[sortConfig.key];

        // Special handling for dates
        if (sortConfig.key === 'dob' || sortConfig.key === 'doj') {
          aValue = new Date(aValue);
          bValue = new Date(bValue);
        }

        if (aValue < bValue) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }

    return filteredUsers;
  };

  // Get sort icon
  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return null;
    }
    return sortConfig.direction === 'asc' ? <BsCaretUpFill /> : <BsCaretDownFill />;
  };

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


  const handleCreateUser = async (e) => {
    e.preventDefault();
    const userData = {
      empId: e.target.empId.value,
      name: e.target.name.value,
      email: e.target.email.value,
      gender: e.target.gender.value,
      dob: e.target.dob.value,
      doj: e.target.doj.value,
      mobile: e.target.mobile.value,
      managerId: e.target.managerId.value,
      password: e.target.password.value,
      role: e.target.role.value,
    };
    console.log(userData);

    try {
      const response = await axios.post('/users/create', userData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      toast.success('User created successfully');
      setShowCreateUserModal(false);
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user'); 
    }
  }

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
              onClick={() => setShowCreateUserModal(true)}
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

        {/* Search Box */}
        <div className="mb-3">
          <InputGroup>
            <InputGroup.Text>
              <BsSearch />
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
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
                    <th onClick={() => requestSort('empId')} style={{ cursor: 'pointer' }}>
                      Employee ID {getSortIcon('empId')}
                    </th>
                    <th onClick={() => requestSort('name')} style={{ cursor: 'pointer' }}>
                      Name {getSortIcon('name')}
                    </th>
                    <th onClick={() => requestSort('email')} style={{ cursor: 'pointer' }}>
                      Email {getSortIcon('email')}
                    </th>
                    <th onClick={() => requestSort('gender')} style={{ cursor: 'pointer' }}>
                      Gender {getSortIcon('gender')}
                    </th>
                    <th onClick={() => requestSort('dob')} style={{ cursor: 'pointer' }}>
                      Date of Birth {getSortIcon('dob')}
                    </th>
                    <th onClick={() => requestSort('doj')} style={{ cursor: 'pointer' }}>
                      Date of Joining {getSortIcon('doj')}
                    </th>
                    <th onClick={() => requestSort('mobile')} style={{ cursor: 'pointer' }}>
                      Mobile {getSortIcon('mobile')}
                    </th>
                    <th onClick={() => requestSort('role')} style={{ cursor: 'pointer' }}>
                      Role {getSortIcon('role')}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {getSortedAndFilteredUsers().map((user) => (
                    <tr key={user.empId}>
                      <td>{user.empId}</td>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td>{user.gender}</td>
                      <td>{new Date(user.dob).toLocaleDateString()}</td>
                      <td>{new Date(user.doj).toLocaleDateString()}</td>
                      <td>{user.mobile}</td>
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
        
        {/* Create User Modal */}
        <Modal show={showCreateUserModal} onHide={() => setShowCreateUserModal(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Create User</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form onSubmit={handleCreateUser}>
              <Form.Group className="mb-3">
                <Form.Label>Employee ID</Form.Label>
                <Form.Control type="text" name="empId" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Name</Form.Label>
                <Form.Control type="text" name="name" required />
              </Form.Group>
              <Form.Group className="mb-3">   
                <Form.Label>Email</Form.Label>
                <Form.Control type="email" name="email" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Gender</Form.Label>
                <Form.Control as="select" name="gender" required>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </Form.Control>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Date of Birth</Form.Label>
                <Form.Control type="date" name="dob" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Date of Joining</Form.Label>
                <Form.Control type="date" name="doj" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Mobile</Form.Label>
                <Form.Control type="text" name="mobile" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Manager ID</Form.Label>
                <Form.Control type="text" name="managerId" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password" name="password" required />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Role</Form.Label>
                <Form.Control as="select" name="role" required>
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                  <option value="superadmin">Super Admin</option>
                  <option value="manager">Manager</option>
                  
                </Form.Control>
              </Form.Group>
              <div className="d-flex justify-content-end">
                <Button variant="secondary" onClick={() => setShowCreateUserModal(false)}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit">
                  Create User
                </Button> 
              </div>
            </Form>
          </Modal.Body>
        </Modal>

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