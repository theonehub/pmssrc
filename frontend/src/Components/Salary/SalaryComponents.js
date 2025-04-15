import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';
import PageLayout from '../../layout/PageLayout';
import { Modal, Button, Form, Spinner, Toast } from 'react-bootstrap';

function SalaryComponents() {
  const [components, setComponents] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', type: 'earning', description: '' });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [toast, setToast] = useState({ show: false, message: '', variant: '' });

  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  // Fetch components from API
  const fetchComponents = async () => {
    setLoading(true);
    try {
      const res = await axios.get('http://localhost:8000/salary-components', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setComponents(res.data);
    } catch (error) {
      console.error('Error fetching components:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchComponents();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setToast({ show: true, message: 'Component name is required.', variant: 'danger' });
      return;
    }

    try {
      if (editingId) {
        await axios.put(`http://localhost:8000/salary-components/${editingId}`, formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setToast({ show: true, message: 'Component updated successfully.', variant: 'success' });
      } else {
        await axios.post('http://localhost:8000/salary-components', formData, {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        setToast({ show: true, message: 'Component added successfully.', variant: 'success' });
      }
      fetchComponents();
      handleCloseForm();
    } catch (err) {
      console.error('Error saving component:', err);
      setToast({ show: true, message: 'Error saving component.', variant: 'danger' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this component?')) return;

    try {
      await axios.delete(`http://localhost:8000/salary-components/${id}`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setToast({ show: true, message: 'Component deleted.', variant: 'info' });
      fetchComponents();
    } catch (err) {
      console.error('Error deleting component:', err);
      setToast({ show: true, message: 'Error deleting component.', variant: 'danger' });
    }
  };

  const handleEdit = (comp) => {
    setFormData({ name: comp.name, type: comp.type, description: comp.description });
    setEditingId(comp.id);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setFormData({ name: '', type: 'earning', description: '' });
    setEditingId(null);
  };

  const filteredComponents = components.filter((comp) =>
    comp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    comp.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredComponents.length / pageSize);
  const paginatedComponents = filteredComponents.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <PageLayout>
      <div className="container mt-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h4>Salary Components</h4>
          <Button onClick={() => setShowForm(true)}>
            <FaPlus className="me-2" /> Add Component
          </Button>
        </div>

        <Form.Control
          type="text"
          placeholder="Search by name or type"
          className="mb-3"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
        />

        {loading ? (
          <div className="text-center py-5">
            <Spinner animation="border" variant="primary" />
          </div>
        ) : (
          <table className="table table-bordered table-hover">
            <thead className="table-light">
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th style={{ width: '100px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedComponents.length > 0 ? (
                paginatedComponents.map((comp) => (
                  <tr key={comp.id}>
                    <td>{comp.name}</td>
                    <td className={comp.type === 'earning' ? 'text-success' : 'text-danger'}>
                      {comp.type.charAt(0).toUpperCase() + comp.type.slice(1)}
                    </td>
                    <td>{comp.description}</td>
                    <td>
                      <Button variant="outline-primary" size="sm" onClick={() => handleEdit(comp)} className="me-2">
                        <FaEdit />
                      </Button>
                      <Button variant="outline-danger" size="sm" onClick={() => handleDelete(comp.id)}>
                        <FaTrash />
                      </Button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center">
                    No components found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <nav>
            <ul className="pagination justify-content-center">
              <li className={`page-item ${currentPage === 1 && 'disabled'}`}>
                <button className="page-link" onClick={() => setCurrentPage(currentPage - 1)}>Previous</button>
              </li>
              {Array.from({ length: totalPages }, (_, i) => (
                <li key={i} className={`page-item ${currentPage === i + 1 && 'active'}`}>
                  <button className="page-link" onClick={() => setCurrentPage(i + 1)}>{i + 1}</button>
                </li>
              ))}
              <li className={`page-item ${currentPage === totalPages && 'disabled'}`}>
                <button className="page-link" onClick={() => setCurrentPage(currentPage + 1)}>Next</button>
              </li>
            </ul>
          </nav>
        )}

        {/* Add/Edit Modal Form */}
        <Modal show={showForm} onHide={handleCloseForm}>
          <Modal.Header closeButton>
            <Modal.Title>{editingId ? 'Edit' : 'Add'} Salary Component</Modal.Title>
          </Modal.Header>
          <Form onSubmit={handleSubmit}>
            <Modal.Body>
              <Form.Group className="mb-3">
                <Form.Label>Name</Form.Label>
                <Form.Control
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Type</Form.Label>
                <Form.Select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                >
                  <option value="earning">Earning</option>
                  <option value="deduction">Deduction</option>
                </Form.Select>
              </Form.Group>

              <Form.Group>
                <Form.Label>Description</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Form.Group>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleCloseForm}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                {editingId ? 'Update' : 'Add'}
              </Button>
            </Modal.Footer>
          </Form>
        </Modal>

        {/* Toast */}
        <Toast
          show={toast.show}
          onClose={() => setToast({ ...toast, show: false })}
          bg={toast.variant}
          className="position-fixed bottom-0 end-0 m-4"
          delay={3000}
          autohide
        >
          <Toast.Body className="text-white">{toast.message}</Toast.Body>
        </Toast>
      </div>
    </PageLayout>
  );
}

export default SalaryComponents;
