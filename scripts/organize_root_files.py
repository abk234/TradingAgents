"""
Script to organize root directory files.

This script organizes:
1. Log files → logs/
2. Documentation → docs/
3. Config files → config/
4. Results → results/
5. Python scripts → scripts/ (with symlinks for backward compatibility)
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple


# Files to keep in root (essential files)
KEEP_IN_ROOT = {
    "main.py",
    "README.md",
    "LICENSE",
    "requirements.txt",
    "setup.py",
    "pyproject.toml",
    "uv.lock",
    "docker-compose.langfuse-v2.yml",
}

# File categories
LOG_FILES = [
    "application_run.log",
    "evaluation_results.log",
    "feature_validation_output.log",
    "ollama_fast_test.log",
    "screener_full_run.log",
    "screener_test_fixed.log",
    "test_run.log",
    "trading_agents_output.log",
    "trading_agents_run2.log",
]

DOCUMENTATION_FILES = [
    "AGENT_DATABASE_TEST_ANALYSIS.md",
    "DATABASE_STATUS.md",
    "FEATURE_STATUS.md",
    "IMPLEMENTATION_SUMMARY.md",
    "INTEGRATION_GUIDE.md",
    "LANGFUSE_FIXED.md",
    "NEXT_STEPS_COMPLETE.md",
    "PROFITABILITY_ANALYSIS_AND_RECOMMENDATIONS.md",
    "QUICK_START_GUIDE.md",
    "SCREENER_TABLE_UPDATE.md",
    "USAGE_GUIDE.md",
    "chainlit.md",
    "CLAUDE.md",
]

CONFIG_FILES = [
    "config_gemini.json",
    "config_ollama.json",
]

RESULT_FILES = [
    "validation_results.json",
    "profitability_performance_report_20251117.txt",
    "SCREENER_ANALYSIS_VISUAL_GUIDE.txt",
]

# Python script categories
ENTRY_POINT_SCRIPTS = [
    "main_gemini.py",
    "main_ollama.py",
    "main_ollama_fast.py",
    "run.py",
    "run_analysis.py",
    "run_with_defaults.py",
    "run_full_validation.py",
]

VALIDATION_SCRIPTS = [
    "validate_agents.py",
    "validate_data_accuracy.py",
    "validate_eddie_prerequisites.py",
    "validate_high_priority_fixes.py",
    "validate_screener.py",
    "validate_system_data_flow.py",
    "verify_setup.py",
]

ANALYSIS_SCRIPTS = [
    "analyze_with_profitability.py",
    "evaluate_application.py",
    "monitor_profitability_performance.py",
]

UTILITY_SCRIPTS = [
    "browse_chromadb.py",
    "connect_docker_redis.py",
    "disable_redis_cache.py",
    "fix_embeddings.py",
    "sync_to_obsidian.py",
    "quick_test.py",
    "test.py",
    "_run_cli.py",
]


def organize_files(dry_run=True, create_symlinks=True):
    """
    Organize root directory files.
    
    Args:
        dry_run: If True, only show what would be done
        create_symlinks: If True, create symlinks for Python scripts
    """
    root_dir = Path(__file__).parent.parent
    
    # Create target directories
    target_dirs = {
        "logs": root_dir / "logs",
        "docs": root_dir / "docs",
        "config": root_dir / "config",
        "results": root_dir / "results",
        "entry_points": root_dir / "scripts" / "entry_points",
        "validation": root_dir / "scripts" / "validation",
        "analysis": root_dir / "scripts" / "analysis",
    }
    
    for target_dir in target_dirs.values():
        target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Root directory: {root_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Create symlinks: {create_symlinks}")
    print("=" * 70)
    
    moved = []
    skipped = []
    errors = []
    
    # Organize log files
    print("\n📋 Log Files → logs/")
    for log_file in LOG_FILES:
        src = root_dir / log_file
        if src.exists():
            dst = target_dirs["logs"] / log_file
            if dry_run:
                print(f"  Would move: {log_file} → logs/")
            else:
                try:
                    shutil.move(str(src), str(dst))
                    print(f"  ✅ MOVED: {log_file}")
                    moved.append((src, dst))
                except Exception as e:
                    print(f"  ❌ ERROR: {log_file} - {e}")
                    errors.append((src, str(e)))
        else:
            skipped.append(log_file)
    
    # Organize documentation
    print("\n📚 Documentation → docs/")
    for doc_file in DOCUMENTATION_FILES:
        src = root_dir / doc_file
        if src.exists():
            dst = target_dirs["docs"] / doc_file
            if dry_run:
                print(f"  Would move: {doc_file} → docs/")
            else:
                try:
                    shutil.move(str(src), str(dst))
                    print(f"  ✅ MOVED: {doc_file}")
                    moved.append((src, dst))
                except Exception as e:
                    print(f"  ❌ ERROR: {doc_file} - {e}")
                    errors.append((src, str(e)))
        else:
            skipped.append(doc_file)
    
    # Organize config files
    print("\n⚙️  Config Files → config/")
    for config_file in CONFIG_FILES:
        src = root_dir / config_file
        if src.exists():
            dst = target_dirs["config"] / config_file
            if dry_run:
                print(f"  Would move: {config_file} → config/")
            else:
                try:
                    shutil.move(str(src), str(dst))
                    print(f"  ✅ MOVED: {config_file}")
                    moved.append((src, dst))
                except Exception as e:
                    print(f"  ❌ ERROR: {config_file} - {e}")
                    errors.append((src, str(e)))
        else:
            skipped.append(config_file)
    
    # Organize result files
    print("\n📊 Result Files → results/")
    for result_file in RESULT_FILES:
        src = root_dir / result_file
        if src.exists():
            dst = target_dirs["results"] / result_file
            if dry_run:
                print(f"  Would move: {result_file} → results/")
            else:
                try:
                    shutil.move(str(src), str(dst))
                    print(f"  ✅ MOVED: {result_file}")
                    moved.append((src, dst))
                except Exception as e:
                    print(f"  ❌ ERROR: {result_file} - {e}")
                    errors.append((src, str(e)))
        else:
            skipped.append(result_file)
    
    # Organize Python scripts
    print("\n🐍 Python Scripts → scripts/")
    
    script_categories = {
        "entry_points": ENTRY_POINT_SCRIPTS,
        "validation": VALIDATION_SCRIPTS,
        "analysis": ANALYSIS_SCRIPTS,
    }
    
    for category, scripts in script_categories.items():
        target_dir = target_dirs[category]
        print(f"\n  {category.replace('_', ' ').title()}:")
        for script_file in scripts:
            src = root_dir / script_file
            if src.exists():
                dst = target_dir / script_file
                if dry_run:
                    print(f"    Would move: {script_file} → scripts/{category}/")
                    if create_symlinks:
                        print(f"      Would create symlink: {script_file} → scripts/{category}/{script_file}")
                else:
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"    ✅ MOVED: {script_file}")
                        
                        # Create symlink
                        if create_symlinks:
                            symlink_path = root_dir / script_file
                            if not symlink_path.exists():
                                symlink_path.symlink_to(dst.relative_to(root_dir))
                                print(f"      ✅ LINKED: {script_file}")
                        
                        moved.append((src, dst))
                    except Exception as e:
                        print(f"    ❌ ERROR: {script_file} - {e}")
                        errors.append((src, str(e)))
            else:
                skipped.append(script_file)
    
    # Utility scripts (already have utilities directory)
    print("\n  Utilities:")
    for script_file in UTILITY_SCRIPTS:
        src = root_dir / script_file
        if src.exists():
            dst = root_dir / "scripts" / "utilities" / script_file
            if dry_run:
                print(f"    Would move: {script_file} → scripts/utilities/")
                if create_symlinks:
                    print(f"      Would create symlink: {script_file} → scripts/utilities/{script_file}")
            else:
                try:
                    shutil.move(str(src), str(dst))
                    print(f"    ✅ MOVED: {script_file}")
                    
                    # Create symlink
                    if create_symlinks:
                        symlink_path = root_dir / script_file
                        if not symlink_path.exists():
                            symlink_path.symlink_to(dst.relative_to(root_dir))
                            print(f"      ✅ LINKED: {script_file}")
                    
                    moved.append((src, dst))
                except Exception as e:
                    print(f"    ❌ ERROR: {script_file} - {e}")
                    errors.append((src, str(e)))
        else:
            skipped.append(script_file)
    
    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  {'Would move' if dry_run else 'Moved'}: {len(moved)} files")
    print(f"  Skipped (not found): {len(skipped)} files")
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
    
    moved, skipped, errors = organize_files(dry_run=dry_run, create_symlinks=not no_symlinks)

