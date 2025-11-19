# Command Output Format Standard

## Overview

All TradingAgents commands should follow a consistent output format that includes:
1. **Analysis/Results Section** - The main command output
2. **Next Steps & Recommendations Section** - Actionable recommendations
3. **Commands to Execute** - Specific commands to follow up
4. **Full Guide Reference** - Link to comprehensive documentation

This format ensures users always know what to do next after running any command.

## Format Structure

### Standard Format

```
[Main Command Output - Analysis, Results, Data, etc.]

═══ NEXT STEPS & RECOMMENDATIONS ═══

[Numbered list of actionable recommendations]

Commands to Execute These Recommendations:

[Category 1:]
  ./quick_run.sh command1    - Description
  ./quick_run.sh command2    - Description

[Category 2:]
  ./quick_run.sh command3    - Description
  ./quick_run.sh command4    - Description

📖 Full Guide: See docs/STRATEGY_RECOMMENDATIONS_COMMANDS.md for complete command reference
```

## Implementation Guide

### Step 1: Import the Helper Function

Add this import to your command module:

```python
from tradingagents.utils import display_next_steps
```

### Step 2: Call at End of Command

Add the recommendations section at the end of your command function, after all output:

```python
def your_command_function(args):
    # ... your command logic ...
    # ... print results ...
    
    # Display next steps and recommendations
    display_next_steps('command_name', context={'key': 'value'})
    
    return 0
```

### Step 3: Command Name Mapping

Use the appropriate command name when calling `display_next_steps()`:

| Command | Command Name |
|---------|--------------|
| `screener` | `'screener'` |
| `analyze TICKER` | `'analyze'` |
| `portfolio` | `'portfolio'` |
| `performance` | `'performance'` |
| `dividends` | `'dividends'` |
| `evaluate` | `'evaluate'` |
| `digest` | `'digest'` |
| `morning` | `'morning'` |
| `alerts` | `'alerts'` |
| `top` | `'top'` |
| `stats` | `'stats'` |
| `indicators` | `'indicators'` |
| `indexes` | `'indexes'` (handled separately) |

### Step 4: Context Parameters (Optional)

Pass relevant context to customize recommendations:

```python
# For commands with ticker
display_next_steps('analyze', context={'ticker': 'AAPL'})

# For commands with limits
display_next_steps('top', context={'limit': 5})

# For commands with results count
display_next_steps('screener', context={'results_count': 20})
```

## Examples

### Example 1: Simple Command (digest)

```python
def digest_command(args):
    digest_gen = MarketDigest()
    digest = digest_gen.generate_digest(target_date)
    print(digest)
    
    # Display next steps and recommendations
    display_next_steps('digest')
```

### Example 2: Command with Context (analyze)

```python
def analyze_ticker(analyzer, ticker, ...):
    results = analyzer.analyze(ticker, ...)
    analyzer.print_results(results, ...)
    
    # Display next steps and recommendations
    display_next_steps('analyze', context={'ticker': ticker})
    return results
```

### Example 3: Command with Multiple Exit Points

```python
def your_command(args):
    if not results:
        print("No results found.")
        return 1
    
    # Print results
    print_results(results)
    
    # Display next steps and recommendations
    display_next_steps('your_command', context={'count': len(results)})
    
    return 0
```

## Adding New Commands

### When Adding a New Command:

1. **Add to `tradingagents/utils/recommendations.py`**:
   - Add command-specific recommendations in `_get_command_recommendations()`
   - Add command-specific command references in `_display_command_references()`

2. **Update Your Command Module**:
   - Import `display_next_steps`
   - Call it at the end of your command function

3. **Test the Output**:
   - Run your command
   - Verify the recommendations section appears
   - Check that commands are relevant and helpful

### Template for New Command Recommendations

```python
# In _get_command_recommendations()
'your_new_command': [
    "Review the analysis results",
    "Check related metrics",
    "Take appropriate action",
    "Monitor for changes",
    "Document decisions"
],

# In _display_command_references()
'your_new_command': [
    ("For Related Analysis:", [
        "./quick_run.sh related_command1",
        "./quick_run.sh related_command2"
    ]),
    ("For Follow-up Actions:", [
        "./quick_run.sh action_command1",
        "./quick_run.sh action_command2"
    ]),
    ("For Monitoring:", [
        "./quick_run.sh monitor_command1",
        "./quick_run.sh monitor_command2"
    ])
],
```

## Best Practices

1. **Always include recommendations** - Every command should end with next steps
2. **Be specific** - Recommendations should be actionable, not vague
3. **Group commands logically** - Organize follow-up commands by purpose
4. **Keep it concise** - 3-5 recommendations, 2-3 command groups
5. **Use context when helpful** - Pass ticker, count, or other relevant data
6. **Maintain consistency** - Follow the same format across all commands

## File Locations

- **Helper Function**: `tradingagents/utils/recommendations.py`
- **Export**: `tradingagents/utils/__init__.py`
- **Example Implementation**: `tradingagents/market/show_indexes.py` (original format)
- **All Command Modules**: `tradingagents/*/__main__.py`

## Reference Commands

To see the format in action, run:
- `./quick_run.sh indexes` - Original format example
- `./quick_run.sh screener` - Screener with recommendations
- `./quick_run.sh analyze AAPL` - Analysis with recommendations
- `./quick_run.sh portfolio` - Portfolio with recommendations

## Questions?

If you're unsure about:
- **What recommendations to include**: Look at similar commands
- **What commands to reference**: Think about what users would logically do next
- **How to structure**: Follow the examples above

Remember: The goal is to guide users from one command to the next, creating a smooth workflow.

