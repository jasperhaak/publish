#!/usr/bin/env python3
"""
Example workflow demonstrating how to use the Quartz Publisher programmatically.

This script shows common operations you might want to automate.
"""

from quartz_publisher import QuartzPublisher
from pathlib import Path
import time
import sys


def main():
    """Demonstrate a typical publication workflow."""
    print("=== Quartz Publisher Example Workflow ===\n")

    # Initialize the publisher
    publisher = QuartzPublisher()

    # 1. Show current status
    print("1. Checking current status...")
    status = publisher.get_status()
    for key, value in status.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    print()

    # 2. Check if Obsidian vault is configured
    if not publisher.config.get("obsidian_vault"):
        print("2. ⚠️  Obsidian vault not configured!")
        print("   Please run: python quartz_publisher.py config --set-obsidian /path/to/vault")
        return
    else:
        print(f"2. ✅ Obsidian vault configured: {publisher.config['obsidian_vault']}")

    # 3. Sync from Obsidian (with dry run first)
    print("\n3. Syncing content from Obsidian...")
    print("   Dry run - showing what would be synced:")
    dry_run = publisher.sync_from_obsidian(dry_run=True)
    for line in dry_run[:5]:  # Show first 5 items
        print(f"   {line}")
    if len(dry_run) > 5:
        print(f"   ... and {len(dry_run) - 5} more files")

    # Ask for confirmation
    response = input("\n   Proceed with sync? (y/n): ")
    if response.lower() == 'y':
        print("   Syncing files...")
        synced = publisher.sync_from_obsidian()
        print(f"   ✅ Synced {len(synced)} files")
    else:
        print("   ❌ Sync cancelled")
        return

    # 4. Build the site
    print("\n4. Building the site...")
    result = publisher.build_site()
    if result.returncode == 0:
        print("   ✅ Build successful!")
    else:
        print("   ❌ Build failed!")
        print(f"   Error: {result.stderr}")
        return

    # 5. Preview the site (optional)
    print("\n5. Starting preview server...")
    try:
        server = publisher.preview_site(port=8080)
        print("   🌐 Preview available at: http://localhost:8080")
        print("   ⏳ Server will run for 10 seconds...")

        # Let the server run for a bit
        time.sleep(10)

        server.terminate()
        print("   ⏹️  Preview server stopped")
    except Exception as e:
        print(f"   ⚠️  Could not start preview: {e}")

    # 6. Ask if user wants to deploy
    print("\n6. Ready to deploy!")
    response = input("   Deploy to GitHub Pages? (y/n): ")
    if response.lower() == 'y':
        print("   Deploying...")
        result = publisher.deploy_to_github()
        if result.returncode == 0:
            print("   ✅ Deployment initiated!")
            print("   📊 Check your GitHub repository for deployment status.")
        else:
            print("   ❌ Deployment failed!")
            print(f"   Error: {result.stderr}")
    else:
        print("   ❌ Deployment cancelled")

    print("\n=== Workflow Complete ===")


if __name__ == "__main__":
    main()