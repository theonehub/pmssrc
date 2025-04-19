import React, { useEffect, useState } from 'react';
import { Button, Modal, Form, Table, Spinner, Alert, Container } from 'react-bootstrap';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';

function CompanyLeaves() {
  const [leaves, setLeaves] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    count: 0,
    is_active: true,
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchLeaves = async () => {
    try {
      const res = await axios.get('http://localhost:8000/company-leaves', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setLeaves(res.data);
    } catch (err) {
      console.error('Error fetching company leaves', err);
      setError('Failed to load company leaves.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaves();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await axios.put(`http://localhost:8000/company-leaves/${editingId}`, formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      } else {
        await axios.post('http://localhost:8000/company-leaves', formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      }
      setShowModal(false);
      setFormData({ name: '', count: 0, is_active: true });
      setEditingId(null);
      fetchLeaves();
    } catch (err) {
      console.error('Error saving company leave', err);
      setError('Failed to save company leave.');
    }
  };

  const handleEdit = (leave) => {
    setFormData({ ...leave });
    setEditingId(leave.id);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this company leave?')) {
      try {
        await axios.delete(`http://localhost:8000/company-leaves/${id}`, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        fetchLeaves();
      } catch (err) {
        console.error('Error deleting company leave', err);
        setError('Failed to delete company leave.');
      }
    }
  };

  return (
    <PageLayout>
      <Container>
        <div className="mt-4 d-flex justify-content-between align-items-center">
          <h2>Company Leaves</h2>
          <Button onClick={() => setShowModal(true)}>Add New Leave</Button>
        </div>

        {error && <Alert variant="danger">{error}</Alert>}

        {loading ? (
          <div className="text-center py-5">
            <Spinner animation="border" variant="primary" />
          </div>
        ) : (
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Name</th>
                <th>Count</th>
                <th>Active</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leaves.map((leave) => (
                <tr key={leave.id}>
                  <td>{leave.name}</td>
                  <td>{leave.count}</td>
                  <td>{leave.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <Button size="sm" variant="info" className="me-2" onClick={() => handleEdit(leave)}>Edit</Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(leave.id)}>Delete</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}

        <Modal show={showModal} onHide={() => { setShowModal(false); setFormData({ name: '', count: 0, is_active: true }); setEditingId(null); }}>
          <Form onSubmit={handleSubmit}>
            <Modal.Header closeButton><Modal.Title>{editingId ? 'Edit' : 'Add'} Company Leave</Modal.Title></Modal.Header>
            <Modal.Body>
              <Form.Group className="mb-3">
                <Form.Label>Leave Name</Form.Label>
                <Form.Control 
                  required 
                  type="text" 
                  placeholder="e.g. Casual Leave, Sick Leave" 
                  value={formData.name} 
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Leave Count</Form.Label>
                <Form.Control 
                  required 
                  type="number" 
                  placeholder="Number of days allowed" 
                  value={formData.count} 
                  onChange={(e) => setFormData({ ...formData, count: parseInt(e.target.value) })} 
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Check 
                  type="checkbox" 
                  label="Active" 
                  checked={formData.is_active} 
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} 
                />
              </Form.Group>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={() => { setShowModal(false); setFormData({ name: '', count: 0, is_active: true }); setEditingId(null); }}>Cancel</Button>
              <Button type="submit" variant="primary">{editingId ? 'Update' : 'Save'}</Button>
            </Modal.Footer>
          </Form>
        </Modal>
      </Container>
    </PageLayout>
  );
}

export default CompanyLeaves; 