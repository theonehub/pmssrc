import { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getTaxationByEmpId, saveTaxationData, calculateTax, computeVrsValue } from '../../../shared/api/taxationService';
import { getDefaultTaxationState, parseIndianNumber } from '../utils/taxationUtils';

/**
 * Transform comprehensive taxation record from backend to frontend form format
 * @param {Object} comprehensiveRecord - Comprehensive taxation record from backend
 * @param {string} empId - Employee ID
 * @returns {Object} Transformed data for frontend form
 */
const transformComprehensiveRecordToFormData = (comprehensiveRecord, empId) => {
  if (!comprehensiveRecord) {
    return getDefaultTaxationState(empId);
  }

  // Helper function to convert Decimal strings to numbers
  const toNumber = (value) => {
    if (value === null || value === undefined) return 0;
    if (typeof value === 'string') return parseFloat(value) || 0;
    if (typeof value === 'number') return value;
    return 0;
  };

  // Helper function to safely extract nested object values
  const safeExtract = (obj, defaultValue = {}) => {
    return obj && typeof obj === 'object' ? obj : defaultValue;
  };

  try {
    // Get default state as base
    const defaultState = getDefaultTaxationState(empId);
    
    // Transform the comprehensive record to form format
    const transformedData = {
      ...defaultState,
      employee_id: comprehensiveRecord.employee_id || empId,
      age: toNumber(comprehensiveRecord.age),
      emp_age: toNumber(comprehensiveRecord.age), // Frontend uses emp_age
      regime: comprehensiveRecord.regime_type || 'old',
      tax_year: comprehensiveRecord.tax_year || defaultState.tax_year,
      is_govt_employee: Boolean(comprehensiveRecord.is_govt_employee),
    };

    // Transform salary income if present
    if (comprehensiveRecord.salary_income) {
      const salaryData = comprehensiveRecord.salary_income;
      transformedData.salary_income = {
        ...defaultState.salary_income,
        basic_salary: toNumber(salaryData.basic_salary),
        dearness_allowance: toNumber(salaryData.dearness_allowance),
        hra_provided: toNumber(salaryData.hra_provided),

        special_allowance: toNumber(salaryData.special_allowance),
        other_allowances: toNumber(salaryData.other_allowances),
        bonus: toNumber(salaryData.bonus),
        commission: toNumber(salaryData.commission),
        medical_allowance: toNumber(salaryData.medical_allowance),
        conveyance_allowance: toNumber(salaryData.conveyance_allowance),


        // All the detailed allowances
        city_compensatory_allowance: toNumber(salaryData.city_compensatory_allowance),
        rural_allowance: toNumber(salaryData.rural_allowance),
        proctorship_allowance: toNumber(salaryData.proctorship_allowance),
        wardenship_allowance: toNumber(salaryData.wardenship_allowance),
        project_allowance: toNumber(salaryData.project_allowance),
        deputation_allowance: toNumber(salaryData.deputation_allowance),
        interim_relief: toNumber(salaryData.interim_relief),
        tiffin_allowance: toNumber(salaryData.tiffin_allowance),
        overtime_allowance: toNumber(salaryData.overtime_allowance),
        servant_allowance: toNumber(salaryData.servant_allowance),

        hills_high_altd_allowance: toNumber(salaryData.hills_high_altd_allowance),
        hills_high_altd_exemption_limit: toNumber(salaryData.hills_high_altd_exemption_limit),
        border_remote_allowance: toNumber(salaryData.border_remote_allowance),
        border_remote_exemption_limit: toNumber(salaryData.border_remote_exemption_limit),
        transport_employee_allowance: toNumber(salaryData.transport_employee_allowance),
        children_education_allowance: toNumber(salaryData.children_education_allowance),
        children_education_count: toNumber(salaryData.children_education_count),
        children_hostel_count: toNumber(salaryData.children_hostel_count),
        underground_mines_allowance: toNumber(salaryData.underground_mines_allowance),

        govt_employee_entertainment_allowance: toNumber(salaryData.govt_employee_entertainment_allowance),
        govt_employees_outside_india_allowance: toNumber(salaryData.govt_employees_outside_india_allowance),
        supreme_high_court_judges_allowance: toNumber(salaryData.supreme_high_court_judges_allowance),
        judge_compensatory_allowance: toNumber(salaryData.judge_compensatory_allowance),
        section_10_14_special_allowances: toNumber(salaryData.section_10_14_special_allowances),
        travel_on_tour_allowance: toNumber(salaryData.travel_on_tour_allowance),
        tour_daily_charge_allowance: toNumber(salaryData.tour_daily_charge_allowance),
        conveyance_in_performace_of_duties: toNumber(salaryData.conveyance_in_performace_of_duties),
        helper_in_performace_of_duties: toNumber(salaryData.helper_in_performace_of_duties),
        academic_research: toNumber(salaryData.academic_research),
        uniform_allowance: toNumber(salaryData.uniform_allowance),
        any_other_allowance_exemption: toNumber(salaryData.any_other_allowance_exemption),
        
      };
    }

    // Transform other sections if present
    if (comprehensiveRecord.house_property_income) {
      const houseData = comprehensiveRecord.house_property_income;
      transformedData.house_property_income = {
        property_type: houseData.property_type || 'Self-Occupied',
        annual_rent_received: toNumber(houseData.annual_rent_received),
        municipal_taxes_paid: toNumber(houseData.municipal_taxes_paid),
        home_loan_interest: toNumber(houseData.home_loan_interest),
        pre_construction_interest: toNumber(houseData.pre_construction_interest),

        
      };
    }

    if (comprehensiveRecord.capital_gains_income) {
      const capitalData = comprehensiveRecord.capital_gains_income;
      transformedData.capital_gains_income = {
        stcg_111a_equity_stt: toNumber(capitalData.stcg_111a_equity_stt),
        stcg_other_assets: toNumber(capitalData.stcg_other_assets),
        ltcg_112a_equity_stt: toNumber(capitalData.ltcg_112a_equity_stt),
        ltcg_other_assets: toNumber(capitalData.ltcg_other_assets),
        ltcg_debt_mf: toNumber(capitalData.ltcg_debt_mf),
      };
    }

    if (comprehensiveRecord.other_income) {
      const otherData = comprehensiveRecord.other_income;
      transformedData.other_income = {
        interest_income: safeExtract(otherData.interest_income),
        dividend_income: toNumber(otherData.dividend_income),
        gifts_received: toNumber(otherData.gifts_received),
        business_professional_income: toNumber(otherData.business_professional_income),
        other_miscellaneous_income: toNumber(otherData.other_miscellaneous_income),
      };
    }

    // Transform deductions if present
    if (comprehensiveRecord.deductions) {
      const deductionsData = comprehensiveRecord.deductions;
      transformedData.deductions = {
        section_80c: safeExtract(deductionsData.section_80c, defaultState.deductions?.section_80c || {}),
        section_80d: safeExtract(deductionsData.section_80d, defaultState.deductions?.section_80d || {}),
        section_80g: safeExtract(deductionsData.section_80g, defaultState.deductions?.section_80g || {}),
        section_80e: safeExtract(deductionsData.section_80e, defaultState.deductions?.section_80e || {}),
        section_80tta_ttb: safeExtract(deductionsData.section_80tta_ttb, defaultState.deductions?.section_80tta_ttb || {}),
        other_deductions: safeExtract(deductionsData.other_deductions, defaultState.deductions?.other_deductions || {}),
      };
    }

    // Transform other complex structures
    if (comprehensiveRecord.perquisites) {
      transformedData.perquisites = safeExtract(comprehensiveRecord.perquisites);
    }

    if (comprehensiveRecord.retirement_benefits) {
      transformedData.retirement_benefits = safeExtract(comprehensiveRecord.retirement_benefits);
    }

    if (comprehensiveRecord.multiple_house_properties) {
      transformedData.multiple_house_properties = safeExtract(comprehensiveRecord.multiple_house_properties);
    }

    if (comprehensiveRecord.monthly_payroll) {
      transformedData.monthly_payroll = safeExtract(comprehensiveRecord.monthly_payroll);
    }

    if (comprehensiveRecord.periodic_salary_income) {
      transformedData.periodic_salary_income = safeExtract(comprehensiveRecord.periodic_salary_income);
    }

    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.log('🔄 Transformed comprehensive record:', {
        employee_id: transformedData.employee_id,
        age: transformedData.age,
        regime: transformedData.regime,
        basic_salary: transformedData.salary_income?.basic_salary,
        has_deductions: !!transformedData.deductions,
      });
    }

    return transformedData;
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('❌ Error transforming comprehensive record:', error);
    }
    // Fallback to default state if transformation fails
    return getDefaultTaxationState(empId);
  }
};

/**
 * Custom hook for managing taxation form state and operations
 * @param {string} empId - Employee ID 
 * @returns {Object} Form state and handlers
 */
const useTaxationForm = (empId) => {
  const [taxationData, setTaxationData] = useState(getDefaultTaxationState(empId));
  const [calculatedTax, setCalculatedTax] = useState(null);
  const [taxCalculationResponse, setTaxCalculationResponse] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const [taxBreakup, setTaxBreakup] = useState(null);
  
  const queryClient = useQueryClient();

  // React Query for fetching taxation data
  const {
    data: fetchedData,
    isLoading: loading,
    error: queryError,
    refetch: refetchTaxationData
  } = useQuery({
    queryKey: ['taxation', empId],
    queryFn: async () => {
      if (!empId) throw new Error('Employee ID is required');
      console.log('🔍 React Query: Fetching taxation data for employee:', empId);
      const result = await getTaxationByEmpId(empId);
      console.log('📦 React Query: Received data from API:', result);
      return result;
    },
    enabled: !!empId,
    retry: (failureCount, error) => {
      console.log('🔄 React Query: Retry attempt', failureCount, 'for error:', error);
      // Don't retry on 404 errors (no record found)
      if (error?.response?.status === 404) {
        return false;
      }
      return failureCount < 2;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes cache time
    onSuccess: (data) => {
      console.log('✅ React Query: Successfully fetched data:', data);
    },
    onError: (error) => {
      console.error('❌ React Query: Error fetching data:', error);
    }
  });

  // Handle data population when query succeeds or fails
  useEffect(() => {
    console.log('🔍 useTaxationForm useEffect triggered:', { 
      hasFetchedData: !!fetchedData, 
      hasQueryError: !!queryError, 
      empId,
      fetchedDataType: typeof fetchedData,
      fetchedDataKeys: fetchedData ? Object.keys(fetchedData) : null
    });
    
    if (fetchedData) {
      console.log('📥 Raw comprehensive taxation data received in hook:', fetchedData);
      
      // Successfully fetched comprehensive taxation record - transform and populate form
      const transformedData = transformComprehensiveRecordToFormData(fetchedData, empId);
      
      console.log('🔄 Transformed data in hook:', transformedData);
      
      setTaxationData(transformedData);
      

      
      // Reset calculated tax when new data is loaded
      setCalculatedTax(null);
      setTaxCalculationResponse(null);
      setError(null);
      
      console.log('✅ Form populated with comprehensive taxation record in hook');
    } else if (queryError) {
      // Handle query error
      if (queryError.response && queryError.response.status === 404) {
        // No existing record found - initialize with default values
        console.log('ℹ️ No existing taxation record found, initializing with defaults');
        const defaultData = getDefaultTaxationState(empId);
        setTaxationData(defaultData);
        setError(null);
      } else {
        // Other errors
        console.error('❌ Error fetching taxation data:', queryError);
        setError('Failed to load taxation data');
      }
    }
  }, [fetchedData, queryError, empId]);

  // Legacy fetchTaxationData function for backward compatibility
  const fetchTaxationData = useCallback(async () => {
    return refetchTaxationData();
  }, [refetchTaxationData]);

  // Handle input change for non-nested fields
  const handleInputChange = (section, field, value) => {
    // Check if this is a calculator expression (starts with '=')
    const isCalculatorExpression = typeof value === 'string' && value.startsWith('=');
    
    // Only log for calculator expressions or important changes
    if (isCalculatorExpression) {
      console.log('🧮 Calculator expression in handleInputChange:', { section, field, value });
    }
    
    // If value is string with numbers, parse it (unless it's a calculator expression)
    let parsedValue;
    const stringFields = [
      'occupancy_status', 'property_address', 'relation_80dd', 'section_80g_100_head',
      'relation_80ddb', 'disability_percentage', 'disability_percentage_80u', 'ev_purchase_date',
      'section_80g_100_ql_head', 'section_80g_50_head', 'section_80g_50_ql_head', 'uncomputed_pension_frequency'
    ];
    
    if (stringFields.includes(field)) {
      // Keep as string for string fields
      parsedValue = value;
    } else if (typeof value === 'boolean') {
      parsedValue = value;
    } else if (isCalculatorExpression) {
      // For calculator expressions, store the raw string value
      // The ValidatedTextField will handle the calculation and conversion
      parsedValue = value;
      console.log('🧮 Calculator expression preserved in state:', { field, parsedValue });
    } else {
      parsedValue = typeof value === 'string' ? parseIndianNumber(value) : value;
      parsedValue = parseFloat(parsedValue) || 0;
    }
    
    // Reset calculatedTax to null when any value changes
    setCalculatedTax(null);
    setTaxCalculationResponse(null);
    
    setTaxationData((prevData) => {
      const newData = {
        ...prevData,
        [section]: {
          ...prevData[section],
          [field]: parsedValue
        }
      };
      
      // Only log calculator expressions
      if (isCalculatorExpression) {
        console.log('📊 Calculator expression stored in taxation data:', { 
          field: `${section}.${field}`, 
          newValue: newData[section][field] 
        });
      }
      
      return newData;
    });
  };

  // Handle input change for nested fields
  const handleNestedInputChange = (section, nestedSection, field, value) => {
    // Check if the field should be treated as a string (not converted to number)
    const stringFields = [
      'accommodation_provided', 'accommodation_city_population', 'car_use', 
      'travel_through', 'loan_type', 'lta_claim_start_date', 'lta_claim_end_date',
      'grant_date', 'vesting_date', 'exercise_date', 'mat_type', 'mau_ownership',
      'loan_start_date', 'uncomputed_pension_frequency', 'mat_number_of_completed_years_of_use',
      'property_type', 'occupancy_status'
    ];
    
    let parsedValue;
    
    if (stringFields.includes(field)) {
      // Keep as string for string fields
      parsedValue = value;
    } else if (typeof value === 'boolean') {
      // Handle boolean values
      parsedValue = value;
    } else {
      // Parse the value to remove commas if it's a string with numbers
      parsedValue = typeof value === 'string' ? parseIndianNumber(value) : value;
      parsedValue = parseFloat(parsedValue) || 0;
    }
    
    // Reset calculatedTax to null when any value changes
    setCalculatedTax(null);
    setTaxCalculationResponse(null);
    
    setTaxationData((prevData) => ({
      ...prevData,
      [section]: {
        ...prevData[section],
        [nestedSection]: {
          ...prevData[section][nestedSection],
          [field]: parsedValue
        }
      }
    }));
  };

  // Handle regime change
  const handleRegimeChange = (event) => {
    // Reset calculatedTax to null when regime changes
    setCalculatedTax(null);
    setTaxCalculationResponse(null);
    
    setTaxationData((prevData) => ({
      ...prevData,
      regime: event.target.value
    }));
  };

  // Handle clearing zero values on focus
  const handleFocus = (section, field, value) => {
    if (value === 0) {
      setTaxationData((prevData) => ({
        ...prevData,
        [section]: {
          ...prevData[section],
          [field]: ''
        }
      }));
    }
  };

  // Handle clearing zero values in nested fields on focus
  const handleNestedFocus = (section, nestedSection, field, value) => {
    if (value === 0) {
      setTaxationData((prevData) => ({
        ...prevData,
        [section]: {
          ...prevData[section],
          [nestedSection]: {
            ...prevData[section][nestedSection],
            [field]: ''
          }
        }
      }));
    }
  };



  // Calculate tax
  const handleCalculateTax = async () => {
    try {
      setSubmitting(true);
      setError(null);
      
      // Create a copy of the taxation data to modify before calculation
      const dataToCalculate = {...taxationData};
      
      // Remove ev_purchase_date field as it's not expected by the backend
      if (dataToCalculate.deductions && dataToCalculate.deductions.ev_purchase_date) {
        delete dataToCalculate.deductions.ev_purchase_date;
      }
      
      // Directly calculate the tax without saving first
      const result = await calculateTax(empId, taxationData.tax_year, taxationData.regime, dataToCalculate);
      setCalculatedTax(result.total_tax_liability);
      setTaxCalculationResponse(result);
      
      setSuccess('Tax calculated successfully!');
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error calculating tax:', err);
      }
      setError('Failed to calculate tax. Please try again later.');
    } finally {
      setSubmitting(false);
    }
  };

  // Submit taxation data
  const handleSubmit = async (navigate) => {
    try {
      setSubmitting(true);
      setError(null);
      
      // Create a copy of the taxation data to modify before submission
      const dataToSubmit = {
        ...taxationData,
        filing_status: 'filed'
      };
      
      // Remove ev_purchase_date field as it's not expected by the backend
      if (dataToSubmit.deductions && dataToSubmit.deductions.ev_purchase_date) {
        delete dataToSubmit.deductions.ev_purchase_date;
      }
      
      // Save the data with filed status
      await saveTaxationData(dataToSubmit);
      
      setSuccess('Tax declaration submitted successfully!');
      
      // Redirect after a short delay
      setTimeout(() => {
        navigate('/taxation');
      }, 2000);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error submitting tax declaration:', err);
      }
      setError('Failed to submit tax declaration. Please try again later.');
    } finally {
      setSubmitting(false);
    }
  };

  // Fetch VRS value from backend
  const fetchVrsValue = async () => {
    try {
      if (!empId) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Employee ID is missing');
        }
        return;
      }
      
      const vrsValue = await computeVrsValue(empId);
      if (vrsValue) {
        handleInputChange('voluntary_retirement', 'voluntary_retirement_amount', vrsValue);
        return vrsValue;
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching VRS value:', error);
      }
      setError('Failed to compute VRS value. Please try again later.');
    }
  };

  const calculateTaxBreakup = async () => {
    try {
      setSubmitting(true);
      setError(null);
      
      const breakup = await calculateTax(empId, taxationData?.tax_year, taxationData?.regime);
      setTaxBreakup(breakup);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error calculating tax:', err);
      }
      setError('Failed to calculate tax');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    refetchTaxationData();
    setError(null);
    setSuccess(null);
    setTaxBreakup(null);
  };

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  return {
    taxationData,
    setTaxationData,
    calculatedTax,
    setCalculatedTax,
    taxCalculationResponse,
    setTaxCalculationResponse,
    loading,
    submitting,
    error,
    setError,
    success,
    setSuccess,

    taxBreakup,
    setTaxBreakup,
    fetchTaxationData,
    handleInputChange,
    handleNestedInputChange,
    handleRegimeChange,
    handleFocus,
    handleNestedFocus,

    handleCalculateTax,
    handleSubmit,
    fetchVrsValue,
    calculateTaxBreakup,
    resetForm,
    clearMessages,
    refetch: fetchTaxationData,
    // React Query specific properties
    queryClient,
    refetchTaxationData,
    isLoading: loading,
    queryError
  };
};

export default useTaxationForm; 