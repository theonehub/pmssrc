import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api';
import { LeaveBalanceData } from '../types';
import { leavesApi, LeaveApprovalRequest } from '../api/leavesApi';

export const useLeavesQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['leaves', filters],
    queryFn: async () => {
      const response = await apiClient.get('/v2/employee-leave/', { params: filters });
      return response.data;
    },
  });
};

export const useLeaveBalanceQuery = () => {
  return useQuery({
    queryKey: ['leave-balance'],
    queryFn: async (): Promise<LeaveBalanceData> => {
      const response = await apiClient.get('/v2/leaves/leave-balance');
      return response.data;
    },
  });
};

export const useApproveLeaveMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ leaveId, approvalData }: { leaveId: string; approvalData: LeaveApprovalRequest }) => {
      return await leavesApi.processLeaveRequest(leaveId, approvalData);
    },
    onSuccess: () => {
      // Invalidate and refetch leaves data
      queryClient.invalidateQueries({ queryKey: ['leaves'] });
    },
  });
}; 