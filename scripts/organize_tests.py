# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Script to organize test files from root into proper test directory structure.

This script:
1. Moves test_*.py files from root to tests/integration_legacy/
2. Creates symlinks or copies (user choice)
3. Updates any import paths if needed
"""

import os
import shutil
from pathlib import Path


def organize_test_files(dry_run=True, create_symlinks=False):
    """
    Organize test files.
    
    Args:
        dry_run: If True, only show what would be done
        create_symlinks: If True, create symlinks instead of moving files
    """
    root_dir = Path(__file__).parent.parent
    test_dir = root_dir / "tests" / "integration_legacy"
    
    # Create test directory if it doesn't exist
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all test_*.py files in root
    test_files = list(root_dir.glob("test_*.py"))
    
    print(f"Found {len(test_files)} test files in root directory")
    print(f"Target directory: {test_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Action: {'Create symlinks' if create_symlinks else 'Move files'}")
    print("=" * 70)
    
    moved = []
    skipped = []
    
    for test_file in test_files:
        target = test_dir / test_file.name
        
        if target.exists():
            print(f"⚠️  SKIP: {test_file.name} (already exists in target)")
            skipped.append(test_file)
            continue
        
        if dry_run:
            print(f"Would {'link' if create_symlinks else 'move'}: {test_file.name}")
        else:
            try:
                if create_symlinks:
                    # Create symlink
                    target.symlink_to(test_file)
                    print(f"✅ LINKED: {test_file.name}")
                else:
                    # Move file
                    shutil.move(str(test_file), str(target))
                    print(f"✅ MOVED: {test_file.name}")
                moved.append(test_file)
            except Exception as e:
                print(f"❌ ERROR: {test_file.name} - {e}")
                skipped.append(test_file)
    
    print("=" * 70)
    print(f"Summary:")
    print(f"  {'Would move' if dry_run else 'Moved'}: {len(moved)} files")
    print(f"  Skipped: {len(skipped)} files")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. Run with dry_run=False to actually move files.")
    
    return moved, skipped


if __name__ == "__main__":
    import sys
    
    dry_run = "--execute" not in sys.argv
    symlinks = "--symlink" in sys.argv
    
    if dry_run:
        print("Running in DRY RUN mode. Use --execute to actually move files.")
        print("Use --symlink to create symlinks instead of moving.\n")
    
    moved, skipped = organize_test_files(dry_run=dry_run, create_symlinks=symlinks)

