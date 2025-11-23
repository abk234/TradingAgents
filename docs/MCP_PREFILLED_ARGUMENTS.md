# MCP Tools - Pre-filled Arguments Feature

## Overview

All MCP tools now automatically pre-fill their arguments when selected, making it easier to use tools without manually typing JSON.

## How It Works

When you select a tool in the MCP Tools view:

1. **Automatic Pre-filling**: All arguments (both required and optional) are automatically populated from the tool's schema
2. **Smart Defaults**: Default values are generated based on:
   - Schema-defined defaults (if available)
   - Field type (string, number, boolean, array, object)
   - Enum values (first enum value for string fields)
   - Examples from schema
   - Sensible fallbacks

## Default Value Generation

### String Fields
- If enum values exist: Uses first enum value
- If example exists: Uses example
- Otherwise: Empty string `""`

### Number/Integer Fields
- If minimum exists: Uses minimum value
- If example exists: Uses example
- Otherwise: `0`

### Boolean Fields
- If example exists: Uses example
- Otherwise: `false`

### Array Fields
- If example exists: Uses example array
- Otherwise: Empty array `[]`

### Object Fields
- If example exists: Uses example object
- Otherwise: Empty object `{}`

## Examples

### Example 1: `analyze_sector`
**Schema:**
```json
{
  "properties": {
    "sector_name": {
      "type": "string"
    }
  },
  "required": ["sector_name"]
}
```

**Pre-filled:**
```json
{
  "sector_name": ""
}
```

**User edits to:**
```json
{
  "sector_name": "Technology"
}
```

### Example 2: `run_screener`
**Schema:**
```json
{
  "properties": {
    "sector_analysis": {
      "type": "boolean",
      "default": true
    },
    "top_n": {
      "type": "integer",
      "default": 10
    }
  }
}
```

**Pre-filled:**
```json
{
  "sector_analysis": true,
  "top_n": 10
}
```

### Example 3: `analyze_stock`
**Schema:**
```json
{
  "properties": {
    "ticker": {
      "type": "string"
    },
    "portfolio_value": {
      "type": "number",
      "default": 100000
    }
  },
  "required": ["ticker"]
}
```

**Pre-filled:**
```json
{
  "ticker": "",
  "portfolio_value": 100000
}
```

## Benefits

1. **Faster Tool Usage**: No need to manually type JSON structure
2. **Fewer Errors**: All fields are visible, reducing missing argument errors
3. **Better UX**: Users can see what fields are available
4. **Type Safety**: Defaults match expected types
5. **Required Field Visibility**: Required fields are clearly marked

## UI Features

- **Required Fields Indicator**: Red text shows which fields are required
- **Pre-filled Notice**: Message indicates all fields are pre-filled
- **Editable**: Users can modify any pre-filled value
- **Validation**: Still validates required fields before execution

## Testing

1. Open MCP Tools view
2. Select any tool (e.g., `analyze_sector`)
3. Notice arguments are automatically pre-filled
4. Edit values as needed
5. Execute tool

## Implementation Details

The `generateDefaultArguments()` function:
- Processes all properties from the tool's input schema
- Handles both required and optional fields
- Respects schema defaults
- Generates sensible defaults based on type
- Returns a complete argument object

This function is called automatically when a tool is selected in the UI.

