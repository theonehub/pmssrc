import apiClient from '../utils/apiClient';

// Helper functions for data mapping between frontend and backend v2 formats
const transformBackendToFrontend = (backendUser) => {
  if (!backendUser) {
    if (process.env.NODE_ENV === 'development') {
      console.warn('No backend user data provided');
    }
    return null;
  }
  // Support both UserResponseDTO (detailed) and UserSummaryDTO (list view)
  const isSummary = !backendUser.personal_details && !backendUser.documents && !backendUser.bank_details;
  const transformed = {
    employee_id: backendUser.employee_id || backendUser.emp_id || '',
    name: backendUser.name || '',
    email: backendUser.email || '',
    mobile: isSummary ? backendUser.mobile || '' : backendUser.personal_details?.mobile || backendUser.mobile || '',
    gender: isSummary ? backendUser.gender || '' : backendUser.personal_details?.gender || backendUser.gender || '',
    date_of_birth: isSummary ? backendUser.date_of_birth || '' : backendUser.personal_details?.date_of_birth || backendUser.date_of_birth || backendUser.dob || '',
    date_of_joining: backendUser.date_of_joining || backendUser.doj || '',
    role: backendUser.role || backendUser.permissions?.role || '',
    department: backendUser.department || '',
    designation: backendUser.designation || '',
    manager_id: backendUser.manager_id || '',
    address: backendUser.address || '',
    emergency_contact: backendUser.emergency_contact || '',
    blood_group: backendUser.blood_group || '',
    location: backendUser.location || '',
    pan_number: isSummary ? backendUser.pan_number || '' : backendUser.personal_details?.pan_number || backendUser.pan_number || '',
    aadhar_number: isSummary ? backendUser.aadhar_number || '' : backendUser.personal_details?.aadhar_number || backendUser.aadhar_number || '',
    uan_number: isSummary ? backendUser.uan_number || '' : backendUser.personal_details?.uan_number || backendUser.uan_number || '',
    esi_number: isSummary ? backendUser.esi_number || '' : backendUser.personal_details?.esi_number || backendUser.esi_number || '',
    created_at: backendUser.created_at || '',
    updated_at: backendUser.updated_at || '',
    is_active: backendUser.is_active !== undefined ? backendUser.is_active : true,
    status: backendUser.status || (backendUser.is_active ? 'active' : 'inactive'),
    profile_picture_url: backendUser.profile_picture_url || '',
    pan_document_path: backendUser.documents?.pan_document_path || backendUser.pan_document_path || '',
    aadhar_document_path: backendUser.documents?.aadhar_document_path || backendUser.aadhar_document_path || '',
    photo_path: backendUser.documents?.photo_path || backendUser.photo_path || '',
    // Bank Details
    account_number: backendUser.bank_details?.account_number || backendUser.account_number || '',
    bank_name: backendUser.bank_details?.bank_name || backendUser.bank_name || '',
    ifsc_code: backendUser.bank_details?.ifsc_code || backendUser.ifsc_code || '',
    account_holder_name: backendUser.bank_details?.account_holder_name || backendUser.account_holder_name || '',
    branch_name: backendUser.bank_details?.branch_name || backendUser.branch_name || '',
    account_type: backendUser.bank_details?.account_type || backendUser.account_type || ''
  };
  return transformed;
};

const transformFrontendToBackend = (frontendUser) => {
  return {
    employee_id: frontendUser.employee_id || frontendUser.emp_id,
    name: frontendUser.name,
    email: frontendUser.email,
    mobile: frontendUser.mobile,
    password: frontendUser.password,
    role: frontendUser.role,
    department: frontendUser.department,
    designation: frontendUser.designation,
    manager_id: frontendUser.manager_id,
    date_of_birth: frontendUser.date_of_birth || frontendUser.dob,
    date_of_joining: frontendUser.date_of_joining || frontendUser.doj,
    gender: frontendUser.gender,
    address: frontendUser.address,
    emergency_contact: frontendUser.emergency_contact,
    blood_group: frontendUser.blood_group,
    location: frontendUser.location,
    pan_number: frontendUser.pan_number,
    aadhar_number: frontendUser.aadhar_number,
    uan_number: frontendUser.uan_number,
    esi_number: frontendUser.esi_number,
    // Bank Details
    account_number: frontendUser.account_number,
    bank_name: frontendUser.bank_name,
    ifsc_code: frontendUser.ifsc_code,
    account_holder_name: frontendUser.account_holder_name,
    branch_name: frontendUser.branch_name,
    account_type: frontendUser.account_type,
  };
};

// Front-end service layer matching back-end FastAPI v2 routes
const dataService = {
  async getUserById(userId) {
    const response = await apiClient.get(`/v2/users/${userId}`);
    const mappedUser = transformBackendToFrontend(response.data);
    
    if (!mappedUser) {
      throw new Error('User data not found or invalid');
    }
    return mappedUser;
  },

  async getUserByEmpIdLegacy(empId, hostname) {
    const response = await apiClient.get(`/v2/users/legacy/${empId}`, {
      params: { hostname }
    });
    const mappedUser = transformBackendToFrontend(response.data);
    if (!mappedUser) {
      throw new Error('User data not found or invalid');
    }
    return mappedUser;
  },

  async updateUserLegacy(empId, userData) {
    const backendData = transformFrontendToBackend(userData);
    const response = await apiClient.put(`/v2/users/${empId}`, backendData);
    return transformBackendToFrontend(response.data);
  },

  async createUserWithFiles(userData, files = {}) {
    const formData = new FormData();
    formData.append('user_data', JSON.stringify(transformFrontendToBackend(userData)));
    
    if (files.pan_file) {
      formData.append('pan_file', files.pan_file);
    }
    if (files.aadhar_file) {
      formData.append('aadhar_file', files.aadhar_file);
    }
    if (files.photo) {
      formData.append('photo', files.photo);
    }

    const response = await apiClient.post('/v2/users/with-files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return transformBackendToFrontend(response.data);
  },

  async createUser(userData) {
    const backendData = transformFrontendToBackend(userData);
    const response = await apiClient.post('/v2/users/create', backendData);
    return transformBackendToFrontend(response.data);
  },

  async importUsers(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/v2/users/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async downloadUserTemplate() {
    const response = await apiClient.get('/v2/users/template', {
      params: { format: 'csv' },
      responseType: 'blob'
    });
    return response.data;
  },
};

export default dataService;
