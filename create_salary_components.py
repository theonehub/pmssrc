#!/usr/bin/env python3
"""
Salary Components Creation Script
Creates all salary components using the REST API
"""

import requests
import json
import time
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SalaryComponentCreator:
    def __init__(self, base_url: str = "http://localhost:8001", auth_token: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Platform': 'web',
            'X-Client-Version': '1.0.0'
        })
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
    
    def create_component(self, component_data: Dict) -> Optional[Dict]:
        """Create a single salary component"""
        try:
            logger.info(f"Creating component: {component_data['code']} - {component_data['name']}")
            
            response = self.session.post(
                f"{self.base_url}/api/v2/salary-components/",
                json=component_data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ Successfully created: {component_data['code']}")
                return result
            else:
                logger.error(f"❌ Failed to create {component_data['code']}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating {component_data['code']}: {str(e)}")
            return None
    
    def create_all_components(self, components: List[Dict]) -> Dict[str, int]:
        """Create all components and return statistics"""
        stats = {"success": 0, "failed": 0, "total": len(components)}
        failed_components = []
        
        logger.info(f"Starting creation of {stats['total']} salary components...")
        
        for component in components:
            result = self.create_component(component)
            if result:
                stats["success"] += 1
            else:
                stats["failed"] += 1
                failed_components.append(component['code'])
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        logger.info(f"Completed! Success: {stats['success']}, Failed: {stats['failed']}")
        
        if failed_components:
            logger.warning(f"Failed components: {', '.join(failed_components)}")
        
        return stats

def get_salary_components() -> List[Dict]:
    """Define all salary components to be created"""
    
    components = []
    
    # Basic Salary Components
    components.extend([
        {
            "code": "BASIC_SALARY",
            "name": "Basic Salary",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Basic salary component - fully taxable"
        },
        {
            "code": "DEARNESS_ALLOWANCE",
            "name": "Dearness Allowance",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Dearness allowance - fully taxable"
        },
        {
            "code": "COMMISSION",
            "name": "Commission",
            "component_type": "EARNING",
            "value_type": "VARIABLE",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Commission earnings - fully taxable"
        },
        {
            "code": "BONUS",
            "name": "Bonus",
            "component_type": "EARNING",
            "value_type": "VARIABLE",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Bonus payments - fully taxable"
        }
    ])
    
    # Fully Taxable Allowances (from the provided list)
    fully_taxable_allowances = [
        {
            "code": "CITY_COMPENSATORY_ALLOWANCE",
            "name": "City Compensatory Allowance",
            "description": "Allowance for working in expensive cities"
        },
        {
            "code": "RURAL_ALLOWANCE",
            "name": "Rural Allowance",
            "description": "Allowance for working in rural areas"
        },
        {
            "code": "PROCTORSHIP_ALLOWANCE",
            "name": "Proctorship Allowance",
            "description": "Allowance for proctorship duties"
        },
        {
            "code": "WARDENSHIP_ALLOWANCE",
            "name": "Wardenship Allowance",
            "description": "Allowance for wardenship responsibilities"
        },
        {
            "code": "PROJECT_ALLOWANCE",
            "name": "Project Allowance",
            "description": "Allowance for project-specific work"
        },
        {
            "code": "DEPUTATION_ALLOWANCE",
            "name": "Deputation Allowance",
            "description": "Allowance for deputation assignments"
        },
        {
            "code": "OVERTIME_ALLOWANCE",
            "name": "Overtime Allowance",
            "description": "Allowance for overtime work"
        },
        {
            "code": "INTERIM_RELIEF",
            "name": "Interim Relief",
            "description": "Interim relief payments"
        },
        {
            "code": "TIFFIN_ALLOWANCE",
            "name": "Tiffin Allowance",
            "description": "Allowance for meal expenses"
        },
        {
            "code": "FIXED_MEDICAL_ALLOWANCE",
            "name": "Fixed Medical Allowance",
            "description": "Fixed medical allowance - fully taxable"
        },
        {
            "code": "SERVANT_ALLOWANCE",
            "name": "Servant Allowance",
            "description": "Allowance for domestic help"
        }
    ]
    
    # Add fully taxable allowances
    for allowance in fully_taxable_allowances:
        components.append({
            "code": allowance["code"],
            "name": allowance["name"],
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": allowance["description"] + " - fully taxable"
        })
    
    # Partially Exempt Allowances
    partially_exempt_allowances = [
        {
            "code": "HRA",
            "name": "House Rent Allowance",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "10(13A)",
            "description": "House rent allowance - partially exempt under Section 10(13A)"
        },
        {
            "code": "LTA",
            "name": "Leave Travel Allowance",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "10(5)",
            "description": "Leave travel allowance - partially exempt under Section 10(5)"
        },
        {
            "code": "CONVEYANCE_ALLOWANCE",
            "name": "Conveyance Allowance",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "10(14)",
            "description": "Conveyance allowance - partially exempt under Section 10(14)"
        },
        {
            "code": "MOBILE_ALLOWANCE",
            "name": "Mobile Allowance",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "17(2)",
            "description": "Mobile phone allowance - partially exempt under Section 17(2)"
        }
    ]
    
    components.extend(partially_exempt_allowances)
    
    # Standard Deductions
    deductions = [
        {
            "code": "PF_EMPLOYEE",
            "name": "Employee Provident Fund",
            "component_type": "DEDUCTION",
            "value_type": "FORMULA",
            "is_taxable": False,
            "exemption_section": "NONE",
            "formula": "BASIC_SALARY * 0.12",
            "description": "Employee contribution to PF (12% of basic)"
        },
        {
            "code": "ESI_EMPLOYEE",
            "name": "Employee State Insurance",
            "component_type": "DEDUCTION",
            "value_type": "FORMULA",
            "is_taxable": False,
            "exemption_section": "NONE",
            "formula": "(BASIC_SALARY + DEARNESS_ALLOWANCE + HRA) * 0.0075",
            "description": "Employee ESI contribution (0.75% of gross)"
        },
        {
            "code": "PROFESSIONAL_TAX",
            "name": "Professional Tax",
            "component_type": "DEDUCTION",
            "value_type": "FIXED",
            "is_taxable": False,
            "exemption_section": "NONE",
            "default_value": 200.0,
            "description": "State professional tax"
        },
        {
            "code": "INCOME_TAX",
            "name": "Income Tax (TDS)",
            "component_type": "DEDUCTION",
            "value_type": "VARIABLE",
            "is_taxable": False,
            "exemption_section": "NONE",
            "description": "Tax deducted at source"
        }
    ]
    
    components.extend(deductions)
    
    # Reimbursements
    reimbursements = [
        {
            "code": "FUEL_REIMBURSEMENT",
            "name": "Fuel Reimbursement",
            "component_type": "REIMBURSEMENT",
            "value_type": "VARIABLE",
            "is_taxable": False,
            "exemption_section": "NONE",
            "description": "Fuel expense reimbursement"
        },
        {
            "code": "MEDICAL_REIMBURSEMENT",
            "name": "Medical Reimbursement",
            "component_type": "REIMBURSEMENT",
            "value_type": "VARIABLE",
            "is_taxable": False,
            "exemption_section": "17(2)",
            "description": "Medical expense reimbursement"
        },
        {
            "code": "TRAVEL_REIMBURSEMENT",
            "name": "Travel Reimbursement",
            "component_type": "REIMBURSEMENT",
            "value_type": "VARIABLE",
            "is_taxable": False,
            "exemption_section": "NONE",
            "description": "Business travel expense reimbursement"
        }
    ]
    
    components.extend(reimbursements)
    
    # Special Allowances
    special_allowances = [
        {
            "code": "PERFORMANCE_INCENTIVE",
            "name": "Performance Incentive",
            "component_type": "EARNING",
            "value_type": "VARIABLE",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Performance-based incentive payments"
        },
        {
            "code": "SHIFT_ALLOWANCE",
            "name": "Shift Allowance",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Allowance for shift work"
        },
        {
            "code": "SPECIAL_ALLOWANCE",
            "name": "Special Allowance",
            "component_type": "EARNING",
            "value_type": "FIXED",
            "is_taxable": True,
            "exemption_section": "NONE",
            "description": "Special allowance - fully taxable"
        }
    ]
    
    components.extend(special_allowances)
    
    return components

def main():
    """Main function to create all salary components"""
    
    # Configuration
    BASE_URL = "http://localhost:8001"  # Salary components service URL
    AUTH_TOKEN = None  # Add your auth token here if required
    
    print("🚀 Salary Components Creation Script")
    print("=" * 50)
    
    # Initialize creator
    creator = SalaryComponentCreator(BASE_URL, AUTH_TOKEN)
    
    # Get all components to create
    components = get_salary_components()
    
    print(f"📋 Total components to create: {len(components)}")
    print("\nComponents breakdown:")
    
    # Group by type for summary
    by_type = {}
    for comp in components:
        comp_type = comp['component_type']
        if comp_type not in by_type:
            by_type[comp_type] = 0
        by_type[comp_type] += 1
    
    for comp_type, count in by_type.items():
        print(f"  - {comp_type}: {count}")
    
    print("\n" + "=" * 50)
    
    # Confirm before proceeding
    response = input("Do you want to proceed with creating all components? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled.")
        return
    
    # Create all components
    stats = creator.create_all_components(components)
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    print(f"✅ Successfully created: {stats['success']}")
    print(f"❌ Failed to create: {stats['failed']}")
    print(f"📋 Total processed: {stats['total']}")
    
    if stats['success'] > 0:
        print(f"\n🎉 {stats['success']} salary components have been created successfully!")
        print("You can now use these components to build employee salary structures.")
    
    if stats['failed'] > 0:
        print(f"\n⚠️  {stats['failed']} components failed to create. Check the logs above for details.")
        print("Common issues:")
        print("  - API server not running")
        print("  - Authentication required")
        print("  - Duplicate component codes")
        print("  - Invalid data format")

if __name__ == "__main__":
    main()
