import { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getTaxationByEmpId, saveTaxationData, calculateTax, computeVrsValue } from '../../../shared/api/taxationService';
import { getDefaultTaxationState, parseIndianNumber } from '../utils/taxationUtils';

/**
 * Custom hook for managing taxation form state and operations
 * @param {string} empId - Employee ID 
 * @returns {Object} Form state and handlers
 */
const useTaxationForm = (empId) => {
  const [taxationData, setTaxationData] = useState(getDefaultTaxationState(empId));
  const [calculatedTax, setCalculatedTax] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [cityForHRA, setCityForHRA] = useState('Others');
  const [autoComputeHRA, setAutoComputeHRA] = useState(true);
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
      return await getTaxationByEmpId(empId);
    },
    enabled: !!empId,
    retry: (failureCount, error) => {
      // Don't retry on 404 errors (no record found)
      if (error?.response?.status === 404) {
        return false;
      }
      return failureCount < 2;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes cache time
  });

  // Handle data population when query succeeds or fails
  useEffect(() => {
    if (fetchedData) {
      // Successfully fetched data - populate form with server data
      setTaxationData(prevData => {
        const updatedData = {
          ...fetchedData,
          // Ensure employee_id is set
          employee_id: empId,
          
          // Populate Employee Age if available from server
          emp_age: fetchedData.emp_age || fetchedData.age || prevData.emp_age || 0,
          
          // Populate Government Employee status if available from server
          is_govt_employee: fetchedData.is_govt_employee !== undefined 
            ? fetchedData.is_govt_employee 
            : prevData.is_govt_employee || false,
            
          // Populate Tax Regime if available from server
          regime: fetchedData.regime || fetchedData.regime_type || prevData.regime || 'old',
        };
        
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.log('Populated taxation data:', {
            emp_age: updatedData.emp_age,
            is_govt_employee: updatedData.is_govt_employee,
            regime: updatedData.regime,
            employee_id: updatedData.employee_id
          });
        }
        
        return updatedData;
      });
      
      // Set city for HRA if available
      if (fetchedData.salary && fetchedData.salary.hra_city) {
        setCityForHRA(fetchedData.salary.hra_city);
      }
      
      // Reset calculated tax when new data is loaded
      setCalculatedTax(null);
      setError(null);
    } else if (queryError) {
      // Handle query error
      if (queryError.response && queryError.response.status === 404) {
        // No existing record found - initialize with default values
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.log('No existing taxation record found, initializing with defaults');
        }
        const defaultData = getDefaultTaxationState(empId);
        setTaxationData(defaultData);
        setError(null);
      } else {
        // Other errors
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('Error fetching taxation data:', queryError);
        }
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
    // If value is string with numbers, parse it
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
    } else {
      parsedValue = typeof value === 'string' ? parseIndianNumber(value) : value;
      parsedValue = parseFloat(parsedValue) || 0;
    }
    
    // Reset calculatedTax to null when any value changes
    setCalculatedTax(null);
    
    setTaxationData((prevData) => ({
      ...prevData,
      [section]: {
        ...prevData[section],
        [field]: parsedValue
      }
    }));
  };

  // Handle input change for nested fields
  const handleNestedInputChange = (section, nestedSection, field, value) => {
    // Check if the field should be treated as a string (not converted to number)
    const stringFields = [
      'accommodation_provided', 'accommodation_city_population', 'car_use', 
      'travel_through', 'loan_type', 'lta_claim_start_date', 'lta_claim_end_date',
      'grant_date', 'vesting_date', 'exercise_date', 'mat_type', 'mau_ownership',
      'loan_start_date', 'loan_end_date', 'uncomputed_pension_frequency', 'mat_number_of_completed_years_of_use'
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

  // Compute HRA based on city and salary components
  const computeHRA = (cities) => {
    const basic = taxationData.salary.basic || 0;
    const da = taxationData.salary.dearness_allowance || 0;
    const baseAmount = basic + da;
    
    const selectedCity = cities.find(city => city.value === cityForHRA);
    const rate = selectedCity ? selectedCity.rate : 0.4;
    handleInputChange('salary', 'hra_percentage', rate);
    
    // Don't use handleInputChange for string values
    setTaxationData((prevData) => ({
      ...prevData,
      salary: {
        ...prevData.salary,
        hra_city: cityForHRA
      }
    }));
    
    return Math.round(baseAmount * rate);
  };

  // Handle city change
  const handleCityChange = (event) => {
    setCityForHRA(event.target.value);
    
    // Directly set the hra_city value without going through handleInputChange
    // This avoids the parseFloat conversion that's causing the issue
    setTaxationData((prevData) => ({
      ...prevData,
      salary: {
        ...prevData.salary,
        hra_city: event.target.value
      }
    }));
  };

  // Handle HRA manual edit
  const handleHRAChange = (e) => {
    setAutoComputeHRA(false);
    handleInputChange('salary', 'hra', e.target.value);
  };

  // Calculate tax
  const handleCalculateTax = async () => {
    try {
      setSubmitting(true);
      setError(null);
      
      // Create a copy of the taxation data to modify before submission
      const dataToSubmit = {...taxationData};
      
      // Remove ev_purchase_date field as it's not expected by the backend
      if (dataToSubmit.deductions && dataToSubmit.deductions.ev_purchase_date) {
        delete dataToSubmit.deductions.ev_purchase_date;
      }
      
      // First save the taxation data
      await saveTaxationData(dataToSubmit);
      
      // Then calculate the tax
      const result = await calculateTax(empId, taxationData.tax_year, taxationData.regime);
      setCalculatedTax(result.total_tax);
      
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
    loading,
    submitting,
    error,
    setError,
    success,
    setSuccess,
    cityForHRA,
    setCityForHRA,
    autoComputeHRA,
    setAutoComputeHRA,
    taxBreakup,
    setTaxBreakup,
    fetchTaxationData,
    handleInputChange,
    handleNestedInputChange,
    handleRegimeChange,
    handleFocus,
    handleNestedFocus,
    computeHRA,
    handleCityChange,
    handleHRAChange,
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