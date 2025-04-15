import React, { useState } from 'react';
import axiosInstance from '../../utils/axios';

function CreateUser() {
    const [userData, setUserData] = useState({
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
        role: 'user',
    });
    const [errors, setErrors] = useState({});
    const [successMessage, setSuccessMessage] = useState('');

    const handleChange = (event) => {
        const { name, value, type, checked } = event.target;
        setUserData((prevData) => ({
            ...prevData,
            [name]: type === 'checkbox' ? checked : value,
        }));
    };

    const validateForm = () => {
        let isValid = true;
        const newErrors = {};
        if (!userData.empId) {
            newErrors.empId = 'Employee ID is required';
            isValid = false;
        }
        if (!userData.email) {
            newErrors.email = 'Email is required';
            isValid = false;
        }
        if (!userData.name) {
            newErrors.name = 'Name is required';
            isValid = false;
        }

        setErrors(newErrors);
        return isValid;
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (validateForm()) {
            try {
                const response = await axiosInstance.post('/createUser', userData);
                setSuccessMessage(response.data.msg);
                setUserData({
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
                    role: 'user',
                })
                setErrors({});
            } catch (error) {
                setErrors({ submit: error.response?.data?.detail || 'An error occurred.' });
            }
        }
    };

    return (
        <div>
            {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
            {errors.submit && <p style={{ color: 'red' }}>{errors.submit}</p>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Employee ID:</label>
                    <input type="text" name="empId" value={userData.empId} onChange={handleChange} />
                    {errors.empId && <p style={{ color: 'red' }}>{errors.empId}</p>}
                </div>
                <div>
                    <label>Email:</label>
                    <input type="email" name="email" value={userData.email} onChange={handleChange} />
                    {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
                </div>
                <div>
                    <label>Name:</label>
                    <input type="text" name="name" value={userData.name} onChange={handleChange} />
                    {errors.name && <p style={{ color: 'red' }}>{errors.name}</p>}
                </div>
                <div>
                    <label>Gender:</label>
                    <input type="text" name="gender" value={userData.gender} onChange={handleChange} />
                </div>
                <div>
                    <label>Date of Birth:</label>
                    <input type="date" name="dob" value={userData.dob} onChange={handleChange} />
                </div>
                <div>
                    <label>Date of Joining:</label>
                    <input type="date" name="doj" value={userData.doj} onChange={handleChange} />
                </div>
                <div>
                    <label>Mobile:</label>
                    <input type="text" name="mobile" value={userData.mobile} onChange={handleChange} />
                </div>
                <div>
                <button type="submit">Create User</button>
                </div>
            </form>
        </div>
    );
}

export default CreateUser;