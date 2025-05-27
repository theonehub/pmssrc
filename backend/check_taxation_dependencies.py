#!/usr/bin/env python3
"""
Taxation Service Dependency Checker
Checks which files still depend on the legacy taxation_service.py before removal
"""

import os
import re
from typing import List, Dict

def check_taxation_service_dependencies() -> Dict[str, any]:
    """Check all dependencies on taxation_service.py"""
    print('🔍 Checking dependencies on taxation_service.py...')
    
    dependencies = []
    
    # Files to check for dependencies
    files_to_check = [
        'app/services/payout_service.py',
        'app/routes/taxation_routes.py', 
        'app/services/salary_history_service.py',
        'app/services/enhanced_taxation_service.py',
        'app/services/employee_lifecycle_service.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Check for various import patterns
                import_patterns = [
                    r'from services\.taxation_service import',
                    r'import services\.taxation_service',
                    r'from \.taxation_service import',
                    r'import \.taxation_service'
                ]
                
                found_imports = []
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        found_imports.extend(matches)
                
                if found_imports:
                    dependencies.append({
                        'file': file_path,
                        'imports': found_imports,
                        'lines': _get_import_lines(content, import_patterns)
                    })
                    print(f'⚠️  {file_path} still imports from taxation_service')
                else:
                    print(f'✅ {file_path} - No taxation_service imports found')
                    
            except Exception as e:
                print(f'❌ Error checking {file_path}: {e}')
        else:
            print(f'📁 {file_path} - File not found')
    
    # Check for SOLID migration components
    solid_components = _check_solid_components()
    
    # Generate report
    report = {
        'dependencies_found': len(dependencies) > 0,
        'total_files_checked': len(files_to_check),
        'files_with_dependencies': len(dependencies),
        'dependency_details': dependencies,
        'solid_components': solid_components,
        'can_remove_safely': len(dependencies) == 0 and solid_components['all_present']
    }
    
    _print_summary(report)
    return report

def _get_import_lines(content: str, patterns: List[str]) -> List[int]:
    """Get line numbers where imports are found"""
    lines = content.split('\n')
    import_lines = []
    
    for i, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line):
                import_lines.append(i)
                break
    
    return import_lines

def _check_solid_components() -> Dict[str, any]:
    """Check if all SOLID architecture components are present"""
    print('\n🏗️  Checking SOLID architecture components...')
    
    components = {
        'domain_events': 'app/domain/events/taxation_events.py',
        'dtos': 'app/application/dto/taxation_dto.py',
        'repository_interfaces': 'app/application/interfaces/repositories/taxation_repository.py',
        'use_cases': 'app/application/use_cases/taxation/',
        'migration_service': 'app/infrastructure/services/taxation_migration_service.py',
        'controller': 'app/api/controllers/taxation_controller.py',
        'routes_v2': 'app/api/routes/taxation_routes_v2.py'
    }
    
    status = {}
    all_present = True
    
    for component, path in components.items():
        exists = os.path.exists(path)
        status[component] = {
            'path': path,
            'exists': exists
        }
        
        if exists:
            print(f'✅ {component}: {path}')
        else:
            print(f'❌ {component}: {path} - MISSING')
            all_present = False
    
    return {
        'components': status,
        'all_present': all_present
    }

def _print_summary(report: Dict[str, any]):
    """Print summary of the dependency check"""
    print(f'\n📊 SUMMARY:')
    print(f'   Total files checked: {report["total_files_checked"]}')
    print(f'   Files with dependencies: {report["files_with_dependencies"]}')
    
    if report['dependency_details']:
        print(f'\n🚫 CANNOT SAFELY REMOVE taxation_service.py yet.')
        print(f'   Dependencies found in:')
        for dep in report['dependency_details']:
            print(f'     - {dep["file"]} (lines: {dep["lines"]})')
        
        print(f'\n📋 NEXT STEPS:')
        print(f'   1. Update the dependent files to use SOLID architecture')
        print(f'   2. Replace imports with TaxationMigrationService')
        print(f'   3. Test the updated services thoroughly')
        print(f'   4. Run this check again')
        
    elif not report['solid_components']['all_present']:
        print(f'\n🚫 CANNOT SAFELY REMOVE taxation_service.py yet.')
        print(f'   Some SOLID components are missing.')
        
    else:
        print(f'\n✅ SAFE TO REMOVE taxation_service.py!')
        print(f'   ✅ No dependencies found in checked files')
        print(f'   ✅ All SOLID components are present')
        print(f'\n🚀 Ready for migration!')

def suggest_migration_commands():
    """Suggest migration commands"""
    print(f'\n🔧 MIGRATION COMMANDS:')
    print(f'   # 1. Backup the current file')
    print(f'   cp app/services/taxation_service.py app/services/taxation_service.py.backup')
    print(f'   ')
    print(f'   # 2. Update dependent services (use provided migration examples)')
    print(f'   # - Update payout_service.py with new imports')
    print(f'   # - Deprecate legacy routes/taxation_routes.py')
    print(f'   ')
    print(f'   # 3. Test the system thoroughly')
    print(f'   pytest app/test_taxation_solid_minimal.py')
    print(f'   ')
    print(f'   # 4. Remove the legacy file (when ready)')
    print(f'   # rm app/services/taxation_service.py')

if __name__ == '__main__':
    try:
        # Change to backend directory if running from root
        if os.path.basename(os.getcwd()) != 'backend':
            if os.path.exists('backend'):
                os.chdir('backend')
        
        report = check_taxation_service_dependencies()
        
        if not report['can_remove_safely']:
            suggest_migration_commands()
            exit(1)
        else:
            print(f'\n🎉 SUCCESS: Ready to remove taxation_service.py safely!')
            exit(0)
            
    except Exception as e:
        print(f'❌ Error running dependency check: {e}')
        exit(1) 