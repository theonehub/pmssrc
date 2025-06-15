// TypeScript type definitions for calculator utilities

export interface CalculatorEvaluationResult {
  isValid: boolean;
  result: number;
  error: string | null;
}

export interface CalculatorValidationResult {
  isValid: boolean;
  message: string;
}

// Function type declarations
export declare function evaluateCalculatorExpression(expression: string): CalculatorEvaluationResult;
export declare function isCalculatorExpression(value: string): boolean;
export declare function validateCalculatorExpression(expression: string): CalculatorValidationResult; 