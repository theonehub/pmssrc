import React, { useEffect, useState } from 'react';
import { Button, Modal, Form, Table, Spinner, Alert, Container } from 'react-bootstrap';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';

function ReimbursementTypes() {
  const [types, setTypes] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    max_limit: 0,
    description: '',
    is_active: true,
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchTypes = async () => {
    try {
      const res = await axios.get('http://localhost:8000/reimbursement-types', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setTypes(res.data);
    } catch (err) {
      console.error('Error fetching reimbursement types', err);
      setError('Failed to load reimbursement types.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTypes();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await axios.put(`http://localhost:8000/reimbursement-types/${editingId}`, formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      } else {
        await axios.post('http://localhost:8000/reimbursement-types', formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
      }
      setShowModal(false);
      setFormData({ name: '', max_limit: 0, description: '', is_active: true });
      setEditingId(null);
      fetchTypes();
    } catch (err) {
      console.error('Error saving reimbursement type', err);
      setError('Failed to save reimbursement type.');
    }
  };

  const handleEdit = (type) => {
    setFormData({ ...type });
    setEditingId(type.id);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this reimbursement type?')) {
      try {
        await axios.delete(`http://localhost:8000/reimbursement-types/${id}`, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        fetchTypes();
      } catch (err) {
        console.error('Error deleting reimbursement type', err);
        setError('Failed to delete reimbursement type.');
      }
    }
  };

  return (
    <PageLayout>
      <Container>
        <div className="mt-4 d-flex justify-content-between align-items-center">
          <h2>Reimbursement Types</h2>
          <Button onClick={() => setShowModal(true)}>Add New Type</Button>
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
                <th>Max Limit</th>
                <th>Description</th>
                <th>Active</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {types.map((type) => (
                <tr key={type.id}>
                  <td>{type.name}</td>
                  <td>{type.max_limit}</td>
                  <td>{type.description}</td>
                  <td>{type.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <Button size="sm" variant="info" className="me-2" onClick={() => handleEdit(type)}>Edit</Button>
                    <Button size="sm" variant="danger" onClick={() => handleDelete(type.id)}>Delete</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}

        <Modal show={showModal} onHide={() => { setShowModal(false); setFormData({ name: '', max_limit: 0, description: '', is_active: true }); setEditingId(null); }}>
          <Form onSubmit={handleSubmit}>
            <Modal.Header closeButton><Modal.Title>{editingId ? 'Edit' : 'Add'} Reimbursement Type</Modal.Title></Modal.Header>
            <Modal.Body>
              <Form.Control required className="mb-3" type="text" placeholder="Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
              <Form.Control required className="mb-3" type="number" placeholder="Max Limit" value={formData.max_limit} onChange={(e) => setFormData({ ...formData, max_limit: e.target.value })} />
              <Form.Control className="mb-3" as="textarea" placeholder="Description" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} />
              <Form.Check type="checkbox" label="Active" checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} />
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={() => { setShowModal(false); setFormData({ name: '', max_limit: 0, description: '', is_active: true }); setEditingId(null); }}>Cancel</Button>
              <Button type="submit" variant="primary">{editingId ? 'Update' : 'Save'}</Button>
            </Modal.Footer>
          </Form>
        </Modal>
      </Container>
    </PageLayout>
  );
}

export default ReimbursementTypes;