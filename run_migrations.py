#!/usr/bin/env python3
"""
Run database migrations for AnythingLLM integration features.

This script runs the SQL migrations for:
- documents table (002_add_documents_table.sql)
- workspaces table (003_add_workspaces_table.sql)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.database import get_db_connection

def run_migration_file(db, migration_file: Path):
    """Run a single migration file."""
    print(f"\n📄 Running migration: {migration_file.name}")
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                for i, statement in enumerate(statements, 1):
                    if statement:
                        try:
                            cur.execute(statement)
                            print(f"   ✓ Statement {i}/{len(statements)} executed")
                        except Exception as e:
                            # Some statements might fail if already exists (IF NOT EXISTS)
                            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                                print(f"   ⚠️  Statement {i} skipped (already exists)")
                            else:
                                print(f"   ❌ Error in statement {i}: {e}")
                                raise
                conn.commit()
        
        print(f"✅ Migration completed: {migration_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Run all migrations."""
    print("=" * 60)
    print("🚀 Running Database Migrations")
    print("=" * 60)
    
    # Get database connection
    try:
        db = get_db_connection()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\n💡 Make sure PostgreSQL is running and accessible")
        print("   Default database: investment_intelligence")
        print("   Default host: localhost:5432")
        sys.exit(1)
    
    # Migration files
    migrations_dir = project_root / "database" / "migrations"
    
    migrations = [
        migrations_dir / "002_add_documents_table.sql",
        migrations_dir / "003_add_workspaces_table.sql",
    ]
    
    success_count = 0
    for migration_file in migrations:
        if run_migration_file(db, migration_file):
            success_count += 1
    
    print("\n" + "=" * 60)
    if success_count == len(migrations):
        print(f"✅ All migrations completed successfully ({success_count}/{len(migrations)})")
    else:
        print(f"⚠️  Completed {success_count}/{len(migrations)} migrations")
    print("=" * 60)
    
    # Verify tables exist
    print("\n🔍 Verifying tables...")
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Check documents table
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'documents'
                    );
                """)
                if cur.fetchone()[0]:
                    print("✅ documents table exists")
                else:
                    print("❌ documents table not found")
                
                # Check workspaces table
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'workspaces'
                    );
                """)
                if cur.fetchone()[0]:
                    print("✅ workspaces table exists")
                else:
                    print("❌ workspaces table not found")
    except Exception as e:
        print(f"⚠️  Could not verify tables: {e}")

if __name__ == "__main__":
    main()

