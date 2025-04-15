import React, { useEffect, useState } from 'react';
import axios from '../utils/axios';
import { getToken } from '../utils/auth'; 
import PageLayout from '../layout/PageLayout'; // Adjust path if needed

function Home() {
  const [stats, setStats] = useState({});

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await axios.get('/users/stats', {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setStats(res.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <PageLayout>
      <h3 className="mb-4">Overview</h3>
      <div className="row">
        <div className="col-md-4 mb-4">
          <div className="card text-white bg-primary">
            <div className="card-body">
              <h5 className="card-title">Total Users</h5>
              <p className="card-text fs-4">{stats.total_users || stats.total_users || 0}</p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card text-white bg-success">
            <div className="card-body">
              <h5 className="card-title">Admins</h5>
              <p className="card-text fs-4">{stats.admin || 0}</p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card text-white bg-info">
            <div className="card-body">
              <h5 className="card-title">SuperAdmins</h5>
              <p className="card-text fs-4">{stats.superadmin || stats.SuperAdmin || 0}</p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card text-white bg-warning">
            <div className="card-body">
              <h5 className="card-title">HR</h5>
              <p className="card-text fs-4">{stats.hr || 0}</p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card text-white bg-secondary">
            <div className="card-body">
              <h5 className="card-title">Leads</h5>
              <p className="card-text fs-4">{stats.lead || 0}</p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card text-white bg-dark">
            <div className="card-body">
              <h5 className="card-title">Users</h5>
              <p className="card-text fs-4">{stats.user || 0}</p>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}

export default Home;