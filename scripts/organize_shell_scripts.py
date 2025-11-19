"""
Script to organize shell scripts into proper directory structure.

This script:
1. Categorizes scripts by purpose
2. Moves them to appropriate directories
3. Creates symlinks in root for backward compatibility
4. Verifies scripts are executable
"""

import os
import shutil
import stat
from pathlib import Path
import subprocess


# Script categories
SCRIPT_CATEGORIES = {
    "main": [
        "quick_run.sh",
        "make_profit.sh",
        "trading_agents.sh",
        "trading_bot.sh",
        "trading_interactive.sh",
        "start_eddie.sh",
    ],
    "workflows": [
        "scripts/phase1_screening.sh",
        "scripts/phase2_agents.sh",
        "scripts/phase3_reports.sh",
        "scripts/phase4_full_workflow.sh",
        "scripts/run_daily_analysis.sh",
        "scripts/eddie_daily_workflow.sh",
        "scripts/eddie_quick_analysis.sh",
        "scripts/morning_briefing.sh",
        "scripts/weekly_report.sh",
        "scripts/daily_evaluation.sh",
    ],
    "maintenance": [
        "scripts/backup_database.sh",
        "scripts/show_database_state.sh",
        "scripts/check_alerts.sh",
        "scripts/dividend_alerts.sh",
        "scripts/update_dividends.sh",
        "scripts/cleanup_price_cache.sh",
        "scripts/setup_cron.sh",
        "setup_redis.sh",
        "fix_redis.sh",
        "check_run_status.sh",
    ],
    "development": [
        "quick_validate.sh",
        "test_all_features.sh",
        "tests/run_tests.sh",
        "scripts/ensure_eddie_prerequisites.sh",
        "scripts/evaluate.sh",
    ],
    "utilities": [
        "browse_chromadb.sh",
        "sync_to_obsidian.sh",
        "run_screener.sh",
    ],
}


def get_script_category(script_path):
    """Determine script category based on path and name."""
    script_name = os.path.basename(script_path)
    
    # Check each category
    for category, scripts in SCRIPT_CATEGORIES.items():
        if script_name in scripts or script_path in scripts:
            return category
    
    # Default categorization based on name/path
    if "test" in script_name.lower() or "validate" in script_name.lower():
        return "development"
    elif "phase" in script_path or "workflow" in script_path or "daily" in script_path:
        return "workflows"
    elif "backup" in script_name or "setup" in script_name or "fix" in script_name:
        return "maintenance"
    elif script_name.startswith("trading_") or script_name.startswith("start_"):
        return "main"
    else:
        return "utilities"


def make_executable(file_path):
    """Make file executable."""
    try:
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return True
    except Exception as e:
        print(f"Warning: Could not make {file_path} executable: {e}")
        return False


def verify_script(script_path):
    """Verify script has shebang and is valid bash."""
    try:
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!'):
                return True
        return False
    except Exception:
        return False


def organize_scripts(dry_run=True, create_symlinks=True):
    """
    Organize shell scripts.
    
    Args:
        dry_run: If True, only show what would be done
        create_symlinks: If True, create symlinks in root for backward compatibility
    """
    root_dir = Path(__file__).parent.parent
    
    # Target directories
    target_dirs = {
        "main": root_dir / "scripts" / "bin",
        "workflows": root_dir / "scripts" / "workflows",
        "maintenance": root_dir / "scripts" / "maintenance",
        "development": root_dir / "scripts" / "development",
        "utilities": root_dir / "scripts" / "utilities",
    }
    
    # Create target directories
    for target_dir in target_dirs.values():
        target_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all .sh files
    all_scripts = []
    for pattern in ["*.sh", "scripts/*.sh", "tests/*.sh"]:
        all_scripts.extend(root_dir.glob(pattern))
    
    # Remove duplicates and filter
    all_scripts = list(set(all_scripts))
    all_scripts = [s for s in all_scripts if s.is_file() and s.suffix == ".sh"]
    
    print(f"Found {len(all_scripts)} shell scripts")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Create symlinks: {create_symlinks}")
    print("=" * 70)
    
    moved = []
    skipped = []
    errors = []
    
    for script_path in sorted(all_scripts):
        script_name = script_path.name
        relative_path = script_path.relative_to(root_dir)
        
        # Skip if already in target directory
        if "scripts/bin" in str(script_path) or \
           "scripts/workflows" in str(script_path) or \
           "scripts/maintenance" in str(script_path) or \
           "scripts/development" in str(script_path) or \
           "scripts/utilities" in str(script_path):
            print(f"⏭️  SKIP: {relative_path} (already in organized location)")
            skipped.append(script_path)
            continue
        
        # Determine category
        category = get_script_category(str(relative_path))
        target_dir = target_dirs[category]
        target_path = target_dir / script_name
        
        # Handle name conflicts
        if target_path.exists() and target_path != script_path:
            # Add parent directory name to avoid conflicts
            parent_name = script_path.parent.name if script_path.parent != root_dir else "root"
            target_path = target_dir / f"{parent_name}_{script_name}"
            print(f"⚠️  Name conflict: Using {target_path.name}")
        
        if dry_run:
            print(f"Would move: {relative_path} → scripts/{category}/{target_path.name}")
        else:
            try:
                # Verify script
                if not verify_script(script_path):
                    print(f"⚠️  WARNING: {relative_path} may not be a valid shell script")
                
                # Move file
                shutil.move(str(script_path), str(target_path))
                
                # Make executable
                make_executable(target_path)
                
                # Create symlink in root if requested
                if create_symlinks and script_path.parent == root_dir:
                    symlink_path = root_dir / script_name
                    if not symlink_path.exists():
                        symlink_path.symlink_to(target_path.relative_to(root_dir))
                        print(f"✅ MOVED & LINKED: {relative_path} → scripts/{category}/{target_path.name}")
                    else:
                        print(f"✅ MOVED: {relative_path} → scripts/{category}/{target_path.name} (symlink exists)")
                else:
                    print(f"✅ MOVED: {relative_path} → scripts/{category}/{target_path.name}")
                
                moved.append((script_path, target_path))
                
            except Exception as e:
                print(f"❌ ERROR: {relative_path} - {e}")
                errors.append((script_path, str(e)))
    
    print("=" * 70)
    print(f"Summary:")
    print(f"  {'Would move' if dry_run else 'Moved'}: {len(moved)} files")
    print(f"  Skipped: {len(skipped)} files")
    print(f"  Errors: {len(errors)} files")
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN. Run with --execute to actually move files.")
    
    return moved, skipped, errors


if __name__ == "__main__":
    import sys
    
    dry_run = "--execute" not in sys.argv
    no_symlinks = "--no-symlinks" in sys.argv
    
    if dry_run:
        print("Running in DRY RUN mode. Use --execute to actually move files.")
        print("Use --no-symlinks to skip creating symlinks.\n")
    
    moved, skipped, errors = organize_scripts(dry_run=dry_run, create_symlinks=not no_symlinks)

