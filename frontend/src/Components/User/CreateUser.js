import React, { useState } from 'react';
import axios from '../../utils/axios';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import PageLayout from '../../layout/PageLayout';

const CreateUser = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    empId: '',
    email: '',
    name: '',
    gender: '',
    dob: '',
    doj: '',
    mobile: '',
    login_required: false,
    username: '',
    password: '',
    role: ''
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Basic validation
    if (!formData.empId) newErrors.empId = 'Employee ID is required';
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.name) newErrors.name = 'Name is required';
    if (!formData.gender) newErrors.gender = 'Gender is required';
    if (!formData.dob) newErrors.dob = 'Date of Birth is required';
    if (!formData.doj) newErrors.doj = 'Date of Joining is required';
    if (!formData.mobile) newErrors.mobile = 'Mobile number is required';

    // Login validation if required
    if (formData.login_required) {
      if (!formData.username) newErrors.username = 'Username is required';
      if (!formData.password) newErrors.password = 'Password is required';
      if (!formData.role) newErrors.role = 'Role is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      const response = await axios.post('/createUser', formData);
      toast.success('User created successfully!');
      navigate('/users');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    }
  };

  return (
    <PageLayout title="Create New User">
      <div className="container-fluid">
        <div className="row justify-content-center">
          <div className="col-md-10">
            <div className="card shadow">
              <div className="card-body">
                <form onSubmit={handleSubmit}>
                  <div className="row">
                    {/* Basic Information */}
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Employee ID *</label>
                      <input
                        type="text"
                        className={`form-control ${errors.empId ? 'is-invalid' : ''}`}
                        name="empId"
                        value={formData.empId}
                        onChange={handleChange}
                      />
                      {errors.empId && <div className="invalid-feedback">{errors.empId}</div>}
                    </div>

                    <div className="col-md-6 mb-3">
                      <label className="form-label">Email *</label>
                      <input
                        type="email"
                        className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                      />
                      {errors.email && <div className="invalid-feedback">{errors.email}</div>}
                    </div>

                    <div className="col-md-6 mb-3">
                      <label className="form-label">Full Name *</label>
                      <input
                        type="text"
                        className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                      />
                      {errors.name && <div className="invalid-feedback">{errors.name}</div>}
                    </div>

                    <div className="col-md-6 mb-3">
                      <label className="form-label">Gender *</label>
                      <select
                        className={`form-select ${errors.gender ? 'is-invalid' : ''}`}
                        name="gender"
                        value={formData.gender}
                        onChange={handleChange}
                      >
                        <option value="">Select Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                      {errors.gender && <div className="invalid-feedback">{errors.gender}</div>}
                    </div>

                    <div className="col-md-6 mb-3">
                      <label className="form-label">Date of Birth *</label>
                      <input
                        type="date"
                        className={`form-control ${errors.dob ? 'is-invalid' : ''}`}
                        name="dob"
                        value={formData.dob}
                        onChange={handleChange}
                      />
                      {errors.dob && <div className="invalid-feedback">{errors.dob}</div>}
                    </div>

                    <div className="col-md-6 mb-3">
                      <label className="form-label">Date of Joining *</label>
                      <input
                        type="date"
                        className={`form-control ${errors.doj ? 'is-invalid' : ''}`}
                        name="doj"
                        value={formData.doj}
                        onChange={handleChange}
                      />
                      {errors.doj && <div className="invalid-feedback">{errors.doj}</div>}
                    </div>

                    <div className="col-md-6 mb-3">
                      <label className="form-label">Mobile Number *</label>
                      <input
                        type="tel"
                        className={`form-control ${errors.mobile ? 'is-invalid' : ''}`}
                        name="mobile"
                        value={formData.mobile}
                        onChange={handleChange}
                      />
                      {errors.mobile && <div className="invalid-feedback">{errors.mobile}</div>}
                    </div>

                    {/* Login Information */}
                    <div className="col-12 mb-3">
                      <div className="form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          name="login_required"
                          checked={formData.login_required}
                          onChange={handleChange}
                        />
                        <label className="form-check-label">Enable Login Access</label>
                      </div>
                    </div>

                    {formData.login_required && (
                      <>
                        <div className="col-md-6 mb-3">
                          <label className="form-label">Username *</label>
                          <input
                            type="text"
                            className={`form-control ${errors.username ? 'is-invalid' : ''}`}
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                          />
                          {errors.username && <div className="invalid-feedback">{errors.username}</div>}
                        </div>

                        <div className="col-md-6 mb-3">
                          <label className="form-label">Password *</label>
                          <input
                            type="password"
                            className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                          />
                          {errors.password && <div className="invalid-feedback">{errors.password}</div>}
                        </div>

                        <div className="col-md-6 mb-3">
                          <label className="form-label">Role *</label>
                          <select
                            className={`form-select ${errors.role ? 'is-invalid' : ''}`}
                            name="role"
                            value={formData.role}
                            onChange={handleChange}
                          >
                            <option value="">Select Role</option>
                            <option value="admin">Admin</option>
                            <option value="superadmin">Super Admin</option>
                            <option value="hr">HR</option>
                            <option value="lead">Lead</option>
                            <option value="user">User</option>
                          </select>
                          {errors.role && <div className="invalid-feedback">{errors.role}</div>}
                        </div>
                      </>
                    )}
                  </div>

                  <div className="d-flex justify-content-between mt-4">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => navigate('/users')}
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary">
                      Create User
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
};

export default CreateUser;