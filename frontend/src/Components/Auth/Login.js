import React, { useState } from 'react';
import axios from '../../utils/axios';
import { useNavigate, Link } from 'react-router-dom';
import { Button, Form, Container, Row, Col, Card, Alert } from 'react-bootstrap';

const Login = () => {
  const [empId, setEmpId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', empId);
      formData.append('password', password);
      console.log(formData)
      const res = await axios.post('/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      localStorage.setItem('token', res.data.access_token);
      navigate('/home');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    }
  };

  return (
    <Container fluid className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
      <Row>
        <Col md={12}>
          <Card>
            <Card.Header className="text-center">
              <h4>Login</h4>
            </Card.Header>
            <Card.Body>
              {error && <Alert variant="danger">{error}</Alert>}
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Employee ID</Form.Label>
                  <Form.Control type="text" value={empId} onChange={(e) => setEmpId(e.target.value)} required />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Password</Form.Label>
                  <Form.Control type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </Form.Group>
                <div className="d-grid gap-2">
                  <Button type="submit">Login</Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Login;