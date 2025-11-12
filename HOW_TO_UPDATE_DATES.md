# How to Update Maintenance Dates

After completing maintenance on equipment, you need to update the date so the system knows when to send the next alert.

## Quick Start - Easiest Method

1. **Open a terminal/command prompt** in the project folder

2. **Run the update script:**
   ```bash
   python update_maintenance_date.py
   ```

3. **Follow the prompts:**
   - The script will show you all available equipment
   - Enter the equipment name when asked
   - If there are multiple equipment with the same name, enter the serial number
   - Choose the maintenance frequency (monthly, bi_annual, or annual)
   - Enter the date you completed maintenance (or press Enter for today's date)

**Example:**
```
=== Equipment Maintenance Date Updater ===

=== Available Equipment ===

1. Blockwise Crimper (S/N: 14024) - Cleanroom
   Maintenance: Bi-Annual (last: 2025-06-25)

2. Oil Free Air Compressor (S/N: 20250623001) - Warehouse
   Maintenance: Monthly (last: 2025-09-10), Bi-Annual (last: 2025-09-10), Annual (last: 2025-09-10)

Enter equipment name: Oil Free Air Compressor
Enter maintenance frequency: monthly
Enter completion date (YYYY-MM-DD) or press Enter for today: 2025-10-15

✓ Updated Oil Free Air Compressor monthly maintenance date to 2025-10-15
```

## Command-Line Method (Faster for Experienced Users)

If you know exactly what you want to update, you can do it in one command:

```bash
python update_maintenance_date.py "Equipment Name" frequency YYYY-MM-DD
```

**Examples:**

```bash
# Update monthly maintenance for Oil Free Air Compressor
python update_maintenance_date.py "Oil Free Air Compressor" monthly 2025-10-15

# Update bi-annual maintenance for Blockwise Crimper (with serial number)
python update_maintenance_date.py "Blockwise Crimper" bi_annual 2025-10-15 14024

# Update annual maintenance for Temperature controller
python update_maintenance_date.py "Temperature controller" annual 2025-10-15
```

## Important Notes

### Separate Dates for Each Frequency

Each maintenance type has its **own independent date**. This means:

- ✅ If you do **bi-annual** maintenance on October 15, 2025, only the bi-annual date is updated
- ✅ The **annual** maintenance date stays the same (e.g., still February 25, 2025)
- ✅ The **monthly** maintenance date stays the same

**Example Scenario:**
- Equipment: Temperature controller
- Last annual maintenance: February 25, 2025
- You do bi-annual maintenance: October 15, 2025
- Result:
  - Bi-annual date updated to: October 15, 2025 (next due: April 15, 2026)
  - Annual date stays: February 25, 2025 (next due: February 25, 2026)

### Date Format

Always use **YYYY-MM-DD** format:
- ✅ Correct: `2025-10-15`
- ❌ Wrong: `10/15/2025` or `10-15-2025`

### Finding Equipment Names

To see all available equipment, run:
```bash
python update_maintenance_date.py list
```

## Manual Method (Advanced)

If you prefer to edit the file directly, open `equipment_data.json` and find the equipment. Update the `last_maintenance_date` within the specific frequency section:

```json
{
  "equipment_name": "Oil Free Air Compressor",
  "maintenance_schedule": {
    "monthly": {
      "last_maintenance_date": "2025-10-15",  // ← Update this date
      "tasks": [...]
    },
    "bi_annual": {
      "last_maintenance_date": "2025-09-10",  // ← This stays separate
      "tasks": [...]
    }
  }
}
```

**⚠️ Warning:** Be careful with manual editing - make sure the JSON format is correct or the program won't work!

## Troubleshooting

**"Equipment not found" error:**
- Check the spelling of the equipment name (it's case-insensitive)
- If there are multiple equipment with the same name, provide the serial number

**"Invalid date format" error:**
- Use YYYY-MM-DD format (e.g., 2025-10-15)
- Don't use slashes or other formats

**"Frequency not found" error:**
- Use: `monthly`, `bi_annual`, or `annual`
- Check that the equipment actually has that maintenance frequency

## After Updating

Once you update a date:
1. The system will calculate the next due date automatically
2. Alerts will be sent when that next date arrives
3. You can run `python maintenance_checker.py` to see what's currently due

