"""
Slack Bot Server for Equipment Maintenance Updates
Allows users to update maintenance dates via Slack commands
"""

from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime

# Import functions from update_maintenance_date module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from update_maintenance_date import (
    load_equipment_data,
    save_equipment_data,
    find_equipment,
    update_maintenance_date as update_date
)
from excel_updater import update_excel_maintenance

app = Flask(__name__)

# Load configuration
def load_config():
    try:
        with open("config.json", 'r') as f:
            return json.load(f)
    except:
        return {}

config = load_config()
SLACK_VERIFICATION_TOKEN = config.get("slack_verification_token", "")


def parse_slack_message(text: str) -> dict:
    """
    Parse Slack message text to extract equipment name/S/N, date, and optional initials.
    Expected format: "equipment_name frequency YYYY-MM-DD [initials]" or "S/N: serial_number frequency YYYY-MM-DD [initials]"
    """
    text = text.strip()
    
    # Handle quoted equipment names
    if text.startswith('"'):
        # Find the closing quote
        end_quote = text.find('"', 1)
        if end_quote > 0:
            equipment_name = text[1:end_quote]  # Extract name without quotes
            remaining = text[end_quote + 1:].strip()
        else:
            # No closing quote, treat as normal
            parts = text.split()
            equipment_name = None
            remaining = text
    else:
        equipment_name = None
        remaining = text
    
    # Parse the remaining parts
    parts = remaining.split()
    if len(parts) < 2:
        return None
    
    # Try to find frequency and date
    frequency = None
    date = None
    initials = None
    
    for i, part in enumerate(parts):
        part_lower = part.lower()
        if part_lower in ["monthly", "bi_annual", "annual", "bi-annual"]:
            frequency = part_lower.replace("-", "_")
        elif len(part) == 10 and part.count("-") == 2:  # Date format YYYY-MM-DD
            date = part
        elif i == len(parts) - 1 and len(part) <= 5 and part.isalnum():
            # Last part that's short and alphanumeric is likely initials
            initials = part.upper()
    
    if not frequency or not date:
        return None
    
    # If we didn't get equipment name from quotes, check for S/N format
    serial_number = None
    if not equipment_name:
        # Check if it starts with S/N:
        if remaining.upper().startswith("S/N:") or remaining.upper().startswith("SN:"):
            s_n_part = remaining.split()[0]
            if ":" in s_n_part:
                serial_number = s_n_part.split(":", 1)[1].strip()
            else:
                # S/N: is separate, get next part
                remaining_parts = remaining.split()
                if len(remaining_parts) > 1:
                    serial_number = remaining_parts[1]
        else:
            # Try to extract equipment name from remaining parts (before frequency)
            name_parts = []
            for part in parts:
                if part.lower() in ["monthly", "bi_annual", "annual", "bi-annual"]:
                    break
                if len(part) == 10 and part.count("-") == 2:
                    break
                name_parts.append(part)
            if name_parts:
                equipment_name = " ".join(name_parts)
    
    return {
        "equipment_name": equipment_name.strip() if equipment_name else None,
        "serial_number": serial_number.strip() if serial_number else None,
        "frequency": frequency,
        "date": date,
        "initials": initials
    }


def find_equipment_by_name_or_sn(equipment_name: str = None, serial_number: str = None):
    """Find equipment by name or serial number."""
    data = load_equipment_data()
    
    if serial_number:
        serial_number = serial_number.strip()
        for eq in data:
            eq_sn = str(eq.get("serial_number", "")).strip().lower()
            if eq_sn == serial_number.lower():
                return eq
    elif equipment_name:
        equipment_name = equipment_name.strip()
        # Remove quotes if present
        if equipment_name.startswith('"') and equipment_name.endswith('"'):
            equipment_name = equipment_name[1:-1]
        
        # Try exact match first
        for eq in data:
            eq_name = str(eq.get("equipment_name", "")).strip().lower()
            if eq_name == equipment_name.lower():
                return eq
        
        # Try partial match
        for eq in data:
            eq_name = str(eq.get("equipment_name", "")).strip().lower()
            if equipment_name.lower() in eq_name or eq_name in equipment_name.lower():
                return eq
    
    return None


@app.route('/slack/command', methods=['POST'])
def slack_command():
    """Handle Slack slash command."""
    # Verify token (optional but recommended)
    token = request.form.get('token')
    if SLACK_VERIFICATION_TOKEN and token != SLACK_VERIFICATION_TOKEN:
        return jsonify({"text": "Invalid token"}), 403
    
    text = request.form.get('text', '').strip()
    user_name = request.form.get('user_name', 'Unknown')
    channel = request.form.get('channel_name', '')
    
    # Handle list command
    if text.lower() == 'list':
        data = load_equipment_data()
        if not data:
            return jsonify({
                "response_type": "ephemeral",
                "text": "No equipment found."
            })
        
        text_response = "*Available Equipment:*\n\n"
        for i, eq in enumerate(data[:20], 1):  # Limit to 20 for Slack
            name = eq.get("equipment_name", "Unknown")
            sn = eq.get("serial_number", "N/A")
            location = eq.get("location", "N/A")
            text_response += f"{i}. *{name}*\n   S/N: {sn} | Location: {location}\n\n"
        
        if len(data) > 20:
            text_response += f"\n_Showing 20 of {len(data)} equipment. Use more specific search._"
        
        return jsonify({
            "response_type": "ephemeral",
            "text": text_response
        })
    
    # Handle status command - show equipment with maintenance dates
    if text.lower() in ['status', 'dates', 'maintenance dates']:
        data = load_equipment_data()
        if not data:
            return jsonify({
                "response_type": "ephemeral",
                "text": "No equipment found."
            })
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Equipment Maintenance Status"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for eq in data[:15]:  # Limit to 15 for Slack blocks
            name = eq.get("equipment_name", "Unknown")
            sn = eq.get("serial_number", "N/A")
            location = eq.get("location", "N/A")
            schedule = eq.get("maintenance_schedule", {})
            
            # Build maintenance dates text
            dates_text = ""
            if "monthly" in schedule:
                last_date = schedule["monthly"].get("last_maintenance_date") or eq.get("last_maintenance_date", "N/A")
                try:
                    date_obj = datetime.strptime(last_date, "%Y-%m-%d")
                    formatted = date_obj.strftime("%b %d, %Y")
                except:
                    formatted = last_date
                dates_text += f"*Monthly:* {formatted}\n"
            
            if "bi_annual" in schedule:
                last_date = schedule["bi_annual"].get("last_maintenance_date") or eq.get("last_maintenance_date", "N/A")
                try:
                    date_obj = datetime.strptime(last_date, "%Y-%m-%d")
                    formatted = date_obj.strftime("%b %d, %Y")
                except:
                    formatted = last_date
                dates_text += f"*Bi-Annual:* {formatted}\n"
            
            if "annual" in schedule:
                last_date = schedule["annual"].get("last_maintenance_date") or eq.get("last_maintenance_date", "N/A")
                try:
                    date_obj = datetime.strptime(last_date, "%Y-%m-%d")
                    formatted = date_obj.strftime("%b %d, %Y")
                except:
                    formatted = last_date
                dates_text += f"*Annual:* {formatted}\n"
            
            if not dates_text:
                dates_text = "No maintenance schedule"
            
            equipment_text = f"*{name}*\n"
            equipment_text += f"S/N: {sn} | Location: {location}\n\n"
            equipment_text += dates_text
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": equipment_text
                }
            })
            blocks.append({
                "type": "divider"
            })
        
        if len(data) > 15:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Showing 15 of {len(data)} equipment._"
                }
            })
        
        return jsonify({
            "response_type": "ephemeral",
            "blocks": blocks
        })
    
    if not text:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Usage:\n"
                   "• `/maintenance list` - List all equipment\n"
                   "• `/maintenance status` - List equipment with maintenance dates\n"
                   "• `/maintenance \"Equipment Name\" frequency YYYY-MM-DD [initials]` - Update date\n"
                   "• `/maintenance S/N: serial_number frequency YYYY-MM-DD [initials]` - Update by S/N\n\n"
                   "Examples:\n"
                   "`/maintenance \"Oil Free Air Compressor\" monthly 2025-11-15 AG`\n"
                   "`/maintenance S/N: 20250623001 bi_annual 2025-11-15 SJ`\n"
                   "`/maintenance \"Temperature controller\" annual 2025-11-15` (uses Slack username if no initials)\n\n"
                   "Frequencies: monthly, bi_annual, annual\n"
                   "Initials: Optional 2-5 character initials (e.g., AG, SJ, AA)"
        })
    
    # Parse the message
    parsed = parse_slack_message(text)
    
    if not parsed:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Invalid format. Use: `<equipment_name> <frequency> <YYYY-MM-DD>`\n"
                   "Example: `Oil Free Air Compressor monthly 2025-11-15`"
        })
    
    # Find equipment
    equipment = find_equipment_by_name_or_sn(
        parsed["equipment_name"],
        parsed["serial_number"]
    )
    
    if not equipment:
        search_term = parsed["serial_number"] if parsed["serial_number"] else parsed["equipment_name"]
        return jsonify({
            "response_type": "ephemeral",
            "text": f"Equipment not found: {search_term}\n"
                   "Use `/maintenance list` to see all equipment."
        })
    
    # Update the date
    equipment_name = equipment.get("equipment_name")
    serial_number = equipment.get("serial_number")
    
    success = update_date(
        equipment_name,
        parsed["frequency"],
        parsed["date"],
        serial_number
    )
    
    if success:
        # Get initials from parsed message or use username
        user_initials = parsed.get('initials') or user_name
        
        # Update Excel file for all frequencies
        excel_result = update_excel_maintenance(
            equipment_name=equipment_name,
            serial_number=serial_number or "",
            frequency=parsed['frequency'],
            date=parsed['date'],
            user_name=user_initials
        )
        
        # Build response message
        response_text = f"*Maintenance Updated*\n"
        response_text += f"*Equipment:* {equipment_name}\n"
        response_text += f"*Serial Number:* {serial_number or 'N/A'}\n"
        response_text += f"*Frequency:* {parsed['frequency'].replace('_', '-').title()}\n"
        response_text += f"*Date:* {parsed['date']}\n"
        response_text += f"*Updated by:* {user_initials}"
        
        if excel_result:
            if excel_result['success']:
                response_text += f"\n*Excel:* Updated successfully"
            else:
                response_text += f"\n*Excel:* {excel_result['message']}"
        
        return jsonify({
            "response_type": "in_channel",
            "text": f"Maintenance updated by @{user_name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response_text
                    }
                }
            ]
        })
    else:
        return jsonify({
            "response_type": "ephemeral",
            "text": "Failed to update maintenance date. Please check the format."
        })


@app.route('/slack/list', methods=['POST'])
def slack_list():
    """List all equipment."""
    token = request.form.get('token')
    if SLACK_VERIFICATION_TOKEN and token != SLACK_VERIFICATION_TOKEN:
        return jsonify({"text": "Invalid token"}), 403
    
    data = load_equipment_data()
    
    if not data:
        return jsonify({
            "response_type": "ephemeral",
            "text": "No equipment found."
        })
    
    text = "*Available Equipment:*\n\n"
    for i, eq in enumerate(data[:20], 1):  # Limit to 20 for Slack
        name = eq.get("equipment_name", "Unknown")
        sn = eq.get("serial_number", "N/A")
        location = eq.get("location", "N/A")
        text += f"{i}. *{name}*\n   S/N: {sn} | Location: {location}\n\n"
    
    if len(data) > 20:
        text += f"\n_Showing 20 of {len(data)} equipment. Use more specific search._"
    
    return jsonify({
        "response_type": "ephemeral",
        "text": text
    })


@app.route('/slack/interactive', methods=['POST'])
def slack_interactive():
    """Handle Slack interactive components (buttons, etc.)."""
    payload = json.loads(request.form.get('payload', '{}'))
    
    # Handle button clicks or other interactions here
    # For now, just acknowledge
    return jsonify({"text": "OK"})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "equipment-maintenance-slack-bot"})


if __name__ == '__main__':
    print("Starting Slack Bot Server...")
    print("Make sure to configure Slack slash command to point to this server")
    print("URL should be: http://your-server:5000/slack/command")
    app.run(host='0.0.0.0', port=5000, debug=True)

