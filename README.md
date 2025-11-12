# Equipment Maintenance Notification System

This program monitors equipment maintenance schedules and sends Slack notifications when maintenance is due.

## Features

- Tracks maintenance schedules (Monthly, Bi-Annual, Annual)
- Calculates due dates based on last maintenance date
- Sends formatted Slack notifications with equipment details and maintenance steps
- Supports multiple equipment items with different maintenance frequencies
- **Slack Bot Integration** - Update maintenance dates directly from Slack using `/maintenance` command

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Slack Webhook

1. Go to your Slack workspace
2. Create a new Slack App or use an existing one
3. Enable "Incoming Webhooks"
4. Create a webhook URL for the channel where you want notifications
5. Copy the webhook URL

### 3. Update Configuration

Edit `config.json` and add your Slack webhook URL:

```json
{
  "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "alert_days_before": 0,
  "check_frequency": "daily"
}
```

### 4. Update Equipment Data

Edit `equipment_data.json` to add or update equipment information. Each equipment entry should include:

- `equipment_name`: Name of the equipment
- `manufacturer`: Manufacturer name
- `model`: Model number
- `serial_number`: Serial number
- `location`: Location of the equipment
- `last_maintenance_date`: Last maintenance date in YYYY-MM-DD format
- `maintenance_schedule`: Object containing maintenance frequencies and tasks
  - `monthly`: Tasks performed monthly
  - `bi_annual`: Tasks performed every 6 months
  - `annual`: Tasks performed yearly

Example:
```json
{
  "equipment_name": "Blockwise Crimper",
  "manufacturer": "Blockwise",
  "model": "CX",
  "serial_number": "14024",
  "location": "Cleanroom",
  "last_maintenance_date": "2023-04-25",
  "maintenance_schedule": {
    "bi_annual": {
      "tasks": [
        "Clean the whole unit with Isopropyl alcohol",
        "Check for leaks, dust, rust and light indicators"
      ]
    }
  }
}
```

## Usage

### Run Continuously (Recommended)

Run the program continuously so it always checks for due maintenance:

**Windows:**
```bash
# Option 1: Double-click run_continuous.bat
# Option 2: Run from command prompt
python maintenance_checker.py --continuous
```

**Linux/Mac:**
```bash
# Option 1: Use the helper script
chmod +x run_continuous.sh
./run_continuous.sh

# Option 2: Run directly
python3 maintenance_checker.py --continuous
```

This will:
- Run continuously in the background
- Check for due maintenance every 24 hours (configurable in `config.json`)
- Automatically reload equipment data to pick up any updates
- Use the current date/time for all checks (always knows the current date)
- Show timestamps for all operations
- Restart automatically if an error occurs

**To stop:** Press `Ctrl+C`

**To change check frequency:** Edit `check_interval_hours` in `config.json` (e.g., `12` for every 12 hours, `1` for hourly)

### Run Once (Single Check)

For a one-time check:

```bash
python maintenance_checker.py
```

### Schedule Regular Checks (Alternative)

#### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 9:00 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\maintenance_checker.py`
7. Start in: `C:\path\to\project\directory`

#### Linux/Mac Cron

Add to crontab (`crontab -e`):

```bash
# Run daily at 9:00 AM
0 9 * * * cd /path/to/project && /usr/bin/python3 maintenance_checker.py
```

## How It Works

1. The program reads equipment data from `equipment_data.json`
2. For each equipment item, it calculates the next due date based on:
   - Last maintenance date
   - Maintenance frequency (Monthly = 1 month, Bi-Annual = 6 months, Annual = 1 year)
3. If today's date is on or past the due date, it's flagged as due
4. All due maintenance items are formatted into a Slack message
5. The notification is sent to the configured Slack channel

## Notification Format

Slack notifications include:
- Equipment name and serial number
- Location
- Maintenance frequency (Monthly/Bi-Annual/Annual)
- List of maintenance steps/tasks

## Updating Last Maintenance Date

**📖 For detailed instructions, see [HOW_TO_UPDATE_DATES.md](HOW_TO_UPDATE_DATES.md)**

### Quick Method (Recommended)

Simply run the update script and follow the prompts:

```bash
python update_maintenance_date.py
```

The script will:
1. Show you all available equipment
2. Ask which equipment you worked on
3. Ask which maintenance type (monthly/bi-annual/annual)
4. Ask for the completion date (or use today if you press Enter)

### Command-Line Method (Faster)

```bash
python update_maintenance_date.py "Equipment Name" frequency YYYY-MM-DD

# Examples:
python update_maintenance_date.py "Oil Free Air Compressor" monthly 2025-10-15
python update_maintenance_date.py "Blockwise Crimper" bi_annual 2025-10-15 14024
```

**Important:** Each maintenance frequency has its own independent date. Updating bi-annual maintenance does NOT affect the annual maintenance date.

## Troubleshooting

- **No notifications received**: Check that the Slack webhook URL is correct in `config.json`
- **Wrong due dates**: Verify `last_maintenance_date` is in YYYY-MM-DD format
- **Missing equipment**: Ensure all equipment is properly formatted in `equipment_data.json`

