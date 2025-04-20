// ViewAssignedSalary.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Modal, Button, Spinner, Alert, Table, TableContainer, TableHead, TableBody, TableRow, TableCell, Box } from "react-bootstrap";
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
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ 
                '& .MuiTableCell-head': { 
                  backgroundColor: 'primary.main',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.875rem',
                  padding: '12px 16px'
                }
              }}>
                <TableCell>Component Name</TableCell>
                <TableCell>Min Amount</TableCell>
                <TableCell>Max Amount</TableCell>
                <TableCell>Editable</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">Loading...</TableCell>
                </TableRow>
              ) : assignedSalary.length > 0 ? (
                assignedSalary.map((item) => (
                  <TableRow 
                    key={item.component_id}
                    sx={{ 
                      '&:hover': { 
                        backgroundColor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <TableCell>{item.component_name}</TableCell>
                    <TableCell>{item.min_amount}</TableCell>
                    <TableCell>{item.max_amount}</TableCell>
                    <TableCell>{item.is_editable ? "Yes" : "No"}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">No salary components assigned yet</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
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