#!/usr/bin/env python3

import sys
import platform
import subprocess

def check_python_version(min_version=(3, 8)):
    """Checks if the current Python version meets the minimum requirement."""
    print(f"[INFO] Checking Python version (Required: {'.'.join(map(str, min_version))}+)")
    current_version = sys.version_info
    if current_version >= min_version:
        print(f"[SUCCESS] Current Python version {sys.version.split()[0]} meets requirements.")
        return True
    else:
        print(f"[ERROR] Current Python version {sys.version.split()[0]} does not meet requirements. Please upgrade to {'.'.join(map(str, min_version))}+.")
        return False

def check_command_exists(command_name):
    """Checks if a given command exists in the system's PATH."""
    print(f"[INFO] Checking for command: {command_name}")
    try:
        # Using --version as a common way to check if a command is executable
        subprocess.run([command_name, '--version'], capture_output=True, check=True, text=True)
        print(f"[SUCCESS] Command '{command_name}' found.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[ERROR] Command '{command_name}' not found or not executable. Please ensure it is installed and added to PATH.")
        return False

def main():
    print("\n[Environment Validation Started]\n")
    all_checks_passed = True

    # Python version check
    if not check_python_version():
        all_checks_passed = False

    # Example: Check for common package managers or tools
    print("\n[Checking for Common Tools]\n")
    required_commands = ['git', 'npm', 'pip3'] # Removed docker as it might not be in all sandboxes
    for cmd in required_commands:
        if not check_command_exists(cmd):
            all_checks_passed = False

    if all_checks_passed:
        print("\n[SUCCESS] All environment checks passed. Environment is ready.\n")
    else:
        print("\n[ERROR] Some environment checks failed. Please review the errors above.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
