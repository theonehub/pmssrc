import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api';

// Types
export interface PublicHoliday {
  id: string;
  name: string;
  holiday_date: string;
  description?: string;
  category?: string;
  observance?: string;
  recurrence?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by?: string;
}

export interface PublicHolidaysResponse {
  holidays: PublicHoliday[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface HolidayFormData {
  name: string;
  holiday_date: string;
  description?: string;
  category?: string;
  observance?: string;
  recurrence?: string;
  is_active?: boolean;
}

export interface PublicHolidayFilters {
  skip?: number;
  limit?: number;
  year?: number;
  month?: number;
  is_active?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// Query Keys
export const publicHolidayKeys = {
  all: ['public-holidays'] as const,
  lists: () => [...publicHolidayKeys.all, 'list'] as const,
  list: (filters: PublicHolidayFilters) => [...publicHolidayKeys.lists(), filters] as const,
  details: () => [...publicHolidayKeys.all, 'detail'] as const,
  detail: (id: string) => [...publicHolidayKeys.details(), id] as const,
};

// Hooks
export const usePublicHolidaysQuery = (filters: PublicHolidayFilters = {}) => {
  return useQuery({
    queryKey: publicHolidayKeys.list(filters),
    queryFn: async (): Promise<PublicHolidaysResponse> => {
      const params = new URLSearchParams();
      
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
      if (filters.year !== undefined) params.append('year', filters.year.toString());
      if (filters.month !== undefined) params.append('month', filters.month.toString());
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.sort_order) params.append('sort_order', filters.sort_order);

      const response = await apiClient.get(`/v2/public-holidays/?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const usePublicHolidayQuery = (id: string) => {
  return useQuery({
    queryKey: publicHolidayKeys.detail(id),
    queryFn: async (): Promise<PublicHoliday> => {
      const response = await apiClient.get(`/v2/public-holidays/${id}`);
      return response.data;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
};

export const useCreatePublicHolidayMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: HolidayFormData): Promise<PublicHoliday> => {
      const response = await apiClient.post('/v2/public-holidays/', data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch public holidays list
      queryClient.invalidateQueries({ queryKey: publicHolidayKeys.lists() });
    },
  });
};

export const useUpdatePublicHolidayMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: HolidayFormData }): Promise<PublicHoliday> => {
      const response = await apiClient.put(`/v2/public-holidays/${id}`, data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidate and refetch public holidays list
      queryClient.invalidateQueries({ queryKey: publicHolidayKeys.lists() });
      // Update the specific holiday in cache
      queryClient.setQueryData(publicHolidayKeys.detail(variables.id), data);
    },
  });
};

export const useDeletePublicHolidayMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await apiClient.delete(`/v2/public-holidays/${id}`);
    },
    onSuccess: (_, id) => {
      // Invalidate and refetch public holidays list
      queryClient.invalidateQueries({ queryKey: publicHolidayKeys.lists() });
      // Remove the specific holiday from cache
      queryClient.removeQueries({ queryKey: publicHolidayKeys.detail(id) });
    },
  });
};

export const useImportPublicHolidaysMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File): Promise<PublicHoliday[]> => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/v2/public-holidays/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch public holidays list
      queryClient.invalidateQueries({ queryKey: publicHolidayKeys.lists() });
    },
  });
}; 