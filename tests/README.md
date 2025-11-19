# TradingAgents Test Suite

Organized test structure for TradingAgents project.

## Directory Structure

```
tests/
├── __init__.py                    # Test package init
├── test_strategy_system.py        # Quick test for strategy system
├── run_tests.sh                   # Test runner script
├── strategies/                    # Strategy system tests
│   ├── test_base.py               # Base class tests
│   ├── test_value_strategy.py     # Value strategy tests
│   ├── test_comparator.py         # Comparator tests
│   └── test_integration.py        # Integration tests
├── integration/                   # Integration layer tests
│   └── (to be added)
├── unit/                          # Unit tests for core components
│   └── (to be added)
└── integration_legacy/             # Legacy tests (moved from root)
    └── (test_*.py files from root)
```

## Running Tests

### Quick Test (Strategy System)
```bash
# Set PYTHONPATH and run
PYTHONPATH=. python tests/test_strategy_system.py

# Or use the test runner
./tests/run_tests.sh
```

### Individual Test Files
```bash
# Run specific test file
PYTHONPATH=. python tests/strategies/test_value_strategy.py

# Run with unittest
PYTHONPATH=. python -m unittest tests.strategies.test_value_strategy
```

### Using pytest (if installed)
```bash
# Run all tests
PYTHONPATH=. pytest tests/

# Run specific test
PYTHONPATH=. pytest tests/strategies/test_value_strategy.py -v
```

## Test Organization

### Strategy Tests (`tests/strategies/`)
- **test_base.py**: Tests for base classes (StrategyResult, Recommendation)
- **test_value_strategy.py**: Tests for Value Strategy
- **test_comparator.py**: Tests for Strategy Comparator
- **test_integration.py**: Full workflow integration tests

### Legacy Tests (`tests/integration_legacy/`)
- Test files moved from root directory
- Original test_*.py files from project root
- May need import path updates

## Organizing Legacy Tests

To move test files from root to test directory:

```bash
# Dry run (see what would be done)
python scripts/organize_tests.py

# Actually move files
python scripts/organize_tests.py --execute

# Create symlinks instead of moving
python scripts/organize_tests.py --execute --symlink
```

## Adding New Tests

1. **Unit Tests**: Add to `tests/strategies/` or `tests/unit/`
2. **Integration Tests**: Add to `tests/integration/`
3. **Follow naming**: `test_*.py` for test files
4. **Use unittest or pytest**: Both are supported

## Test Coverage Goals

- **New Code**: 80%+ coverage
- **Critical Paths**: 100% coverage
- **Existing Code**: Maintain current coverage

## Notes

- Tests require PYTHONPATH to be set to project root
- Some tests may require API keys or network access
- Integration tests marked with `@unittest.skip` if they require real data
- Mock data used for unit tests to avoid external dependencies

