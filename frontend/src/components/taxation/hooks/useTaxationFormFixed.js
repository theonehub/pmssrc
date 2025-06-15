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
  console.log('🔄 Starting transformation of comprehensive record:', comprehensiveRecord);
  
  if (!comprehensiveRecord) {
    console.log('⚠️ No comprehensive record provided, returning default state');
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
      console.log('💰 Transforming salary income:', comprehensiveRecord.salary_income);
      const salaryData = comprehensiveRecord.salary_income;
      transformedData.salary_income = {
        ...defaultState.salary_income,
        basic_salary: toNumber(salaryData.basic_salary),
        dearness_allowance: toNumber(salaryData.dearness_allowance),
        hra_received: toNumber(salaryData.hra_received),
        actual_rent_paid: toNumber(salaryData.actual_rent_paid),
        hra_city_type: salaryData.hra_city_type || 'non_metro',
        special_allowance: toNumber(salaryData.special_allowance),
        conveyance_allowance: toNumber(salaryData.conveyance_allowance),
        medical_allowance: toNumber(salaryData.medical_allowance),
        other_allowances: toNumber(salaryData.other_allowances),
        bonus: toNumber(salaryData.bonus),
        commission: toNumber(salaryData.commission),
        lta_received: toNumber(salaryData.lta_received),
        // All the detailed allowances
        city_compensatory_allowance: toNumber(salaryData.city_compensatory_allowance),
        rural_allowance: toNumber(salaryData.rural_allowance),
        proctorship_allowance: toNumber(salaryData.proctorship_allowance),
        wardenship_allowance: toNumber(salaryData.wardenship_allowance),
        project_allowance: toNumber(salaryData.project_allowance),
        deputation_allowance: toNumber(salaryData.deputation_allowance),
        overtime_allowance: toNumber(salaryData.overtime_allowance),
        interim_relief: toNumber(salaryData.interim_relief),
        tiffin_allowance: toNumber(salaryData.tiffin_allowance),
        servant_allowance: toNumber(salaryData.servant_allowance),
        govt_employees_outside_india_allowance: toNumber(salaryData.govt_employees_outside_india_allowance),
        supreme_high_court_judges_allowance: toNumber(salaryData.supreme_high_court_judges_allowance),
        judge_compensatory_allowance: toNumber(salaryData.judge_compensatory_allowance),
        section_10_14_special_allowances: toNumber(salaryData.section_10_14_special_allowances),
        any_other_allowance_exemption: toNumber(salaryData.any_other_allowance_exemption),
        travel_on_tour_allowance: toNumber(salaryData.travel_on_tour_allowance),
        tour_daily_charge_allowance: toNumber(salaryData.tour_daily_charge_allowance),
        conveyance_in_performace_of_duties: toNumber(salaryData.conveyance_in_performace_of_duties),
        helper_in_performace_of_duties: toNumber(salaryData.helper_in_performace_of_duties),
        academic_research: toNumber(salaryData.academic_research),
        uniform_allowance: toNumber(salaryData.uniform_allowance),
        hills_high_altd_allowance: toNumber(salaryData.hills_high_altd_allowance),
        hills_high_altd_exemption_limit: toNumber(salaryData.hills_high_altd_exemption_limit),
        border_remote_allowance: toNumber(salaryData.border_remote_allowance),
        border_remote_exemption_limit: toNumber(salaryData.border_remote_exemption_limit),
        transport_employee_allowance: toNumber(salaryData.transport_employee_allowance),
        children_education_allowance: toNumber(salaryData.children_education_allowance),
        children_education_count: toNumber(salaryData.children_education_count),
        children_education_months: toNumber(salaryData.children_education_months),
        hostel_allowance: toNumber(salaryData.hostel_allowance),
        hostel_count: toNumber(salaryData.hostel_count),
        hostel_months: toNumber(salaryData.hostel_months),
        transport_months: toNumber(salaryData.transport_months),
        underground_mines_allowance: toNumber(salaryData.underground_mines_allowance),
        underground_mines_months: toNumber(salaryData.underground_mines_months),
        govt_employee_entertainment_allowance: toNumber(salaryData.govt_employee_entertainment_allowance),
      };
      console.log('✅ Transformed salary income:', transformedData.salary_income);
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
        fair_rental_value: toNumber(houseData.fair_rental_value),
        standard_rent: toNumber(houseData.standard_rent),
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
      console.log('📋 Transforming deductions:', comprehensiveRecord.deductions);
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

    console.log('✅ Final transformed data:', {
      employee_id: transformedData.employee_id,
      age: transformedData.age,
      regime: transformedData.regime,
      basic_salary: transformedData.salary_income?.basic_salary,
      has_deductions: !!transformedData.deductions,
    });

    return transformedData;
  } catch (error) {
    console.error('❌ Error transforming comprehensive record:', error);
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
      console.log('🔍 Fetching taxation data for employee:', empId);
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
    console.log('🔍 useEffect triggered with:', { 
      hasFetchedData: !!fetchedData, 
      hasQueryError: !!queryError, 
      empId,
      fetchedDataKeys: fetchedData ? Object.keys(fetchedData) : null
    });
    
    if (fetchedData) {
      console.log('📥 Raw comprehensive taxation data received:', fetchedData);
      
      // Successfully fetched comprehensive taxation record - transform and populate form
      const transformedData = transformComprehensiveRecordToFormData(fetchedData, empId);
      
      console.log('🔄 Setting transformed data to state');
      setTaxationData(transformedData);
      
      // Set city for HRA if available
      if (transformedData.salary_income?.hra_city_type) {
        const cityMapping = {
          'metro': 'Delhi', // Default metro city
          'non_metro': 'Others'
        };
        setCityForHRA(cityMapping[transformedData.salary_income.hra_city_type] || 'Others');
        console.log('🏙️ Set city for HRA:', cityMapping[transformedData.salary_income.hra_city_type] || 'Others');
      }
      
      // Reset calculated tax when new data is loaded
      setCalculatedTax(null);
      setError(null);
      
      console.log('✅ Form populated with comprehensive taxation record');
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

  // Rest of the hook methods remain the same...
  // (I'll include the essential methods for brevity)

  const handleInputChange = (section, field, value) => {
    const isCalculatorExpression = typeof value === 'string' && value.startsWith('=');
    
    let parsedValue;
    const stringFields = [
      'occupancy_status', 'property_address', 'relation_80dd', 'section_80g_100_head',
      'relation_80ddb', 'disability_percentage', 'disability_percentage_80u', 'ev_purchase_date',
      'section_80g_100_ql_head', 'section_80g_50_head', 'section_80g_50_ql_head', 'uncomputed_pension_frequency',
      'hra_city_type'
    ];
    
    if (stringFields.includes(field)) {
      parsedValue = value;
    } else if (typeof value === 'boolean') {
      parsedValue = value;
    } else if (isCalculatorExpression) {
      parsedValue = value;
    } else {
      parsedValue = typeof value === 'string' ? parseIndianNumber(value) : value;
      parsedValue = parseFloat(parsedValue) || 0;
    }
    
    setCalculatedTax(null);
    
    setTaxationData((prevData) => ({
      ...prevData,
      [section]: {
        ...prevData[section],
        [field]: parsedValue
      }
    }));
  };

  const handleSubmit = async (navigate) => {
    try {
      setSubmitting(true);
      setError(null);
      
      const dataToSubmit = {
        ...taxationData,
        filing_status: 'filed'
      };
      
      await saveTaxationData(dataToSubmit);
      setSuccess('Tax declaration submitted successfully!');
      
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
    handleInputChange,
    handleSubmit,
    // Add other methods as needed
    queryClient,
    refetchTaxationData,
    isLoading: loading,
    queryError
  };
};

export default useTaxationForm; 