import { useQuery } from '@tanstack/react-query';
import { taxationApi } from '../api/taxationApi';
import { EmployeeSelectionQuery, EmployeeSelectionResponse } from '../types/api';
import { useQueryClient } from '@tanstack/react-query';

export const useEmployeeSelection = (query: EmployeeSelectionQuery = {}) => {
  return useQuery<EmployeeSelectionResponse>({
    queryKey: ['employee-selection', query],
    queryFn: () => taxationApi.getEmployeesForSelection(query),
    staleTime: 5 * 60 * 1000, // 5 minutes - data stays fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes - cache time (renamed from cacheTime in v5)
    retry: 2, // Retry failed requests twice
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
  });
};

// Hook for refreshing employee selection data
export const useRefreshEmployeeSelection = () => {
  const queryClient = useQueryClient();
  
  return (query?: EmployeeSelectionQuery) => {
    return queryClient.invalidateQueries({
      queryKey: ['employee-selection', query],
    });
  };
}; 