import { useQuery, useMutation } from '@tanstack/react-query';
import { EmployeeExportRequest, EmployeeExportPreviewRequest } from '../types/api';
import { employeeApi } from '../api/employeeApi';

// Types for better type safety
export interface EmployeeExportFilters {
  search?: string;
  department?: string;
  role?: string;
  designation?: string;
  location?: string;
  manager_id?: string;
  include_inactive?: boolean;
  include_deleted?: boolean;
  // Date filters
  date_of_joining_from?: string;
  date_of_joining_to?: string;
  date_of_leaving_from?: string;
  date_of_leaving_to?: string;
  date_of_birth_from?: string;
  date_of_birth_to?: string;
}

export interface EmployeeExportResponse {
  success: boolean;
  message: string;
  download_url?: string;
}

// Query Keys following the project pattern
export const employeeExportKeys = {
  all: ['employeeExport'] as const,
  previews: () => [...employeeExportKeys.all, 'preview'] as const,
  preview: (request: EmployeeExportPreviewRequest) => [...employeeExportKeys.previews(), request] as const,
  exports: () => [...employeeExportKeys.all, 'export'] as const,
  export: (request: EmployeeExportRequest) => [...employeeExportKeys.exports(), request] as const,
};

// Hook for preview data - uses useQuery for caching and automatic state management
export const useEmployeePreviewQuery = (request: EmployeeExportPreviewRequest, enabled = false) => {
  return useQuery({
    queryKey: employeeExportKeys.preview(request),
    queryFn: async (): Promise<any[]> => {
      // Get employee data using the basic API
      const filters: any = {
        limit: request.limit || 10,
        skip: 0,
      };
      
      // Only add defined values to avoid undefined issues
      if (request.filters.search) filters.search = request.filters.search;
      if (request.filters.department) filters.department = request.filters.department;
      if (request.filters.role) filters.role = request.filters.role;
      if (request.filters.designation) filters.designation = request.filters.designation;
      if (request.filters.location) filters.location = request.filters.location;
      if (request.filters.manager_id) filters.manager_id = request.filters.manager_id;
      if (request.filters.include_inactive !== undefined) filters.include_inactive = request.filters.include_inactive;
      if (request.filters.include_deleted !== undefined) filters.include_deleted = request.filters.include_deleted;
      
      const response = await employeeApi.getEmployees(filters);
      
      // Define which fields are available for preview (from basic API)
      const availableForPreview = [
        'employee_id', 'name', 'email', 'mobile', 'role', 'status', 
        'department', 'designation', 'date_of_joining', 'manager_id', 
        'location', 'gender', 'is_active', 'profile_completion_percentage',
        'last_login_at', 'created_at'
      ];
      
      // Return only the selected fields that are actually available for preview
      return response.employees.map((employee: any) => {
        const filteredEmployee: any = {};
        request.fields.forEach(field => {
          let value = '';
          
          if (availableForPreview.includes(field)) {
            // Field is available in preview
            value = employee[field] || '';
          } else {
            // Field not available in preview - show placeholder
            value = '[Not available in preview]';
          }
          
          // Convert boolean values
          if (typeof value === 'boolean') {
            value = value ? 'Yes' : 'No';
          } else if (value === null || value === undefined) {
            value = '';
          }
          
          filteredEmployee[field] = String(value);
        });
        return filteredEmployee;
      });
    },
    enabled: enabled && request.fields.length > 0,
    staleTime: 2 * 60 * 1000, // 2 minutes - shorter since it's preview data
    gcTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
};

// Hook for export operations - uses useMutation for side effects
export const useEmployeeExportMutation = () => {
  return useMutation({
    mutationFn: async (request: EmployeeExportRequest): Promise<Blob> => {
      // Prepare filters for the API call
      const filters = {
        ...request.filters,
        fields: request.fields,
        format: request.format,
      };
      
      return await employeeApi.exportEmployees(filters);
    },
    onSuccess: () => {
      // Optionally invalidate related queries after successful export
      // queryClient.invalidateQueries({ queryKey: employeeExportKeys.previews() });
    },
    onError: (error) => {
      console.error('Export failed:', error);
    },
  });
};

// Legacy hook interface for backward compatibility
export const useEmployeeExport = () => {
  const exportMutation = useEmployeeExportMutation();
  
  return {
    exportEmployees: exportMutation.mutate,
    isExporting: exportMutation.isPending,
    exportError: exportMutation.error?.message || null,
    // Legacy preview function - now just a wrapper
    previewEmployees: async (request: EmployeeExportPreviewRequest): Promise<any[]> => {
      // For immediate preview, we'll use the query directly
      // In practice, components should use useEmployeePreviewQuery directly
      const filters: any = {
        limit: request.limit || 10,
        skip: 0,
      };
      
      if (request.filters.search) filters.search = request.filters.search;
      if (request.filters.department) filters.department = request.filters.department;
      if (request.filters.role) filters.role = request.filters.role;
      if (request.filters.designation) filters.designation = request.filters.designation;
      if (request.filters.location) filters.location = request.filters.location;
      if (request.filters.manager_id) filters.manager_id = request.filters.manager_id;
      if (request.filters.include_inactive !== undefined) filters.include_inactive = request.filters.include_inactive;
      if (request.filters.include_deleted !== undefined) filters.include_deleted = request.filters.include_deleted;
      
      const response = await employeeApi.getEmployees(filters);
      
      const availableForPreview = [
        'employee_id', 'name', 'email', 'mobile', 'role', 'status', 
        'department', 'designation', 'date_of_joining', 'manager_id', 
        'location', 'gender', 'is_active', 'profile_completion_percentage',
        'last_login_at', 'created_at'
      ];
      
      return response.employees.map((employee: any) => {
        const filteredEmployee: any = {};
        request.fields.forEach(field => {
          let value = '';
          
          if (availableForPreview.includes(field)) {
            value = employee[field] || '';
          } else {
            value = '[Not available in preview]';
          }
          
          if (typeof value === 'boolean') {
            value = value ? 'Yes' : 'No';
          } else if (value === null || value === undefined) {
            value = '';
          }
          
          filteredEmployee[field] = String(value);
        });
        return filteredEmployee;
      });
    },
    isLoadingPreview: false, // This should be handled by the query hook
  };
}; 