import React, { useState } from 'react';
import axios from 'axios';
import { getToken } from '../../utils/auth';
import PageLayout from '../../layout/PageLayout';
import { Button, Form, Spinner, Toast } from 'react-bootstrap';

function UserImport() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', variant: '' });

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setToast({ show: true, message: 'Please select a file to upload.', variant: 'danger' });
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/users/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${getToken()}`,
        },
      });
      setToast({ show: true, message: res.data.message || 'File uploaded successfully.', variant: 'success' });
      setFile(null);
    } catch (error) {
      console.error('Error importing users:', error);
      setToast({ show: true, message: error.response?.data?.message || 'Error uploading file.', variant: 'danger' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageLayout>
      <div className="container mt-4">
        <h3 className="mb-4">Import Users from Excel</h3>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Select Excel File</Form.Label>
            <Form.Control type="file" accept=".xlsx, .xls" onChange={handleFileChange} />
          </Form.Group>
          <Button type="submit" variant="primary" disabled={loading}>
            {loading ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                Uploading...
              </>
            ) : (
              'Upload'
            )}
          </Button>
        </Form>
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

export default UserImport;
