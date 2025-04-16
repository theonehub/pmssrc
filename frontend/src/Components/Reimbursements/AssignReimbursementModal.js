import React, { useState, useEffect } from 'react';
import axios from '../../utils/axios';
import { Modal, Button, Form, Spinner } from 'react-bootstrap';

const AssignReimbursementModal = ({ show, onClose, userId, userName }) => {
  const [reimbursementTypes, setReimbursementTypes] = useState([]);
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchReimbursementTypes = async () => {
      setLoading(true);
      try {
        const res = await axios.get('/reimbursement-types');
        setReimbursementTypes(res.data);
        
        // Fetch current assignments for the user
        const assignmentsRes = await axios.get(`/reimbursements/assignment/user/${userId}`);
        if (assignmentsRes.data && assignmentsRes.data.assigned_reimbursements) {
          setSelectedTypes(assignmentsRes.data.assigned_reimbursements.map(r => r.id));
        }
      } catch (err) {
        console.error('Error fetching reimbursement types:', err);
      } finally {
        setLoading(false);
      }
    };

    if (show) fetchReimbursementTypes();
  }, [show, userId]);

  const handleCheckboxChange = (typeId) => {
    setSelectedTypes(prev => {
      if (prev.includes(typeId)) {
        return prev.filter(id => id !== typeId);
      } else {
        return [...prev, typeId];
      }
    });
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      await axios.post('/reimbursements/assignment/assign', {
        user_id: userId,
        reimbursement_type_ids: selectedTypes
      });
      onClose();
    } catch (err) {
      console.error('Error assigning reimbursement types:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal show={show} onHide={onClose}>
      <Modal.Header closeButton>
        <Modal.Title>Assign Reimbursement Types to {userName}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading ? (
          <div className="text-center py-3"><Spinner animation="border" /></div>
        ) : (
          <Form>
            {reimbursementTypes.map(type => (
              <Form.Check
                key={type.id}
                type="checkbox"
                label={type.name}
                checked={selectedTypes.includes(type.id)}
                onChange={() => handleCheckboxChange(type.id)}
              />
            ))}
          </Form>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>Cancel</Button>
        <Button variant="primary" onClick={handleSubmit} disabled={saving}>
          {saving ? 'Saving...' : 'Save'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AssignReimbursementModal;