/**
 * Constants for taxation forms
 */

// Cities for HRA calculation
export const cities = [
  { value: 'Delhi', label: 'Delhi', rate: 0.5 },
  { value: 'Mumbai', label: 'Mumbai', rate: 0.5 },
  { value: 'Kolkata', label: 'Kolkata', rate: 0.5 },
  { value: 'Chennai', label: 'Chennai', rate: 0.5 },
  { value: 'Others', label: 'Others (Tier 2 & 3 cities)', rate: 0.4 }
];

// Stepper configuration for form steps
export const formSteps = [
  'Tax Regime',
  'Salary Income',
  'Perquisites',
  'Other Income',
  'Deductions',
  'Review & Submit'
];

// Perquisite sections
export const perquisiteSections = [
  'Accommodation',
  'Car & Transport',
  'Medical Reimbursement',
  'Leave Travel Allowance',
  'Free Education',
  'Gas, Electricity, Water',
  'Interest-free/Concession Loan',
  'ESOP & Stock Options',
  'Movable Assets',
  'Other Perquisites'
];

// Section 80G donation heads
export const section80G100WoQlHeads = [
  'National Defence Fund set up by Central Government',
  'Prime Minister national relief fund',
  'Approved university',
  'Any other eligible donations for 100% deduction'
];

export const section80G50WoQlHeads = [
  'Prime Minister\'s Drought Relief Fund'
];

export const section80G100QlHeads = [
  'Donations to government or any approved local authority to promote family planning',
  'Any other fund that satisfies the conditions'
];

export const section80G50QlHeads = [
  'Donations to government or any approved local authority to except to promote family planning',
  'Any Corporation for promoting interest of minority community',
  'For repair or renovation of any notified temple, mosque, gurudwara, church or other places of worship',
  'Any other fund that satisfies the conditions'
];

// Disability percentage options
export const disabilityPercentageOptions = [
  'Between 40%-80%',
  'More than 80%'
];

// Family member relation options
export const relationOptions = [
  'Spouse',
  'Child',
  'Parents',
  'Sibling'
]; 

export const occupancyStatuses = [
  'Self-Occupied',
  'Let-Out',
  'Per-Construction'
];