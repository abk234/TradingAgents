# Scripts Directory

Organized shell scripts for TradingAgents project.

## Directory Structure

```
scripts/
├── bin/              # Main entry point scripts
├── workflows/        # Daily/weekly workflows
├── maintenance/      # Maintenance & setup scripts
├── development/      # Development & testing scripts
├── utilities/        # Utility scripts
└── verify_scripts.sh # Script verification tool
```

## Quick Access

### Main Scripts
```bash
./scripts/bin/quick_run.sh          # Quick access menu
./scripts/bin/make_profit.sh        # Profit workflow
./scripts/bin/start_eddie.sh        # Start Eddie
```

### Workflows
```bash
./scripts/workflows/phase1_screening.sh    # Phase 1: Screening
./scripts/workflows/phase2_agents.sh        # Phase 2: Agents
./scripts/workflows/phase3_reports.sh       # Phase 3: Reports
./scripts/workflows/phase4_full_workflow.sh # Phase 4: Full workflow
```

### Maintenance
```bash
./scripts/maintenance/backup_database.sh   # Backup database
./scripts/maintenance/show_database_state.sh # Show DB state
./scripts/maintenance/setup_redis.sh        # Setup Redis
```

### Development
```bash
./scripts/development/run_tests.sh          # Run tests
./scripts/development/quick_validate.sh     # Quick validation
```

### Utilities
```bash
./scripts/utilities/browse_chromadb.sh      # Browse ChromaDB
./scripts/utilities/run_screener.sh        # Run screener
```

## Script Runner

Use the script runner for easy access:

```bash
# List all scripts
./scripts/bin/run.sh list

# Run a script
./scripts/bin/run.sh main quick_run
./scripts/bin/run.sh workflows phase1_screening
```

## Backward Compatibility

Common scripts are accessible from root via symlinks:

```bash
# These still work from root
./quick_run.sh
./make_profit.sh
./start_eddie.sh
```

## Verification

Verify all scripts are valid:

```bash
./scripts/verify_scripts.sh
```

## Documentation

See `docs/SHELL_SCRIPTS_ORGANIZATION.md` for complete documentation.

