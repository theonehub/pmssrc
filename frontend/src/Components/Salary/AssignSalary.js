import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import { Modal, Button, Table, Form, Alert } from 'react-bootstrap';

const AssignSalary = ({ show, onClose, userId }) => {
  const [components, setComponents] = useState([]);
  const [assignedComponents, setAssignedComponents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchComponents = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get('http://localhost:8000/salary-components', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setComponents(res.data);
    } catch (err) {
      setError('Failed to fetch salary components.');
    } finally {
      setLoading(false);
    }
  };

  const handleComponentChange = (componentId, field, value) => {
    setAssignedComponents((prev) => {
      const compIndex = prev.findIndex((comp) => comp.component_id === componentId);
      if (compIndex === -1) {
        return [...prev, { component_id: componentId, [field]: value }];
      } else {
        const newComponents = [...prev];
        newComponents[compIndex][field] = value;
        return newComponents;
      }
    });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await axios.post(
        `http://localhost:8000/employee-salary/assign/${userId}`,
        assignedComponents,
        {
          headers: { Authorization: `Bearer ${getToken()}` },
        }
      );
      setSuccess('Salary components assigned successfully!');
    } catch (err) {
      setError('Failed to assign salary components.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (show) fetchComponents();
  }, [show]);

  return (
    <Modal show={show} onHide={onClose} centered size="lg" scrollable>
      <Modal.Header closeButton>
        <Modal.Title>Assign Salary Components</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>Component Name</th>
              <th>Min Amount</th>
              <th>Max Amount</th>
              <th>Editable</th>
            </tr>
          </thead>
          <tbody>
            {components.map((component) => (
              <tr key={component.id}>
                <td>{component.name}</td>
                <td>
                  <Form.Control type="number" onChange={(e) => handleComponentChange(component.id, 'min_amount', e.target.value)} />
                </td>
                <td>
                  <Form.Control type="number" onChange={(e) => handleComponentChange(component.id, 'max_amount', e.target.value)} />
                </td>
                <td>
                  <Form.Check type="checkbox" onChange={(e) => handleComponentChange(component.id, 'is_editable', e.target.checked)} />
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AssignSalary;