#!/usr/bin/env python3
"""
Version Update Script for GS1 GPC Import

This script updates the version number in all necessary files:
- gs1_gpc/__init__.py
- pyproject.toml
- setup.cfg (if exists)
- setup.py (if exists)

Usage:
    python version_update.py 0.1.1
"""

import re
import sys
import os


def update_version(new_version):
    """Update version in all required files"""
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"Error: Version '{new_version}' does not match format X.Y.Z")
        return False

    # Update __init__.py
    init_path = os.path.join('gs1_gpc', '__init__.py')
    update_file(init_path, r"__version__ = '[^']+'", f"__version__ = '{new_version}'")

    # Update pyproject.toml
    update_file('pyproject.toml', r'version = "[^"]+"', f'version = "{new_version}"')

    # Update setup.cfg if it exists
    if os.path.exists('setup.cfg'):
        update_file('setup.cfg', r'version = \d+\.\d+\.\d+', f'version = {new_version}')

    # Update setup.py if it exists
    if os.path.exists('setup.py'):
        update_file('setup.py', r'version="[^"]+"', f'version="{new_version}"')

    print(f"Version updated to {new_version} in all files.")
    return True


def update_file(file_path, pattern, replacement):
    """Update version in a specific file"""
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found.")
        return False

    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(pattern, replacement, content)

    if content == updated_content:
        print(f"No version pattern found in {file_path}")
        return False

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(updated_content)

    print(f"Updated {file_path}")
    return True


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} NEW_VERSION")
        print("Example: python version_update.py 0.1.1")
        return 1

    new_version = sys.argv[1]
    success = update_version(new_version)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())