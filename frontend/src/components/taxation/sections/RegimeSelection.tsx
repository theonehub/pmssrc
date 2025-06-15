import React from 'react';
import {
  Box,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Paper,
  Card,
  CardContent,
  Alert,
  Divider,
  FormControlLabel as MuiFormControlLabel,
  Switch
} from '@mui/material';
import ValidatedTextField from '../components/ValidatedTextField';
import { TAXATION_LIMITS } from '../utils/validationRules';
import { TaxationData, TaxRegime } from '../../../shared/types';

interface ValidationErrors {
  [key: string]: string;
}

interface RegimeSelectionProps {
  taxationData: TaxationData;
  validationErrors?: ValidationErrors;
  handleRegimeChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleInputChange: (section: string, field: string, value: string | number | boolean) => void;
}

/**
 * RegimeSelection component - Step 1 of tax declaration
 * FIXES APPLIED:
 * 1. Added comprehensive age validation using ValidatedTextField
 * 2. Added regime comparison and guidance
 * 3. Added government employee status
 * 4. Better UI/UX with regime explanations
 * 5. Proper validation integration
 */
const RegimeSelection: React.FC<RegimeSelectionProps> = ({
  taxationData,
  validationErrors = {},
  handleRegimeChange,
  handleInputChange
}) => {
  const getRegimeGuidance = (): React.ReactElement | null => {
    if (!taxationData.age) {
      return null;
    }

    const age = parseInt(String(taxationData.age));
    let guidance = '';

    if (age >= TAXATION_LIMITS.SUPER_SENIOR_CITIZEN_AGE) {
      guidance = 'As a super senior citizen (80+), you may benefit from higher exemption limits in the old regime.';
    } else if (age >= TAXATION_LIMITS.SENIOR_CITIZEN_AGE) {
      guidance = 'As a senior citizen (60+), you get additional benefits in the old regime including higher Section 80D limits.';
    } else {
      guidance = 'Consider your deductions and investments to choose the optimal regime.';
    }

    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">{guidance}</Typography>
      </Alert>
    );
  };

  const handleCardClick = (regime: TaxRegime): void => {
    const syntheticEvent = {
      target: { value: regime }
    } as React.ChangeEvent<HTMLInputElement>;
    handleRegimeChange(syntheticEvent);
  };

  const handleSwitchChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    handleInputChange('', 'is_govt_employee', event.target.checked);
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h5" color="primary" gutterBottom>
        Tax Regime & Basic Information
      </Typography>
      <Divider sx={{ mb: 3 }} />

      <Box sx={{ display: 'grid', gap: 3 }}>
        {/* Employee Age and Government Employee Status */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
          gap: 3 
        }}>
          <ValidatedTextField
            label="Employee Age"
            value={taxationData.age || ''}
            onChange={(value) => handleInputChange('', 'age', value)}
            fieldType="age"
            required
            helperText="Age determines senior citizen benefits and tax slabs"
          />

          <Box sx={{ mt: 2 }}>
            <MuiFormControlLabel
              control={
                <Switch
                  checked={taxationData.is_govt_employee || false}
                  onChange={handleSwitchChange}
                />
              }
              label="Government Employee"
            />
            <Typography variant="caption" display="block" color="text.secondary">
              Government employees have specific allowance exemptions
            </Typography>
          </Box>
        </Box>

        {/* Tax Regime Selection */}
        <Box>
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend">
              <Typography variant="h6" sx={{ mb: 2 }}>
                Select Tax Regime
              </Typography>
            </FormLabel>
            
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
              gap: 3 
            }}>
              {/* Old Regime Card */}
              <Card 
                variant={taxationData.regime === 'old' ? 'elevation' : 'outlined'}
                sx={{ 
                  height: '100%',
                  border: taxationData.regime === 'old' ? '2px solid' : '1px solid',
                  borderColor: taxationData.regime === 'old' ? 'primary.main' : 'divider',
                  cursor: 'pointer'
                }}
                onClick={() => handleCardClick('old')}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Radio
                      checked={taxationData.regime === 'old'}
                      value="old"
                      name="regime"
                      onChange={handleRegimeChange}
                    />
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      Old Tax Regime
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Traditional regime with extensive deductions and exemptions
                  </Typography>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Key Features:
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    <li>
                      <Typography variant="body2">
                        Section 80C deductions up to ₹1.5 lakh
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Section 80D health insurance premiums
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        HRA exemption for salaried employees
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Various allowance exemptions
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Higher tax slabs but with deductions
                      </Typography>
                    </li>
                  </ul>
                  
                  <Typography variant="caption" color="primary" sx={{ mt: 2, display: 'block' }}>
                    Best for: Employees with significant investments and expenses
                  </Typography>
                </CardContent>
              </Card>

              {/* New Regime Card */}
              <Card 
                variant={taxationData.regime === 'new' ? 'elevation' : 'outlined'}
                sx={{ 
                  height: '100%',
                  border: taxationData.regime === 'new' ? '2px solid' : '1px solid',
                  borderColor: taxationData.regime === 'new' ? 'primary.main' : 'divider',
                  cursor: 'pointer'
                }}
                onClick={() => handleCardClick('new')}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Radio
                      checked={taxationData.regime === 'new'}
                      value="new"
                      name="regime"
                      onChange={handleRegimeChange}
                    />
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      New Tax Regime
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Simplified regime with lower tax rates but limited deductions
                  </Typography>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Key Features:
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: '20px' }}>
                    <li>
                      <Typography variant="body2">
                        Lower tax rates across all slabs
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Standard deduction of ₹75,000 (Budget 2025)
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        No Section 80C, 80D deductions
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        No HRA exemption
                      </Typography>
                    </li>
                    <li>
                      <Typography variant="body2">
                        Simplified tax calculation
                      </Typography>
                    </li>
                  </ul>
                  
                  <Typography variant="caption" color="primary" sx={{ mt: 2, display: 'block' }}>
                    Best for: Employees with minimal investments and deductions
                  </Typography>
                </CardContent>
              </Card>
            </Box>

            {/* Regime Selection using Radio Group (hidden, controlled by card clicks) */}
            <RadioGroup
              value={taxationData.regime}
              onChange={handleRegimeChange}
              sx={{ display: 'none' }}
            >
              <FormControlLabel value="old" control={<Radio />} label="Old Tax Regime" />
              <FormControlLabel value="new" control={<Radio />} label="New Tax Regime" />
            </RadioGroup>
          </FormControl>
        </Box>

        {/* Age-based guidance */}
        {getRegimeGuidance()}

        {/* Important Note */}
        <Alert severity="warning">
          <Typography variant="subtitle2" gutterBottom>
            Important Notes:
          </Typography>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            <li>
              <Typography variant="body2">
                You can switch between regimes each financial year
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Once you file ITR, the regime choice becomes final for that year
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Consider consulting a tax advisor for complex scenarios
              </Typography>
            </li>
          </ul>
        </Alert>

        {/* Validation Warnings Display */}
        {validationErrors && Object.keys(validationErrors).length > 0 && (
          <Alert severity="warning">
            <Typography variant="subtitle2">Please review the following warnings:</Typography>
            {Object.entries(validationErrors).map(([field, warning]) => (
              <Typography key={field} variant="body2">
                • {warning}
              </Typography>
            ))}
          </Alert>
        )}

        {/* Tax Year Display */}
        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Declaration Details
          </Typography>
          <Typography variant="body1">
            <strong>Financial Year:</strong> {taxationData.tax_year}
          </Typography>
          <Typography variant="body1">
            <strong>Assessment Year:</strong> {(() => {
              const [, endYear] = taxationData.tax_year.split('-');
              return `${parseInt(endYear || '2024')}-${parseInt(endYear || '2024') + 1}`;
            })()}
          </Typography>
          <Typography variant="body1">
            <strong>Employee ID:</strong> {taxationData.employee_id}
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
};

export default RegimeSelection; 