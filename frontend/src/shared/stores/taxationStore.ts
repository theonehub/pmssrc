import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import taxationApi from '../api/taxationApi';
import * as Types from '../types/api';
import { LoadingState, ErrorState } from '../types/domain';
import { CURRENT_TAX_YEAR } from '../constants/taxation';

interface TaxationState {
  currentCalculation: Types.PeriodicTaxCalculationResponseDTO | null;
  calculationLoading: LoadingState;
  calculationError: ErrorState;
  formData: Types.ComprehensiveTaxInputDTO;
  currentStep: number;
  isMobileView: boolean;
}

interface TaxationActions {
  calculateTax: (input: Types.ComprehensiveTaxInputDTO) => Promise<void>;
  updateFormData: (section: string, data: any) => void;
  setCurrentStep: (step: number) => void;
  setMobileView: (isMobile: boolean) => void;
  clearError: () => void;
}

const initialFormData: Types.ComprehensiveTaxInputDTO = {
  tax_year: CURRENT_TAX_YEAR,
  regime_type: 'new',
  age: 25,
  residential_status: 'resident'
};

export const useTaxationStore = create<TaxationState & TaxationActions>()(
  devtools(
    persist(
      immer((set, _get) => ({
        // Initial state
        currentCalculation: null,
        calculationLoading: { isLoading: false },
        calculationError: { hasError: false },
        formData: initialFormData,
        currentStep: 0,
        isMobileView: false,
        
        // Actions
        calculateTax: async (input: Types.ComprehensiveTaxInputDTO) => {
          set((state) => {
            state.calculationLoading = { isLoading: true, operation: 'Calculating tax...' };
            state.calculationError = { hasError: false };
          });
          
          try {
            const result = await taxationApi.calculateComprehensiveTax(input);
            
            set((state) => {
              state.currentCalculation = result;
              state.calculationLoading = { isLoading: false };
              state.formData = input;
            });
          } catch (error: any) {
            set((state) => {
              state.calculationLoading = { isLoading: false };
              state.calculationError = {
                hasError: true,
                message: error.message || 'Failed to calculate tax',
                code: error.code,
                timestamp: new Date().toISOString()
              };
            });
            throw error;
          }
        },
        
        updateFormData: (section: string, data: any) => {
          set((state) => {
            (state.formData as any)[section] = data;
          });
        },
        
        setCurrentStep: (step: number) => {
          set((state) => {
            state.currentStep = step;
          });
        },
        
        setMobileView: (isMobile: boolean) => {
          set((state) => {
            state.isMobileView = isMobile;
          });
        },
        
        clearError: () => {
          set((state) => {
            state.calculationError = { hasError: false };
          });
        }
      })),
      {
        name: 'taxation-store',
        partialize: (state) => ({
          formData: state.formData,
          currentStep: state.currentStep,
          isMobileView: state.isMobileView
        })
      }
    ),
    { name: 'taxation-store' }
  )
); 