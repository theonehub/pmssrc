import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Divider,
  Tooltip,
  SelectChangeEvent
} from '@mui/material';
import { formatIndianNumber } from '../utils/taxationUtils';
import { cities } from '../utils/taxationConstants';
import { TaxationData } from '../../../types';

interface SalarySectionProps {
  taxationData: TaxationData;
  handleInputChange: (section: string, field: string, value: string | number | boolean) => void;
  handleFocus: (section: string, field: string, value: string | number) => void;
  cityForHRA: string;
  handleCityChange: (event: SelectChangeEvent<string>) => void;
  autoComputeHRA: boolean;
  setAutoComputeHRA: (value: boolean) => void;
  handleHRAChange: (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  computeHRA: (cities: any) => number;
}

/**
 * Salary Section Component for comprehensive salary components management
 */
const SalarySection: React.FC<SalarySectionProps> = ({
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
  // Type-safe event handlers
  const handleTextFieldChange = (section: string, field: string, event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleInputChange(section, field, event.target.value);
  };

  const handleTextFieldFocus = (section: string, field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    handleFocus(section, field, event.target.value);
  };

  const handleSwitchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setAutoComputeHRA(event.target.checked);
  };

  // Update HRA when basic salary, DA, or city changes
  useEffect(() => {
    if (autoComputeHRA) {
      const calculatedHRA = computeHRA(cities);
      handleInputChange('salary', 'hra', calculatedHRA);
    }
  }, [taxationData.salary.basic, taxationData.salary.dearness_allowance, cityForHRA, autoComputeHRA, computeHRA, handleInputChange]);

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
      
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 3,
          width: '100%'
        }}
      >
        {/* Basic Salary */}
        <TextField
          fullWidth
          label="Basic Salary"
          type="text"
          value={formatIndianNumber(taxationData.salary.basic)}
          onChange={(e) => handleTextFieldChange('salary', 'basic', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'basic', e)}
        />
        
        {/* Dearness Allowance */}
        <TextField
          fullWidth
          label="Dearness Allowance (DA)"
          type="text"
          value={formatIndianNumber(taxationData.salary.dearness_allowance)}
          onChange={(e) => handleTextFieldChange('salary', 'dearness_allowance', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'dearness_allowance', e)}
        />
        
        {/* HRA City */}
        <FormControl fullWidth>
          <InputLabel>City Category for HRA</InputLabel>
          <Box>
            <Tooltip title="City Category for HRA" placement="top" arrow>
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
          </Box>
        </FormControl>
        
        {/* HRA */}
        <Box>
          <TextField
            fullWidth
            label="House Rent Allowance (HRA)"
            type="text"
            value={formatIndianNumber(taxationData.salary.hra)}
            onChange={handleHRAChange}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'hra', e)}
          />
          <FormControlLabel
            control={
              <Switch
                checked={autoComputeHRA}
                onChange={handleSwitchChange}
              />
            }
            label="Auto-calculate HRA"
          />
        </Box>

        {/* Rent Paid */}
        <TextField
          fullWidth
          label="Actual Rent Paid"
          type="text"
          value={formatIndianNumber(taxationData.salary.actual_rent_paid)}
          onChange={(e) => handleTextFieldChange('salary', 'actual_rent_paid', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'actual_rent_paid', e)}
        />

        {/* Special Allowance */}
        <TextField
          fullWidth
          label="Special Allowance"
          type="text"
          value={formatIndianNumber(taxationData.salary.special_allowance)}
          onChange={(e) => handleTextFieldChange('salary', 'special_allowance', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'special_allowance', e)}
        />
        
        {/* Bonus */}
        <TextField
          fullWidth
          label="Bonus"
          type="text"
          value={formatIndianNumber(taxationData.salary.bonus)}
          onChange={(e) => handleTextFieldChange('salary', 'bonus', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'bonus', e)}
        />
        
        {/* Commission */}
        <TextField
          fullWidth
          label="Commission"
          type="text"
          value={formatIndianNumber(taxationData.salary.commission)}
          onChange={(e) => handleTextFieldChange('salary', 'commission', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'commission', e)}
        />
        
        {/* City Compensatory Allowance */}
        <TextField
          fullWidth
          label="City Compensatory Allowance"
          type="text"
          value={formatIndianNumber(taxationData.salary.city_compensatory_allowance)}
          onChange={(e) => handleTextFieldChange('salary', 'city_compensatory_allowance', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'city_compensatory_allowance', e)}
        />

        {/* Section Header: Additional Allowances */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Additional Allowances (if applicable)</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>
        
        {/* Rural Allowance */}
        <TextField
          fullWidth
          label="Rural Allowance"
          type="text"
          value={formatIndianNumber(taxationData.salary.rural_allowance)}
          onChange={(e) => handleTextFieldChange('salary', 'rural_allowance', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'rural_allowance', e)}
        />

        <TextField 
          fullWidth 
          label="Proctorship Allowance" 
          type="text" 
          value={formatIndianNumber(taxationData.salary.proctorship_allowance)} 
          onChange={(e) => handleTextFieldChange('salary', 'proctorship_allowance', e)}
          InputProps={{ startAdornment: '₹' }} 
          onFocus={(e) => handleTextFieldFocus('salary', 'proctorship_allowance', e)}
        />

        <TextField 
          fullWidth 
          label="Wardenship Allowance" 
          type="text" 
          value={formatIndianNumber(taxationData.salary.wardenship_allowance)} 
          onChange={(e) => handleTextFieldChange('salary', 'wardenship_allowance', e)}
          InputProps={{ startAdornment: '₹' }} 
          onFocus={(e) => handleTextFieldFocus('salary', 'wardenship_allowance', e)}
        />

        <TextField 
          fullWidth 
          label="Project Allowance" 
          type="text" 
          value={formatIndianNumber(taxationData.salary.project_allowance)} 
          onChange={(e) => handleTextFieldChange('salary', 'project_allowance', e)}
          InputProps={{ startAdornment: '₹' }} 
          onFocus={(e) => handleTextFieldFocus('salary', 'project_allowance', e)}
        />

        <TextField 
          fullWidth 
          label="Deputation Allowance" 
          type="text" 
          value={formatIndianNumber(taxationData.salary.deputation_allowance)} 
          onChange={(e) => handleTextFieldChange('salary', 'deputation_allowance', e)}
          InputProps={{ startAdornment: '₹' }} 
          onFocus={(e) => handleTextFieldFocus('salary', 'deputation_allowance', e)}
        />

        <TextField 
          fullWidth 
          label="Interim Relief" 
          type="text" 
          value={formatIndianNumber(taxationData.salary.interim_relief)} 
          onChange={(e) => handleTextFieldChange('salary', 'interim_relief', e)}
          InputProps={{ startAdornment: '₹' }} 
          onFocus={(e) => handleTextFieldFocus('salary', 'interim_relief', e)}
        />

        <TextField 
          fullWidth 
          label="Tiffin Allowance" 
          type="text" 
          value={formatIndianNumber(taxationData.salary.tiffin_allowance)} 
          onChange={(e) => handleTextFieldChange('salary', 'tiffin_allowance', e)}
          InputProps={{ startAdornment: '₹' }} 
          onFocus={(e) => handleTextFieldFocus('salary', 'tiffin_allowance', e)}
        />

        {/* Fixed Medical Allowance */}
        <TextField
          fullWidth
          label="Fixed Medical Allowance"
          type="text"
          value={formatIndianNumber(taxationData.salary.fixed_medical_allowance)}
          onChange={(e) => handleTextFieldChange('salary', 'fixed_medical_allowance', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'fixed_medical_allowance', e)}
        />
        
        {/* Overtime Allowance */}
        <TextField
          fullWidth
          label="Overtime Allowance"
          type="text"
          value={formatIndianNumber(taxationData.salary.overtime_allowance)}
          onChange={(e) => handleTextFieldChange('salary', 'overtime_allowance', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'overtime_allowance', e)}
        />

        <TextField 
          fullWidth 
          label="Servant Allowance" 
          type="text" 
          value={formatIndianNumber(taxationData.salary.servant_allowance)} 
          onChange={(e) => handleTextFieldChange('salary', 'servant_allowance', e)}
          InputProps={{ startAdornment: '₹' }} 
          onFocus={(e) => handleTextFieldFocus('salary', 'servant_allowance', e)}
        />

        {/* Section Header: Hills/High Altitude Allowance */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Hills/High Altitude Allowance</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>
        
        {/* Hills/High Altitude Allowance */}
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
            onChange={(e) => handleTextFieldChange('salary', 'hills_high_altd_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'hills_high_altd_allowance', e)}
          />
        </Tooltip>

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
            onChange={(e) => handleTextFieldChange('salary', 'hills_high_altd_exemption_limit', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'hills_high_altd_exemption_limit', e)}
          />
        </Tooltip>

        {/* Section Header: Border/Remote Area Allowance */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Border/Remote Area Allowance</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>

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
            onChange={(e) => handleTextFieldChange('salary', 'border_remote_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'border_remote_allowance', e)}
          />
        </Tooltip>

        <Tooltip 
          title={
            <>
              Exemption limit for Border/Remote Area Allowance<br/>
              '₹ 100 per month for remote areas'<br/>
              '₹ 300 per month for border areas'<br/>
              'Provide Annual Allowance value'<br/>
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
            onChange={(e) => handleTextFieldChange('salary', 'border_remote_exemption_limit', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'border_remote_exemption_limit', e)}
          />
        </Tooltip>

        {/* Section Header: Transport Employee Allowance */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Transport Employee Allowance</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>

        <Tooltip title={
          <>
            Allowance for transport employees<br/>
            'No Max Limit'<br/>
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
            onChange={(e) => handleTextFieldChange('salary', 'transport_employee_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'transport_employee_allowance', e)}
          />
        </Tooltip>

        {/* Section Header: Children Education Allowance */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Children Education Allowance</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>

        <Tooltip title={
          <>
            Education allowance for children<br/>
            '₹ 100 per month per child (max 2 children)'<br/>
            'Provide Annual Allowance value'
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
            onChange={(e) => handleTextFieldChange('salary', 'children_education_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'children_education_allowance', e)}
          />
        </Tooltip>

        <TextField
          fullWidth
          label="Number of Children"
          type="text"
          value={formatIndianNumber(taxationData.salary.children_education_count)}
          onChange={(e) => handleTextFieldChange('salary', 'children_education_count', e)}
          onFocus={(e) => handleTextFieldFocus('salary', 'children_education_count', e)}
        />

        <TextField
          fullWidth
          label="Number of Months"
          type="text"
          value={formatIndianNumber(taxationData.salary.children_education_months)}
          onChange={(e) => handleTextFieldChange('salary', 'children_education_months', e)}
          onFocus={(e) => handleTextFieldFocus('salary', 'children_education_months', e)}
        />

        {/* Section Header: Hostel Allowance */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Hostel Allowance</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>

        <Tooltip title={
          <>
            Hostel allowance for children<br/>
            '₹ 300 per month per child (max 2 children)'<br/>
            'Provide Annual Allowance value'
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
            onChange={(e) => handleTextFieldChange('salary', 'hostel_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'hostel_allowance', e)}
          />
        </Tooltip>

        <TextField
          fullWidth
          label="Number of Children in Hostel"
          type="text"
          value={formatIndianNumber(taxationData.salary.hostel_count)}
          onChange={(e) => handleTextFieldChange('salary', 'hostel_count', e)}
          onFocus={(e) => handleTextFieldFocus('salary', 'hostel_count', e)}
        />

        <TextField
          fullWidth
          label="Hostel Months"
          type="text"
          value={formatIndianNumber(taxationData.salary.hostel_months)}
          onChange={(e) => handleTextFieldChange('salary', 'hostel_months', e)}
          onFocus={(e) => handleTextFieldFocus('salary', 'hostel_months', e)}
        />

        {/* Section Header: Transport Allowance */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Transport Allowance</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>

        <Tooltip title={
          <>
            Transport allowance for commuting<br/>
            '₹ 1600 per month for non-disabled'<br/>
            '₹ 3200 per month for disabled'<br/>
            'Provide Annual Allowance value'
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
            onChange={(e) => handleTextFieldChange('salary', 'transport_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'transport_allowance', e)}
          />
        </Tooltip>

        <TextField
          fullWidth
          label="Transport Months"
          type="text"
          value={formatIndianNumber(taxationData.salary.transport_months)}
          onChange={(e) => handleTextFieldChange('salary', 'transport_months', e)}
          onFocus={(e) => handleTextFieldFocus('salary', 'transport_months', e)}
        />

        {/* Section Header: Underground Mines Allowance */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Underground Mines Allowance</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>

        <Tooltip title={
          <>
            Allowance for underground mine workers<br/>
            'No Max Limit'<br/>
            'Provide Annual Allowance value'
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
            onChange={(e) => handleTextFieldChange('salary', 'underground_mines_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'underground_mines_allowance', e)}
          />
        </Tooltip>

        <TextField
          fullWidth
          label="Underground Mines Months"
          type="text"
          value={formatIndianNumber(taxationData.salary.underground_mines_months)}
          onChange={(e) => handleTextFieldChange('salary', 'underground_mines_months', e)}
          onFocus={(e) => handleTextFieldFocus('salary', 'underground_mines_months', e)}
        />

        {/* Section Header: Government Employee Specific Allowances */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Government Employee Specific Allowances</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>

        <Tooltip title={
          <>
            Entertainment allowance for government employees<br/>
            '20% of salary or ₹5000 whichever is less'<br/>
            'Provide Annual Allowance value'
          </>
        }
        placement="top"
        arrow
        >
          <TextField
            fullWidth
            label="Government Employee Entertainment Allowance"
            type="text"
            value={formatIndianNumber(taxationData.salary.govt_employee_entertainment_allowance)}
            onChange={(e) => handleTextFieldChange('salary', 'govt_employee_entertainment_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'govt_employee_entertainment_allowance', e)}
          />
        </Tooltip>

        {taxationData.is_govt_employee && (
          <>
            <Tooltip title={
              <>
                Allowance for government employees posted outside India<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
            }
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="Government Employees Outside India Allowance"
                type="text"
                value={formatIndianNumber(taxationData.salary.govt_employees_outside_india_allowance)}
                onChange={(e) => handleTextFieldChange('salary', 'govt_employees_outside_india_allowance', e)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleTextFieldFocus('salary', 'govt_employees_outside_india_allowance', e)}
              />
            </Tooltip>

            <Tooltip title={
              <>
                Special allowance for Supreme/High Court judges<br/>
                'No Max Limit'<br/>
                'Provide Annual Allowance value'
              </>
            }
            placement="top"
            arrow
            >
              <TextField
                fullWidth
                label="Supreme/High Court Judges Allowance"
                type="text"
                value={formatIndianNumber(taxationData.salary.supreme_high_court_judges_allowance)}
                onChange={(e) => handleTextFieldChange('salary', 'supreme_high_court_judges_allowance', e)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleTextFieldFocus('salary', 'supreme_high_court_judges_allowance', e)}
              />
            </Tooltip>

            <Tooltip title={
              <>
                Compensatory allowance for judges<br/>
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
                onChange={(e) => handleTextFieldChange('salary', 'judge_compensatory_allowance', e)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleTextFieldFocus('salary', 'judge_compensatory_allowance', e)}
              />
            </Tooltip>

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
                onChange={(e) => handleTextFieldChange('salary', 'section_10_14_special_allowances', e)}
                InputProps={{ startAdornment: '₹' }}
                onFocus={(e) => handleTextFieldFocus('salary', 'section_10_14_special_allowances', e)}
              />
            </Tooltip>
          </>
        )}
        
        {/* Section Header: Duty Related Allowances */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Duty Related Allowances</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>
        
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
            onChange={(e) => handleTextFieldChange('salary', 'travel_on_tour_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'travel_on_tour_allowance', e)}
          />
        </Tooltip>

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
            onChange={(e) => handleTextFieldChange('salary', 'tour_daily_charge_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'tour_daily_charge_allowance', e)}
          />
        </Tooltip>

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
            onChange={(e) => handleTextFieldChange('salary', 'conveyance_in_performace_of_duties', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'conveyance_in_performace_of_duties', e)}
          />
        </Tooltip>

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
            onChange={(e) => handleTextFieldChange('salary', 'helper_in_performace_of_duties', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'helper_in_performace_of_duties', e)}
          />
        </Tooltip>

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
            onChange={(e) => handleTextFieldChange('salary', 'academic_research', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'academic_research', e)}
          />
        </Tooltip>

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
            onChange={(e) => handleTextFieldChange('salary', 'uniform_allowance', e)}
            InputProps={{ startAdornment: '₹' }}
            onFocus={(e) => handleTextFieldFocus('salary', 'uniform_allowance', e)}
          />
        </Tooltip>

        {/* Any Other Allowance */}
        <TextField
          fullWidth
          label="Any Other Allowance"
          type="text"
          value={formatIndianNumber(taxationData.salary.any_other_allowance)}
          onChange={(e) => handleTextFieldChange('salary', 'any_other_allowance', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'any_other_allowance', e)}
        />
        
        {/* Any Other Allowance Exemption */}
        <TextField
          fullWidth
          label="Any Other Allowance Exemption"
          type="text"
          value={formatIndianNumber(taxationData.salary.any_other_allowance_exemption)}
          onChange={(e) => handleTextFieldChange('salary', 'any_other_allowance_exemption', e)}
          InputProps={{ startAdornment: '₹' }}
          onFocus={(e) => handleTextFieldFocus('salary', 'any_other_allowance_exemption', e)}
        />
      </Box>
    </Box>
  );
};

export default SalarySection; 