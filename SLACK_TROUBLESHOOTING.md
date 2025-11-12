# Slack Integration Troubleshooting

If `/maintenance` command is not working in Slack, check these:

## Step 1: Verify Server is Running

Run the test script:
```bash
python test_slack_endpoint.py
```

This will verify your server is responding correctly.

## Step 2: Check Slack App Installation

**CRITICAL:** The app must be **installed to your workspace**!

1. Go to https://api.slack.com/apps
2. Select your "Maintenance" app
3. Click **"Install App"** in the left sidebar
4. Click **"Install to Workspace"**
5. Authorize the app
6. You should see "Success! Your app has been installed"

**If you skip this step, the slash command won't work!**

## Step 3: Verify Slash Command Configuration

1. In your Slack app, go to "Slash Commands"
2. Click on `/maintenance` to edit it
3. Check the **Request URL**:
   - Should be: `https://tournament-syracuse-subsequent-distribution.trycloudflare.com/slack/command`
   - Make sure it's HTTPS (not HTTP)
   - Make sure it ends with `/slack/command`
4. Click "Save Changes"

## Step 4: Test the Endpoint Directly

Open a browser and go to:
```
https://tournament-syracuse-subsequent-distribution.trycloudflare.com/health
```

You should see: `{"status":"ok","service":"equipment-maintenance-slack-bot"}`

If this doesn't work, your Cloudflare tunnel might not be running or the URL changed.

## Step 5: Check Slack App Permissions

1. Go to "OAuth & Permissions" in your Slack app
2. Under "Scopes" → "Bot Token Scopes", make sure you have:
   - `commands` (for slash commands)
   - `chat:write` (to send messages)
3. If you added scopes, you may need to **reinstall the app** to your workspace

## Step 6: Reinstall the App

Sometimes you need to reinstall after making changes:

1. Go to "Install App"
2. Click "Reinstall to Workspace"
3. Authorize again

## Step 7: Check Slack Logs

1. In your Slack app, go to "Event Subscriptions" (if enabled)
2. Or check the "Activity" tab to see if requests are coming through

## Common Issues

### "Command not found" or "is not a valid command"
- **Solution:** App is not installed to workspace (see Step 2)

### "Timeout" or no response
- **Solution:** Check that both cloudflared and slack_bot_server.py are running
- Verify the Request URL is correct
- Test the health endpoint (Step 4)

### "Invalid token" error
- **Solution:** Add `slack_verification_token` to config.json (optional but recommended)

### Command works but returns error
- Check the server logs in the slack_bot_server.py window
- Verify equipment_data.json exists and is valid JSON

## Quick Test Checklist

- [ ] slack_bot_server.py is running (shows "Running on http://127.0.0.1:5000")
- [ ] cloudflared is running (shows tunnel URL)
- [ ] Health endpoint works: `https://your-tunnel-url/health`
- [ ] App is installed to workspace (Step 2)
- [ ] Slash command Request URL is correct
- [ ] App has required permissions
- [ ] Tried `/maintenance list` in Slack

## Still Not Working?

1. Check the slack_bot_server.py window for error messages
2. Check the cloudflared window for connection issues
3. Try restarting both services
4. Make sure you're using the correct Slack workspace where the app is installed

