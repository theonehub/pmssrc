#!/usr/bin/env python3
"""
Salary Components Creation Script with Authentication
Creates all salary components using the REST API with automatic token generation
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SalaryComponentCreatorWithAuth:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
        # Set headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-Platform': 'web',
            'X-Client-Version': '1.0.0'
        })
    
    def generate_auth_token(self) -> str:
        """Generate a JWT token for authentication"""
        try:
            # Try to import jose for JWT creation
            from jose import jwt
        except ImportError:
            logger.error("❌ python-jose library not found. Please install it:")
            logger.error("   pip install python-jose")
            raise Exception("python-jose library required for authentication")
        
        # JWT Configuration (should match the API server)
        JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        
        # Token expires in 24 hours
        expires_delta = timedelta(hours=24)
        expire = datetime.utcnow() + expires_delta
        
        # Create token payload with required claims
        token_data = {
            "sub": "EMP001",  # employee_id (subject)
            "username": "admin",
            "employee_id": "EMP001",
            "role": "admin", 
            "hostname": "global_database",
            "permissions": ["read", "write", "salary.read", "salary.write", "salary.manage"],
            "iat": datetime.utcnow().timestamp(),  # Issued at
            "exp": expire.timestamp(),  # Expiration
            "type": "access_token"
        }
        
        # Generate JWT token
        token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        logger.info("✅ Authentication token generated successfully")
        logger.info(f"   Token expires at: {datetime.fromtimestamp(expire.timestamp()).strftime('%Y-%m-%d %H:%M:%S')}")
        
        return token
    
    def set_auth_token(self, token: str = None):
        """Set authentication token for requests"""
        if token is None:
            token = self.generate_auth_token()
        
        self.auth_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
        logger.info("�� Authentication token set for API requests")
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        try:
            logger.info("🔍 Testing authentication...")
            
            # Try to access the components list endpoint
            response = self.session.get(f"{self.base_url}/api/v2/salary-components/")
            
            if response.status_code == 200:
                logger.info("✅ Authentication successful")
                return True
            elif response.status_code == 401:
                logger.error("❌ Authentication failed - Invalid token")
                return False
            else:
                logger.warning(f"⚠️  Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {str(e)}")
            return False
    
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
            elif response.status_code == 401:
                logger.error(f"❌ Authentication failed for {component_data['code']}")
                return None
            elif response.status_code == 409:
                logger.warning(f"⚠️  Component {component_data['code']} already exists")
                return None
            else:
                logger.error(f"❌ Failed to create {component_data['code']}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating {component_data['code']}: {str(e)}")
            return None
    
    def create_all_components(self, components: List[Dict]) -> Dict[str, int]:
        """Create all components and return statistics"""
        stats = {"success": 0, "failed": 0, "skipped": 0, "total": len(components)}
        failed_components = []
        skipped_components = []
        
        logger.info(f"Starting creation of {stats['total']} salary components...")
        
        for component in components:
            result = self.create_component(component)
            if result:
                stats["success"] += 1
            elif result is None:
                # Check if it was skipped (already exists) or failed
                response = self.session.get(f"{self.base_url}/api/v2/salary-components/code/{component['code']}")
                if response.status_code == 200:
                    stats["skipped"] += 1
                    skipped_components.append(component['code'])
                    logger.info(f"⏭️  Skipped {component['code']} (already exists)")
                else:
                    stats["failed"] += 1
                    failed_components.append(component['code'])
            else:
                stats["failed"] += 1
                failed_components.append(component['code'])
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        logger.info(f"Completed! Success: {stats['success']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}")
        
        if failed_components:
            logger.warning(f"Failed components: {', '.join(failed_components)}")
        if skipped_components:
            logger.info(f"Skipped components (already exist): {', '.join(skipped_components)}")
        
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
    """Main function to create all salary components with authentication"""
    
    # Configuration
    BASE_URL = "http://localhost:8001"  # Salary components service URL
    
    print("🚀 Salary Components Creation Script (with Authentication)")
    print("=" * 65)
    
    # Initialize creator
    creator = SalaryComponentCreatorWithAuth(BASE_URL)
    
    try:
        # Step 1: Generate and set authentication token
        print("🔐 Step 1: Setting up authentication...")
        creator.set_auth_token()
        
        # Step 2: Test authentication
        print("🔍 Step 2: Testing authentication...")
        if not creator.test_authentication():
            print("❌ Authentication failed. Please check:")
            print("   - API server is running on port 8001")
            print("   - JWT_SECRET environment variable matches the server")
            print("   - python-jose library is installed (pip install python-jose)")
            return
        
        # Step 3: Get components to create
        components = get_salary_components()
        
        print(f"📋 Step 3: Preparing to create {len(components)} components...")
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
        
        print("\n" + "=" * 65)
        
        # Confirm before proceeding
        response = input("Do you want to proceed with creating all components? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled.")
            return
        
        # Step 4: Create all components
        print("🚀 Step 4: Creating salary components...")
        stats = creator.create_all_components(components)
        
        print("\n" + "=" * 65)
        print("📊 FINAL RESULTS")
        print("=" * 65)
        print(f"✅ Successfully created: {stats['success']}")
        print(f"⏭️  Skipped (already exist): {stats['skipped']}")
        print(f"❌ Failed to create: {stats['failed']}")
        print(f"📋 Total processed: {stats['total']}")
        
        if stats['success'] > 0:
            print(f"\n🎉 {stats['success']} salary components have been created successfully!")
            print("You can now use these components to build employee salary structures.")
        
        if stats['skipped'] > 0:
            print(f"\n⏭️  {stats['skipped']} components were skipped (already existed).")
        
        if stats['failed'] > 0:
            print(f"\n⚠️  {stats['failed']} components failed to create. Check the logs above for details.")
        
        # Step 5: Verification
        if stats['success'] > 0 or stats['skipped'] > 0:
            print(f"\n🔍 Step 5: Verification")
            print("Run the verification script to check created components:")
            print("   python verify_components.py")
            
    except ImportError as e:
        print("❌ Missing required library:")
        print("   pip install python-jose")
        print(f"   Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
