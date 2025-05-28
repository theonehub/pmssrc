/**
 * Organisation model types for frontend
 */

// Organisation model matching the backend model
export const OrganisationModel = {
  id: '',
  name: '',
  address: '',
  city: '',
  state: '',
  country: '',
  postal_code: '',
  contact_number: '',
  email: '',
  website: '',
  description: '',
  is_active: true,
  created_at: '',
  updated_at: '',
};

// Empty organisation for initializing forms
export const EmptyOrganisation = {
  name: '',
  address: '',
  city: '',
  state: '',
  country: '',
  pin_code: '',
  phone: '',
  email: '',
  website: '',
  description: '',
  is_active: true,
  hostname: '',
  employee_strength: '',
  pan_number: '',
  gst_number: '',
  tan_number: '',
};
