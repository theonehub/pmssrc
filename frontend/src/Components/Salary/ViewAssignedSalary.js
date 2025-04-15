// ViewAssignedSalary.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Modal, Button, Spinner, Alert, Table } from "react-bootstrap";
import { getToken } from "../utils/auth"; // Adjust path as needed

const ViewAssignedSalary = ({ show, onClose, userId }) => {
  const [assignedSalary, setAssignedSalary] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchAssignedSalary = async () => {
    if (!userId) return;

    setLoading(true);
    setError("");
    try {
      const token = getToken();
      const response = await axios.get(
        `http://localhost:8000/employee-salary/${userId}/salary-structure/view`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setAssignedSalary(response.data);
    } catch (err) {
      setError("Failed to fetch assigned salary.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (show) fetchAssignedSalary();
  }, [show, userId]);

  return (
    <Modal show={show} onHide={() => onClose(false)} centered size="lg" scrollable>
      <Modal.Header closeButton>
        <Modal.Title>Assigned Salary Components</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading ? (
          <div className="text-center py-3">
            <Spinner animation="border" />
          </div>
        ) : error ? (
          <Alert variant="danger">{error}</Alert>
        ) : assignedSalary.length === 0 ? (
          <p>No salary components assigned yet.</p>
        ) : (
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
              {assignedSalary.map((item) => (
                <tr key={item.component_id}>
                  <td>{item.component_name}</td>
                  <td>{item.min_amount}</td>
                  <td>{item.max_amount}</td>
                  <td>{item.is_editable ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => onClose(false)}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ViewAssignedSalary;