export interface ContactInfo {
  email: string;
  phone: string;
  website?: string;
  fax?: string;
}

export interface Address {
  street_address: string;
  city: string;
  state: string;
  country: string;
  pin_code: string;
  landmark?: string;
}

export interface TaxInfo {
  pan_number: string;
  gst_number?: string;
  tan_number?: string;
  cin_number?: string;
  esi_establishment_id?: string;
  pf_establishment_id?: string;
}

export interface BankDetails {
  bank_name: string;
  account_number: string;
  ifsc_code: string;
  branch_name: string;
  branch_address: string;
  account_type: string;
  account_holder_name: string;
}

export interface Organisation {
  organisation_id?: string;
  name: string;
  description?: string;
  organisation_type: string;
  status: string;
  
  // Flat fields from backend summary response
  email?: string;
  phone?: string;
  city?: string;
  
  // Original nested fields (still used in detail views)
  contact_info?: ContactInfo | null;
  address?: Address | null;
  tax_info?: TaxInfo | null;
  bank_details?: BankDetails | null;
  
  employee_strength: number;
  used_employee_strength?: number;
  hostname: string;
  logo_path?: string;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  is_active: boolean;
}

export const EmptyOrganisation: Organisation = {
  organisation_id: '',
  name: '',
  description: '',
  organisation_type: 'private_limited',
  status: 'active',
  contact_info: {
    email: '',
    phone: '',
    website: '',
    fax: '',
  },
  address: {
    street_address: '',
    city: '',
    state: '',
    country: '',
    pin_code: '',
    landmark: '',
  },
  tax_info: {
    pan_number: '',
    gst_number: '',
    tan_number: '',
    cin_number: '',
    esi_establishment_id: '',
    pf_establishment_id: '',
  },
  bank_details: {
    bank_name: '',
    account_number: '',
    ifsc_code: '',
    branch_name: '',
    branch_address: '',
    account_type: '',
    account_holder_name: '',
  },
  employee_strength: 10,
  used_employee_strength: 0,
  hostname: '',
  logo_path: '',
  created_at: '',
  updated_at: '',
  created_by: '',
  updated_by: '',
  is_active: true,
}; 