export interface CompanyLeave {
  company_leave_id: string;
  leave_type: string;
  leave_name: string;
  accrual_type: string;
  annual_allocation: number;
  computed_monthly_allocation: number;
  is_active: boolean;
  description: string | null;
  encashable: boolean;
  is_allowed_on_probation: boolean;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
}

export const EmptyCompanyLeave: CompanyLeave = {
  company_leave_id: '',
  leave_type: '',
  leave_name: '',
  accrual_type: 'annually',
  annual_allocation: 0,
  computed_monthly_allocation: 0,
  is_active: true,
  description: null,
  encashable: false,
  is_allowed_on_probation: false,
  created_at: '',
  updated_at: '',
  created_by: null,
  updated_by: null,
}; 