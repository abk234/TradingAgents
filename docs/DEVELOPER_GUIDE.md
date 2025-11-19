# Developer Guide

## Quick Reference

### Adding New Commands

When adding a new command to TradingAgents, follow the standard output format:

**📖 Full Documentation:** See [COMMAND_OUTPUT_FORMAT.md](./COMMAND_OUTPUT_FORMAT.md)

**Quick Steps:**

1. **Import the helper:**
   ```python
   from tradingagents.utils import display_next_steps
   ```

2. **Add recommendations at end of command:**
   ```python
   def your_command(args):
       # ... your command logic ...
       print_results()
       
       # Display next steps and recommendations
       display_next_steps('your_command', context={'key': 'value'})
       return 0
   ```

3. **Update recommendations.py:**
   - Add command-specific recommendations in `_get_command_recommendations()`
   - Add command references in `_display_command_references()`

### Command Output Format

All commands should follow this structure:

```
[Main Analysis/Results Output]

═══ NEXT STEPS & RECOMMENDATIONS ═══

1. Recommendation 1
2. Recommendation 2
3. Recommendation 3

Commands to Execute These Recommendations:

[Category 1:]
  ./quick_run.sh command1    - Description
  ./quick_run.sh command2    - Description

📖 Full Guide: See docs/STRATEGY_RECOMMENDATIONS_COMMANDS.md
```

### Example Implementation

See existing commands for examples:
- `tradingagents/screener/__main__.py` - `cmd_run()` function
- `tradingagents/analyze/__main__.py` - `main()` function
- `tradingagents/portfolio/__main__.py` - Command handlers

### Testing

After adding a new command:
1. Run the command: `./quick_run.sh your-command`
2. Verify recommendations section appears
3. Check that follow-up commands are relevant
4. Ensure format matches other commands

### Questions?

- **Format questions:** See `docs/COMMAND_OUTPUT_FORMAT.md`
- **Command reference:** See `docs/STRATEGY_RECOMMENDATIONS_COMMANDS.md`
- **Code examples:** Check `tradingagents/utils/recommendations.py`

