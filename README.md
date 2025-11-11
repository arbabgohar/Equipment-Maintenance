# Equipment Maintenance Notification System

This program monitors equipment maintenance schedules and sends Slack notifications when maintenance is due.

## Features

- Tracks maintenance schedules (Monthly, Bi-Annual, Annual)
- Calculates due dates based on last maintenance date
- Sends formatted Slack notifications with equipment details and maintenance steps
- Supports multiple equipment items with different maintenance frequencies

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

### Run Once

```bash
python maintenance_checker.py
```

### Schedule Regular Checks

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

After completing maintenance, update the `last_maintenance_date` field in `equipment_data.json` to the completion date (YYYY-MM-DD format).

## Troubleshooting

- **No notifications received**: Check that the Slack webhook URL is correct in `config.json`
- **Wrong due dates**: Verify `last_maintenance_date` is in YYYY-MM-DD format
- **Missing equipment**: Ensure all equipment is properly formatted in `equipment_data.json`

