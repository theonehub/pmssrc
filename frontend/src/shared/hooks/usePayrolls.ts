import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

export interface Payout {
  id: string;
  pay_period_start: string;
  pay_period_end: string;
  total_employees: number;
  total_amount: number;
  status: string;
  payout_date: string;
  employees?: Array<{
    id: string;
    name: string;
    department: string;
    gross_salary: number;
    total_deductions: number;
    net_salary: number;
  }>;
}

export interface PayrollsResponse {
  payouts: Payout[];
  total: number;
  page: number;
  limit: number;
}

interface UsePayrollsQueryParams {
  year?: number;
  month?: number | null;
  page?: number;
  limit?: number;
}

export const usePayrollsQuery = (params: UsePayrollsQueryParams = {}) => {
  const { year, month, page = 1, limit = 10 } = params;

  return useQuery<PayrollsResponse>({
    queryKey: ['payrolls', year, month, page, limit],
    queryFn: async () => {
      const response = await apiClient.get('/api/v2/payouts', {
        params: {
          year,
          month,
          page,
          limit
        }
      });
      return response.data;
    },
    enabled: !!year
  });
}; 