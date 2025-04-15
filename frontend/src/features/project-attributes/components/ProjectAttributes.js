import React, { useEffect, useState } from "react";
import { Container, Table, Button, Modal, Form, Alert } from "react-bootstrap";
import PageLayout from "../../../layout/PageLayout";
import { useAuth } from "../../../hooks/useAuth";
import axios from "axios";

const ProjectAttributes = () => {
  const { token, user } = useAuth();
  const [attributes, setAttributes] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ key: "", value: "", default_value: "", description: "" });
  const [editKey, setEditKey] = useState(null);
  const [error, setError] = useState("");

  const isSuperAdmin = user?.role === "superadmin";

  useEffect(() => {
    if (isSuperAdmin) fetchAttributes();
  }, [isSuperAdmin]);

  const fetchAttributes = async () => {
    try {
      const res = await axios.get("http://localhost:8000/attributes", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAttributes(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async () => {
    try {
      if (!form.key || !form.value || !form.default_value) {
        setError("Key, Value and Default Value are required.");
        return;
      }

      if (editKey) {
        await axios.put(`http://localhost:8000/attributes/${editKey}`, form, {
          headers: { Authorization: `Bearer ${token}` },
        });
      } else {
        await axios.post("http://localhost:8000/attributes", form, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }

      setForm({ key: "", value: "", default_value: "", description: "" });
      setShowModal(false);
      setEditKey(null);
      fetchAttributes();
    } catch (err) {
      console.error(err);
      setError("Error saving attribute.");
    }
  };

  const handleEdit = (attr) => {
    setForm(attr);
    setEditKey(attr.key);
    setShowModal(true);
  };

  const handleDelete = async (key) => {
    if (!window.confirm("Are you sure you want to delete this attribute?")) return;
    try {
      await axios.delete(`http://localhost:8000/attributes/${key}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchAttributes();
    } catch (err) {
      console.error(err);
    }
  };

  if (!isSuperAdmin) {
    return (
      <PageLayout>
        <Container className="mt-4">
          <Alert variant="danger">Access Denied</Alert>
        </Container>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <Container className="mt-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h4>Project Attributes</h4>
          <Button variant="primary" onClick={() => setShowModal(true)}>
            + Add Attribute
          </Button>
        </div>

        <Table bordered hover>
          <thead>
            <tr>
              <th>Key</th>
              <th>Value</th>
              <th>Default Value</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {attributes.map((attr) => (
              <tr key={attr.key}>
                <td>{attr.key}</td>
                <td>{attr.value}</td>
                <td>{attr.default_value}</td>
                <td>{attr.description}</td>
                <td>
                  <Button size="sm" variant="info" onClick={() => handleEdit(attr)} className="me-2">
                    Edit
                  </Button>
                  <Button size="sm" variant="danger" onClick={() => handleDelete(attr.key)}>
                    Delete
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Container>

      {/* Add/Edit Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{editKey ? "Edit Attribute" : "Add Attribute"}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && <Alert variant="danger">{error}</Alert>}
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Key</Form.Label>
                <Form.Control
                  type="text"
                  value={form.key}
                  disabled={!!editKey}
                  onChange={(e) => setForm({ ...form, key: e.target.value })}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Value</Form.Label>
                <Form.Control
                  type="text"
                  value={form.value}
                  onChange={(e) => setForm({ ...form, value: e.target.value })}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Default Value</Form.Label>
                <Form.Control
                  type="text"
                  value={form.default_value}
                  onChange={(e) => setForm({ ...form, default_value: e.target.value })}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Description (optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSubmit}>
              {editKey ? "Update" : "Save"}
            </Button>
          </Modal.Footer>
        </Modal>
      </PageLayout>
    );
  };

  export default ProjectAttributes;