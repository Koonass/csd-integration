# Field Mapping Review Instructions

## Overview

You now have a working webhook connection! The data is flowing from JotForm → PythonAnywhere → Database.

The next step is to **review and customize** how your JotForm fields map to the CSD Portal fields.

## Current Status

✅ **Working:**
- JotForm webhook receives submissions
- Data is parsed and stored in database
- Dashboard shows submission data

⚠️ **Needs Review:**
- Many fields are mapped to "COMPOSITE_NOTES" (they get combined into a notes field)
- Some CSD required fields are auto-generated
- Value transformations may need adjustment
- You may want to add fields to your JotForm

## How to Review Mappings

### Step 1: Open the Spreadsheet

Open **FIELD_MAPPING_WORKSHEET.csv** in Excel or Google Sheets.

This shows:
- All your JotForm fields
- Where they currently map in CSD Portal
- What needs your decision

### Step 2: Review Each Row

For each field, ask yourself:

1. **Is the mapping correct?**
   - Does this JotForm field go to the right CSD field?
   - Example: Is "lotAnd" correctly going to Address field?

2. **Should it be in notes or have its own field?**
   - Many fields go to COMPOSITE_NOTES (combined into one notes field)
   - Does CSD Portal have a dedicated field for this?

3. **Are the values formatted correctly?**
   - Example: "Stick Built" → "Stick-built" transformation
   - Do the dropdown values match CSD's expected values?

4. **Are required CSD fields covered?**
   - Project Name (currently auto-generated from builder + plan)
   - State (currently defaults to "GA")

### Step 3: Make Decisions

In the **"Decision Needed"** column, write your decisions:

**Examples:**
```
- "Keep as-is" - Current mapping is good
- "Move to [field name]" - Should go to different CSD field
- "Add to JotForm" - Need to add this to JotForm form
- "Remove" - Don't send this to CSD
- "Combine with [other field]" - Merge with another field
```

### Step 4: Identify Missing Fields

**JotForm fields that might be needed:**
- Email address (for notifications)
- Phone number (for contact)
- Project Name (instead of auto-generating)
- State/Province (instead of defaulting to GA)
- City, Zip Code

**Mark which ones to add to your JotForm.**

## Key Questions to Answer

### About Composite Notes

Currently these go into a combined "notes" field:
- Foundation Type
- Is this a sold job?
- Job specifications (joist depth, manufacturer, etc.)
- Fireplace construction

**Question:** Is this okay, or should any have dedicated CSD fields?

### About Required CSD Fields

**Project Name:**
- Currently: Auto-generated as "Builder Name - Plan Name"
- Option: Add dedicated "Project Name" field to JotForm
- **What do you prefer?**

**State/Province:**
- Currently: Defaults to "GA" (Georgia)
- Option: Add state selection to JotForm
- **What do you prefer?** (Since you're Atlanta-based, GA default might be fine)

### About Contact Info

CSD Portal accepts:
- Name
- Email
- Phone

Currently:
- Name = Salesman email
- Email = Not collected
- Phone = Not collected

**Should we add Email and Phone fields to JotForm?**

### About Conditional Fields

**"If roof is trussed by others" field:**
- Only relevant when roofType = "Trussed by Others"
- Currently goes to notes
- **Is this okay?**

## What Happens Next

After you've reviewed the spreadsheet:

1. **We'll update field_mapping.json** based on your decisions
2. **Add any new fields to JotForm** (if needed)
3. **Test CSD Portal submission** to verify data goes where you want
4. **Iterate until perfect**

## Important Notes

### Don't Worry About:

- ✅ File uploads - Not fully implemented yet, we can add this later
- ✅ Complex transformations - We can handle these in code
- ✅ Making mistakes - Easy to change later!

### Focus On:

1. **Core data mapping** - Builder, plan, location, specifications
2. **Required fields** - Make sure CSD gets what it needs
3. **User experience** - Does your team need to fill in more/less on JotForm?

## Example Review Process

Let's walk through one field as an example:

**Field: "lotAnd" (Lot and Subdivision)**

| Current | Question | Options |
|---------|----------|---------|
| Maps to: Address field | Is this correct? | • Yes, keep as-is<br>• No, should go to different field<br>• Combine with other location data |
| Decision → | Write in spreadsheet | "Keep as-is - Address field is correct for lot info" |

Do this for each row in the spreadsheet!

## Next Steps

1. **Review the spreadsheet** - Go through each field (15-30 minutes)
2. **Make notes** in the "Decision Needed" column
3. **Share your decisions** - We'll implement them together
4. **Test** - Submit form and verify data goes to right places

## Questions to Consider

As you review, think about:

- **What does CSD Portal need** to process your design requests?
- **What's essential** vs. nice-to-have?
- **Will your team** fill this out consistently?
- **Does the current form** collect all necessary info?

## Getting Help

If you're unsure about any mapping:

1. **Look at CSD Portal form** - See what fields they have
2. **Check existing submissions** - What data did you enter manually before?
3. **Ask your team** - What info is always needed?
4. **Test it** - We can always change it later!

---

**Ready to review?** Open the CSV file and start making notes!

When you're done, we'll update the configuration and test the CSD Portal submission together.
