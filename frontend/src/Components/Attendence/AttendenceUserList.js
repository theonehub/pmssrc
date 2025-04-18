import React, { useState, useEffect } from 'react';
import axios from '../../utils/axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PageLayout from '../../layout/PageLayout';
import ProtectedRoute from '../Common/ProtectedRoute';
import { Button, Table, Spinner, Modal, Form, Pagination, Dropdown, InputGroup } from 'react-bootstrap';
import { BsPlusCircle, BsFileEarmarkExcel, BsChevronLeft, BsChevronRight, BsSearch, BsCaretUpFill, BsCaretDownFill } from 'react-icons/bs';
import AttendanceCalendar from './AttendanceCalendar';
import './AttendanceCalendar.css';

function AttendenceUserList() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [selectedEmpId, setSelectedEmpId] = useState(null);
  const [showCalendar, setShowCalendar] = useState(false);

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

  const handleViewAttendance = (empId) => {
    console.log(empId);
    setSelectedEmpId(empId);
    setShowCalendar(true);
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
                    <th onClick={() => requestSort('doj')} style={{ cursor: 'pointer' }}>
                      Date of Joining {getSortIcon('doj')}
                    </th>
                    <th onClick={() => requestSort('mobile')} style={{ cursor: 'pointer' }}>
                      Mobile {getSortIcon('mobile')}
                    </th>
                    <th>
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {getSortedAndFilteredUsers().map((user) => (
                    <tr key={user.empId}>
                      <td>{user.empId}</td>
                      <td>{user.name}</td>
                      <td>{user.email}</td>
                      <td>{user.doj}</td>
                      <td>{user.mobile}</td>
                      <td>
                        <Button variant="primary" onClick={() => handleViewAttendance(user.empId)}>
                          View Attendance
                        </Button>
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

        <AttendanceCalendar
          empId={selectedEmpId}
          show={showCalendar}
          onHide={() => setShowCalendar(false)}
        />
      </div>
    </PageLayout>
  );
};
export default AttendenceUserList;