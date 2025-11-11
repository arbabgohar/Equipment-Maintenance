"""
Equipment Maintenance Notification System
Checks for due maintenance and sends Slack notifications
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from dateutil.relativedelta import relativedelta


class MaintenanceChecker:
    def __init__(self, equipment_file: str = "equipment_data.json", config_file: str = "config.json"):
        """Initialize the maintenance checker with equipment data and configuration."""
        self.equipment_file = equipment_file
        self.config_file = config_file
        self.equipment_list = self._load_equipment_data()
        self.config = self._load_config()
        
    def _load_equipment_data(self) -> List[Dict[str, Any]]:
        """Load equipment data from JSON file."""
        try:
            with open(self.equipment_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.equipment_file} not found!")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.equipment_file}!")
            return []
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {self.config_file} not found. Using default configuration.")
            return {
                "slack_webhook_url": "",
                "alert_days_before": 0,
                "check_frequency": "daily"
            }
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.config_file}!")
            return {}
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in YYYY-MM-DD format."""
        return datetime.strptime(date_str, "%Y-%m-%d")
    
    def _calculate_next_due_date(self, last_date: datetime, frequency: str) -> datetime:
        """Calculate the next due date based on frequency."""
        if frequency == "monthly":
            return last_date + relativedelta(months=1)
        elif frequency == "bi_annual":
            return last_date + relativedelta(months=6)
        elif frequency == "annual":
            return last_date + relativedelta(years=1)
        else:
            raise ValueError(f"Unknown frequency: {frequency}")
    
    def _is_due(self, last_date_str: str, frequency: str) -> bool:
        """Check if maintenance is due based on last maintenance date and frequency."""
        try:
            last_date = self._parse_date(last_date_str)
            next_due_date = self._calculate_next_due_date(last_date, frequency)
            today = datetime.now().date()
            
            # Check if today is on or past the due date
            return today >= next_due_date.date()
        except Exception as e:
            print(f"Error checking due date: {e}")
            return False
    
    def _get_due_maintenance(self) -> List[Dict[str, Any]]:
        """Get list of equipment with due maintenance."""
        due_items = []
        
        for equipment in self.equipment_list:
            maintenance_schedule = equipment.get("maintenance_schedule", {})
            
            # Check bi-annual maintenance
            if "bi_annual" in maintenance_schedule:
                # Try to get frequency-specific last maintenance date, fall back to general one
                last_maintenance = maintenance_schedule["bi_annual"].get("last_maintenance_date") or equipment.get("last_maintenance_date")
                if last_maintenance and self._is_due(last_maintenance, "bi_annual"):
                    due_items.append({
                        "equipment": equipment,
                        "frequency": "Bi-Annual",
                        "tasks": maintenance_schedule["bi_annual"]["tasks"]
                    })
            
            # Check annual maintenance
            if "annual" in maintenance_schedule:
                # Try to get frequency-specific last maintenance date, fall back to general one
                last_maintenance = maintenance_schedule["annual"].get("last_maintenance_date") or equipment.get("last_maintenance_date")
                if last_maintenance and self._is_due(last_maintenance, "annual"):
                    due_items.append({
                        "equipment": equipment,
                        "frequency": "Annual",
                        "tasks": maintenance_schedule["annual"]["tasks"]
                    })
            
            # Check monthly maintenance
            if "monthly" in maintenance_schedule:
                # Try to get frequency-specific last maintenance date, fall back to general one
                last_maintenance = maintenance_schedule["monthly"].get("last_maintenance_date") or equipment.get("last_maintenance_date")
                if last_maintenance and self._is_due(last_maintenance, "monthly"):
                    due_items.append({
                        "equipment": equipment,
                        "frequency": "Monthly",
                        "tasks": maintenance_schedule["monthly"]["tasks"]
                    })
        
        return due_items
    
    def _format_slack_message(self, due_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format the maintenance due items into a Slack message."""
        if not due_items:
            return None
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️ Equipment Maintenance Due"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for item in due_items:
            equipment = item["equipment"]
            frequency = item["frequency"]
            tasks = item["tasks"]
            
            # Equipment header
            equipment_text = f"*{equipment['equipment_name']}*"
            if equipment.get('serial_number'):
                equipment_text += f" (S/N: {equipment['serial_number']})"
            if equipment.get('location'):
                equipment_text += f" - {equipment['location']}"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": equipment_text
                }
            })
            
            # Frequency
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Frequency:* {frequency}"
                }
            })
            
            # Tasks
            tasks_text = "*Maintenance Steps:*\n"
            for i, task in enumerate(tasks, 1):
                tasks_text += f"{i}. {task}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": tasks_text
                }
            })
            
            blocks.append({
                "type": "divider"
            })
        
        return {
            "blocks": blocks
        }
    
    def _send_slack_notification(self, message: Dict[str, Any]) -> bool:
        """Send notification to Slack via webhook."""
        webhook_url = self.config.get("slack_webhook_url")
        
        if not webhook_url:
            print("Warning: Slack webhook URL not configured. Skipping notification.")
            return False
        
        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()
            print("Slack notification sent successfully!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending Slack notification: {e}")
            return False
    
    def check_and_notify(self) -> None:
        """Main method to check for due maintenance and send notifications."""
        print(f"Checking maintenance due dates... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        
        due_items = self._get_due_maintenance()
        
        if not due_items:
            print("No maintenance due at this time.")
            return
        
        print(f"Found {len(due_items)} equipment item(s) with due maintenance.")
        
        # Format and send Slack message
        slack_message = self._format_slack_message(due_items)
        if slack_message:
            self._send_slack_notification(slack_message)
        
        # Also print to console
        print("\n=== Maintenance Due ===")
        for item in due_items:
            equipment = item["equipment"]
            print(f"\nEquipment: {equipment['equipment_name']}")
            print(f"Frequency: {item['frequency']}")
            print(f"Location: {equipment.get('location', 'N/A')}")
            print("Tasks:")
            for i, task in enumerate(item['tasks'], 1):
                print(f"  {i}. {task}")


def main():
    """Main entry point."""
    checker = MaintenanceChecker()
    checker.check_and_notify()


if __name__ == "__main__":
    main()

