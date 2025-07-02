import React from 'react';
import {
  Box,
  Typography,
  Divider,
  Tooltip
} from '@mui/material';
import { formatIndianNumber, parseIndianNumber } from '../utils/taxationUtils';
import { TaxationData } from '../../../shared/types';
import ValidatedTextField from '../components/ValidatedTextField';

interface SalarySectionProps {
  taxationData: TaxationData;
  handleInputChange: (section: string, field: string, value: string | number | boolean) => void;
  handleFocus: (section: string, field: string, value: string | number) => void;
}

/**
 * Salary Section Component for comprehensive salary components management
 */
const SalarySection: React.FC<SalarySectionProps> = ({
  taxationData,
  handleInputChange,
  handleFocus
}) => {
  // Helper function to safely format salary values
  const formatSalaryValue = (value: number | string | undefined): string => {
    // If value is a calculator expression (starts with '='), return it as-is
    if (typeof value === 'string' && value.startsWith('=')) {
      console.log('✅ Calculator expression detected in formatSalaryValue:', value);
      return value;
    }
    // Otherwise, format as Indian number (ensure it's a number)
    const numValue = typeof value === 'number' ? value : 0;
    const formatted = formatIndianNumber(numValue);
    return formatted;
  };

  const handleTextFieldFocus = (section: string, field: string, event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>): void => {
    const value = parseIndianNumber(event.target.value);
    handleFocus(section, field, value);
  };



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
        <ValidatedTextField
          label="Basic Salary"
          value={formatSalaryValue(taxationData.salary_income?.basic_salary)}
          onChange={(value) => handleInputChange('salary_income', 'basic_salary', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'basic_salary', e)}
          fieldType="amount"
          required
          helperText="Enter your basic salary amount"
        />
        
        {/* Dearness Allowance */}
        <ValidatedTextField
          label="Dearness Allowance (DA)"
          value={formatSalaryValue(taxationData.salary_income?.dearness_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'dearness_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'dearness_allowance', e)}
          fieldType="amount"
          helperText="Enter your dearness allowance amount"
        />
        
        {/* HRA */}
        <ValidatedTextField
          label="House Rent Allowance (HRA) Provided by Employer"
          value={formatSalaryValue(taxationData.salary_income?.hra_provided)}
          onChange={(value) => handleInputChange('salary_income', 'hra_provided', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'hra_provided', e)}
          fieldType="amount"
          helperText="Enter the HRA amount provided by your employer. For exemption calculation, fill details in Deductions section."
        />



        {/* Special Allowance */}
        <ValidatedTextField
          label="Special Allowance"
          value={formatSalaryValue(taxationData.salary_income?.special_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'special_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'special_allowance', e)}
          fieldType="amount"
          helperText="Enter your special allowance amount"
        />
        
        {/* Bonus */}
        <ValidatedTextField
          label="Bonus"
          value={formatSalaryValue(taxationData.salary_income?.bonus)}
          onChange={(value) => handleInputChange('salary_income', 'bonus', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'bonus', e)}
          fieldType="amount"
          helperText="Enter your bonus amount"
        />
        
        {/* Commission */}
        <ValidatedTextField
          label="Commission"
          value={formatSalaryValue(taxationData.salary_income?.commission)}
          onChange={(value) => handleInputChange('salary_income', 'commission', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'commission', e)}
          fieldType="amount"
          helperText="Enter your commission amount"
        />
        
        {/* City Compensatory Allowance */}
        <ValidatedTextField
          label="City Compensatory Allowance"
          value={formatSalaryValue(taxationData.salary_income?.city_compensatory_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'city_compensatory_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'city_compensatory_allowance', e)}
          fieldType="amount"
          helperText="Enter your city compensatory allowance amount"
        />

        {/* Section Header: Additional Allowances */}
        <Box sx={{ gridColumn: '1 / -1', width: '100%', display: 'flex', justifyContent: 'left' }}>
          <Typography variant="h6" color="primary">Additional Allowances (if applicable)</Typography>
        </Box>
        <Box sx={{ gridColumn: '1 / -1', my: 0, width: '100%' }}>
          <Divider />
        </Box>
        
        {/* Rural Allowance */}
        <ValidatedTextField
          label="Rural Allowance"
          value={formatSalaryValue(taxationData.salary_income?.rural_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'rural_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'rural_allowance', e)}
          fieldType="amount"
          helperText="Enter your rural allowance amount"
        />

        {/* Proctorship Allowance */}
        <ValidatedTextField
          label="Proctorship Allowance"
          value={formatSalaryValue(taxationData.salary_income?.proctorship_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'proctorship_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'proctorship_allowance', e)}
          fieldType="amount"
          helperText="Enter your proctorship allowance amount"
        />

        {/* Wardenship Allowance */}
        <ValidatedTextField
          label="Wardenship Allowance"
          value={formatSalaryValue(taxationData.salary_income?.wardenship_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'wardenship_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'wardenship_allowance', e)}
          fieldType="amount"
          helperText="Enter your wardenship allowance amount"
        />

        {/* Project Allowance */}
        <ValidatedTextField
          label="Project Allowance"
          value={formatSalaryValue(taxationData.salary_income?.project_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'project_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'project_allowance', e)}
          fieldType="amount"
          helperText="Enter your project allowance amount"
        />

        {/* Deputation Allowance */}
        <ValidatedTextField
          label="Deputation Allowance"
          value={formatSalaryValue(taxationData.salary_income?.deputation_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'deputation_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'deputation_allowance', e)}
          fieldType="amount"
          helperText="Enter your deputation allowance amount"
        />

        {/* Interim Relief */}
        <ValidatedTextField
          label="Interim Relief"
          value={formatSalaryValue(taxationData.salary_income?.interim_relief)}
          onChange={(value) => handleInputChange('salary_income', 'interim_relief', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'interim_relief', e)}
          fieldType="amount"
          helperText="Enter your interim relief amount"
        />

        {/* Tiffin Allowance */}
        <ValidatedTextField
          label="Tiffin Allowance"
          value={formatSalaryValue(taxationData.salary_income?.tiffin_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'tiffin_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'tiffin_allowance', e)}
          fieldType="amount"
          helperText="Enter your tiffin allowance amount"
        />

        {/* Fixed Medical Allowance */}
        <ValidatedTextField
          label="Fixed Medical Allowance"
          value={formatSalaryValue(taxationData.salary_income?.medical_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'medical_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'medical_allowance', e)}
          fieldType="amount"
          helperText="Enter your fixed medical allowance amount"
        />
        
        {/* Overtime Allowance */}
        <ValidatedTextField
          label="Overtime Allowance"
          value={formatSalaryValue(taxationData.salary_income?.overtime_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'overtime_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'overtime_allowance', e)}
          fieldType="amount"
          helperText="Enter your overtime allowance amount"
        />

        {/* Servant Allowance */}
        <ValidatedTextField
          label="Servant Allowance"
          value={formatSalaryValue(taxationData.salary_income?.servant_allowance)}
          onChange={(value) => handleInputChange('salary_income', 'servant_allowance', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'servant_allowance', e)}
          fieldType="amount"
          helperText="Enter your servant allowance amount"
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
          <ValidatedTextField
            label="Hills/High Altitude Allowance"
            value={formatSalaryValue(taxationData.salary_income?.hills_high_altd_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'hills_high_altd_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'hills_high_altd_allowance', e)}
            fieldType="amount"
            helperText="Enter allowance for employees working in hilly areas"
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
          <ValidatedTextField
            label="Hills/High Altitude Allowance Exemption Limit"
            value={formatSalaryValue(taxationData.salary_income?.hills_high_altd_exemption_limit)}
            onChange={(value) => handleInputChange('salary_income', 'hills_high_altd_exemption_limit', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'hills_high_altd_exemption_limit', e)}
            fieldType="amount"
            helperText="Enter exemption limit for hills/high altitude allowance"
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
          <ValidatedTextField
            label="Border/Remote Area Allowance"
            value={formatSalaryValue(taxationData.salary_income?.border_remote_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'border_remote_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'border_remote_allowance', e)}
            fieldType="amount"
            helperText="Enter allowance for employees working in border or remote areas"
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
          <ValidatedTextField
            label="Border/Remote Area Allowance Exemption Limit"
            value={formatSalaryValue(taxationData.salary_income?.border_remote_exemption_limit)}
            onChange={(value) => handleInputChange('salary_income', 'border_remote_exemption_limit', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'border_remote_exemption_limit', e)}
            fieldType="amount"
            helperText="Enter exemption limit for border/remote area allowance"
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
          <ValidatedTextField
            label="Transport Employee Allowance"
            value={formatSalaryValue(taxationData.salary_income?.transport_employee_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'transport_employee_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'transport_employee_allowance', e)}
            fieldType="amount"
            helperText="Enter allowance for transport employees"
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
          <ValidatedTextField
            label="Children Education Allowance"
            value={formatSalaryValue(taxationData.salary_income?.children_education_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'children_education_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'children_education_allowance', e)}
            fieldType="amount"
            helperText="Enter education allowance for children"
          />
        </Tooltip>

        <ValidatedTextField
          label="Number of Children"
          value={formatSalaryValue(taxationData.salary_income?.children_education_count)}
          onChange={(value) => handleInputChange('salary_income', 'children_education_count', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'children_education_count', e)}
          fieldType="number"
          helperText="Enter number of children (max 2)"
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
          <ValidatedTextField
            label="Hostel Allowance"
            value={formatSalaryValue(taxationData.salary_income?.hostel_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'hostel_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'hostel_allowance', e)}
            fieldType="amount"
            helperText="Enter hostel allowance for children"
          />
        </Tooltip>

        <ValidatedTextField
          label="Number of Children in Hostel"
          value={formatSalaryValue(taxationData.salary_income?.children_hostel_count)}
          onChange={(value) => handleInputChange('salary_income', 'children_hostel_count', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'children_hostel_count', e)}
          fieldType="number"
          helperText="Enter number of children in hostel (max 2)"
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
            '₹ 3200 per month for  blind or deaf and dumb'<br/>
          </>
        }
        placement="top"
        arrow
        >
          <ValidatedTextField
            label="Transport Allowance"
            value={formatSalaryValue(taxationData.salary_income?.conveyance_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'conveyance_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'conveyance_allowance', e)}
            fieldType="amount"
            helperText="Enter transport allowance for commuting"
          />
        </Tooltip>

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
          <ValidatedTextField
            label="Underground Mines Allowance"
            value={formatSalaryValue(taxationData.salary_income?.underground_mines_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'underground_mines_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'underground_mines_allowance', e)}
            fieldType="amount"
            helperText="Enter allowance for underground mine workers"
          />
        </Tooltip>

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
          <ValidatedTextField
            label="Government Employee Entertainment Allowance"
            value={formatSalaryValue(taxationData.salary_income?.govt_employee_entertainment_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'govt_employee_entertainment_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'govt_employee_entertainment_allowance', e)}
            fieldType="amount"
            helperText="Enter entertainment allowance for government employees"
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
              <ValidatedTextField
                label="Government Employees Outside India Allowance"
                value={formatSalaryValue(taxationData.salary_income?.govt_employees_outside_india_allowance)}
                onChange={(value) => handleInputChange('salary_income', 'govt_employees_outside_india_allowance', value)}
                onFocus={(e) => handleTextFieldFocus('salary_income', 'govt_employees_outside_india_allowance', e)}
                fieldType="amount"
                helperText="Enter allowance for government employees posted outside India"
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
              <ValidatedTextField
                label="Supreme/High Court Judges Allowance"
                value={formatSalaryValue(taxationData.salary_income?.supreme_high_court_judges_allowance)}
                onChange={(value) => handleInputChange('salary_income', 'supreme_high_court_judges_allowance', value)}
                onFocus={(e) => handleTextFieldFocus('salary_income', 'supreme_high_court_judges_allowance', e)}
                fieldType="amount"
                helperText="Enter special allowance for Supreme/High Court judges"
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
              <ValidatedTextField
                label="Judge Compensatory Allowance"
                value={formatSalaryValue(taxationData.salary_income?.judge_compensatory_allowance)}
                onChange={(value) => handleInputChange('salary_income', 'judge_compensatory_allowance', value)}
                onFocus={(e) => handleTextFieldFocus('salary_income', 'judge_compensatory_allowance', e)}
                fieldType="amount"
                helperText="Enter compensatory allowance for judges"
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
              <ValidatedTextField
                label="Section 10(14) Special Allowances"
                value={formatSalaryValue(taxationData.salary_income?.section_10_14_special_allowances)}
                onChange={(value) => handleInputChange('salary_income', 'section_10_14_special_allowances', value)}
                onFocus={(e) => handleTextFieldFocus('salary_income', 'section_10_14_special_allowances', e)}
                fieldType="amount"
                helperText="Enter Section 10(14) special allowances"
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
          <ValidatedTextField
            label="Travel Allowance (Tour)"
            value={formatSalaryValue(taxationData.salary_income?.travel_on_tour_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'travel_on_tour_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'travel_on_tour_allowance', e)}
            fieldType="amount"
            helperText="Enter allowance granted to meet cost of travel on tour"
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
          <ValidatedTextField
            label="Tour Daily Charge Allowance"
            value={formatSalaryValue(taxationData.salary_income?.tour_daily_charge_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'tour_daily_charge_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'tour_daily_charge_allowance', e)}
            fieldType="amount"
            helperText="Enter allowance granted to meet cost of daily charges incurred on tour"
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
          <ValidatedTextField
            label="Conveyance Allowance (Duties)"
            value={formatSalaryValue(taxationData.salary_income?.conveyance_in_performace_of_duties)}
            onChange={(value) => handleInputChange('salary_income', 'conveyance_in_performace_of_duties', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'conveyance_in_performace_of_duties', e)}
            fieldType="amount"
            helperText="Enter allowance granted to meet expenditure incurred on conveyance in performance of duties"
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
          <ValidatedTextField
            label="Helper Allowance (Duties)"
            value={formatSalaryValue(taxationData.salary_income?.helper_in_performace_of_duties)}
            onChange={(value) => handleInputChange('salary_income', 'helper_in_performace_of_duties', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'helper_in_performace_of_duties', e)}
            fieldType="amount"
            helperText="Enter allowance granted to meet expenditure incurred on helper in performance of duties"
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
          <ValidatedTextField
            label="Academic/Research Allowance"
            value={formatSalaryValue(taxationData.salary_income?.academic_research)}
            onChange={(value) => handleInputChange('salary_income', 'academic_research', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'academic_research', e)}
            fieldType="amount"
            helperText="Enter allowance granted for encouraging academic, research & training pursuits"
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
          <ValidatedTextField
            label="Uniform Allowance (Duties)"
            value={formatSalaryValue(taxationData.salary_income?.uniform_allowance)}
            onChange={(value) => handleInputChange('salary_income', 'uniform_allowance', value)}
            onFocus={(e) => handleTextFieldFocus('salary_income', 'uniform_allowance', e)}
            fieldType="amount"
            helperText="Enter allowance granted for expenditure incurred on purchase or maintenance of uniform"
          />
        </Tooltip>

        {/* Any Other Allowance */}
        <ValidatedTextField
          label="Any Other Allowance"
          value={formatSalaryValue(taxationData.salary_income?.other_allowances)}
          onChange={(value) => handleInputChange('salary_income', 'other_allowances', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'other_allowances', e)}
          fieldType="amount"
          helperText="Enter any other allowance amount"
        />
        
        {/* Any Other Allowance Exemption */}
        <ValidatedTextField
          label="Any Other Allowance Exemption"
          value={formatSalaryValue(taxationData.salary_income?.any_other_allowance_exemption)}
          onChange={(value) => handleInputChange('salary_income', 'any_other_allowance_exemption', value)}
          onFocus={(e) => handleTextFieldFocus('salary_income', 'any_other_allowance_exemption', e)}
          fieldType="amount"
          helperText="Enter any other allowance exemption amount"
        />
      </Box>
    </Box>
  );
};

export default SalarySection; 