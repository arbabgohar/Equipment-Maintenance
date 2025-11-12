# Slack Bot Setup Guide

This guide will help you set up Slack integration so users can update maintenance dates directly from Slack.

## Features

Users can update maintenance dates by sending commands in Slack:
- `/maintenance "Equipment Name" monthly 2025-11-15`
- `/maintenance S/N: 20250623001 bi_annual 2025-11-15`
- `/maintenance list` - See all equipment

## Setup Steps

### 1. Install Additional Dependencies

```bash
pip install flask
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

### 2. Set Up Slack Slash Command

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "Equipment Maintenance")
4. Select your workspace
5. Go to "Slash Commands" in the left sidebar
6. Click "Create New Command"
7. Fill in:
   - **Command:** `/maintenance`
   - **Request URL:** `http://your-server-ip:5000/slack/command`
     - For local testing: Use ngrok (see below)
     - For production: Use your server's public IP/domain
   - **Short Description:** Update equipment maintenance dates
   - **Usage Hint:** `"Equipment Name" frequency YYYY-MM-DD`
8. Click "Save"

### 3. Get Verification Token (Optional but Recommended)

1. In your Slack app settings, go to "Basic Information"
2. Under "App Credentials", copy the "Verification Token"
3. Add it to `config.json`:
   ```json
   {
     "slack_webhook_url": "...",
     "slack_verification_token": "your-verification-token-here",
     ...
   }
   ```

### 4. Expose Your Server (For Local Development)

**Option A: Cloudflare Tunnel (Recommended - No Installation)**

1. Download cloudflared from: https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
2. Rename it to `cloudflared.exe` and place it in your project folder
3. Start your bot server:
   ```bash
   python slack_bot_server.py
   ```
4. In another terminal, run:
   ```bash
   cloudflared.exe tunnel --url http://localhost:5000
   ```
   Or double-click `setup_cloudflare_tunnel.bat`
5. Copy the HTTPS URL (e.g., `https://random-name.trycloudflare.com`)
6. Use this URL in your Slack slash command

**Option B: ngrok (If Available)**

1. Install ngrok: https://ngrok.com/download
2. Run: `ngrok http 5000`
3. Use the HTTPS URL in Slack

**Option C: Deploy to Cloud (Best for Production)**

See `ALTERNATIVES_TO_NGROK.md` for Railway, Render, or Fly.io deployment options.

### 5. Run the Bot Server

**Option A: Run separately (Recommended)**
```bash
# Terminal 1: Run the maintenance checker
python maintenance_checker.py --continuous

# Terminal 2: Run the Slack bot server
python slack_bot_server.py
```

**Option B: Run as Windows Service (Production)**

For production, you'll want to run both as services. See production deployment guide.

## Usage Examples

### Update by Equipment Name
```
/maintenance "Oil Free Air Compressor" monthly 2025-11-15
```

### Update by Serial Number
```
/maintenance S/N: 20250623001 bi_annual 2025-11-15
```

### List All Equipment
```
/maintenance list
```

## Command Format

```
/maintenance <equipment_identifier> <frequency> <date>
```

- **equipment_identifier:** Equipment name (in quotes if spaces) OR `S/N: <serial_number>`
- **frequency:** `monthly`, `bi_annual`, or `annual`
- **date:** `YYYY-MM-DD` format (e.g., `2025-11-15`)

## Troubleshooting

### "Invalid token" error
- Make sure you added `slack_verification_token` to `config.json`
- Or remove token verification from the code (less secure)

### "Equipment not found"
- Use `/maintenance list` to see all equipment names
- Make sure equipment name matches exactly (case-insensitive)
- Or use serial number format: `S/N: <serial_number>`

### Server not receiving requests
- Check that ngrok is running (for local development)
- Verify the Request URL in Slack app settings matches your server
- Check firewall settings if using a server

## Security Notes

- The verification token helps ensure requests come from Slack
- For production, use HTTPS (ngrok provides this)
- Consider adding IP whitelisting for additional security
- Store sensitive tokens securely (not in git)

## Production Deployment

For production, you'll want to:
1. Deploy the bot server on a cloud service (AWS, Azure, Heroku, etc.)
2. Set up proper domain/SSL certificate
3. Run both services as daemons/services
4. Set up monitoring and logging
5. Use environment variables for sensitive data

