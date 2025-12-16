#!/usr/bin/env python3
"""
Quartz Publisher - A Python tool to assist with publishing Obsidian vaults to GitHub Pages using Quartz.

This tool provides a convenient interface for managing Quartz content, building the site,
and deploying to GitHub Pages.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, List
import argparse
from datetime import datetime


class QuartzPublisher:
    """Main class for managing Quartz publication workflow."""

    def __init__(self, quartz_dir: Optional[Path] = None, obsidian_vault: Optional[Path] = None):
        """
        Initialize the Quartz Publisher.

        Args:
            quartz_dir: Path to Quartz installation
            obsidian_vault: Path to Obsidian vault directory
        """
        # Try to load quartz_dir from tool's config first
        tool_config_file = Path(__file__).parent / "config.json"
        if not quartz_dir and tool_config_file.exists():
            with open(tool_config_file, 'r') as f:
                tool_config = json.load(f)
                quartz_dir = tool_config.get("quartz_dir")

        self.quartz_dir = Path(quartz_dir) if quartz_dir else Path.cwd()
        self.obsidian_vault = Path(obsidian_vault) if obsidian_vault else None
        self.content_dir = self.quartz_dir / "content"
        self.public_dir = self.quartz_dir / "public"
        self.config_file = self.quartz_dir / "quartz-publisher.json"

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)

        # Default configuration
        default_config = {
            "obsidian_vault": str(self.obsidian_vault) if self.obsidian_vault else "",
            "exclude_patterns": [
                ".obsidian",
                ".trash",
                ".DS_Store",
                "Thumbs.db"
            ],
            "include_patterns": [
                "*.md",
                "*.png",
                "*.jpg",
                "*.jpeg",
                "*.gif",
                "*.svg",
                "*.pdf"
            ],
            "auto_sync": False,
            "default_branch": "v4",
            "build_command": "npx quartz build",
            "serve_command": "npx quartz build --serve",
            "github_pages": {
                "enabled": True,
                "branch": "gh-pages",
                "auto_deploy": True
            }
        }

        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def sync_from_obsidian(self, dry_run: bool = False) -> List[str]:
        """
        Sync content from Obsidian vault to Quartz content directory.

        Args:
            dry_run: If True, show what would be synced without actually doing it

        Returns:
            List of synced files
        """
        if not self.obsidian_vault:
            raise ValueError("Obsidian vault path not configured")

        if not self.obsidian_vault.exists():
            raise ValueError(f"Obsidian vault not found: {self.obsidian_vault}")

        # Ensure content directory exists
        self.content_dir.mkdir(exist_ok=True)

        synced_files = []

        # Walk through obsidian vault
        for item in self.obsidian_vault.rglob("*"):
            # Skip directories and excluded patterns
            if item.is_dir():
                continue

            # Check exclusions
            if any(item.match(pattern) for pattern in self.config.get("exclude_patterns", [])):
                continue

            # Check inclusions
            if not any(item.match(pattern) for pattern in self.config.get("include_patterns", [])):
                continue

            # Calculate relative path
            rel_path = item.relative_to(self.obsidian_vault)
            dest_path = self.content_dir / rel_path

            if dry_run:
                synced_files.append(f"Would copy: {item} -> {dest_path}")
                continue

            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(item, dest_path)
            synced_files.append(f"Copied: {item} -> {dest_path}")

        return synced_files

    def build_site(self, serve: bool = False) -> subprocess.CompletedProcess:
        """
        Build the Quartz site.

        Args:
            serve: If True, build and serve the site locally

        Returns:
            Result of the build command
        """
        os.chdir(self.quartz_dir)

        if serve:
            cmd = self.config.get("serve_command", "npx quartz build --serve").split()
        else:
            cmd = self.config.get("build_command", "npx quartz build").split()

        return subprocess.run(cmd, capture_output=True, text=True)

    def preview_site(self, port: int = 8080) -> subprocess.Popen:
        """
        Start a preview server for the built site.

        Args:
            port: Port to serve on

        Returns:
            Process object for the server
        """
        if not self.public_dir.exists():
            raise ValueError("Site not built. Run build_site() first.")

        os.chdir(self.public_dir)
        return subprocess.Popen(
            ["python", "-m", "http.server", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def deploy_to_github(self, commit_message: Optional[str] = None) -> subprocess.CompletedProcess:
        """
        Commit and push changes to trigger GitHub Pages deployment.

        Args:
            commit_message: Custom commit message

        Returns:
            Result of the git commands
        """
        os.chdir(self.quartz_dir)

        if not commit_message:
            commit_message = f"Quartz sync: {datetime.now().strftime('%Y-%m-%d, %I:%M %p')}"

        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True
        )

        # Push if commit was successful
        if result.returncode == 0:
            push_result = subprocess.run(
                ["git", "push", "origin", self.config.get("default_branch", "v4")],
                capture_output=True,
                text=True
            )
            return push_result

        return result

    def get_status(self) -> Dict:
        """Get current status of the Quartz setup."""
        status = {
            "quartz_dir": str(self.quartz_dir),
            "content_dir": str(self.content_dir),
            "content_files": len(list(self.content_dir.rglob("*.md"))) if self.content_dir.exists() else 0,
            "public_dir": str(self.public_dir),
            "site_built": self.public_dir.exists() and any(self.public_dir.iterdir()),
            "config_file": str(self.config_file),
            "obsidian_vault": self.config.get("obsidian_vault", "Not configured"),
            "github_pages_enabled": self.config.get("github_pages", {}).get("enabled", False)
        }

        # Git status
        try:
            os.chdir(self.quartz_dir)
            git_status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            status["git_clean"] = len(git_status.stdout.strip()) == 0
            status["git_branch"] = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            ).stdout.strip()
        except subprocess.CalledProcessError:
            status["git_clean"] = False
            status["git_branch"] = "Unknown"

        return status


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Quartz Publisher - Manage your Quartz site")
    parser.add_argument("--quartz-dir", type=Path, help="Path to Quartz installation")
    parser.add_argument("--obsidian-vault", type=Path, help="Path to Obsidian vault")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync from Obsidian vault")
    sync_parser.add_argument("--dry-run", action="store_true", help="Show what would be synced")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the site")
    build_parser.add_argument("--serve", action="store_true", help="Build and serve locally")

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview the built site")
    preview_parser.add_argument("--port", type=int, default=8080, help="Port to serve on")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to GitHub Pages")
    deploy_parser.add_argument("--message", help="Custom commit message")

    # Status command
    subparsers.add_parser("status", help="Show current status")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--set-obsidian", type=Path, help="Set Obsidian vault path")
    config_parser.add_argument("--set-quartz", type=Path, help="Set Quartz directory path")
    config_parser.add_argument("--show", action="store_true", help="Show current config")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize publisher
    publisher = QuartzPublisher(
        quartz_dir=args.quartz_dir,
        obsidian_vault=args.obsidian_vault
    )

    # Handle commands
    if args.command == "sync":
        try:
            synced = publisher.sync_from_obsidian(dry_run=args.dry_run)
            for file in synced:
                print(file)
            print(f"\nSynced {len(synced)} files")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "build":
        try:
            print("Building site...")
            result = publisher.build_site(serve=args.serve)
            if result.returncode == 0:
                print("Build successful!")
                if not args.serve:
                    print(f"Site built in: {publisher.public_dir}")
            else:
                print("Build failed!")
                print(result.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "preview":
        try:
            print(f"Starting preview server on port {args.port}...")
            server = publisher.preview_site(port=args.port)
            print(f"Preview available at: http://localhost:{args.port}")
            print("Press Ctrl+C to stop")

            try:
                server.wait()
            except KeyboardInterrupt:
                server.terminate()
                print("\nPreview server stopped")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "deploy":
        try:
            print("Deploying to GitHub Pages...")
            result = publisher.deploy_to_github(commit_message=args.message)
            if result.returncode == 0:
                print("Deployment initiated successfully!")
                print("Check your GitHub repository actions for deployment status.")
            else:
                print("Deployment failed!")
                print(result.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "status":
        status = publisher.get_status()
        print("\n=== Quartz Publisher Status ===\n")
        for key, value in status.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    elif args.command == "config":
        if args.set_obsidian:
            publisher.config["obsidian_vault"] = str(args.set_obsidian.resolve())
            publisher._save_config(publisher.config)
            print(f"Obsidian vault set to: {args.set_obsidian}")

        if args.set_quartz:
            # Update tool's config file
            tool_config_file = Path(__file__).parent / "config.json"
            tool_config = {}
            if tool_config_file.exists():
                with open(tool_config_file, 'r') as f:
                    tool_config = json.load(f)

            tool_config["quartz_dir"] = str(args.set_quartz.resolve())

            # Copy other settings from current config
            for key in ["obsidian_vault", "exclude_patterns", "include_patterns",
                       "default_branch", "build_command", "serve_command", "github_pages"]:
                if key in publisher.config:
                    tool_config[key] = publisher.config[key]

            with open(tool_config_file, 'w') as f:
                json.dump(tool_config, f, indent=2)

            print(f"Quartz directory set to: {args.set_quartz}")
            print(f"Configuration saved to: {tool_config_file}")

        if args.show:
            print("\n=== Current Configuration ===\n")
            print(json.dumps(publisher.config, indent=2))


if __name__ == "__main__":
    main()