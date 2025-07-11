import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getToken } from '../../shared/utils/auth';
import { API_CONFIG } from '../../shared/utils/constants';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Divider,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Avatar,
} from '@mui/material';
import {
  Edit as EditIcon,
  Business as BusinessIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Language as WebsiteIcon,
  Fax as FaxIcon,
} from '@mui/icons-material';

interface BankDetails {
  bank_name: string;
  account_number: string;
  ifsc_code: string;
  account_holder_name: string;
  branch_name?: string;
  account_type?: string;
  masked_account_number?: string;
}

interface ContactInformation {
  email: string;
  phone: string;
  website?: string;
  fax?: string;
}

interface Address {
  street_address: string;
  city: string;
  state: string;
  country: string;
  pin_code: string;
  landmark?: string;
  full_address?: string;
}

interface TaxInformation {
  pan_number: string;
  gst_number?: string;
  tan_number?: string;
  cin_number?: string;
  esi_establishment_id?: string;
  pf_establishment_id?: string;
  is_gst_registered?: boolean;
}

interface Organisation {
  organisation_id: string;
  name: string;
  description?: string;
  organisation_type: string;
  status: string;
  contact_info: ContactInformation;
  address: Address;
  tax_info: TaxInformation;
  employee_strength: number;
  used_employee_strength: number;
  available_capacity: number;
  utilization_percentage: number;
  hostname?: string;
  logo_path?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  is_active: boolean;
  bank_details?: BankDetails;
}

const OrganisationDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [organisation, setOrganisation] = useState<Organisation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrganisationDetails = async () => {
      try {
        const token = getToken();
        if (!token) {
          throw new Error('No authentication token found');
        }

        const response = await axios.get(`${API_CONFIG.BASE_URL}/api/v2/organisations/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setOrganisation(response.data);
        setError(null);
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch organisation details';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchOrganisationDetails();
  }, [id]);

  const handleEdit = () => {
    navigate(`/organisations/edit/${id}`);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box m={2}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!organisation) {
    return (
      <Box m={2}>
        <Alert severity="info">Organisation not found</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center">
          {organisation.logo_path ? (
            <Avatar
              src={`${API_CONFIG.BASE_URL}/${organisation.logo_path}`}
              alt={organisation.name}
              sx={{ 
                width: 80, 
                height: 80, 
                mr: 2,
                border: '1px solid #e0e0e0'
              }}
            />
          ) : (
            <BusinessIcon sx={{ fontSize: 80, mr: 2 }} />
          )}
          <Box>
            <Typography variant="h4">{organisation.name}</Typography>
            <Typography variant="subtitle1" color="textSecondary">
              {organisation.organisation_type}
            </Typography>
          </Box>
        </Box>
        <Box>
          <Chip
            label={organisation.is_active ? 'Active' : 'Inactive'}
            color={organisation.is_active ? 'success' : 'default'}
            sx={{ mr: 2 }}
          />
          <Button
            variant="contained"
            startIcon={<EditIcon />}
            onClick={handleEdit}
          >
            Edit
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="textSecondary">Description</Typography>
                  <Typography>{organisation.description || 'No description provided'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Created At</Typography>
                  <Typography>{new Date(organisation.created_at).toLocaleDateString()}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Last Updated</Typography>
                  <Typography>{new Date(organisation.updated_at).toLocaleDateString()}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Contact Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Box display="flex" alignItems="center">
                    <EmailIcon sx={{ mr: 1 }} />
                    <Typography>{organisation.contact_info.email}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box display="flex" alignItems="center">
                    <PhoneIcon sx={{ mr: 1 }} />
                    <Typography>{organisation.contact_info.phone}</Typography>
                  </Box>
                </Grid>
                {organisation.contact_info.website && (
                  <Grid item xs={12}>
                    <Box display="flex" alignItems="center">
                      <WebsiteIcon sx={{ mr: 1 }} />
                      <Typography>{organisation.contact_info.website}</Typography>
                    </Box>
                  </Grid>
                )}
                {organisation.contact_info.fax && (
                  <Grid item xs={12}>
                    <Box display="flex" alignItems="center">
                      <FaxIcon sx={{ mr: 1 }} />
                      <Typography>{organisation.contact_info.fax}</Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Address */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Address
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex">
                <LocationIcon sx={{ mr: 2, mt: 1 }} />
                <Typography>
                  {organisation.address.street_address}<br />
                  {organisation.address.landmark && `${organisation.address.landmark}, `}
                  {organisation.address.city}, {organisation.address.state}<br />
                  {organisation.address.country} - {organisation.address.pin_code}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Tax Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Tax Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">PAN Number</Typography>
                  <Typography>{organisation.tax_info.pan_number}</Typography>
                </Grid>
                {organisation.tax_info.gst_number && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">GST Number</Typography>
                    <Typography>{organisation.tax_info.gst_number}</Typography>
                  </Grid>
                )}
                {organisation.tax_info.tan_number && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">TAN Number</Typography>
                    <Typography>{organisation.tax_info.tan_number}</Typography>
                  </Grid>
                )}
                {organisation.tax_info.cin_number && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">CIN Number</Typography>
                    <Typography>{organisation.tax_info.cin_number}</Typography>
                  </Grid>
                )}
                {organisation.tax_info.esi_establishment_id && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">ESI Establishment ID</Typography>
                    <Typography>{organisation.tax_info.esi_establishment_id}</Typography>
                  </Grid>
                )}
                {organisation.tax_info.pf_establishment_id && (
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">PF Establishment ID</Typography>
                    <Typography>{organisation.tax_info.pf_establishment_id}</Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Bank Details */}
        {organisation.bank_details && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Bank Details
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">Bank Name</Typography>
                    <Typography>{organisation.bank_details.bank_name}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Account Number</Typography>
                    <Typography>
                      {organisation.bank_details.masked_account_number || organisation.bank_details.account_number}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">IFSC Code</Typography>
                    <Typography>{organisation.bank_details.ifsc_code}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">Account Holder</Typography>
                    <Typography>{organisation.bank_details.account_holder_name}</Typography>
                  </Grid>
                  {organisation.bank_details.branch_name && (
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Branch</Typography>
                      <Typography>{organisation.bank_details.branch_name}</Typography>
                    </Grid>
                  )}
                  {organisation.bank_details.account_type && (
                    <Grid item xs={6}>
                      <Typography variant="body2" color="textSecondary">Account Type</Typography>
                      <Typography>
                        {organisation.bank_details.account_type.split('_')
                          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                          .join(' ')} Account
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Employee Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Employee Statistics
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Total Capacity</Typography>
                  <Typography>{organisation.employee_strength}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Current Employees</Typography>
                  <Typography>{organisation.used_employee_strength}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Available Positions</Typography>
                  <Typography>{organisation.available_capacity}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">Utilization</Typography>
                  <Typography>{organisation.utilization_percentage.toFixed(1)}%</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default OrganisationDetails; 