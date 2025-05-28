import React, { useEffect, useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Checkbox,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Container,
  CircularProgress,
  Box,
  IconButton,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  SelectChangeEvent
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../../utils/apiUtils';
import PageLayout from '../../layout/PageLayout';

// Define interfaces
interface LeaveType {
  code: string;
  name: string;
  category: string;
}

interface LeavePolicy {
  annual_allocation: number;
  accrual_type: string;
  max_carryover_days: number | null;
  min_advance_notice_days: number;
  max_continuous_days: number | null;
  requires_approval: boolean;
  auto_approve_threshold: number | null;
  requires_medical_certificate: boolean;
  medical_certificate_threshold: number | null;
  is_encashable: boolean;
  max_encashment_days: number | null;
  available_during_probation: boolean;
  probation_allocation: number | null;
  gender_specific: string | null;
}

interface CompanyLeave {
  company_leave_id: string;
  leave_type: LeaveType;
  policy: LeavePolicy;
  description: string;
  effective_from?: string | null;
  is_active: boolean;
}

interface FormData {
  leave_type_code: string;
  leave_type_name: string;
  leave_category: string;
  annual_allocation: number;
  description: string;
  accrual_type: string;
  max_carryover_days: number | null;
  min_advance_notice_days: number;
  max_continuous_days: number | null;
  requires_approval: boolean;
  auto_approve_threshold: number | null;
  requires_medical_certificate: boolean;
  medical_certificate_threshold: number | null;
  is_encashable: boolean;
  max_encashment_days: number | null;
  available_during_probation: boolean;
  probation_allocation: number | null;
  gender_specific: string | null;
  effective_from: string | null;
}

interface DropdownOption {
  value: string;
  label: string;
}

interface GenderOption {
  value: string | null;
  label: string;
}

const CompanyLeaves: React.FC = () => {
  const [leaves, setLeaves] = useState<CompanyLeave[]>([]);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [formData, setFormData] = useState<FormData>({
    leave_type_code: '',
    leave_type_name: '',
    leave_category: 'casual',
    annual_allocation: 0,
    description: '',
    accrual_type: 'annually',
    max_carryover_days: null,
    min_advance_notice_days: 1,
    max_continuous_days: null,
    requires_approval: true,
    auto_approve_threshold: null,
    requires_medical_certificate: false,
    medical_certificate_threshold: null,
    is_encashable: false,
    max_encashment_days: null,
    available_during_probation: true,
    probation_allocation: null,
    gender_specific: null,
    effective_from: null,
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Options for dropdowns
  const leaveCategories: DropdownOption[] = [
    { value: 'annual', label: 'Annual' },
    { value: 'sick', label: 'Sick' },
    { value: 'casual', label: 'Casual' },
    { value: 'maternity', label: 'Maternity' },
    { value: 'paternity', label: 'Paternity' },
    { value: 'emergency', label: 'Emergency' },
    { value: 'compensatory', label: 'Compensatory' },
    { value: 'sabbatical', label: 'Sabbatical' },
    { value: 'unpaid', label: 'Unpaid' },
    { value: 'bereavement', label: 'Bereavement' },
    { value: 'study', label: 'Study' },
    { value: 'religious', label: 'Religious' }
  ];

  const accrualTypes: DropdownOption[] = [
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'annually', label: 'Annually' },
    { value: 'immediate', label: 'Immediate' },
    { value: 'none', label: 'None' }
  ];

  const genderOptions: GenderOption[] = [
    { value: null, label: 'All Genders' },
    { value: 'male', label: 'Male Only' },
    { value: 'female', label: 'Female Only' }
  ];

  const fetchLeaves = async (): Promise<void> => {
    try {
      const res = await api.get('/api/v2/company-leaves');
      setLeaves(res.data || []);
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching company leaves', err);
      }
      setError('Failed to load company leaves.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaves();
  }, []);

  const resetFormData = (): void => {
    setFormData({
      leave_type_code: '',
      leave_type_name: '',
      leave_category: 'casual',
      annual_allocation: 0,
      description: '',
      accrual_type: 'annually',
      max_carryover_days: null,
      min_advance_notice_days: 1,
      max_continuous_days: null,
      requires_approval: true,
      auto_approve_threshold: null,
      requires_medical_certificate: false,
      medical_certificate_threshold: null,
      is_encashable: false,
      max_encashment_days: null,
      available_during_probation: true,
      probation_allocation: null,
      gender_specific: null,
      effective_from: null,
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      // Prepare request data according to backend DTO
      const requestData = {
        leave_type_code: formData.leave_type_code.toUpperCase(),
        leave_type_name: formData.leave_type_name,
        leave_category: formData.leave_category,
        annual_allocation: parseInt(String(formData.annual_allocation)) || 0,
        description: formData.description || null,
        accrual_type: formData.accrual_type,
        max_carryover_days: formData.max_carryover_days ? parseInt(String(formData.max_carryover_days)) : null,
        min_advance_notice_days: formData.min_advance_notice_days ? parseInt(String(formData.min_advance_notice_days)) : null,
        max_continuous_days: formData.max_continuous_days ? parseInt(String(formData.max_continuous_days)) : null,
        requires_approval: formData.requires_approval,
        auto_approve_threshold: formData.auto_approve_threshold ? parseInt(String(formData.auto_approve_threshold)) : null,
        requires_medical_certificate: formData.requires_medical_certificate,
        medical_certificate_threshold: formData.medical_certificate_threshold ? parseInt(String(formData.medical_certificate_threshold)) : null,
        is_encashable: formData.is_encashable,
        max_encashment_days: formData.max_encashment_days ? parseInt(String(formData.max_encashment_days)) : null,
        available_during_probation: formData.available_during_probation,
        probation_allocation: formData.probation_allocation ? parseInt(String(formData.probation_allocation)) : null,
        gender_specific: formData.gender_specific,
        effective_from: formData.effective_from || null,
      };

      if (editingId) {
        // For update, we need to use the update DTO structure
        const updateData = {
          leave_type_name: requestData.leave_type_name,
          annual_allocation: requestData.annual_allocation,
          description: requestData.description,
          max_carryover_days: requestData.max_carryover_days,
          min_advance_notice_days: requestData.min_advance_notice_days,
          max_continuous_days: requestData.max_continuous_days,
          requires_approval: requestData.requires_approval,
          auto_approve_threshold: requestData.auto_approve_threshold,
          requires_medical_certificate: requestData.requires_medical_certificate,
          medical_certificate_threshold: requestData.medical_certificate_threshold,
          is_encashable: requestData.is_encashable,
          max_encashment_days: requestData.max_encashment_days,
          available_during_probation: requestData.available_during_probation,
          probation_allocation: requestData.probation_allocation,
        };
        await api.put(`/api/v2/company-leaves/${editingId}`, updateData);
      } else {
        await api.post('/api/v2/company-leaves', requestData);
      }
      setShowModal(false);
      resetFormData();
      setEditingId(null);
      fetchLeaves();
    } catch (err: any) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error saving company leave', err);
      }
      setError('Failed to save company leave.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (leave: CompanyLeave): void => {
    // Transform backend response to form format
    let effectiveFromDate: string | null = null;
    if (leave.effective_from && typeof leave.effective_from === 'string') {
      const datePart = leave.effective_from.split('T')[0];
      effectiveFromDate = datePart || null;
    }
    
    setFormData({
      leave_type_code: leave.leave_type?.code || '',
      leave_type_name: leave.leave_type?.name || '',
      leave_category: leave.leave_type?.category || 'casual',
      annual_allocation: leave.policy?.annual_allocation || 0,
      description: leave.description || '',
      accrual_type: leave.policy?.accrual_type || 'annually',
      max_carryover_days: leave.policy?.max_carryover_days || null,
      min_advance_notice_days: leave.policy?.min_advance_notice_days || 1,
      max_continuous_days: leave.policy?.max_continuous_days || null,
      requires_approval: leave.policy?.requires_approval ?? true,
      auto_approve_threshold: leave.policy?.auto_approve_threshold || null,
      requires_medical_certificate: leave.policy?.requires_medical_certificate ?? false,
      medical_certificate_threshold: leave.policy?.medical_certificate_threshold || null,
      is_encashable: leave.policy?.is_encashable ?? false,
      max_encashment_days: leave.policy?.max_encashment_days || null,
      available_during_probation: leave.policy?.available_during_probation ?? true,
      probation_allocation: leave.policy?.probation_allocation || null,
      gender_specific: leave.policy?.gender_specific || null,
      effective_from: effectiveFromDate,
    });
    setEditingId(leave.company_leave_id);
    setShowModal(true);
  };

  const handleDelete = async (id: string): Promise<void> => {
    if (window.confirm('Are you sure you want to delete this company leave?')) {
      try {
        await api.delete(`/api/v2/company-leaves/${id}`);
        fetchLeaves();
      } catch (err: any) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Error deleting company leave', err);
        }
        setError('Failed to delete company leave.');
      }
    }
  };

  const handleFormDataChange = (field: keyof FormData, value: any): void => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSelectChange = (e: SelectChangeEvent<string>, field: keyof FormData): void => {
    handleFormDataChange(field, e.target.value);
  };

  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>, field: keyof FormData): void => {
    const value = e.target.value ? parseInt(e.target.value) : null;
    handleFormDataChange(field, value);
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>, field: keyof FormData): void => {
    handleFormDataChange(field, e.target.checked);
  };

  const handleCloseModal = (): void => {
    setShowModal(false);
    resetFormData();
    setEditingId(null);
  };

  return (
    <PageLayout title="Company Leave Policies">
      <Container maxWidth="xl">
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4">Company Leave Policies</Typography>
          <Button variant="contained" color="primary" onClick={() => setShowModal(true)}>
            Add New Leave Policy
          </Button>
        </Box>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
            <CircularProgress color="primary" />
          </Box>
        ) : (
          <TableContainer component={Paper} sx={{ mt: 2 }}>
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
                  <TableCell>Code</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Annual Allocation</TableCell>
                  <TableCell>Requires Approval</TableCell>
                  <TableCell>Encashable</TableCell>
                  <TableCell>During Probation</TableCell>
                  <TableCell>Active</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {leaves.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      No leave policies defined.
                    </TableCell>
                  </TableRow>
                ) : (
                  leaves.map((leave) => (
                    <TableRow key={leave.company_leave_id}>
                      <TableCell>{leave.leave_type?.code || 'N/A'}</TableCell>
                      <TableCell>{leave.leave_type?.name || 'N/A'}</TableCell>
                      <TableCell sx={{ textTransform: 'capitalize' }}>
                        {leave.leave_type?.category || 'N/A'}
                      </TableCell>
                      <TableCell>{leave.policy?.annual_allocation || 0} days</TableCell>
                      <TableCell>{leave.policy?.requires_approval ? 'Yes' : 'No'}</TableCell>
                      <TableCell>{leave.policy?.is_encashable ? 'Yes' : 'No'}</TableCell>
                      <TableCell>{leave.policy?.available_during_probation ? 'Yes' : 'No'}</TableCell>
                      <TableCell>{leave.is_active ? 'Yes' : 'No'}</TableCell>
                      <TableCell>
                        <IconButton 
                          color="primary" 
                          onClick={() => handleEdit(leave)}
                          size="small"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton 
                          color="error" 
                          onClick={() => handleDelete(leave.company_leave_id)}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Dialog 
          open={showModal} 
          onClose={handleCloseModal}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>{editingId ? 'Edit' : 'Add'} Company Leave Policy</DialogTitle>
          <DialogContent>
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, 
                gap: 2 
              }}>
                {/* Basic Information */}
                <Box>
                  <TextField
                    required
                    fullWidth
                    label="Leave Type Code"
                    placeholder="e.g. CL, SL, AL"
                    value={formData.leave_type_code}
                    onChange={(e) => handleFormDataChange('leave_type_code', e.target.value.toUpperCase())}
                    inputProps={{ maxLength: 10 }}
                    disabled={!!editingId} // Don't allow editing code for existing leaves
                  />
                </Box>
                <Box>
                  <TextField
                    required
                    fullWidth
                    label="Leave Type Name"
                    placeholder="e.g. Casual Leave, Sick Leave"
                    value={formData.leave_type_name}
                    onChange={(e) => handleFormDataChange('leave_type_name', e.target.value)}
                    inputProps={{ maxLength: 100 }}
                  />
                </Box>
                
                <Box>
                  <FormControl fullWidth required>
                    <InputLabel>Leave Category</InputLabel>
                    <Select
                      value={formData.leave_category}
                      onChange={(e) => handleSelectChange(e, 'leave_category')}
                      label="Leave Category"
                      disabled={!!editingId} // Don't allow editing category for existing leaves
                    >
                      {leaveCategories.map((category) => (
                        <MenuItem key={category.value} value={category.value}>
                          {category.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
                
                <Box>
                  <TextField
                    required
                    fullWidth
                    type="number"
                    label="Annual Allocation"
                    placeholder="Number of days per year"
                    value={formData.annual_allocation}
                    onChange={(e) => handleFormDataChange('annual_allocation', parseInt(e.target.value) || 0)}
                    inputProps={{ min: 0, max: 365 }}
                  />
                </Box>

                <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    label="Description"
                    placeholder="Optional description of the leave policy"
                    value={formData.description}
                    onChange={(e) => handleFormDataChange('description', e.target.value)}
                  />
                </Box>

                {/* Policy Configuration */}
                <Box>
                  <FormControl fullWidth>
                    <InputLabel>Accrual Type</InputLabel>
                    <Select
                      value={formData.accrual_type}
                      onChange={(e) => handleSelectChange(e, 'accrual_type')}
                      label="Accrual Type"
                    >
                      {accrualTypes.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Carryover Days"
                    placeholder="Optional"
                    value={formData.max_carryover_days || ''}
                    onChange={(e) => handleNumberChange(e, 'max_carryover_days')}
                    inputProps={{ min: 0 }}
                  />
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="number"
                    label="Min Advance Notice Days"
                    value={formData.min_advance_notice_days || ''}
                    onChange={(e) => handleFormDataChange('min_advance_notice_days', parseInt(e.target.value) || 1)}
                    inputProps={{ min: 0 }}
                  />
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Continuous Days"
                    placeholder="Optional"
                    value={formData.max_continuous_days || ''}
                    onChange={(e) => handleNumberChange(e, 'max_continuous_days')}
                    inputProps={{ min: 1 }}
                  />
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="number"
                    label="Auto Approve Threshold"
                    placeholder="Days (Optional)"
                    value={formData.auto_approve_threshold || ''}
                    onChange={(e) => handleNumberChange(e, 'auto_approve_threshold')}
                    inputProps={{ min: 1 }}
                  />
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="number"
                    label="Medical Certificate Threshold"
                    placeholder="Days (Optional)"
                    value={formData.medical_certificate_threshold || ''}
                    onChange={(e) => handleNumberChange(e, 'medical_certificate_threshold')}
                    inputProps={{ min: 1 }}
                  />
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="number"
                    label="Max Encashment Days"
                    placeholder="Optional"
                    value={formData.max_encashment_days || ''}
                    onChange={(e) => handleNumberChange(e, 'max_encashment_days')}
                    inputProps={{ min: 0 }}
                    disabled={!formData.is_encashable}
                  />
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="number"
                    label="Probation Allocation"
                    placeholder="Days (Optional)"
                    value={formData.probation_allocation || ''}
                    onChange={(e) => handleNumberChange(e, 'probation_allocation')}
                    inputProps={{ min: 0 }}
                    disabled={!formData.available_during_probation}
                  />
                </Box>

                <Box>
                  <FormControl fullWidth>
                    <InputLabel>Gender Specific</InputLabel>
                    <Select
                      value={formData.gender_specific || ''}
                      onChange={(e) => handleFormDataChange('gender_specific', e.target.value || null)}
                      label="Gender Specific"
                    >
                      {genderOptions.map((option) => (
                        <MenuItem key={option.value || 'all'} value={option.value || ''}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>

                <Box>
                  <TextField
                    fullWidth
                    type="date"
                    label="Effective From"
                    value={formData.effective_from || ''}
                    onChange={(e) => handleFormDataChange('effective_from', e.target.value || null)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>

                {/* Checkboxes */}
                <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    <FormControlLabel
                      control={
                        <Checkbox 
                          checked={formData.requires_approval} 
                          onChange={(e) => handleCheckboxChange(e, 'requires_approval')} 
                        />
                      }
                      label="Requires Approval"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox 
                          checked={formData.requires_medical_certificate} 
                          onChange={(e) => handleCheckboxChange(e, 'requires_medical_certificate')} 
                        />
                      }
                      label="Requires Medical Certificate"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox 
                          checked={formData.is_encashable} 
                          onChange={(e) => handleCheckboxChange(e, 'is_encashable')} 
                        />
                      }
                      label="Encashable"
                    />
                    <FormControlLabel
                      control={
                        <Checkbox 
                          checked={formData.available_during_probation} 
                          onChange={(e) => handleCheckboxChange(e, 'available_during_probation')} 
                        />
                      }
                      label="Available During Probation"
                    />
                  </Box>
                </Box>
              </Box>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button 
              onClick={(e: any) => handleSubmit(e)} 
              type="submit" 
              variant="contained" 
              color="primary" 
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : (editingId ? 'Update' : 'Save')}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </PageLayout>
  );
};

export default CompanyLeaves; 