import axios from 'axios';
import { getAuthToken } from '../utils/auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Set up axios instance with auth token
const apiClient = () => {
  const token = getAuthToken();
  return axios.create({
    baseURL: `${API_URL}`,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });
};

// Get all taxation records with optional filters
export const getAllTaxation = async (taxYear = null, filingStatus = null) => {
  try {
    let url = '/all-taxation';
    const params = {};
    
    if (taxYear) params.tax_year = taxYear;
    if (filingStatus) params.filing_status = filingStatus;
    
    const response = await apiClient().get(url, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching taxation data:', error);
    throw error;
  }
};

// Get taxation data for a specific employee
export const getTaxationByEmpId = async (empId) => {
  try {
    const response = await apiClient().get(`/taxation/${empId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching employee taxation data:', error);
    throw error;
  }
};

// Calculate tax for an employee
export const calculateTax = async (empId, taxYear = null, regime = null) => {
  try {
    const response = await apiClient().post('/calculate-tax', {
      emp_id: empId,
      tax_year: taxYear,
      regime: regime
    });
    return response.data;
  } catch (error) {
    console.error('Error calculating tax:', error);
    throw error;
  }
};

// Submit or update taxation data
export const saveTaxationData = async (taxationData) => {
  try {
    // Add filing_status if not present
    if (!taxationData.filing_status) {
      taxationData.filing_status = 'draft';
    }
    
    // Add default values for other required fields if not present
    if (!taxationData.tax_breakup) {
      taxationData.tax_breakup = {};
    }
    
    // Make sure salary components exist
    if (!taxationData.salary) {
      taxationData.salary = {
        basic: 0,
        dearness_allowance: 0,
        hra: 0,
        special_allowance: 0,
        bonus: 0,
        perquisites: {
          company_car: 0,
          rent_free_accommodation: 0,
          concessional_loan: 0,
          gift_vouchers: 0
        }
      };
    } else if (!taxationData.salary.perquisites) {
      // Initialize perquisites if missing
      taxationData.salary.perquisites = {
        company_car: 0,
        rent_free_accommodation: 0,
        concessional_loan: 0,
        gift_vouchers: 0
      };
    }
    
    // Initialize payment fields if not present
    if (taxationData.tax_payable === undefined) taxationData.tax_payable = 0;
    if (taxationData.tax_paid === undefined) taxationData.tax_paid = 0;
    if (taxationData.tax_due === undefined) taxationData.tax_due = 0;
    if (taxationData.tax_refundable === undefined) taxationData.tax_refundable = 0;
    if (taxationData.tax_pending === undefined) taxationData.tax_pending = 0;
    
    const response = await apiClient().post('/save-taxation-data', taxationData);
    return response.data;
  } catch (error) {
    console.error('Error saving taxation data:', error);
    throw error;
  }
};

// Update tax payment
export const updateTaxPayment = async (empId, amountPaid) => {
  try {
    const response = await apiClient().post('/update-tax-payment', {
      emp_id: empId,
      amount_paid: amountPaid
    });
    return response.data;
  } catch (error) {
    console.error('Error updating tax payment:', error);
    throw error;
  }
};

// Update filing status
export const updateFilingStatus = async (empId, status) => {
  try {
    const response = await apiClient().post('/update-filing-status', {
      emp_id: empId,
      status: status
    });
    return response.data;
  } catch (error) {
    console.error('Error updating filing status:', error);
    throw error;
  }
};

// Get current user's taxation data
export const getMyTaxation = async () => {
  try {
    const response = await apiClient().get(`/my-taxation`);
    return response.data;
  } catch (error) {
    console.error('Error fetching my taxation data:', error);
    throw error;
  }
}; 