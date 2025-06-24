#!/usr/bin/env python3
"""
Verify Salary Components Script
Lists and verifies created salary components
"""

import requests
import json
from typing import Optional, Dict, List

def verify_components(base_url: str = "http://localhost:8001", auth_token: Optional[str] = None):
    """Verify created salary components"""
    
    print("🔍 Verifying Salary Components")
    print("=" * 50)
    
    # Setup session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'X-Platform': 'web',
        'X-Client-Version': '1.0.0'
    })
    
    if auth_token:
        session.headers.update({
            'Authorization': f'Bearer {auth_token}'
        })
    
    try:
        # Get all components
        response = session.get(f"{base_url}/api/v2/salary-components/")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract components based on response format
            components = []
            if isinstance(data, dict):
                if 'data' in data:
                    if isinstance(data['data'], dict) and 'components' in data['data']:
                        components = data['data']['components']
                    elif isinstance(data['data'], list):
                        components = data['data']
                elif 'components' in data:
                    components = data['components']
            elif isinstance(data, list):
                components = data
            
            print(f"📊 Total Components Found: {len(components)}")
            
            if components:
                # Group by type
                by_type = {}
                by_value_type = {}
                taxable_count = 0
                
                for comp in components:
                    # Group by component type
                    comp_type = comp.get('component_type', 'UNKNOWN')
                    if comp_type not in by_type:
                        by_type[comp_type] = []
                    by_type[comp_type].append(comp)
                    
                    # Group by value type
                    val_type = comp.get('value_type', 'UNKNOWN')
                    if val_type not in by_value_type:
                        by_value_type[val_type] = 0
                    by_value_type[val_type] += 1
                    
                    # Count taxable
                    if comp.get('is_taxable', False):
                        taxable_count += 1
                
                print("\n📈 Components by Type:")
                for comp_type, comps in by_type.items():
                    print(f"  {comp_type}: {len(comps)}")
                    for comp in comps[:5]:  # Show first 5
                        status = "✅" if comp.get('is_active', True) else "❌"
                        taxable = "💰" if comp.get('is_taxable', False) else "🆓"
                        print(f"    {status} {taxable} {comp.get('code', 'N/A')} - {comp.get('name', 'N/A')}")
                    if len(comps) > 5:
                        print(f"    ... and {len(comps) - 5} more")
                
                print(f"\n📊 Value Types:")
                for val_type, count in by_value_type.items():
                    print(f"  {val_type}: {count}")
                
                print(f"\n�� Tax Treatment:")
                print(f"  Taxable: {taxable_count}")
                print(f"  Non-taxable: {len(components) - taxable_count}")
                
                # Check for expected components
                print(f"\n🔍 Checking Expected Components:")
                expected_codes = [
                    'BASIC_SALARY', 'HRA', 'DEARNESS_ALLOWANCE', 'PF_EMPLOYEE',
                    'CITY_COMPENSATORY_ALLOWANCE', 'RURAL_ALLOWANCE', 'OVERTIME_ALLOWANCE'
                ]
                
                found_codes = [comp.get('code', '') for comp in components]
                
                for code in expected_codes:
                    if code in found_codes:
                        print(f"  ✅ {code}")
                    else:
                        print(f"  ❌ {code} (missing)")
                
                # Check for formula components
                formula_components = [comp for comp in components if comp.get('formula')]
                print(f"\n🧮 Formula Components: {len(formula_components)}")
                for comp in formula_components:
                    print(f"  📐 {comp.get('code', 'N/A')}: {comp.get('formula', 'N/A')}")
                
            else:
                print("⚠️  No components found")
                print("💡 Run the creation script first")
                
        elif response.status_code == 401:
            print("❌ Authentication required")
        elif response.status_code == 404:
            print("❌ Endpoint not found")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - API server may not be running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    BASE_URL = "http://localhost:8001"
    AUTH_TOKEN = None  # Add your token here if needed
    
    verify_components(BASE_URL, AUTH_TOKEN)

if __name__ == "__main__":
    main()
