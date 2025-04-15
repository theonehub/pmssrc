import React, { useState, useEffect } from 'react';
import axiosInstance from '../../utils/axios';

function UsersList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axiosInstance.get('/users');
        setUsers(response.data.users);
      } catch (err) {
        setError(err.message || 'An error occurred while fetching users.');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  return (
    <div>
      <h2>Users List</h2>
      {loading && <p>Loading users...</p>}
      {error && <p>Error: {error}</p>}
      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Emp ID</th>
              <th>Email</th>
              <th>Name</th>
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
                <td>{user.email}</td>
                <td>{user.name}</td>
                <td>{user.gender}</td>
                <td>{user.dob}</td>
                <td>{user.doj}</td>
                <td>{user.mobile}</td>
                <td>{user.username}</td>
                <td>{user.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default UsersList;