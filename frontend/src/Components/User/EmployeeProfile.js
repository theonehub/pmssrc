import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout'; // Adjust path if needed

function EmployeeProfile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await axios.get('http://localhost:8000/employee/profile', {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setProfile(res.data);
      } catch (err) {
        setError(err.message || 'Failed to load profile.');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  return (
    <PageLayout>
      <div className="container mt-4">
        <h3 className="mb-4">Your Profile</h3>
        {loading && <p>Loading...</p>}
        {error && <p className="text-danger">{error}</p>}
        {profile && (
          <table className="table table-bordered">
            <tbody>
              <tr><th>Name</th><td>{profile.name}</td></tr>
              <tr><th>Email</th><td>{profile.email}</td></tr>
              <tr><th>Date of Joining</th><td>{profile.date_of_joining}</td></tr>
              <tr><th>Gender</th><td>{profile.gender}</td></tr>
              <tr><th>Mobile Number</th><td>{profile.mobile_number}</td></tr>
            </tbody>
          </table>
        )}
      </div>
    </PageLayout>
  );
}

export default EmployeeProfile;