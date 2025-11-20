# Field Mapping Customization Guide

This guide explains how to customize field mappings between JotForm and CSD Portal.

## Understanding Field Mapping

The `field_mapping.json` file controls how data flows from JotForm to CSD Portal. Each mapping entry connects a JotForm field to its destination in CSD Portal.

## Mapping Entry Structure

```json
{
  "jotform_field": "builderName",      // JotForm field name
  "jotform_label": "Builder Name",      // Human-readable label
  "csd_field": "ctl00_cphBody_txtBuilderName",  // CSD Portal field ID
  "csd_field_type": "text",            // Field type
  "required": true,                     // Is field required?
  "transform": null,                    // Transformation function
  "notes": "Main builder/company name"  // Documentation
}
```

## Mapping Types

### 1. Direct Mapping (Simple)

Value copied directly from JotForm to CSD Portal:

```json
{
  "jotform_field": "planName",
  "csd_field": "ctl00_cphBody_txtPlanName",
  "csd_field_type": "text",
  "transform": null
}
```

### 2. Composite Notes Mapping

Multiple JotForm fields combined into CSD notes field:

```json
{
  "jotform_field": "jobNotes",
  "csd_field": "COMPOSITE_NOTES",
  "csd_field_type": "composite",
  "transform": "append_to_notes"
}
```

All COMPOSITE_NOTES entries are combined into a single notes field sent to CSD Portal.

### 3. Value Transformation

Map JotForm values to different CSD Portal values:

```json
{
  "jotform_field": "roofType",
  "csd_field": "rblRoofingFrame",
  "transform": "map_roof_type",
  "value_mapping": {
    "Stick Built": "Stick-built",
    "Trussed by Others": "Trusses",
    "Trussed by CBC": "Trusses"
  }
}
```

## How to Find CSD Portal Field Names

### Method 1: Browser Developer Tools (Recommended)

1. Open CSD Portal form in Chrome/Edge
2. Press **F12** to open Developer Tools
3. Click **Elements** tab
4. Right-click on a form field → **Inspect**
5. Look for the `name=` attribute in the HTML
6. Example: `<input name="ctl00_cphBody_txtBuilderName">`

### Method 2: View Page Source

1. Right-click on CSD Portal page
2. Click "View Page Source"
3. Search for `<input`, `<select>`, or `<textarea>` tags
4. Find the `name` attribute

### Common CSD Portal Fields

Based on our inspection, here are the key fields:

| CSD Portal Field Name | Type | Purpose |
|----------------------|------|---------|
| `ctl00_cphBody_txtName` | text | Contact Name |
| `ctl00_cphBody_txtPhone` | text | Phone Number |
| `ctl00_cphBody_txtEmail` | text | Email Address |
| `ctl00_cphBody_txtBuilderName` | text | Builder Name |
| `ctl00_cphBody_txtBuilderLocation` | text | Builder Location |
| `ctl00_cphBody_txtProjectName` | text | Project Name (REQUIRED) |
| `ctl00_cphBody_txtPlanName` | text | Plan Name |
| `ctl00_cphBody_txtAddress` | text | Address |
| `ctl00_cphBody_ddlProvince` | select | State (REQUIRED) |
| `rblRoofingFrame` | radio | Roof Framing Type |
| `rblHangerManufactuerer` | radio | Hanger Manufacturer |

## Common Customization Scenarios

### Scenario 1: Add a New Field

Add new JotForm field to the mapping:

```json
{
  "jotform_field": "newFieldName",
  "jotform_label": "New Field Label",
  "csd_field": "ctl00_cphBody_txtNewField",
  "csd_field_type": "text",
  "required": false,
  "transform": null,
  "notes": "Description of what this field does"
}
```

### Scenario 2: Move Field from Notes to Direct Mapping

Change from composite notes to direct field:

**Before:**
```json
{
  "jotform_field": "foundationType",
  "csd_field": "COMPOSITE_NOTES",
  "transform": "append_to_notes"
}
```

**After:**
```json
{
  "jotform_field": "foundationType",
  "csd_field": "ctl00_cphBody_ddlFoundationType",
  "csd_field_type": "select",
  "transform": null
}
```

### Scenario 3: Add Value Transformation

If JotForm and CSD use different value formats:

```json
{
  "jotform_field": "projectType",
  "csd_field": "ctl00_cphBody_ddlProjectType",
  "transform": "map_project_type",
  "value_mapping": {
    "New Construction": "Residential",
    "Remodel": "Remodel",
    "Commercial Build": "Commercial"
  }
}
```

### Scenario 4: Make Field Required

Add validation in JotForm AND mark required in mapping:

```json
{
  "jotform_field": "deliveryDate",
  "required": true  // Mark as required
}
```

## Testing Your Changes

After editing `field_mapping.json`:

1. **Validate JSON syntax:**
   ```bash
   python -c "import json; json.load(open('field_mapping.json'))"
   ```

2. **Restart Flask application:**
   ```bash
   # Stop the app (Ctrl+C)
   python app.py
   ```

3. **Test with sample data:**
   ```bash
   python test_webhook.py
   ```

4. **Check the mapping UI:**
   - Go to http://localhost:5000/mapping
   - Verify your changes appear correctly

5. **Submit test form:**
   - Submit your JotForm
   - Check logs: `tail -f logs/submissions.log`
   - Verify data in CSD Portal

## Handling Special Cases

### File Attachments

```json
{
  "jotform_field": "attachPlans",
  "csd_field": "ctl00_cphBody_ajaxFileUploader",
  "csd_field_type": "file",
  "transform": "upload_file"
}
```

Note: File handling requires downloading from JotForm and uploading to CSD Portal.

### Checkbox Fields (Multiple Values)

```json
{
  "jotform_field": "chooseAny",
  "csd_field": "COMPOSITE_NOTES",
  "csd_field_type": "composite",
  "transform": "append_to_notes",
  "options": ["Option 1", "Option 2", "Option 3"]
}
```

Multiple selected values are combined with commas.

### Conditional Fields

```json
"conditional_fields": {
  "ifRoof": {
    "show_when": {
      "roofType": "Trussed by Others"
    }
  }
}
```

## Best Practices

1. **Backup before editing:**
   ```bash
   cp field_mapping.json field_mapping.json.backup
   ```

2. **Use meaningful notes:**
   ```json
   "notes": "Builder company name - required for CSD tracking"
   ```

3. **Test incrementally:**
   - Change one mapping at a time
   - Test after each change
   - Don't change multiple mappings at once

4. **Document transformations:**
   - If using custom transform, document in notes
   - Explain value mappings

5. **Keep version history:**
   - Update `last_updated` field
   - Consider version control (Git)

## Troubleshooting

### JSON Syntax Error

```bash
# Validate JSON
python -c "import json; json.load(open('field_mapping.json'))"
```

Common issues:
- Missing comma between entries
- Trailing comma after last entry
- Unclosed brackets or braces
- Unescaped quotes in strings

### Field Not Mapping

1. Check JotForm field name matches exactly
2. Verify CSD Portal field name is correct
3. Check field is not disabled/hidden in CSD form
4. Review logs for mapping errors

### Value Not Transforming

1. Verify `transform` function exists in code
2. Check `value_mapping` entries match JotForm values exactly
3. Case sensitivity matters!

### CSD Portal Rejects Submission

1. Check required fields are populated
2. Verify value formats match CSD expectations
3. Check field character limits
4. Review CSD Portal error message in logs

## Getting Help

1. **View current mappings:**
   - http://localhost:5000/mapping

2. **Check logs:**
   ```bash
   tail -f logs/submissions.log
   ```

3. **Test specific field:**
   - Submit JotForm with only that field filled
   - Check what gets sent to CSD Portal

4. **Validate mapping file:**
   ```python
   from utils import get_field_mapping_summary
   print(get_field_mapping_summary())
   ```

## Example: Complete Customization Workflow

Let's say you want to add a "Priority" field:

1. **Add field to JotForm:**
   - Create dropdown: "Priority" with options: "High", "Normal", "Low"
   - Field name: `priority`

2. **Find corresponding CSD field:**
   - Inspect CSD Portal form
   - Find priority/urgency field: `ctl00_cphBody_ddlPriority`
   - Note CSD uses: "Urgent", "Standard", "Low"

3. **Add mapping entry:**
   ```json
   {
     "jotform_field": "priority",
     "jotform_label": "Priority",
     "csd_field": "ctl00_cphBody_ddlPriority",
     "csd_field_type": "select",
     "required": false,
     "transform": "map_priority",
     "value_mapping": {
       "High": "Urgent",
       "Normal": "Standard",
       "Low": "Low"
     },
     "notes": "Maps JotForm priority levels to CSD urgency levels"
   }
   ```

4. **Update transform function** (in csd_submitter.py):
   ```python
   elif transform == 'map_priority' and value_mapping:
       mapped_value = value_mapping.get(jotform_value, 'Standard')
       csd_data[csd_field] = mapped_value
   ```

5. **Test:**
   ```bash
   python test_webhook.py
   ```

6. **Verify:**
   - Check logs
   - Check database
   - Submit to CSD Portal
   - Confirm priority appears correctly

## Reference: Available Transform Functions

Current transform functions in `csd_submitter.py`:

- `append_to_notes` - Add to composite notes field
- `map_roof_type` - Transform roof type values
- `map_manufacturer` - Handle manufacturer preferences
- `map_to_joist_fields` - Dynamic joist field handling
- `upload_file` - File download and upload

To add custom transforms, edit the `_map_jotform_to_csd()` method in `csd_submitter.py`.

---

**Remember:** Always test changes in development before deploying to production!
