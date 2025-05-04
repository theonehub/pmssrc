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

    // Initialize other_sources if missing
    if (!taxationData.other_sources) {
      taxationData.other_sources = {
        interest_savings: 0,
        interest_fd: 0,
        interest_rd: 0,
        dividend_income: 0,
        gifts: 0,
        other_interest: 0,
        other_income: 0
      };
    }

    // Initialize capital_gains if missing
    if (!taxationData.capital_gains) {
      taxationData.capital_gains = {
        stcg_111a: 0,
        stcg_any_other_asset: 0,
        stcg_debt_mutual_fund: 0,
        ltcg_112a: 0,
        ltcg_any_other_asset: 0,
        ltcg_debt_mutual_fund: 0
      };
    }

    // Initialize deductions if missing
    if (!taxationData.deductions) {
      taxationData.deductions = {
        section_80c_lic: 0,
        section_80c_epf: 0,
        section_80c_ssp: 0,
        section_80c_nsc: 0,
        section_80c_ulip: 0,
        section_80c_tsmf: 0,
        section_80c_tffte2c: 0,
        section_80c_paphl: 0,
        section_80c_sdpphp: 0,
        section_80c_tsfdsb: 0,
        section_80c_scss: 0,
        section_80c_others: 0,
        section_80ccc_ppic: 0,
        section_80ccd_1_nps: 0,
        section_80ccd_1b_additional: 0,
        section_80ccd_2_enps: 0,
        section_80d_hisf: 0,
        section_80d_phcs: 0,
        section_80d_hi_parent: 0,
        section_80dd: 0,
        relation_80dd: '',
        disability_percentage: '',
        section_80ddb: 0,
        relation_80ddb: '',
        age_80ddb: 0,
        section_80eeb: 0,
        ev_purchase_date: null,
        section_80g: 0,
        section_80g_100_wo_ql: 0,
        section_80g_100_head: '',
        section_80g_50_wo_ql: 0,
        section_80g_50_head: '',
        section_80g_100_ql: 0,
        section_80g_100_ql_head: '',
        section_80g_50_ql: 0,
        section_80g_50_ql_head: '',
        section_80ggc: 0,
        section_80u: 0,
        disability_percentage_80u: ''
      };
    }
    
    // Initialize government employment status if missing
    if (taxationData.is_govt_employee === undefined) {
      taxationData.is_govt_employee = false;
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