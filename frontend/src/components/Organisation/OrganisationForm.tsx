import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Divider,
  Alert
} from '@mui/material';
import { EmptyOrganisation } from '../../models/organisation';
import type { Organisation } from '../../models/organisation';

interface OrganisationFormProps {
  organisation?: Organisation;
  onSubmit: (data: Organisation) => Promise<void>;
}

const OrganisationForm: React.FC<OrganisationFormProps> = ({
  organisation = EmptyOrganisation,
  onSubmit
}) => {
  // Simple flat state to avoid nested update issues
  const [name, setName] = useState(organisation.name || '');
  const [hostname, setHostname] = useState(organisation.hostname || '');
  const [description, setDescription] = useState(organisation.description || '');
  const [organisationType, setOrganisationType] = useState(organisation.organisation_type || 'private_limited');
  const [status, setStatus] = useState(organisation.status || 'active');
  const [employeeStrength, setEmployeeStrength] = useState(organisation.employee_strength?.toString() || '10');
  const [isActive, setIsActive] = useState(organisation.is_active !== undefined ? organisation.is_active : true);
  
  // Contact info
  const [email, setEmail] = useState(organisation.contact_info?.email || '');
  const [phone, setPhone] = useState(organisation.contact_info?.phone || '');
  const [website, setWebsite] = useState(organisation.contact_info?.website || '');
  
  // Address info
  const [address, setAddress] = useState(organisation.address?.street_address || '');
  const [city, setCity] = useState(organisation.address?.city || '');
  const [state, setState] = useState(organisation.address?.state || '');
  const [country, setCountry] = useState(organisation.address?.country || '');
  const [pinCode, setPinCode] = useState(organisation.address?.pin_code || '');
  
  // Tax info
  const [panNumber, setPanNumber] = useState(organisation.tax_info?.pan_number || '');
  const [gstNumber, setGstNumber] = useState(organisation.tax_info?.gst_number || '');
  const [tanNumber, setTanNumber] = useState(organisation.tax_info?.tan_number || '');
  
  // Bank details
  const [bankName, setBankName] = useState(organisation.bank_details?.bank_name || '');
  const [accountNumber, setAccountNumber] = useState(organisation.bank_details?.account_number || '');
  const [ifscCode, setIfscCode] = useState(organisation.bank_details?.ifsc_code || '');
  const [branchName, setBranchName] = useState(organisation.bank_details?.branch_name || '');
  const [branchAddress, setBranchAddress] = useState(organisation.bank_details?.branch_address || '');
  const [accountType, setAccountType] = useState(organisation.bank_details?.account_type || '');
  const [accountHolderName, setAccountHolderName] = useState(organisation.bank_details?.account_holder_name || '');
  
  // Error states - individual for each field
  const [nameError, setNameError] = useState('');
  const [hostnameError, setHostnameError] = useState('');
  const [employeeStrengthError, setEmployeeStrengthError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [websiteError, setWebsiteError] = useState('');
  const [addressError, setAddressError] = useState('');
  const [cityError, setCityError] = useState('');
  const [countryError, setCountryError] = useState('');
  const [pinCodeError, setPinCodeError] = useState('');
  const [panNumberError, setPanNumberError] = useState('');
  const [gstNumberError, setGstNumberError] = useState('');
  const [tanNumberError, setTanNumberError] = useState('');
  const [bankNameError, setBankNameError] = useState('');
  const [accountNumberError, setAccountNumberError] = useState('');
  const [ifscCodeError, setIfscCodeError] = useState('');
  const [branchNameError, setBranchNameError] = useState('');
  const [branchAddressError, setBranchAddressError] = useState('');
  const [accountHolderNameError, setAccountHolderNameError] = useState('');
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  // Validation functions
  const validateRequired = (value: string, fieldName: string): string => {
    return !value.trim() ? `${fieldName} is required` : '';
  };

  const validateEmail = (email: string): string => {
    if (!email.trim()) return '';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return !emailRegex.test(email) ? 'Invalid email format' : '';
  };

  const validatePhone = (phone: string): string => {
    if (!phone.trim()) return '';
    const phoneRegex = /^[0-9+\-\s()]*$/;
    return !phoneRegex.test(phone) ? 'Invalid phone number format' : '';
  };

  const validateWebsite = (website: string): string => {
    if (!website.trim()) return '';
    const websiteRegex = /^https?:\/\/.+/;
    return !websiteRegex.test(website) ? 'Website must start with http:// or https://' : '';
  };

  const validatePinCode = (pinCode: string): string => {
    if (!pinCode.trim()) return '';
    const pinCodeRegex = /^\d{6}$/;
    return !pinCodeRegex.test(pinCode) ? 'Pin code must be 6 digits' : '';
  };

  const validatePAN = (pan: string): string => {
    if (!pan.trim()) return 'PAN number is required';
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return !panRegex.test(pan) ? 'Invalid PAN format (e.g., ABCDE1234F)' : '';
  };

  const validateGST = (gst: string): string => {
    if (!gst.trim()) return '';
    const gstRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
    return !gstRegex.test(gst) ? 'Invalid GST format (e.g., 22AAAAA0000A1Z5)' : '';
  };

  const validateTAN = (tan: string): string => {
    if (!tan.trim()) return '';
    const tanRegex = /^[A-Z]{4}[0-9]{5}[A-Z]{1}$/;
    return !tanRegex.test(tan) ? 'Invalid TAN format (e.g., ABCD12345E)' : '';
  };

  const validateIFSC = (ifsc: string): string => {
    if (!ifsc.trim()) return 'IFSC code is required';
    const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/;
    return !ifscRegex.test(ifsc.toUpperCase()) ? 'Invalid IFSC format (e.g., SBIN0001234)' : '';
  };

  const validateAccountNumber = (accountNumber: string): string => {
    if (!accountNumber.trim()) return 'Account number is required';
    const accountRegex = /^\d{9,18}$/;
    return !accountRegex.test(accountNumber) ? 'Account number must be 9-18 digits' : '';
  };

  const validateBankName = (bankName: string): string => {
    return !bankName.trim() ? 'Bank name is required' : '';
  };

  const validateBranchName = (branchName: string): string => {
    return !branchName.trim() ? 'Branch name is required' : '';
  };

  const validateBranchAddress = (branchAddress: string): string => {
    return !branchAddress.trim() ? 'Branch address is required' : '';
  };

  const validateAccountHolderName = (accountHolderName: string): string => {
    return !accountHolderName.trim() ? 'Account holder name is required' : '';
  };

  const validateEmployeeStrength = (value: string): string => {
    if (!value.trim()) return 'Employee strength is required';
    const num = parseInt(value);
    if (isNaN(num) || num <= 0) return 'Employee strength must be a positive number';
    return '';
  };

  // Real-time validation handlers
  const handleNameChange = (value: string) => {
    setName(value);
    setNameError(validateRequired(value, 'Organisation name'));
  };

  const handleHostnameChange = (value: string) => {
    setHostname(value);
    setHostnameError(validateRequired(value, 'Hostname'));
  };

  const handleEmployeeStrengthChange = (value: string) => {
    setEmployeeStrength(value);
    setEmployeeStrengthError(validateEmployeeStrength(value));
  };

  const handleEmailChange = (value: string) => {
    setEmail(value);
    setEmailError(validateEmail(value));
  };

  const handlePhoneChange = (value: string) => {
    setPhone(value);
    setPhoneError(validatePhone(value));
  };

  const handleWebsiteChange = (value: string) => {
    setWebsite(value);
    setWebsiteError(validateWebsite(value));
  };

  const handleAddressChange = (value: string) => {
    setAddress(value);
    setAddressError(validateRequired(value, 'Address'));
  };

  const handleCityChange = (value: string) => {
    setCity(value);
    setCityError(validateRequired(value, 'City'));
  };

  const handleCountryChange = (value: string) => {
    setCountry(value);
    setCountryError(validateRequired(value, 'Country'));
  };

  const handlePinCodeChange = (value: string) => {
    setPinCode(value);
    setPinCodeError(validatePinCode(value));
  };

  const handlePanNumberChange = (value: string) => {
    const upperValue = value.toUpperCase();
    setPanNumber(upperValue);
    setPanNumberError(validatePAN(upperValue));
  };

  const handleGstNumberChange = (value: string) => {
    const upperValue = value.toUpperCase();
    setGstNumber(upperValue);
    setGstNumberError(validateGST(upperValue));
  };

  const handleTanNumberChange = (value: string) => {
    const upperValue = value.toUpperCase();
    setTanNumber(upperValue);
    setTanNumberError(validateTAN(upperValue));
  };

  const handleIfscCodeChange = (value: string) => {
    const upperValue = value.toUpperCase();
    setIfscCode(upperValue);
    setIfscCodeError(validateIFSC(upperValue));
  };

  const handleAccountNumberChange = (value: string) => {
    setAccountNumber(value);
    setAccountNumberError(validateAccountNumber(value));
  };

  const handleBankNameChange = (value: string) => {
    setBankName(value);
    setBankNameError(validateBankName(value));
  };

  const handleBranchNameChange = (value: string) => {
    setBranchName(value);
    setBranchNameError(validateBranchName(value));
  };

  const handleBranchAddressChange = (value: string) => {
    setBranchAddress(value);
    setBranchAddressError(validateBranchAddress(value));
  };

  const handleAccountHolderNameChange = (value: string) => {
    setAccountHolderName(value);
    setAccountHolderNameError(validateAccountHolderName(value));
  };

  // Form validation
  const validateForm = (): boolean => {
    let isValid = true;
    
    // Validate required fields
    const nameErr = validateRequired(name, 'Organisation name');
    const hostnameErr = validateRequired(hostname, 'Hostname');
    const addressErr = validateRequired(address, 'Address');
    const cityErr = validateRequired(city, 'City');
    const countryErr = validateRequired(country, 'Country');
    const employeeStrengthErr = validateEmployeeStrength(employeeStrength);
    const panErr = validatePAN(panNumber);
    
    // Validate bank details
    const bankNameErr = validateBankName(bankName);
    const accountNumberErr = validateAccountNumber(accountNumber);
    const ifscErr = validateIFSC(ifscCode);
    const branchNameErr = validateBranchName(branchName);
    const branchAddressErr = validateBranchAddress(branchAddress);
    const accountHolderNameErr = validateAccountHolderName(accountHolderName);
    
    // Validate optional but formatted fields
    const emailErr = validateEmail(email);
    const phoneErr = validatePhone(phone);
    const websiteErr = validateWebsite(website);
    const pinCodeErr = validatePinCode(pinCode);
    const gstErr = validateGST(gstNumber);
    const tanErr = validateTAN(tanNumber);

    // Set all errors
    setNameError(nameErr);
    setHostnameError(hostnameErr);
    setAddressError(addressErr);
    setCityError(cityErr);
    setCountryError(countryErr);
    setEmployeeStrengthError(employeeStrengthErr);
    setPanNumberError(panErr);
    setEmailError(emailErr);
    setPhoneError(phoneErr);
    setWebsiteError(websiteErr);
    setPinCodeError(pinCodeErr);
    setGstNumberError(gstErr);
    setTanNumberError(tanErr);
    setBankNameError(bankNameErr);
    setAccountNumberError(accountNumberErr);
    setIfscCodeError(ifscErr);
    setBranchNameError(branchNameErr);
    setBranchAddressError(branchAddressErr);
    setAccountHolderNameError(accountHolderNameErr);

    // Check if any errors exist
    if (nameErr || hostnameErr || addressErr || cityErr || countryErr || 
        employeeStrengthErr || panErr || emailErr || phoneErr || websiteErr || 
        pinCodeErr || gstErr || tanErr || bankNameErr || accountNumberErr || 
        ifscErr || branchNameErr || branchAddressErr || accountHolderNameErr) {
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    
    if (!validateForm()) {
      setSubmitError('Please fix the errors above before submitting.');
      return;
    }
    
    setIsSubmitting(true);
    try {
      // Construct the nested Organisation object
      const organisationData: Organisation = {
        ...organisation,
        name,
        hostname,
        description,
        organisation_type: organisationType,
        status,
        employee_strength: parseInt(employeeStrength) || 10,
        is_active: isActive,
        contact_info: {
          ...organisation.contact_info,
          email,
          phone,
          website,
          fax: organisation.contact_info?.fax || '',
        },
        address: {
          ...organisation.address,
          street_address: address,
          city,
          state,
          country,
          pin_code: pinCode,
          landmark: organisation.address?.landmark || '',
        },
        tax_info: {
          ...organisation.tax_info,
          pan_number: panNumber,
          gst_number: gstNumber,
          tan_number: tanNumber,
          cin_number: organisation.tax_info?.cin_number || '',
        },
        bank_details: {
          ...organisation.bank_details,
          bank_name: bankName,
          account_number: accountNumber,
          ifsc_code: ifscCode,
          branch_name: branchName,
          branch_address: branchAddress,
          account_type: accountType,
          account_holder_name: accountHolderName,
        }
      };
      
      await onSubmit(organisationData);
    } catch (error: any) {
      console.error('Submit error:', error);
      setSubmitError(error.message || 'An error occurred while saving. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        {organisation.organisation_id ? 'Edit Organisation' : 'Create Organisation'}
      </Typography>

      {submitError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {submitError}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        
        {/* Basic Information */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Basic Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="Organisation Name"
              value={name}
              onChange={(e) => handleNameChange(e.target.value)}
              error={!!nameError}
              helperText={nameError}
              required
            />
            
            <TextField
              fullWidth
              label="Hostname"
              value={hostname}
              onChange={(e) => handleHostnameChange(e.target.value)}
              error={!!hostnameError}
              helperText={hostnameError}
              required
              placeholder="e.g., company.com"
            />
            
            <TextField
              select
              fullWidth
              label="Organisation Type"
              value={organisationType}
              onChange={(e) => setOrganisationType(e.target.value)}
            >
              <MenuItem value="private_limited">Private Limited</MenuItem>
              <MenuItem value="public_limited">Public Limited</MenuItem>
              <MenuItem value="partnership">Partnership</MenuItem>
              <MenuItem value="sole_proprietorship">Sole Proprietorship</MenuItem>
              <MenuItem value="llp">Limited Liability Partnership</MenuItem>
            </TextField>
            
            <TextField
              select
              fullWidth
              label="Status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
              <MenuItem value="deleted">Deleted</MenuItem>
            </TextField>
            
            <TextField
              fullWidth
              label="Employee Strength"
              type="number"
              value={employeeStrength}
              onChange={(e) => handleEmployeeStrengthChange(e.target.value)}
              error={!!employeeStrengthError}
              helperText={employeeStrengthError}
              required
              inputProps={{ min: 1 }}
            />
          </Box>
          
          <TextField
            fullWidth
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={3}
            placeholder="Brief description of the organisation..."
            sx={{ mt: 2 }}
          />
        </Box>

        {/* Contact Information */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Contact Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => handleEmailChange(e.target.value)}
              error={!!emailError}
              helperText={emailError}
            />
            
            <TextField
              fullWidth
              label="Phone"
              value={phone}
              onChange={(e) => handlePhoneChange(e.target.value)}
              error={!!phoneError}
              helperText={phoneError}
            />
            
            <TextField
              fullWidth
              label="Website"
              value={website}
              onChange={(e) => handleWebsiteChange(e.target.value)}
              error={!!websiteError}
              helperText={websiteError}
              placeholder="https://www.example.com"
              sx={{ gridColumn: { md: 'span 2' } }}
            />
          </Box>
        </Box>

        {/* Address Information */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Address Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Address"
              value={address}
              onChange={(e) => handleAddressChange(e.target.value)}
              error={!!addressError}
              helperText={addressError}
              multiline
              rows={2}
              required
            />
            
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
              <TextField
                fullWidth
                label="City"
                value={city}
                onChange={(e) => handleCityChange(e.target.value)}
                error={!!cityError}
                helperText={cityError}
                required
              />
              
              <TextField
                fullWidth
                label="State/Province"
                value={state}
                onChange={(e) => setState(e.target.value)}
              />
              
              <TextField
                fullWidth
                label="Country"
                value={country}
                onChange={(e) => handleCountryChange(e.target.value)}
                error={!!countryError}
                helperText={countryError}
                required
              />
              
              <TextField
                fullWidth
                label="Pin Code"
                value={pinCode}
                onChange={(e) => handlePinCodeChange(e.target.value)}
                error={!!pinCodeError}
                helperText={pinCodeError}
                placeholder="123456"
              />
            </Box>
          </Box>
        </Box>

        {/* Tax Information */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Tax & Legal Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="PAN Number"
              value={panNumber}
              onChange={(e) => handlePanNumberChange(e.target.value)}
              error={!!panNumberError}
              helperText={panNumberError}
              placeholder="ABCDE1234F"
              required
            />
            
            <TextField
              fullWidth
              label="GST Number"
              value={gstNumber}
              onChange={(e) => handleGstNumberChange(e.target.value)}
              error={!!gstNumberError}
              helperText={gstNumberError}
              placeholder="22AAAAA0000A1Z5"
            />
            
            <TextField
              fullWidth
              label="TAN Number"
              value={tanNumber}
              onChange={(e) => handleTanNumberChange(e.target.value)}
              error={!!tanNumberError}
              helperText={tanNumberError}
              placeholder="ABCD12345E"
            />
          </Box>
        </Box>

        {/* Bank Details */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Bank Details
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="Bank Name"
              value={bankName}
              onChange={(e) => handleBankNameChange(e.target.value)}
              error={!!bankNameError}
              helperText={bankNameError}
              required
            />
            
            <TextField
              fullWidth
              label="Account Number"
              value={accountNumber}
              onChange={(e) => handleAccountNumberChange(e.target.value)}
              error={!!accountNumberError}
              helperText={accountNumberError}
              required
            />
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="IFSC Code"
              value={ifscCode}
              onChange={(e) => handleIfscCodeChange(e.target.value)}
              error={!!ifscCodeError}
              helperText={ifscCodeError}
              required
            />
            
            <TextField
              fullWidth
              label="Branch Name"
              value={branchName}
              onChange={(e) => handleBranchNameChange(e.target.value)}
              error={!!branchNameError}
              helperText={branchNameError}
              required
            />
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="Branch Address"
              value={branchAddress}
              onChange={(e) => handleBranchAddressChange(e.target.value)}
              error={!!branchAddressError}
              helperText={branchAddressError}
              multiline
              rows={2}
              required
            />
            
            <TextField
              select
              fullWidth
              label="Account Type"
              value={accountType}
              onChange={(e) => setAccountType(e.target.value)}
            >
              <MenuItem value="savings">Savings</MenuItem>
              <MenuItem value="current">Current</MenuItem>
              <MenuItem value="fixed_deposit">Fixed Deposit</MenuItem>
              <MenuItem value="recurring_deposit">Recurring Deposit</MenuItem>
            </TextField>
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <TextField
              fullWidth
              label="Account Holder Name"
              value={accountHolderName}
              onChange={(e) => handleAccountHolderNameChange(e.target.value)}
              error={!!accountHolderNameError}
              helperText={accountHolderNameError}
              required
            />
          </Box>
        </Box>

        {/* Status */}
        <Box>
          <Typography variant="h6" color="primary" gutterBottom>
            Status
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <FormControlLabel
            control={
              <Checkbox
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                color="primary"
              />
            }
            label="Organisation is active"
          />
        </Box>

        {/* Submit Button */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', pt: 2 }}>
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isSubmitting}
            sx={{ minWidth: 150 }}
          >
            {isSubmitting ? 'Saving...' : (organisation.organisation_id ? 'Update' : 'Create')} Organisation
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default OrganisationForm;