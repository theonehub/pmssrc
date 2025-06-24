import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import {
  salaryComponentApi,
  CreateSalaryComponentRequest,
  UpdateSalaryComponentRequest,
  SalaryComponentFilters,
  FormulaValidationRequest,
  CreateEmployeeMappingRequest
} from '../api/salaryComponentApi';

// Query keys for React Query
const QUERY_KEYS = {
  SALARY_COMPONENTS: 'salary-components',
  SALARY_COMPONENT: 'salary-component',
  EMPLOYEE_MAPPINGS: 'employee-mappings',
  FORMULA_VALIDATION: 'formula-validation',
} as const;

export const useSalaryComponents = (filters?: SalaryComponentFilters) => {
  const queryClient = useQueryClient();

  // Get salary components list
  const {
    data: componentsData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: [QUERY_KEYS.SALARY_COMPONENTS, filters],
    queryFn: () => salaryComponentApi.getSalaryComponents(filters),
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Create component mutation
  const createComponentMutation = useMutation({
    mutationFn: (componentData: CreateSalaryComponentRequest) => 
      salaryComponentApi.createSalaryComponent(componentData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SALARY_COMPONENTS] });
      toast.success('Salary component created successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create salary component');
    },
  });

  // Update component mutation
  const updateComponentMutation = useMutation({
    mutationFn: ({ componentId, componentData }: { componentId: string; componentData: UpdateSalaryComponentRequest }) =>
      salaryComponentApi.updateSalaryComponent(componentId, componentData),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SALARY_COMPONENTS] });
      queryClient.setQueryData([QUERY_KEYS.SALARY_COMPONENT, data.component_id], data);
      toast.success('Salary component updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update salary component');
    },
  });

  // Delete component mutation
  const deleteComponentMutation = useMutation({
    mutationFn: (componentId: string) => salaryComponentApi.deleteSalaryComponent(componentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SALARY_COMPONENTS] });
      toast.success('Salary component deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete salary component');
    },
  });

  const createComponent = useCallback((componentData: CreateSalaryComponentRequest) => {
    return createComponentMutation.mutateAsync(componentData);
  }, [createComponentMutation]);

  const updateComponent = useCallback((componentId: string, componentData: UpdateSalaryComponentRequest) => {
    return updateComponentMutation.mutateAsync({ componentId, componentData });
  }, [updateComponentMutation]);

  const deleteComponent = useCallback((componentId: string) => {
    return deleteComponentMutation.mutateAsync(componentId);
  }, [deleteComponentMutation]);

  return {
    // Data
    components: componentsData?.components || [],
    total: componentsData?.total || 0,
    page: componentsData?.page || 1,
    limit: componentsData?.limit || 10,
    
    // Loading states
    isLoading,
    isCreating: createComponentMutation.isPending,
    isUpdating: updateComponentMutation.isPending,
    isDeleting: deleteComponentMutation.isPending,
    
    // Error states
    error,
    createError: createComponentMutation.error,
    updateError: updateComponentMutation.error,
    deleteError: deleteComponentMutation.error,
    
    // Actions
    createComponent,
    updateComponent,
    deleteComponent,
    refetch,
  };
};

export const useSalaryComponent = (componentId: string) => {
  const {
    data: component,
    isLoading,
    error
  } = useQuery({
    queryKey: [QUERY_KEYS.SALARY_COMPONENT, componentId],
    queryFn: () => salaryComponentApi.getSalaryComponent(componentId),
    enabled: !!componentId,
    staleTime: 5 * 60 * 1000,
  });

  return {
    component,
    isLoading,
    error,
  };
};

export const useFormulaValidation = () => {
  const [isValidating, setIsValidating] = useState(false);

  const validateFormula = useCallback(async (formulaData: FormulaValidationRequest) => {
    setIsValidating(true);
    try {
      const result = await salaryComponentApi.validateFormula(formulaData);
      return result;
    } catch (error: any) {
      toast.error(error.message || 'Failed to validate formula');
      throw error;
    } finally {
      setIsValidating(false);
    }
  }, []);

  return {
    validateFormula,
    isValidating,
  };
};

export const useEmployeeMappings = (employeeId?: string, componentId?: string) => {
  const queryClient = useQueryClient();

  const {
    data: mappings,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: [QUERY_KEYS.EMPLOYEE_MAPPINGS, employeeId, componentId],
    queryFn: () => salaryComponentApi.getEmployeeMappings(employeeId, componentId),
    staleTime: 5 * 60 * 1000,
  });

  // Create mapping mutation
  const createMappingMutation = useMutation({
    mutationFn: (mappingData: CreateEmployeeMappingRequest) =>
      salaryComponentApi.createEmployeeMapping(mappingData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.EMPLOYEE_MAPPINGS] });
      toast.success('Employee mapping created successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create employee mapping');
    },
  });

  // Update mapping mutation
  const updateMappingMutation = useMutation({
    mutationFn: ({ mappingId, mappingData }: { mappingId: string; mappingData: Partial<CreateEmployeeMappingRequest> }) =>
      salaryComponentApi.updateEmployeeMapping(mappingId, mappingData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.EMPLOYEE_MAPPINGS] });
      toast.success('Employee mapping updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to update employee mapping');
    },
  });

  // Delete mapping mutation
  const deleteMappingMutation = useMutation({
    mutationFn: (mappingId: string) => salaryComponentApi.deleteEmployeeMapping(mappingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.EMPLOYEE_MAPPINGS] });
      toast.success('Employee mapping deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete employee mapping');
    },
  });

  const createMapping = useCallback((mappingData: CreateEmployeeMappingRequest) => {
    return createMappingMutation.mutateAsync(mappingData);
  }, [createMappingMutation]);

  const updateMapping = useCallback((mappingId: string, mappingData: Partial<CreateEmployeeMappingRequest>) => {
    return updateMappingMutation.mutateAsync({ mappingId, mappingData });
  }, [updateMappingMutation]);

  const deleteMapping = useCallback((mappingId: string) => {
    return deleteMappingMutation.mutateAsync(mappingId);
  }, [deleteMappingMutation]);

  return {
    // Data
    mappings: mappings || [],
    
    // Loading states
    isLoading,
    isCreating: createMappingMutation.isPending,
    isUpdating: updateMappingMutation.isPending,
    isDeleting: deleteMappingMutation.isPending,
    
    // Error states
    error,
    createError: createMappingMutation.error,
    updateError: updateMappingMutation.error,
    deleteError: deleteMappingMutation.error,
    
    // Actions
    createMapping,
    updateMapping,
    deleteMapping,
    refetch,
  };
};

export const useCalculationTest = () => {
  const [isCalculating, setIsCalculating] = useState(false);

  const testCalculation = useCallback(async (employeeId: string, componentId: string) => {
    setIsCalculating(true);
    try {
      const result = await salaryComponentApi.testCalculation(employeeId, componentId);
      return result;
    } catch (error: any) {
      toast.error(error.message || 'Failed to test calculation');
      throw error;
    } finally {
      setIsCalculating(false);
    }
  }, []);

  return {
    testCalculation,
    isCalculating,
  };
}; 