#!/usr/bin/env python3
"""
Test script to check compilation of SOLID routes v2
"""
import sys
sys.path.append('.')

def test_compilation():
    """Test compilation of all new SOLID routes and controllers."""
    results = []
    
    # Test Controllers
    controller_tests = [
        ("Auth Controller", "app.api.controllers.auth_controller", "AuthController"),
        ("Employee Salary Controller", "app.api.controllers.employee_salary_controller", "EmployeeSalaryController"),
        ("Payslip Controller", "app.api.controllers.payslip_controller", "PayslipController")
    ]
    
    for name, module_path, class_name in controller_tests:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            results.append(f"✅ {name}: COMPILED SUCCESSFULLY")
        except Exception as e:
            results.append(f"❌ {name}: {e}")
    
    # Test Routes
    route_tests = [
        ("Auth Routes v2", "app.api.routes.auth_routes_v2", "router"),
        ("Employee Salary Routes v2", "app.api.routes.employee_salary_routes_v2", "router"),
        ("Payslip Routes v2", "app.api.routes.payslip_routes_v2", "router")
    ]
    
    for name, module_path, router_name in route_tests:
        try:
            module = __import__(module_path, fromlist=[router_name])
            getattr(module, router_name)
            results.append(f"✅ {name}: COMPILED SUCCESSFULLY")
        except Exception as e:
            results.append(f"❌ {name}: {e}")
    
    # Test DTOs
    dto_tests = [
        ("Auth DTOs", "app.application.dto.auth_dto", "LoginRequestDTO"),
        ("Employee Salary DTOs", "app.application.dto.employee_salary_dto", "EmployeeSalaryCreateRequestDTO"),
        ("Payslip DTOs", "app.application.dto.payslip_dto", "PayslipGenerationRequestDTO")
    ]
    
    for name, module_path, class_name in dto_tests:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            results.append(f"✅ {name}: COMPILED SUCCESSFULLY")
        except Exception as e:
            results.append(f"❌ {name}: {e}")
    
    return results

if __name__ == "__main__":
    print("🔄 Testing SOLID Routes v2 Compilation...")
    print("="*60)
    
    results = test_compilation()
    
    for result in results:
        print(result)
    
    # Summary
    successful = len([r for r in results if "✅" in r])
    total = len(results)
    
    print("="*60)
    print(f"📊 SUMMARY: {successful}/{total} components compiled successfully")
    
    if successful == total:
        print("🎉 ALL COMPONENTS COMPILED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print(f"⚠️  {total - successful} components failed to compile")
        sys.exit(1) 