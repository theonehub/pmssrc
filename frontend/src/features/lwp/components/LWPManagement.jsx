import React, { useEffect, useState } from 'react';
import { Button, Container, Table, Form, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { getToken } from '../../../utils/auth';
import PageLayout from '../../../layout/PageLayout';
import * as XLSX from 'xlsx';

const LWPManagement = () => {
  const [lwpRecords, setLwpRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({ message: '', type: '' });
  const [isUpdatingBulk, setIsUpdatingBulk] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [updateStatus, setUpdateStatus] = useState({ message: '', type: '' });

  useEffect(() => {
    fetchLWPRecords();
  }, []);

  const fetchLWPRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/lwp', {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setLwpRecords(response.data);
    } catch (err) {
      setError('Failed to fetch LWP records.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLWP = async (id, presentDays) => {
    setUpdateStatus({ message: '', type: '' });
    try {
      await axios.put(`http://localhost:8000/lwp/${id}`, { present_days: presentDays }, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setUpdateStatus({ message: 'LWP updated successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err) {
      setUpdateStatus({ message: 'Failed to update LWP.', type: 'danger' });
    }
  };

  const handleBulkUpdate = async () => {
    setIsUpdatingBulk(true);
    setUpdateStatus({ message: '', type: '' });
    try {
      await axios.post('http://localhost:8000/lwp/update-bulk', lwpRecords, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setUpdateStatus({ message: 'Bulk LWP updated successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err) {
      setUpdateStatus({ message: 'Failed to bulk update LWP.', type: 'danger' });
    } finally {
      setIsUpdatingBulk(false);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setUploadStatus({ message: 'Please select a file.', type: 'danger' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/lwp/import', formData, {
        headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'multipart/form-data' },
      });
      setUploadStatus({ message: response.data.msg || 'LWP data imported successfully.', type: 'success' });
      fetchLWPRecords();
    } catch (err) {
      setUploadStatus({ message: 'Failed to import LWP data.', type: 'danger' });
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const response = await axios.get('http://localhost:8000/lwp/export', {
        headers: { Authorization: `Bearer ${getToken()}` },
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `LWP_Export_${new Date().toISOString()}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting data:', err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <PageLayout>
      <Container>
        <h3 className="mt-4 mb-4">LWP Management</h3>
        {/* Existing LWP Records */}
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Employee Name</th>
              <th>Month</th>
              <th>Year</th>
              <th>Present Days</th>
            </tr>
          </thead>
          <tbody>
            {lwpRecords.map((record) => (
              <tr key={record.id}>
                <td>{record.employee_name}</td>
                <td>{record.month}</td>
                <td>{record.year}</td>
                <td>
                  <Form.Control type="number" value={record.present_days} onChange={(e) => {
                    const newPresentDays = parseInt(e.target.value, 10);
                    setLwpRecords(lwpRecords.map(r => r.id === record.id ? { ...r, present_days: newPresentDays } : r));
                  }} />
                </td>
                <td>
                  <Button size="sm" onClick={() => handleUpdateLWP(record.id, record.present_days)}>Update</Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
        {updateStatus.message && (
          <Alert variant={updateStatus.type}>{updateStatus.message}</Alert>
        )}
        {/* Bulk Update Button */}
        <Button className="mt-3" variant="warning" onClick={handleBulkUpdate} disabled={isUpdatingBulk}>
          {isUpdatingBulk ? (
            <>
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
              Updating...
            </>
          ) : (
            'Update Bulk'
          )}
        </Button>
        {/* Import/Export Section */}
        <h4 className="mt-5">Import/Export LWP Data</h4>
        {/* Export Button */}
        <Button className="mb-3" variant="outline-success" onClick={handleExport} disabled={isExporting}>
          {isExporting ? (
            <>
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
              Exporting...
            </>
          ) : (
            'Export'
          )}
        </Button>
        {/* Import Section */}
        <Form.Group className="mb-3">
          <Form.Label>Import LWP Data</Form.Label>
          <Form.Control type="file" accept=".xlsx, .xls" onChange={(e) => setFile(e.target.files[0])} />
        </Form.Group>
        <Button onClick={handleImport}>Import</Button>
        {uploadStatus.message && (
          <Alert variant={uploadStatus.type} className="mt-3">{uploadStatus.message}</Alert>
        )}
      </Container>
    </PageLayout>
  );
};

export default LWPManagement;