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
}

export interface Organisation {
  organisation_id?: string;
  name: string;
  description?: string;
  organisation_type: string;
  status: string;
  contact_info: ContactInfo;
  address: Address;
  tax_info: TaxInfo;
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