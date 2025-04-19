import React, { useEffect, useState } from 'react';
import axios from '../../utils/axios';
import { Modal, Button, Form, Table, Spinner, Alert } from 'react-bootstrap';
import PageLayout from '../../layout/PageLayout';

function MyReimbursements () {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ type_id: '', amount: '', note: '', file: null });
  const [types, setTypes] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reqRes, typesRes] = await Promise.all([
        axios.get('/reimbursements/assigned'),
        axios.get('/reimbursement-types')
      ]);
      setRequests(reqRes.data);
      setTypes(typesRes.data);
    } catch (err) {
      setError('Failed to load data.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = new FormData();
    Object.keys(formData).forEach(key => data.append(key, formData[key]));
    try {
      await axios.post('/reimbursements', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setShowModal(false);
      fetchData();
    } catch (err) {
      setError('Failed to submit request.');
    }
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, file: e.target.files[0] });
  };

  return (
    <PageLayout>
      <div className="container mt-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h4>My Reimbursements</h4>
          <Button onClick={() => setShowModal(true)}>+</Button>
        </div>

        {error && <Alert variant="danger">{error}</Alert>}

        {loading ? (
          <Spinner animation="border" />
        ) : (
          <Table bordered hover>
            <thead>
              <tr>
                <th>Type</th>
                <th>Amount</th>
                <th>Note</th>
                <th>Status</th>
                <th>Requested On</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((req) => (
                <tr key={req.id}>
                  <td>{req.type_name}</td>
                  <td>{req.amount}</td>
                  <td>{req.note}</td>
                  <td>{req.status}</td>
                  <td>{req.created_at}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}

        <Modal show={showModal} onHide={() => setShowModal(false)}>
          <Modal.Header closeButton>Submit Reimbursement Request</Modal.Header>
          <Form onSubmit={handleSubmit}>
            <Modal.Body>
              <Form.Select onChange={(e) => setFormData({ ...formData, type_id: e.target.value })} required>
                <option value="">Select Type</option>
                {types.map((type) => <option key={type.id} value={type.id}>{type.name}</option>)}
              </Form.Select>
              <Form.Control type="number" onChange={(e) => setFormData({ ...formData, amount: e.target.value })} placeholder="Amount" className="mt-3" required />
              <Form.Control as="textarea" onChange={(e) => setFormData({ ...formData, note: e.target.value })} placeholder="Note" className="mt-3" required />
              <Form.Control type="file" onChange={handleFileChange} className="mt-3" />
            </Modal.Body>
            <Modal.Footer><Button type="submit">Submit</Button></Modal.Footer>
          </Form>
        </Modal>
      </div>
    </PageLayout>
  );
};

export default MyReimbursements;