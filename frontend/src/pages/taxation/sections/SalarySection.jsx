import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Divider,
  Tooltip
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import { cities } from '../utils/taxationConstants';

/**
 * Salary Section Component
 * @param {Object} props - Component props
 * @param {Object} props.taxationData - Taxation data state
 * @param {Function} props.handleInputChange - Function to handle input change
 * @param {Function} props.handleFocus - Function to handle focus
 * @param {string} props.cityForHRA - Selected city for HRA
 * @param {Function} props.handleCityChange - Function to handle city change
 * @param {boolean} props.autoComputeHRA - Auto compute HRA flag
 * @param {Function} props.setAutoComputeHRA - Function to set auto compute HRA
 * @param {Function} props.handleHRAChange - Function to handle HRA change
 * @param {Function} props.computeHRA - Function to compute HRA
 * @returns {JSX.Element} Salary section component
 */
const SalarySection = ({
  taxationData,
  handleInputChange,
  handleFocus,
  cityForHRA,
  handleCityChange,
  autoComputeHRA,
  setAutoComputeHRA,
  handleHRAChange,
  computeHRA
}) => {
  // Update HRA when basic salary, DA, or city changes
  useEffect(() => {
    if (autoComputeHRA) {
      const calculatedHRA = computeHRA(cities);
      handleInputChange('salary', 'hra', calculatedHRA);
    }
  }, [taxationData.salary.basic, taxationData.salary.dearness_allowance, cityForHRA]);

  return (
    <Box sx={{ py: 2 }}>
      <Box 
        sx={{ 
          width: '100%', 
          display: 'flex',
          justifyContent: 'left'
        }}
      >
      <Typography variant="h5" color="primary">
        Salary Components
      </Typography>
      </Box>
      <Box sx={{ py: 2 }}>
        <Divider sx={{ my: 0, width: '100%' }} />
      </Box>
      
      <Grid container spacing={3}>
        {/* Basic Salary */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Basic Salary"
            type="text"
            value={formatIndianNumber(taxationData.salary.basic)}
            onChange={(e) => handleInputChange('salary', 'basic', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'basic', e.target.value)}
          />
        </Grid>
        
        {/* Dearness Allowance */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Dearness Allowance (DA)"
            type="text"
            value={formatIndianNumber(taxationData.salary.dearness_allowance)}
            onChange={(e) => handleInputChange('salary', 'dearness_allowance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'dearness_allowance', e.target.value)}
          />
        </Grid>
        
        {/* HRA City */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>City Category for HRA</InputLabel>
            <Tooltip title="City Category for HRA"
            placement="top"
            arrow
            >
              <Select
              value={cityForHRA}
              label="City Category for HRA"
              onChange={handleCityChange}
            >
              {cities.map((city) => (
                <MenuItem key={city.value} value={city.value}>
                  {city.label}
                </MenuItem>
              ))}
            </Select>
          </Tooltip>
          </FormControl>
        </Grid>
        
        {/* HRA */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="House Rent Allowance (HRA)"
            type="text"
            value={formatIndianNumber(taxationData.salary.hra)}
            onChange={handleHRAChange}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'hra', e.target.value)}
          />
          <FormControlLabel
            control={
              <Switch
                checked={autoComputeHRA}
                onChange={(e) => setAutoComputeHRA(e.target.checked)}
              />
            }
            label="Auto-calculate HRA"
          />
        </Grid>

        {/* Rent Paid */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Actual Rent Paid"
            type="text"
            value={formatIndianNumber(taxationData.salary.actual_rent_paid)}
            onChange={(e) => handleInputChange('salary', 'actual_rent_paid', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'actual_rent_paid', e.target.value)}
          />
        </Grid>

        {/* Special Allowance */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Special Allowance"
            type="text"
            value={formatIndianNumber(taxationData.salary.special_allowance)}
            onChange={(e) => handleInputChange('salary', 'special_allowance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'special_allowance', e.target.value)}
          />
        </Grid>
        
        {/* Bonus */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Bonus"
            type="text"
            value={formatIndianNumber(taxationData.salary.bonus)}
            onChange={(e) => handleInputChange('salary', 'bonus', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'bonus', e.target.value)}
          />
        </Grid>
        
        {/* Commission */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Commission"
            type="text"
            value={formatIndianNumber(taxationData.salary.commission)}
            onChange={(e) => handleInputChange('salary', 'commission', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'commission', e.target.value)}
          />
        </Grid>
        
        {/* City Compensatory Allowance */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="City Compensatory Allowance"
            type="text"
            value={formatIndianNumber(taxationData.salary.city_compensatory_allowance)}
            onChange={(e) => handleInputChange('salary', 'city_compensatory_allowance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'city_compensatory_allowance', e.target.value)}
          />
        </Grid>
    
        
                        
        {/* Allowances Group */}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Additional Allowances (if applicable)</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        {/* Rural Allowance */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Rural Allowance"
            type="text"
            value={formatIndianNumber(taxationData.salary.rural_allowance)}
            onChange={(e) => handleInputChange('salary', 'rural_allowance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'rural_allowance', e.target.value)}
          />
        </Grid>
        <Grid item xs={12} md={6}>
            <TextField 
              fullWidth 
              label="Proctorship Allowance" 
              type="text" 
              value={formatIndianNumber(taxationData.salary.proctorship_allowance)} 
              onChange={(e) => handleInputChange('salary', 'proctorship_allowance', e.target.value)} 
              InputProps={{ startAdornment: '₹' }} 
            onFocus={(e) => handleFocus('salary', 'proctorship_allowance', e.target.value)}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField 
            fullWidth 
            label="Wardenship Allowance" 
            type="text" 
            value={formatIndianNumber(taxationData.salary.wardenship_allowance)} 
            onChange={(e) => handleInputChange('salary', 'wardenship_allowance', e.target.value)} 
            InputProps={{ startAdornment: '₹' }} 
            onFocus={(e) => handleFocus('salary', 'wardenship_allowance', e.target.value)} />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField 
            fullWidth 
            label="Project Allowance" 
            type="text" 
            value={formatIndianNumber(taxationData.salary.project_allowance)} 
            onChange={(e) => handleInputChange('salary', 'project_allowance', e.target.value)} 
            InputProps={{ startAdornment: '₹' }} 
            onFocus={(e) => handleFocus('salary', 'project_allowance', e.target.value)} />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField 
            fullWidth 
            label="Deputation Allowance" 
            type="text" 
            value={formatIndianNumber(taxationData.salary.deputation_allowance)} 
            onChange={(e) => handleInputChange('salary', 'deputation_allowance', e.target.value)} 
            InputProps={{ startAdornment: '₹' }} 
            onFocus={(e) => handleFocus('salary', 'deputation_allowance', e.target.value)} />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField 
            fullWidth 
            label="Interim Relief" 
            type="text" 
            value={formatIndianNumber(taxationData.salary.interim_relief)} 
            onChange={(e) => handleInputChange('salary', 'interim_relief', e.target.value)} 
            InputProps={{ startAdornment: '₹' }} 
            onFocus={(e) => handleFocus('salary', 'interim_relief', e.target.value)} />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField 
            fullWidth 
            label="Tiffin Allowance" 
            type="text" 
            value={formatIndianNumber(taxationData.salary.tiffin_allowance)} 
            onChange={(e) => handleInputChange('salary', 'tiffin_allowance', e.target.value)} 
            InputProps={{ startAdornment: '₹' }} 
            onFocus={(e) => handleFocus('salary', 'tiffin_allowance', e.target.value)} />
        </Grid>
        {/* Fixed Medical Allowance */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Fixed Medical Allowance"
            type="text"
            value={formatIndianNumber(taxationData.salary.fixed_medical_allowance)}
            onChange={(e) => handleInputChange('salary', 'fixed_medical_allowance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'fixed_medical_allowance', e.target.value)}
          />
        </Grid>
        
        {/* Overtime Allowance */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Overtime Allowance"
            type="text"
            value={formatIndianNumber(taxationData.salary.overtime_allowance)}
            onChange={(e) => handleInputChange('salary', 'overtime_allowance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'overtime_allowance', e.target.value)}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField 
            fullWidth 
            label="Servant Allowance" 
            type="text" 
            value={formatIndianNumber(taxationData.salary.servant_allowance)} 
            onChange={(e) => handleInputChange('salary', 'servant_allowance', e.target.value)} 
            InputProps={{ startAdornment: '₹' }} 
            onFocus={(e) => handleFocus('salary', 'servant_allowance', e.target.value)} />
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Hills/High Altitude Allowance</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        
        {/* Hills/High Altitude Allowance */}
        <Grid item xs={12} md={6}>
          <Tooltip title={
            <>
            Allowance for employees working in hilly areas<br/>
            'Provide Annual Allowance value'
            </>
            }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Hills/High Altitude Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.hills_high_altd_allowance)}
              onChange={(e) => handleInputChange('salary', 'hills_high_altd_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'hills_high_altd_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip 
            title={
              <>
                Exemption limit for Hills/High Altitude Allowance<br/>
                '₹ 800 for specific hills/high altitude areas'<br/>
                '₹ 7000 for Siachen'<br/>
                '₹ 300 for other high altitude areas'<br/>
                'Provide Annual Allowance value'<br/>
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Hills/High Altitude Allowance Exemption Limit"
              type="text"
              value={formatIndianNumber(taxationData.salary.hills_high_altd_exemption_limit)}
              onChange={(e) => handleInputChange('salary', 'hills_high_altd_exemption_limit', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'hills_high_altd_exemption_limit', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Border/Remote Area Allowance</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance for employees working in border or remote areas<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Border/Remote Area Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.border_remote_allowance)}
              onChange={(e) => handleInputChange('salary', 'border_remote_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'border_remote_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Exemption limit for Border/Remote Area Allowance<br/>
                '₹ 200 to 1300 per month as per Rule 2BB'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Border/Remote Area Allowance Exemption Limit"
              type="text"
              value={formatIndianNumber(taxationData.salary.border_remote_exemption_limit)}
              onChange={(e) => handleInputChange('salary', 'border_remote_exemption_limit', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'border_remote_exemption_limit', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Employee Transportation Allowance</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance for Employees Transportation<br/>
                'Max Limit: 10000 or 70% of the actual expenditure'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Transport Employee Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.transport_employee_allowance)}
              onChange={(e) => handleInputChange('salary', 'transport_employee_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'transport_employee_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Children Education Allowance</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance for Children Education<br/>
                'Max Limit: 100 per child per month'<br/>
                'Provide Annual Allowance value for both children'<br/>
                'Provide Number of Children (max 2)'<br/>
                'Provide Number of Months (max 12)'<br/>
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Children Education Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.children_education_allowance)}
              onChange={(e) => handleInputChange('salary', 'children_education_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'children_education_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title="Children Count"
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Children Count"
              type="text"
              value={formatIndianNumber(taxationData.salary.children_education_count)}
              onChange={(e) => handleInputChange('salary', 'children_education_count', e.target.value)}
              onFocus={(e) => handleFocus('salary', 'children_education_count', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title="Children Education Months"
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Children Education Months"
              type="text"
              value={formatIndianNumber(taxationData.salary.children_education_months)}
              onChange={(e) => handleInputChange('salary', 'children_education_months', e.target.value)}
              onFocus={(e) => handleFocus('salary', 'children_education_months', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Hostel Allowance for Children</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance for Hostel Expenses<br/>
                'Max Limit: 300 per child per month'<br/>
                'Provide Annual Allowance value for both children'<br/>
                'Provide Number of Children (max 2)'<br/>
                'Provide Number of Months (max 12)'<br/>
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Hostel Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.hostel_allowance)}
              onChange={(e) => handleInputChange('salary', 'hostel_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'hostel_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>

        <Grid item xs={12} md={6}>
          <Tooltip title="Count of Children"
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Count of Children"
              type="text"
              value={formatIndianNumber(taxationData.salary.hostel_count)}
              onChange={(e) => handleInputChange('salary', 'hostel_count', e.target.value)}
              onFocus={(e) => handleFocus('salary', 'hostel_count', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title="Months for Hostel Allowance"
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Months for Hostel Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.hostel_months)} 
              onChange={(e) => handleInputChange('salary', 'hostel_months', e.target.value)}
              onFocus={(e) => handleFocus('salary', 'hostel_months', e.target.value)}
            />
          </Tooltip>
        </Grid>
        
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Transport Allowance</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance for Transportation's Employee<br/>
                'Max Limit: 3200 per month'<br/>
                'Provide Annual Allowance value'<br/>
                'Provide Number of Months (max 12)'<br/>
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Transport Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.transport_allowance)}
              onChange={(e) => handleInputChange('salary', 'transport_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'transport_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title="Months for Transport Allowance"
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Months for Transport Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.transport_months)}
              onChange={(e) => handleInputChange('salary', 'transport_months', e.target.value)}
              onFocus={(e) => handleFocus('salary', 'transport_months', e.target.value)}
            />
          </Tooltip>
        </Grid>

        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Underground Mines Allowance</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />

        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance for employees working in underground mines<br/>
                'Max Limit: 800 per month'<br/>
                'Provide Annual Allowance value'<br/>
                'Provide Number of Months (max 12)'<br/>
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Underground Mines Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.underground_mines_allowance)}
              onChange={(e) => handleInputChange('salary', 'underground_mines_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'underground_mines_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
            <Tooltip title="Months for Underground Mines Allowance"
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Months for Underground Mines Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.underground_mines_months)}
              onChange={(e) => handleInputChange('salary', 'underground_mines_months', e.target.value)}
              onFocus={(e) => handleFocus('salary', 'underground_mines_months', e.target.value)}
            />
          </Tooltip>
        </Grid>
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Entertainment Allowance</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance for Entertainment<br/>
                'Max Limit: 5000 or 2% of the basic salary(Govt Employees only)'<br/>
                'Provide Annual Allowance value'<br/>
              </>
              }
            placement="top"
            arrow
            >
            <TextField
              fullWidth
              label="Entertainment Allowance"
              type="text"
              value={formatIndianNumber(taxationData.salary.govt_employee_entertainment_allowance)}
              onChange={(e) => handleInputChange('salary', 'govt_employee_entertainment_allowance', e.target.value)}
              InputProps={{ startAdornment: '₹' }}
              onFocus={(e) => handleFocus('salary', 'govt_employee_entertainment_allowance', e.target.value)}
            />
          </Tooltip>
        </Grid>
        {/* Govt Employee - related fields could be conditionally rendered based on is_govt_employee flag */}
        {taxationData.is_govt_employee && (
          <>
            <Box 
              sx={{ 
                width: '100%', 
                display: 'flex',
                justifyContent: 'left'
              }}
            >
              <Typography variant="h6" color="primary">Government Employee Allowances</Typography>
            </Box>
            <Divider sx={{ my: 0, width: '100%' }} />
            {/* Government-specific allowances */}
            <Grid item xs={12} md={6}>
              <Tooltip title={
                <>
                Govt Employees Outside India Allowance<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
                </>
                }
                placement="top"
                arrow
                >
                <TextField 
                  fullWidth 
                  label="Outside India Employee Allowance" 
                  type="text" 
                  value={formatIndianNumber(taxationData.salary.govt_employees_outside_india_allowance)} 
                  onChange={(e) => handleInputChange('salary', 'govt_employees_outside_india_allowance', e.target.value)} 
                  InputProps={{ startAdornment: '₹' }} 
                  onFocus={(e) => handleFocus('salary', 'govt_employees_outside_india_allowance', e.target.value)} 
                />
              </Tooltip>
            </Grid>
            <Grid item xs={12} md={6}>
              <Tooltip title={
                <>
                High Court and Supreme Court Judges Allowance<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
                </>
                }
                placement="top"
                arrow
                >
                <TextField 
                  fullWidth 
                  label="HC/SC Judges Allowance" 
                  type="text" 
                  value={formatIndianNumber(taxationData.salary.supreme_high_court_judges_allowance)} 
                  onChange={(e) => handleInputChange('salary', 'supreme_high_court_judges_allowance', e.target.value)} 
                  InputProps={{ startAdornment: '₹' }} 
                  onFocus={(e) => handleFocus('salary', 'supreme_high_court_judges_allowance', e.target.value)} 
                />
              </Tooltip>
            </Grid>
            <Grid item xs={12} md={6}>
              <Tooltip title={
                <>
                Compensatory Allowance received by a Judge.<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
                </>
                }
                placement="top"
                arrow
                >
                <TextField 
                  fullWidth 
                  label="Judge Compensatory Allowance" 
                  type="text" 
                  value={formatIndianNumber(taxationData.salary.judge_compensatory_allowance)} 
                  onChange={(e) => handleInputChange('salary', 'judge_compensatory_allowance', e.target.value)} 
                  InputProps={{ startAdornment: '₹' }} 
                  onFocus={(e) => handleFocus('salary', 'judge_compensatory_allowance', e.target.value)} 
                />
              </Tooltip>
            </Grid>
            <Grid item xs={12} md={6}>
              <Tooltip title={
                <>
                Section 10(14) Special Allowances<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
                </>
                }
                placement="top"
                arrow
                >
                <TextField 
                  fullWidth 
                  label="Section 10(14) Special Allowances" 
                  type="text" 
                  value={formatIndianNumber(taxationData.salary.section_10_14_special_allowances)} 
                  onChange={(e) => handleInputChange('salary', 'section_10_14_special_allowances', e.target.value)} 
                  InputProps={{ startAdornment: '₹' }} 
                  onFocus={(e) => handleFocus('salary', 'section_10_14_special_allowances', e.target.value)} 
                />
              </Tooltip>
            </Grid>
          </>
        )}
        
                        
        {/* Duty Related Allowances */}
        <Box 
          sx={{ 
            width: '100%', 
            display: 'flex',
            justifyContent: 'left'
          }}
        >
          <Typography variant="h6" color="primary">Duty Related Allowances</Typography>
        </Box>
        <Divider sx={{ my: 0, width: '100%' }} />
        
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance granted to meet cost of travel on tour.<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField 
              fullWidth 
              label="Travel Allowance (Tour)" 
              type="text" 
              value={formatIndianNumber(taxationData.salary.travel_on_tour_allowance)} 
              onChange={(e) => handleInputChange('salary', 'travel_on_tour_allowance', e.target.value)} 
              InputProps={{ startAdornment: '₹' }} 
              onFocus={(e) => handleFocus('salary', 'travel_on_tour_allowance', e.target.value)} 
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance granted to meet cost of daily charges incurred on tour.<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField 
              fullWidth 
              label="Tour Daily Charge Allowance" 
              type="text" 
              value={formatIndianNumber(taxationData.salary.tour_daily_charge_allowance)} 
              onChange={(e) => handleInputChange('salary', 'tour_daily_charge_allowance', e.target.value)} 
              InputProps={{ startAdornment: '₹' }} 
              onFocus={(e) => handleFocus('salary', 'tour_daily_charge_allowance', e.target.value)} 
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance granted to meet expenditure incurred on conveyance in performace of duties.<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField 
              fullWidth 
              label="Conveyance Allowance (Duties)" 
              type="text" 
              value={formatIndianNumber(taxationData.salary.conveyance_in_performace_of_duties)} 
              onChange={(e) => handleInputChange('salary', 'conveyance_in_performace_of_duties', e.target.value)} 
              InputProps={{ startAdornment: '₹' }} 
              onFocus={(e) => handleFocus('salary', 'conveyance_in_performace_of_duties', e.target.value)} 
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance granted to meet expenditure incurred on helper in performace of duties.<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField 
              fullWidth 
              label="Helper Allowance (Duties)" 
              type="text" 
              value={formatIndianNumber(taxationData.salary.helper_in_performace_of_duties)} 
              onChange={(e) => handleInputChange('salary', 'helper_in_performace_of_duties', e.target.value)} 
              InputProps={{ startAdornment: '₹' }} 
              onFocus={(e) => handleFocus('salary', 'helper_in_performace_of_duties', e.target.value)} 
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance granted for encouraging the academic, research & training pursuits in educational & research institutions.<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField 
              fullWidth 
              label="Academic/Research Allowance" 
              type="text" 
              value={formatIndianNumber(taxationData.salary.academic_research)} 
              onChange={(e) => handleInputChange('salary', 'academic_research', e.target.value)} 
              InputProps={{ startAdornment: '₹' }} 
              onFocus={(e) => handleFocus('salary', 'academic_research', e.target.value)} 
            />
          </Tooltip>
        </Grid>
        <Grid item xs={12} md={6}>
          <Tooltip title={
              <>
                Allowance granted for expenditure incurred on purchase or maintenance of uniform for wear during performace of duties.<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
              }
            placement="top"
            arrow
            >
            <TextField 
              fullWidth 
              label="Uniform Allowance (Duties)" 
              type="text" 
              value={formatIndianNumber(taxationData.salary.uniform_allowance)} 
              onChange={(e) => handleInputChange('salary', 'uniform_allowance', e.target.value)} 
              InputProps={{ startAdornment: '₹' }} 
              onFocus={(e) => handleFocus('salary', 'uniform_allowance', e.target.value)} 
            />
          </Tooltip>
        </Grid>
        {/* Any Other Allowance */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Any Other Allowance"
            type="text"
            value={formatIndianNumber(taxationData.salary.any_other_allowance)}
            onChange={(e) => handleInputChange('salary', 'any_other_allowance', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'any_other_allowance', e.target.value)}
          />
        </Grid>
        
        {/* Any Other Allowance Exemption */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Any Other Allowance Exemption"
            type="text"
            value={formatIndianNumber(taxationData.salary.any_other_allowance_exemption)}
            onChange={(e) => handleInputChange('salary', 'any_other_allowance_exemption', e.target.value)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleFocus('salary', 'any_other_allowance_exemption', e.target.value)}
          />
        </Grid>
      </Grid>
      
    </Box>
  );
};

export default SalarySection; 