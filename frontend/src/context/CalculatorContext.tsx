import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define the context value interface
interface CalculatorContextValue {
  isCalculatorOpen: boolean;
  openCalculator: () => void;
  closeCalculator: () => void;
}

// Define the provider props interface
interface CalculatorProviderProps {
  children: ReactNode;
}

// Create context with proper typing
const CalculatorContext = createContext<CalculatorContextValue | undefined>(undefined);

// Custom hook with proper error handling and typing
export const useCalculator = (): CalculatorContextValue => {
  const context = useContext(CalculatorContext);
  if (!context) {
    throw new Error('useCalculator must be used within a CalculatorProvider');
  }
  return context;
};

// Provider component with proper TypeScript typing
export const CalculatorProvider: React.FC<CalculatorProviderProps> = ({ children }) => {
  const [isCalculatorOpen, setIsCalculatorOpen] = useState<boolean>(false);

  const openCalculator = (): void => {
    setIsCalculatorOpen(true);
  };

  const closeCalculator = (): void => {
    setIsCalculatorOpen(false);
  };

  const value: CalculatorContextValue = {
    isCalculatorOpen,
    openCalculator,
    closeCalculator,
  };

  return (
    <CalculatorContext.Provider value={value}>
      {children}
    </CalculatorContext.Provider>
  );
}; 