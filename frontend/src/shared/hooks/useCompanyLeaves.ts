import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api';

// Types
export interface CompanyLeave {
  company_leave_id: string;
  leave_type: string;
  leave_name: string;
  accrual_type: string;
  annual_allocation: number;
  computed_monthly_allocation: number;
  is_active: boolean;
  description: string | null;
  encashable: boolean;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
}

export interface CompanyLeavesResponse {
  data?: {
    items: CompanyLeave[];
    total_count?: number;
    page?: number;
    page_size?: number;
  };
  items?: CompanyLeave[];
  total_count?: number;
  page?: number;
  page_size?: number;
}

export interface CompanyLeaveFormData {
  leave_type?: string;
  leave_name: string;
  accrual_type: string;
  annual_allocation: number;
  computed_monthly_allocation?: number;
  description?: string | null;
  encashable: boolean;
  is_active: boolean;
}

export interface CompanyLeaveFilters {
  organisation_id?: string;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}

// Query Keys
export const companyLeaveKeys = {
  all: ['companyLeaves'] as const,
  lists: () => [...companyLeaveKeys.all, 'list'] as const,
  list: (filters: CompanyLeaveFilters) => [...companyLeaveKeys.lists(), filters] as const,
  details: () => [...companyLeaveKeys.all, 'detail'] as const,
  detail: (id: string) => [...companyLeaveKeys.details(), id] as const,
};

// Hooks
export const useCompanyLeavesQuery = (filters: CompanyLeaveFilters = {}) => {
  return useQuery({
    queryKey: companyLeaveKeys.list(filters),
    queryFn: async (): Promise<CompanyLeavesResponse> => {
      const params = new URLSearchParams();
      
      if (filters.organisation_id) params.append('organisation_id', filters.organisation_id);
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());

      const queryString = params.toString();
      const response = await apiClient.get(`/api/v2/company-leaves${queryString ? `?${queryString}` : ''}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useCompanyLeaveQuery = (id: string) => {
  return useQuery({
    queryKey: companyLeaveKeys.detail(id),
    queryFn: async (): Promise<CompanyLeave> => {
      const response = await apiClient.get(`/api/v2/company-leaves/${id}`);
      return response.data;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useCreateCompanyLeaveMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CompanyLeaveFormData): Promise<CompanyLeave> => {
      const response = await apiClient.post('/api/v2/company-leaves', data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch company leaves list
      queryClient.invalidateQueries({ queryKey: companyLeaveKeys.lists() });
    },
  });
};

export const useUpdateCompanyLeaveMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: CompanyLeaveFormData }): Promise<CompanyLeave> => {
      const response = await apiClient.put(`/api/v2/company-leaves/${id}`, data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidate and refetch company leaves list
      queryClient.invalidateQueries({ queryKey: companyLeaveKeys.lists() });
      // Update the specific leave in cache
      queryClient.setQueryData(companyLeaveKeys.detail(variables.id), data);
    },
  });
};

export const useDeleteCompanyLeaveMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await apiClient.delete(`/api/v2/company-leaves/${id}`);
    },
    onSuccess: (_, id) => {
      // Invalidate and refetch company leaves list
      queryClient.invalidateQueries({ queryKey: companyLeaveKeys.lists() });
      // Remove the specific leave from cache
      queryClient.removeQueries({ queryKey: companyLeaveKeys.detail(id) });
    },
  });
}; 