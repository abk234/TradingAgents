#!/bin/bash
# Investment Intelligence System - Database Backup Script
#
# This script creates compressed backups of the PostgreSQL database
#
# Usage:
#   ./scripts/backup_database.sh

set -e

# Configuration
DB_NAME="investment_intelligence"
BACKUP_DIR="$HOME/iis_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/iis_backup_$TIMESTAMP.sql.gz"
PG_DUMP="/opt/homebrew/opt/postgresql@14/bin/pg_dump"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "======================================================================="
echo "Investment Intelligence System - Database Backup"
echo "======================================================================="
echo "Database: $DB_NAME"
echo "Backup location: $BACKUP_FILE"
echo ""

# Perform backup
echo "Creating backup..."
$PG_DUMP -d "$DB_NAME" | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✓ Backup completed successfully"
    echo "  Size: $BACKUP_SIZE"
    echo ""

    # Keep only last 30 backups
    echo "Cleaning old backups (keeping last 30)..."
    cd "$BACKUP_DIR"
    ls -t iis_backup_*.sql.gz | tail -n +31 | xargs -r rm

    TOTAL_BACKUPS=$(ls -1 iis_backup_*.sql.gz 2>/dev/null | wc -l)
    echo "✓ Total backups: $TOTAL_BACKUPS"

else
    echo "✗ Backup failed!"
    exit 1
fi

echo ""
echo "======================================================================="
echo "To restore this backup, run:"
echo "  gunzip < $BACKUP_FILE | psql -d $DB_NAME"
echo "======================================================================="
