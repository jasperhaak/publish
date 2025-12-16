#!/usr/bin/env python3
"""
Quartz Publisher GUI - Standalone version with all functionality built-in.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import json
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import os


class QuartzPublisherStandalone:
    """Standalone version of Quartz Publisher with GUI."""

    def __init__(self, root):
        self.root = root
        self.root.title("Quartz Publisher - GUI")
        self.root.geometry("900x700")

        # Configuration
        self.config_file = Path(__file__).parent / "config.json"
        self.quartz_dir = None
        self.obsidian_vault = None
        self.config = self.load_config()

        # Initialize paths from config
        if "quartz_dir" in self.config:
            self.quartz_dir = Path(self.config["quartz_dir"])
        if "obsidian_vault" in self.config and self.config["obsidian_vault"]:
            self.obsidian_vault = Path(self.config["obsidian_vault"])

        # Queue for thread communication
        self.queue = queue.Queue()

        # Setup UI
        self.setup_ui()

        # Update status periodically
        self.update_status()
        self.root.after(1000, self.process_queue)

    def load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")

        # Default configuration
        return {
            "obsidian_vault": "",
            "quartz_dir": "",
            "exclude_patterns": [".obsidian", ".trash", ".DS_Store", "Thumbs.db"],
            "include_patterns": ["*.md", "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.pdf"],
            "default_branch": "v4",
            "build_command": "npx quartz build",
            "serve_command": "npx quartz build --serve",
            "github_pages": {"enabled": True}
        }

    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
            return False

    def setup_ui(self):
        """Setup the main UI components."""
        # Create main notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Dashboard
        dashboard_frame = ttk.Frame(notebook)
        notebook.add(dashboard_frame, text="Dashboard")
        self.setup_dashboard(dashboard_frame)

        # Tab 2: Configuration
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self.setup_config(config_frame)

        # Tab 3: Logs
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Logs")
        self.setup_logs(logs_frame)

    def setup_dashboard(self, parent):
        """Setup the dashboard tab."""
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)

        self.status_vars = {}
        status_items = [
            ("Quartz Directory:", "quartz_dir"),
            ("Content Files:", "content_files"),
            ("Site Built:", "site_built"),
            ("Git Branch:", "git_branch"),
            ("Git Clean:", "git_clean"),
            ("Obsidian Vault:", "obsidian_vault"),
            ("GitHub Pages:", "github_pages_enabled")
        ]

        for i, (label, key) in enumerate(status_items):
            ttk.Label(status_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            var = tk.StringVar()
            self.status_vars[key] = var
            ttk.Label(status_frame, textvariable=var, foreground="blue").grid(row=i, column=1, sticky='w', padx=10, pady=2)

        # Actions frame
        actions_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        actions_frame.pack(fill='x', padx=10, pady=5)

        # Create buttons
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack()

        ttk.Button(btn_frame, text="Sync from Obsidian", command=self.sync_obsidian).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Build Site", command=self.build_site).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Preview", command=self.preview_site).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Deploy", command=self.deploy_site).grid(row=0, column=3, padx=5, pady=5)

        # Quick info frame
        info_frame = ttk.LabelFrame(parent, text="Quick Info", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        info_text = """
• Sync: Copy files from Obsidian vault to Quartz content directory
• Build: Generate the static site from your content
• Preview: View the site locally before deploying
• Deploy: Push changes to GitHub Pages
        """

        ttk.Label(info_frame, text=info_text, justify='left').pack()

    def setup_config(self, parent):
        """Setup the configuration tab."""
        # Obsidian Vault Path
        obsidian_frame = ttk.LabelFrame(parent, text="Obsidian Vault", padding=10)
        obsidian_frame.pack(fill='x', padx=10, pady=5)

        self.obsidian_var = tk.StringVar(value=self.config.get("obsidian_vault", ""))
        ttk.Entry(obsidian_frame, textvariable=self.obsidian_var, width=70).pack(side='left', padx=5)
        ttk.Button(obsidian_frame, text="Browse...", command=self.browse_obsidian).pack(side='left')

        # Quartz Directory Path
        quartz_frame = ttk.LabelFrame(parent, text="Quartz Directory", padding=10)
        quartz_frame.pack(fill='x', padx=10, pady=5)

        self.quartz_var = tk.StringVar(value=self.config.get("quartz_dir", ""))
        ttk.Entry(quartz_frame, textvariable=self.quartz_var, width=70).pack(side='left', padx=5)
        ttk.Button(quartz_frame, text="Browse...", command=self.browse_quartz).pack(side='left')

        # Save button
        ttk.Button(parent, text="Save Configuration", command=self.save_config_ui).pack(pady=10)

    def setup_logs(self, parent):
        """Setup the logs tab."""
        # Log display
        self.log_text = scrolledtext.ScrolledText(parent, wrap='word', width=100, height=30)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Clear button
        ttk.Button(parent, text="Clear Logs", command=self.clear_logs).pack(pady=5)

    def log_message(self, message):
        """Add a message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.root.update_idletasks()

    def clear_logs(self):
        """Clear the log display."""
        self.log_text.delete('1.0', 'end')

    def get_status(self):
        """Get current status."""
        status = {}

        if self.quartz_dir and self.quartz_dir.exists():
            status["quartz_dir"] = str(self.quartz_dir)
            content_dir = self.quartz_dir / "content"
            public_dir = self.quartz_dir / "public"

            # Count markdown files
            if content_dir.exists():
                status["content_files"] = len(list(content_dir.rglob("*.md")))
            else:
                status["content_files"] = 0

            # Check if site is built
            status["site_built"] = public_dir.exists() and any(public_dir.iterdir())

            # Git status
            try:
                os.chdir(self.quartz_dir)
                git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
                status["git_clean"] = len(git_status.stdout.strip()) == 0
                git_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
                status["git_branch"] = git_branch.stdout.strip()
            except:
                status["git_clean"] = False
                status["git_branch"] = "Unknown"
        else:
            status["quartz_dir"] = "Not configured"
            status["content_files"] = 0
            status["site_built"] = False
            status["git_clean"] = False
            status["git_branch"] = "Unknown"

        status["obsidian_vault"] = self.obsidian_vault if self.obsidian_vault else "Not configured"
        status["github_pages_enabled"] = self.config.get("github_pages", {}).get("enabled", False)

        return status

    def update_status(self):
        """Update the status display."""
        try:
            status = self.get_status()
            for key, var in self.status_vars.items():
                if key in status:
                    value = status[key]
                    if key == "site_built":
                        value = "Yes" if value else "No"
                    elif key == "git_clean":
                        value = "Yes" if value else "No"
                    elif key == "github_pages_enabled":
                        value = "Yes" if value else "No"
                    var.set(str(value))
        except Exception as e:
            self.log_message(f"Error updating status: {e}")

        # Schedule next update
        self.root.after(5000, self.update_status)  # Update every 5 seconds

    def browse_obsidian(self):
        """Browse for Obsidian vault directory."""
        directory = filedialog.askdirectory(
            title="Select Obsidian Vault Directory",
            initialdir=self.obsidian_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.obsidian_var.set(directory)

    def browse_quartz(self):
        """Browse for Quartz directory."""
        directory = filedialog.askdirectory(
            title="Select Quartz Directory",
            initialdir=self.quartz_var.get() or os.path.expanduser("~")
        )
        if directory:
            self.quartz_var.set(directory)

    def save_config_ui(self):
        """Save configuration from UI."""
        try:
            # Update config
            self.config["obsidian_vault"] = self.obsidian_var.get()
            self.config["quartz_dir"] = self.quartz_var.get()

            # Update paths
            if self.config["quartz_dir"]:
                self.quartz_dir = Path(self.config["quartz_dir"])
            if self.config["obsidian_vault"]:
                self.obsidian_vault = Path(self.config["obsidian_vault"])

            # Save to file
            if self.save_config():
                messagebox.showinfo("Success", "Configuration saved successfully!")
                self.log_message("Configuration saved")
                self.update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            self.log_message(f"Error saving config: {e}")

    def run_in_thread(self, func, *args, **kwargs):
        """Run a function in a separate thread."""
        def thread_func():
            try:
                result = func(*args, **kwargs)
                self.queue.put(("success", result))
            except Exception as e:
                self.queue.put(("error", str(e)))

        threading.Thread(target=thread_func, daemon=True).start()

    def process_queue(self):
        """Process messages from background threads."""
        try:
            while True:
                msg_type, msg = self.queue.get_nowait()
                if msg_type == "success":
                    if isinstance(msg, list):
                        for line in msg:
                            self.log_message(str(line))
                    else:
                        self.log_message(str(msg))
                    messagebox.showinfo("Success", "Operation completed successfully!")
                elif msg_type == "error":
                    self.log_message(f"Error: {msg}")
                    messagebox.showerror("Error", msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def sync_from_obsidian(self):
        """Sync content from Obsidian vault to Quartz content directory."""
        if not self.obsidian_vault:
            raise ValueError("Obsidian vault not configured")

        if not self.obsidian_vault.exists():
            raise ValueError(f"Obsidian vault not found: {self.obsidian_vault}")

        if not self.quartz_dir:
            raise ValueError("Quartz directory not configured")

        content_dir = self.quartz_dir / "content"
        content_dir.mkdir(exist_ok=True)

        synced_files = []
        exclude_patterns = self.config.get("exclude_patterns", [])
        include_patterns = self.config.get("include_patterns", [])

        for item in self.obsidian_vault.rglob("*"):
            if item.is_dir():
                continue

            # Check exclusions
            if any(item.match(pattern) for pattern in exclude_patterns):
                continue

            # Check inclusions
            if not any(item.match(pattern) for pattern in include_patterns):
                continue

            # Calculate relative path
            rel_path = item.relative_to(self.obsidian_vault)
            dest_path = content_dir / rel_path

            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(item, dest_path)
            synced_files.append(f"Copied: {rel_path}")

        return synced_files or ["No files to sync"]

    def build_site(self):
        """Build the Quartz site."""
        if not self.quartz_dir or not self.quartz_dir.exists():
            raise ValueError("Quartz directory not found")

        os.chdir(self.quartz_dir)
        cmd = self.config.get("build_command", "npx quartz build").split()

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Build failed: {result.stderr}")

        return ["Build completed successfully"]

    def preview_site(self):
        """Start a preview server."""
        if not self.quartz_dir:
            raise ValueError("Quartz directory not configured")

        public_dir = self.quartz_dir / "public"
        if not public_dir.exists():
            raise ValueError("Site not built. Run build first.")

        os.chdir(public_dir)
        server = subprocess.Popen(
            ["python", "-m", "http.server", "8080"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return ["Preview server started at http://localhost:8080"]

    def deploy_site(self):
        """Deploy to GitHub Pages."""
        if not self.quartz_dir:
            raise ValueError("Quartz directory not configured")

        os.chdir(self.quartz_dir)

        # Stage all changes
        subprocess.run(["git", "add", "."], check=True)

        # Commit with message
        commit_message = f"Quartz sync: {datetime.now().strftime('%Y-%m-%d, %I:%M %p')}"
        result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)

        # Push if commit was successful
        if result.returncode == 0:
            push_result = subprocess.run(
                ["git", "push", "origin", self.config.get("default_branch", "v4")],
                capture_output=True,
                text=True
            )
            if push_result.returncode != 0:
                raise RuntimeError(f"Push failed: {push_result.stderr}")
            return ["Deployment initiated successfully"]
        else:
            return ["No changes to commit"]

    def sync_obsidian(self):
        """Sync from Obsidian vault."""
        if not self.obsidian_var.get():
            messagebox.showwarning("Warning", "Please configure your Obsidian vault path first!")
            return
        self.log_message("Starting sync from Obsidian...")
        self.run_in_thread(self.sync_from_obsidian)

    def build_site_action(self):
        """Build the site."""
        self.log_message("Building site...")
        self.run_in_thread(self.build_site)

    def preview_site_action(self):
        """Preview the site."""
        self.log_message("Starting preview server...")
        self.run_in_thread(self.preview_site)

    def deploy_site_action(self):
        """Deploy to GitHub Pages."""
        self.log_message("Deploying to GitHub Pages...")
        self.run_in_thread(self.deploy_site)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = QuartzPublisherStandalone(root)

    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()