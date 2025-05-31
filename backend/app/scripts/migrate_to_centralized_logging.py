#!/usr/bin/env python3
"""
Migration Script for Centralized Logging
Automatically updates Python files to use the new centralized logger
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Tuple

def find_python_files(base_path: str) -> List[str]:
    """Find all Python files in the project."""
    python_files = []
    
    # Search patterns
    patterns = [
        os.path.join(base_path, "**/*.py"),
    ]
    
    for pattern in patterns:
        python_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out some directories/files
    exclude_patterns = [
        "__pycache__",
        ".venv",
        "env",
        "migrations",
        "tests",
        "migrate_to_centralized_logging.py"  # Don't modify this script
    ]
    
    filtered_files = []
    for file_path in python_files:
        if not any(exclude in file_path for exclude in exclude_patterns):
            filtered_files.append(file_path)
    
    return filtered_files

def analyze_file(file_path: str) -> Tuple[bool, List[str]]:
    """Analyze a file to see if it needs migration."""
    needs_migration = False
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for old logging patterns
        if 'import logging' in content:
            issues.append("Has 'import logging'")
            needs_migration = True
        
        if 'logging.getLogger(' in content:
            issues.append("Uses 'logging.getLogger()'")
            needs_migration = True
        
        if 'logging.basicConfig(' in content:
            issues.append("Uses 'logging.basicConfig()'")
            needs_migration = True
        
        if 'logger.setLevel(' in content:
            issues.append("Uses 'logger.setLevel()'")
            needs_migration = True
        
        # Check if already migrated
        if 'from utils.logger import get_logger' in content or 'from app.utils.logger import get_logger' in content:
            if needs_migration:
                issues.append("Partially migrated - has both old and new patterns")
            else:
                needs_migration = False
                issues = ["Already migrated"]
    
    except Exception as e:
        issues.append(f"Error reading file: {e}")
    
    return needs_migration, issues

def migrate_file(file_path: str, dry_run: bool = True) -> bool:
    """Migrate a single file to use centralized logging."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        content = original_content
        
        # Replace import statements
        # Replace 'import logging' with centralized logger import
        if 'import logging' in content and 'from utils.logger import get_logger' not in content and 'from app.utils.logger import get_logger' not in content:
            # Determine correct import path based on file location
            if '/app/' in file_path:
                import_line = "from app.utils.logger import get_logger"
            else:
                import_line = "from utils.logger import get_logger"
            
            # Replace the first occurrence of 'import logging'
            content = re.sub(
                r'^import logging\s*$',
                import_line,
                content,
                count=1,
                flags=re.MULTILINE
            )
        
        # Replace logger initialization
        # Replace 'logger = logging.getLogger(__name__)' with 'logger = get_logger(__name__)'
        content = re.sub(
            r'logger\s*=\s*logging\.getLogger\(__name__\)',
            'logger = get_logger(__name__)',
            content
        )
        
        # Replace other getLogger calls
        content = re.sub(
            r'logging\.getLogger\(([^)]+)\)',
            r'get_logger(\1)',
            content
        )
        
        # Remove logging.basicConfig calls (commented out for safety)
        content = re.sub(
            r'^logging\.basicConfig\(',
            '# logging.basicConfig(',
            content,
            flags=re.MULTILINE
        )
        
        # Remove logger.setLevel calls (commented out for safety)
        content = re.sub(
            r'^(\s*)logger\.setLevel\(',
            r'\1# logger.setLevel(',
            content,
            flags=re.MULTILINE
        )
        
        # Remove standalone 'import logging' if it's still there and not needed
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() == 'import logging' and 'get_logger' in content:
                new_lines.append('# ' + line + '  # Replaced with centralized logger')
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
        
        # Only write if content changed
        if content != original_content:
            if not dry_run:
                # Create backup
                backup_path = file_path + '.backup'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write migrated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✓ Migrated: {file_path}")
                print(f"  Backup created: {backup_path}")
            else:
                print(f"Would migrate: {file_path}")
            
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
    
    except Exception as e:
        print(f"✗ Error migrating {file_path}: {e}")
        return False

def main():
    """Main migration function."""
    print("Centralized Logging Migration Tool")
    print("=" * 40)
    
    # Get base path
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Base path: {base_path}")
    
    # Find Python files
    print("\nFinding Python files...")
    python_files = find_python_files(base_path)
    print(f"Found {len(python_files)} Python files")
    
    # Analyze files
    print("\nAnalyzing files...")
    files_to_migrate = []
    already_migrated = []
    no_migration_needed = []
    
    for file_path in python_files:
        needs_migration, issues = analyze_file(file_path)
        
        relative_path = os.path.relpath(file_path, base_path)
        
        if needs_migration:
            if "Already migrated" not in issues:
                files_to_migrate.append((file_path, issues))
                print(f"  📝 {relative_path}: {', '.join(issues)}")
            else:
                already_migrated.append(file_path)
        else:
            if "Already migrated" in issues:
                already_migrated.append(file_path)
            else:
                no_migration_needed.append(file_path)
    
    # Summary
    print(f"\nSummary:")
    print(f"  Files needing migration: {len(files_to_migrate)}")
    print(f"  Files already migrated: {len(already_migrated)}")
    print(f"  Files not needing migration: {len(no_migration_needed)}")
    
    if not files_to_migrate:
        print("\n🎉 All files are already using centralized logging!")
        return
    
    # Ask for confirmation
    print(f"\nFiles to migrate:")
    for file_path, issues in files_to_migrate:
        relative_path = os.path.relpath(file_path, base_path)
        print(f"  • {relative_path}")
    
    print("\nDry run (preview changes)...")
    for file_path, issues in files_to_migrate:
        migrate_file(file_path, dry_run=True)
    
    print("\n" + "="*50)
    response = input("Do you want to proceed with the migration? (y/N): ")
    
    if response.lower() == 'y':
        print("\nPerforming migration...")
        migrated_count = 0
        
        for file_path, issues in files_to_migrate:
            if migrate_file(file_path, dry_run=False):
                migrated_count += 1
        
        print(f"\n✅ Migration completed!")
        print(f"   Migrated {migrated_count} files")
        print(f"   Backup files created with .backup extension")
        print(f"\nNext steps:")
        print(f"   1. Test your application to ensure everything works")
        print(f"   2. Remove .backup files if everything is working correctly")
        print(f"   3. Update any remaining manual logging configurations")
    else:
        print("\nMigration cancelled.")

if __name__ == "__main__":
    main() 