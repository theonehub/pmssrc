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
  /*'Separation',*/
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
  'Any other eligible donations for 100% deduction',
  'National Foundation for Communal Harmony',
  'An approved university/educational institution of National eminence',
  'Zila Saksharta Samiti constituted in any district under the chairmanship of the Collector of that district',
  'Fund set up by a state government for medical relief to the poor',
  'National Illness Assistance Fund',
  'National Blood Transfusion Council or any State Blood Transfusion Council',
  'National Trust for Welfare of Persons with Autism, Cerebral Palsy, Mental Retardation, and Multiple Disabilities',
  'National Sports Fund',
  'National Cultural Fund',
  'Fund for Technology Development and Application',
  'National Children Fund',
  'Chief Minister Relief Fund or Lieutenant Governor Relief Fund with respect to any State or Union Territory',
  'The Army Central Welfare Fund or the Indian Naval Benevolent Fund or the Air Force Central Welfare Fund, Andhra Pradesh Chief Minister’s Cyclone Relief Fund, 1996',
  'Chief Minister Earthquake Relief Fund, Maharashtra',
  'Any fund set up by the State Government of Gujarat exclusively for providing relief to the victims of the earthquake in Gujarat',
  'Prime Minister Armenia Earthquake Relief Fund',
  'Africa (Public Contributions India) Fund',
  'Swachh Bharat Kosh (applicable from FY 2014-15)',
  'Clean Ganga Fund (applicable from FY 2014-15)',
  'National Fund for Control of Drug Abuse (applicable from FY 2015-16)', 
  'Any 2 or more of the above'
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
  'Let-Out'
];