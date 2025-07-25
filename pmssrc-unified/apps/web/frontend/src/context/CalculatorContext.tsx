// Deprecated: CalculatorContext is now replaced by Zustand store.
// This file re-exports the Zustand hook for compatibility.

export { useCalculatorStore as useCalculator } from '../shared/stores/calculatorStore';

// No-op provider for legacy compatibility
export const CalculatorProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => <>{children}</>; 