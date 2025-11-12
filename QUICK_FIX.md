# Quick Fix for "dispatch_failed" Error

## The Problem
Slack can't reach your server. This usually means:
1. The Request URL is wrong
2. The server isn't running
3. The endpoint path is incorrect

## Step-by-Step Fix

### 1. Verify Your Server is Running
Check the window where you ran `python slack_bot_server.py`. It should show:
```
Running on http://127.0.0.1:5000
```

If it's not running, start it:
```bash
python slack_bot_server.py
```

### 2. Test the Health Endpoint
Open a browser and go to:
```
https://funk-mpegs-strictly-happy.trycloudflare.com/health
```

You should see: `{"status":"ok","service":"equipment-maintenance-slack-bot"}`

If you see "Not Found" or an error, the tunnel isn't working.

### 3. Check Slack Command Configuration
1. Go to https://api.slack.com/apps
2. Select your app → "Slash Commands"
3. Edit `/maintenance`
4. **Request URL MUST be exactly:**
   ```
   https://funk-mpegs-strictly-happy.trycloudflare.com/slack/command
   ```
   - Must be HTTPS (not HTTP)
   - Must end with `/slack/command`
   - No trailing slash

### 4. Verify Cloudflare Tunnel is Running
Check the cloudflared window. It should show:
- The tunnel URL: `https://funk-mpegs-strictly-happy.trycloudflare.com`
- "Registered tunnel connection"

### 5. Test the Endpoint Directly
Run this test script:
```bash
python test_slack_endpoint.py
```

This will tell you if your server is working.

### 6. Check Server Logs
Look at the `slack_bot_server.py` window. When you try the command in Slack, you should see a request come in. If you don't see anything, Slack isn't reaching your server.

## Common Issues

### Issue: Health endpoint works but Slack command doesn't
**Solution:** Make sure the Request URL ends with `/slack/command` (not just `/`)

### Issue: Nothing appears in server logs
**Solution:** 
- Cloudflare tunnel might not be forwarding correctly
- Try restarting cloudflared
- Make sure both services are running

### Issue: Server shows errors
**Solution:** Check the error message in the server window and fix the issue

## Still Not Working?

1. **Restart everything:**
   - Stop cloudflared (Ctrl+C)
   - Stop slack_bot_server.py (Ctrl+C)
   - Start slack_bot_server.py first
   - Then start cloudflared
   - Get the new URL from cloudflared
   - Update Slack with the new URL

2. **Check firewall/antivirus:**
   - Make sure nothing is blocking port 5000
   - Windows Firewall might be blocking

3. **Try a different approach:**
   - Use Railway or Render for a permanent URL (see ALTERNATIVES_TO_NGROK.md)

