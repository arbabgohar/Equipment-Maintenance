# Alternatives to ngrok for Slack Integration

Since you can't install ngrok, here are several alternatives:

## Option 1: Use Cloudflare Tunnel (Cloudflared) - FREE & Easy

Cloudflare Tunnel is free and doesn't require installation (portable executable).

### Steps:
1. Download cloudflared from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   - Or direct download: https://github.com/cloudflare/cloudflared/releases
   - Download the Windows executable

2. Run it (no installation needed):
   ```bash
   cloudflared tunnel --url http://localhost:5000
   ```

3. It will give you a URL like: `https://random-name.trycloudflare.com`
   - Use this URL in your Slack slash command

**Advantages:**
- No installation required (just download and run)
- Free
- Works immediately

## Option 2: Use localtunnel (Node.js based)

If you have Node.js installed:

```bash
npm install -g localtunnel
lt --port 5000
```

This gives you a public URL.

## Option 3: Deploy to Free Cloud Service (Best for Production)

### Railway (Recommended - Very Easy)
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your Equipment-Maintenance repo
5. Railway auto-detects Flask and deploys
6. Get your public URL from Railway dashboard
7. Use that URL in Slack

### Render (Also Easy)
1. Go to https://render.com
2. Sign up
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python slack_bot_server.py`
6. Deploy and get public URL

### Fly.io (Another Option)
1. Go to https://fly.io
2. Install flyctl: `powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"`
3. Run: `fly launch`
4. Follow prompts
5. Get your URL

## Option 4: Use Your Own Server/VPS

If you have a server with a public IP:
1. Deploy the bot server there
2. Use your server's public IP/domain
3. Make sure port 5000 is open

## Option 5: Simplified Approach - Manual Updates Only

If Slack integration is too complex right now, you can:
- Keep using the `update_maintenance_date.py` script
- Or create a simple web form that runs locally
- Users update dates manually via the script

## Recommendation

**For quick testing:** Use Cloudflare Tunnel (Option 1) - it's the easiest and requires no installation.

**For production:** Use Railway or Render (Option 3) - they're free, easy, and give you a permanent URL.

