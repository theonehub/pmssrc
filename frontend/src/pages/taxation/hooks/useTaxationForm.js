import { useState, useEffect } from 'react';
import { getTaxationByEmpId, saveTaxationData, calculateTax, computeVrsValue } from '../../../services/taxationService';
import { getDefaultTaxationState, parseIndianNumber } from '../utils/taxationUtils';

/**
 * Custom hook for managing taxation form state and operations
 * @param {string} empId - Employee ID 
 * @returns {Object} Form state and handlers
 */
const useTaxationForm = (empId) => {
  const [taxationData, setTaxationData] = useState(getDefaultTaxationState(empId));
  const [calculatedTax, setCalculatedTax] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [cityForHRA, setCityForHRA] = useState('Others');
  const [autoComputeHRA, setAutoComputeHRA] = useState(true);

  // Fetch taxation data
  const fetchTaxationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await getTaxationByEmpId(empId);
      
      if (result) {
        setTaxationData(result);
        
        // Set city for HRA if available
        if (result.salary && result.salary.hra_city) {
          setCityForHRA(result.salary.hra_city);
        }
        
        // Reset calculated tax
        setCalculatedTax(null);
      }
    } catch (err) {
      console.error('Error fetching taxation data:', err);
      setError('Failed to fetch taxation data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Load data on initial render
  useEffect(() => {
    fetchTaxationData();
  }, [empId]);

  // Handle input change for non-nested fields
  const handleInputChange = (section, field, value) => {
    // If value is string with numbers, parse it
    let parsedValue;
    const stringFields = [
      'occupancy_status', 'property_address', 'relation_80dd', 'section_80g_100_head',
      'relation_80ddb', 'disability_percentage', 'disability_percentage_80u', 'ev_purchase_date',
      'section_80g_100_ql_head', 'section_80g_50_head', 'section_80g_50_ql_head',
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
      console.error('Error calculating tax:', err);
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
      console.error('Error submitting tax declaration:', err);
      setError('Failed to submit tax declaration. Please try again later.');
    } finally {
      setSubmitting(false);
    }
  };

  // Fetch VRS value from backend
  const fetchVrsValue = async () => {
    try {
      if (!empId) {
        console.error('Employee ID is missing');
        return;
      }
      
      const vrsValue = await computeVrsValue(empId);
      if (vrsValue) {
        handleInputChange('voluntary_retirement', 'voluntary_retirement_amount', vrsValue);
        return vrsValue;
      }
    } catch (error) {
      console.error('Error fetching VRS value:', error);
      setError('Failed to compute VRS value. Please try again later.');
    }
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
    fetchVrsValue
  };
};

export default useTaxationForm; 