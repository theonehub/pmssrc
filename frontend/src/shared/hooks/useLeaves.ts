import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';
import { LeaveBalanceData } from '../types';

export const useLeavesQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['leaves', filters],
    queryFn: async () => {
      const response = await apiClient.get('/api/v2/employee-leave/', { params: filters });
      return response.data;
    },
  });
};

export const useLeaveBalanceQuery = () => {
  return useQuery({
    queryKey: ['leave-balance'],
    queryFn: async (): Promise<LeaveBalanceData> => {
      const response = await apiClient.get('/api/v2/leaves/leave-balance');
      return response.data;
    },
  });
}; 