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
    Parse Slack message text to extract equipment name/S/N and date.
    Expected format: "equipment_name frequency YYYY-MM-DD" or "S/N: serial_number frequency YYYY-MM-DD"
    """
    parts = text.strip().split()
    if len(parts) < 3:
        return None
    
    # Try to find frequency
    frequency = None
    date = None
    equipment_input = []
    
    for part in parts:
        part_lower = part.lower()
        if part_lower in ["monthly", "bi_annual", "annual", "bi-annual"]:
            frequency = part_lower.replace("-", "_")
        elif len(part) == 10 and part.count("-") == 2:  # Date format YYYY-MM-DD
            date = part
        else:
            equipment_input.append(part)
    
    if not frequency or not date:
        return None
    
    # Check if it's a serial number format
    equipment_name = " ".join(equipment_input)
    serial_number = None
    
    # Check for "S/N:" prefix
    if equipment_input[0].upper() in ["S/N:", "SN:", "SERIAL:"]:
        serial_number = " ".join(equipment_input[1:])
        equipment_name = None
    elif equipment_input[0].upper().startswith("S/N:"):
        serial_number = equipment_input[0][4:].strip()
        equipment_name = " ".join(equipment_input[1:]) if len(equipment_input) > 1 else None
    
    return {
        "equipment_name": equipment_name if equipment_name else None,
        "serial_number": serial_number,
        "frequency": frequency,
        "date": date
    }


def find_equipment_by_name_or_sn(equipment_name: str = None, serial_number: str = None):
    """Find equipment by name or serial number."""
    data = load_equipment_data()
    
    if serial_number:
        for eq in data:
            if eq.get("serial_number", "").lower() == serial_number.lower():
                return eq
    elif equipment_name:
        # Try exact match first
        for eq in data:
            if eq.get("equipment_name", "").lower() == equipment_name.lower():
                return eq
        # Try partial match
        for eq in data:
            if equipment_name.lower() in eq.get("equipment_name", "").lower():
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
                   "• `/maintenance \"Equipment Name\" frequency YYYY-MM-DD` - Update date\n"
                   "• `/maintenance S/N: serial_number frequency YYYY-MM-DD` - Update by S/N\n\n"
                   "Examples:\n"
                   "`/maintenance \"Oil Free Air Compressor\" monthly 2025-11-15`\n"
                   "`/maintenance S/N: 20250623001 bi_annual 2025-11-15`\n\n"
                   "Frequencies: monthly, bi_annual, annual"
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
        return jsonify({
            "response_type": "in_channel",
            "text": f"Maintenance updated by @{user_name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Maintenance Updated*\n"
                               f"*Equipment:* {equipment_name}\n"
                               f"*Serial Number:* {serial_number or 'N/A'}\n"
                               f"*Frequency:* {parsed['frequency'].replace('_', '-').title()}\n"
                               f"*Date:* {parsed['date']}"
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

