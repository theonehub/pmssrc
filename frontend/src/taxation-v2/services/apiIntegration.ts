import axios, { AxiosInstance, AxiosResponse } from 'axios';

// =============================================================================
// INTERFACES & TYPES
// =============================================================================

interface BankAccount {
  id: string;
  bankName: string;
  accountNumber: string;
  accountType: 'savings' | 'current' | 'salary';
  balance: number;
  currency: string;
}

interface BankTransaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: 'debit' | 'credit';
  category: string;
  balance: number;
}

interface InvestmentAccount {
  id: string;
  provider: string;
  accountType: 'mutual_fund' | 'stocks' | 'bonds' | 'ppf' | 'nps';
  currentValue: number;
  investedAmount: number;
  gains: number;
  gainsPercentage: number;
}

interface InvestmentTransaction {
  id: string;
  date: string;
  type: 'buy' | 'sell' | 'dividend' | 'interest';
  instrument: string;
  quantity?: number;
  price?: number;
  amount: number;
  tax?: number;
}

interface TaxRuleUpdate {
  effectiveDate: string;
  section: string;
  description: string;
  impact: 'benefit' | 'liability' | 'neutral';
  details: string;
}

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

interface PaginatedResponse<T> {
  data: T[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

// =============================================================================
// API INTEGRATION SERVICE
// =============================================================================

export class ApiIntegrationService {
  private bankingApi: AxiosInstance;
  private investmentApi: AxiosInstance;
  private governmentApi: AxiosInstance;

  constructor() {
    // Banking API (e.g., Open Banking APIs)
    this.bankingApi = axios.create({
      baseURL: process.env.REACT_APP_BANKING_API_URL || 'https://api.openbanking.demo.com',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Investment Platform APIs (e.g., Zerodha, Groww, etc.)
    this.investmentApi = axios.create({
      baseURL: process.env.REACT_APP_INVESTMENT_API_URL || 'https://api.investment-platform.com',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Government APIs (e.g., Income Tax Department)
    this.governmentApi = axios.create({
      baseURL: process.env.REACT_APP_GOVERNMENT_API_URL || 'https://api.incometax.gov.in',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  // =============================================================================
  // SETUP INTERCEPTORS
  // =============================================================================

  private setupInterceptors() {
    // Request interceptors to add auth headers
    const addAuthHeader = (config: any) => {
      const token = localStorage.getItem('api_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    };

    this.bankingApi.interceptors.request.use(addAuthHeader);
    this.investmentApi.interceptors.request.use(addAuthHeader);
    this.governmentApi.interceptors.request.use(addAuthHeader);

    // Response interceptors for error handling
    const handleApiError = (error: any) => {
      console.error('API Error:', error);
      
      if (error.response?.status === 401) {
        // Handle unauthorized access
        localStorage.removeItem('api_token');
      }
      
      return Promise.reject(error);
    };

    this.bankingApi.interceptors.response.use((response) => response, handleApiError);
    this.investmentApi.interceptors.response.use((response) => response, handleApiError);
    this.governmentApi.interceptors.response.use((response) => response, handleApiError);
  }

  // =============================================================================
  // BANKING INTEGRATION
  // =============================================================================

  async linkBankAccount(bankId: string, credentials: any): Promise<BankAccount> {
    try {
      const response: AxiosResponse<ApiResponse<BankAccount>> = await this.bankingApi.post('/accounts/link', {
        bankId,
        credentials
      });
      
      return response.data.data;
    } catch (error) {
      throw new Error('Failed to link bank account');
    }
  }

  async getBankAccounts(): Promise<BankAccount[]> {
    try {
      const response: AxiosResponse<ApiResponse<BankAccount[]>> = await this.bankingApi.get('/accounts');
      return response.data.data;
    } catch (error) {
      throw new Error('Failed to fetch bank accounts');
    }
  }

  async getBankTransactions(
    accountId: string, 
    fromDate: string, 
    toDate: string,
    page: number = 1,
    limit: number = 50
  ): Promise<PaginatedResponse<BankTransaction>> {
    try {
      const response: AxiosResponse<ApiResponse<PaginatedResponse<BankTransaction>>> = 
        await this.bankingApi.get(`/accounts/${accountId}/transactions`, {
          params: { fromDate, toDate, page, limit }
        });
      
      return response.data.data;
    } catch (error) {
      throw new Error('Failed to fetch bank transactions');
    }
  }

  // =============================================================================
  // INVESTMENT INTEGRATION
  // =============================================================================

  async getInvestmentAccounts(): Promise<InvestmentAccount[]> {
    try {
      const response: AxiosResponse<ApiResponse<InvestmentAccount[]>> = 
        await this.investmentApi.get('/accounts');
      
      return response.data.data;
    } catch (error) {
      throw new Error('Failed to fetch investment accounts');
    }
  }

  async getInvestmentTransactions(
    accountId: string,
    fromDate: string,
    toDate: string
  ): Promise<InvestmentTransaction[]> {
    try {
      const response: AxiosResponse<ApiResponse<InvestmentTransaction[]>> = 
        await this.investmentApi.get(`/accounts/${accountId}/transactions`, {
          params: { fromDate, toDate }
        });
      
      return response.data.data;
    } catch (error) {
      throw new Error('Failed to fetch investment transactions');
    }
  }

  // =============================================================================
  // GOVERNMENT API INTEGRATION
  // =============================================================================

  async getTaxRuleUpdates(): Promise<TaxRuleUpdate[]> {
    try {
      const response: AxiosResponse<ApiResponse<TaxRuleUpdate[]>> = 
        await this.governmentApi.get('/tax-rules/updates');
      
      return response.data.data;
    } catch (error) {
      console.error('Failed to fetch tax rule updates:', error);
      return [];
    }
  }

  async validatePAN(panNumber: string): Promise<boolean> {
    try {
      const response: AxiosResponse<ApiResponse<{ valid: boolean }>> = 
        await this.governmentApi.post('/validate-pan', { panNumber });
      
      return response.data.data.valid;
    } catch (error) {
      console.error('Failed to validate PAN:', error);
      return true; // Assume valid if service is unavailable
    }
  }

  // =============================================================================
  // DEMO DATA GENERATORS
  // =============================================================================

  generateMockBankData(): { accounts: BankAccount[], transactions: BankTransaction[] } {
    const accounts: BankAccount[] = [
      {
        id: 'acc_001',
        bankName: 'HDFC Bank',
        accountNumber: '****1234',
        accountType: 'salary',
        balance: 250000,
        currency: 'INR'
      },
      {
        id: 'acc_002',
        bankName: 'ICICI Bank',
        accountNumber: '****5678',
        accountType: 'savings',
        balance: 180000,
        currency: 'INR'
      }
    ];

    const transactions: BankTransaction[] = Array.from({ length: 20 }, (_, i) => ({
      id: `txn_${i + 1}`,
      date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
      description: i % 5 === 0 ? 'Salary Credit' : i % 3 === 0 ? 'Investment SIP' : 'General Expense',
      amount: i % 5 === 0 ? 85000 : Math.random() * 10000,
      type: i % 5 === 0 ? 'credit' : 'debit',
      category: i % 5 === 0 ? 'salary' : i % 3 === 0 ? 'investment' : 'expense',
      balance: 250000 - i * 1000
    }));

    return { accounts, transactions };
  }

  generateMockInvestmentData(): { accounts: InvestmentAccount[], transactions: InvestmentTransaction[] } {
    const accounts: InvestmentAccount[] = [
      {
        id: 'inv_001',
        provider: 'Zerodha',
        accountType: 'stocks',
        currentValue: 450000,
        investedAmount: 380000,
        gains: 70000,
        gainsPercentage: 18.42
      },
      {
        id: 'inv_002',
        provider: 'Groww',
        accountType: 'mutual_fund',
        currentValue: 320000,
        investedAmount: 290000,
        gains: 30000,
        gainsPercentage: 10.34
      }
    ];

    const transactions: InvestmentTransaction[] = Array.from({ length: 15 }, (_, i) => {
      const transactionType = i % 4 === 0 ? 'sell' : i % 6 === 0 ? 'dividend' : 'buy';
      const baseTransaction: InvestmentTransaction = {
        id: `inv_txn_${i + 1}`,
        date: new Date(Date.now() - i * 7 * 24 * 60 * 60 * 1000).toISOString(),
        type: transactionType,
        instrument: i % 2 === 0 ? 'RELIANCE' : 'HDFC_EQUITY_FUND',
        amount: Math.random() * 50000
      };

      // Only add optional properties when they have values
      if (transactionType !== 'dividend') {
        baseTransaction.quantity = Math.floor(Math.random() * 100);
        baseTransaction.price = Math.random() * 1000;
      }

      if (transactionType === 'sell') {
        baseTransaction.tax = Math.random() * 1000;
      }

      return baseTransaction;
    });

    return { accounts, transactions };
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

export const apiIntegrationService = new ApiIntegrationService();
export default apiIntegrationService; 