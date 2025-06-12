module.exports = {
  extends: [
    'react-app',
    'react-app/jest',
  ],
  rules: {
    // General JavaScript rules
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-var': 'error',
    'prefer-const': 'error',
    
    // Code quality rules
    'prefer-template': 'warn',
    'object-shorthand': 'warn',
  },
}; 