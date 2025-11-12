"""
Utility script to update maintenance dates after maintenance is completed.
This ensures each maintenance frequency (monthly, bi-annual, annual) has its own independent date.
"""

import json
import sys
from datetime import datetime
from typing import Optional


def load_equipment_data(filename: str = "equipment_data.json") -> list:
    """Load equipment data from JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}!")
        sys.exit(1)


def save_equipment_data(data: list, filename: str = "equipment_data.json") -> None:
    """Save equipment data to JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Successfully updated {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)


def find_equipment(data: list, equipment_name: str, serial_number: Optional[str] = None) -> Optional[dict]:
    """Find equipment by name and optionally serial number."""
    for equipment in data:
        if equipment.get("equipment_name", "").lower() == equipment_name.lower():
            if serial_number is None:
                return equipment
            elif equipment.get("serial_number", "").lower() == serial_number.lower():
                return equipment
    return None


def list_equipment(data: list) -> None:
    """List all equipment with their details."""
    print("\n=== Available Equipment ===\n")
    for i, equipment in enumerate(data, 1):
        name = equipment.get("equipment_name", "Unknown")
        serial = equipment.get("serial_number", "N/A")
        location = equipment.get("location", "N/A")
        print(f"{i}. {name} (S/N: {serial}) - {location}")
        
        # Show maintenance frequencies
        schedule = equipment.get("maintenance_schedule", {})
        frequencies = []
        if "monthly" in schedule:
            last_date = schedule["monthly"].get("last_maintenance_date") or equipment.get("last_maintenance_date", "N/A")
            frequencies.append(f"Monthly (last: {last_date})")
        if "bi_annual" in schedule:
            last_date = schedule["bi_annual"].get("last_maintenance_date") or equipment.get("last_maintenance_date", "N/A")
            frequencies.append(f"Bi-Annual (last: {last_date})")
        if "annual" in schedule:
            last_date = schedule["annual"].get("last_maintenance_date") or equipment.get("last_maintenance_date", "N/A")
            frequencies.append(f"Annual (last: {last_date})")
        
        if frequencies:
            print(f"   Maintenance: {', '.join(frequencies)}")
        print()


def update_maintenance_date(
    equipment_name: str,
    frequency: str,
    date: str,
    serial_number: Optional[str] = None,
    filename: str = "equipment_data.json"
) -> bool:
    """
    Update the last maintenance date for a specific equipment and frequency.
    
    Args:
        equipment_name: Name of the equipment
        frequency: 'monthly', 'bi_annual', or 'annual'
        date: Date in YYYY-MM-DD format
        serial_number: Optional serial number to identify specific equipment
        filename: Path to equipment data file
    
    Returns:
        True if successful, False otherwise
    """
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2025-08-25)")
        return False
    
    # Validate frequency
    valid_frequencies = ["monthly", "bi_annual", "annual"]
    if frequency.lower() not in valid_frequencies:
        print(f"Error: Invalid frequency. Must be one of: {', '.join(valid_frequencies)}")
        return False
    
    # Load data
    data = load_equipment_data(filename)
    
    # Find equipment
    equipment = find_equipment(data, equipment_name, serial_number)
    if not equipment:
        print(f"Error: Equipment '{equipment_name}' not found!")
        if serial_number:
            print(f"   (with serial number: {serial_number})")
        print("\nAvailable equipment:")
        list_equipment(data)
        return False
    
    # Check if frequency exists in schedule
    maintenance_schedule = equipment.get("maintenance_schedule", {})
    if frequency.lower() not in maintenance_schedule:
        print(f"Error: Equipment '{equipment_name}' does not have {frequency} maintenance schedule!")
        return False
    
    # Update the date
    # Store frequency-specific date in the schedule
    maintenance_schedule[frequency.lower()]["last_maintenance_date"] = date
    
    # Also update the general last_maintenance_date if it's the only/maintenance type
    # (for backward compatibility)
    schedule_keys = list(maintenance_schedule.keys())
    if len(schedule_keys) == 1 and schedule_keys[0] == frequency.lower():
        equipment["last_maintenance_date"] = date
    
    # Save data
    save_equipment_data(data, filename)
    
    print(f"\n✓ Updated {equipment_name} {frequency} maintenance date to {date}")
    if serial_number:
        print(f"  (S/N: {serial_number})")
    
    return True


def interactive_update():
    """Interactive mode to update maintenance dates."""
    print("=== Equipment Maintenance Date Updater ===\n")
    
    data = load_equipment_data()
    list_equipment(data)
    
    # Get equipment name
    equipment_name = input("Enter equipment name: ").strip()
    if not equipment_name:
        print("Error: Equipment name is required!")
        return
    
    # Check if multiple equipment with same name
    matches = [eq for eq in data if eq.get("equipment_name", "").lower() == equipment_name.lower()]
    if len(matches) > 1:
        print(f"\nFound {len(matches)} equipment with name '{equipment_name}':")
        for i, eq in enumerate(matches, 1):
            print(f"  {i}. S/N: {eq.get('serial_number', 'N/A')} - {eq.get('location', 'N/A')}")
        
        serial_number = input("\nEnter serial number to specify: ").strip()
        if not serial_number:
            print("Error: Serial number required when multiple equipment match!")
            return
    else:
        serial_number = None
    
    # Get frequency
    print("\nAvailable frequencies: monthly, bi_annual, annual")
    frequency = input("Enter maintenance frequency: ").strip().lower()
    if not frequency:
        print("Error: Frequency is required!")
        return
    
    # Get date
    date = input("Enter completion date (YYYY-MM-DD) or press Enter for today: ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
        print(f"Using today's date: {date}")
    
    # Update
    update_maintenance_date(equipment_name, frequency, date, serial_number)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command-line mode
        if sys.argv[1] == "list":
            data = load_equipment_data()
            list_equipment(data)
        elif len(sys.argv) >= 4:
            # update_maintenance_date.py <equipment_name> <frequency> <date> [serial_number]
            equipment_name = sys.argv[1]
            frequency = sys.argv[2]
            date = sys.argv[3]
            serial_number = sys.argv[4] if len(sys.argv) > 4 else None
            update_maintenance_date(equipment_name, frequency, date, serial_number)
        else:
            print("Usage:")
            print("  python update_maintenance_date.py list")
            print("  python update_maintenance_date.py <equipment_name> <frequency> <date> [serial_number]")
            print("  python update_maintenance_date.py  (interactive mode)")
            print("\nExample:")
            print("  python update_maintenance_date.py 'Oil Free Air Compressor' monthly 2025-08-25")
            print("  python update_maintenance_date.py 'Blockwise Crimper' bi_annual 2025-08-25 14024")
    else:
        # Interactive mode
        interactive_update()


if __name__ == "__main__":
    main()

