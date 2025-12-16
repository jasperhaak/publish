#!/usr/bin/env python3
"""
Quartz Publisher GUI - A graphical user interface for managing Quartz publication workflow.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import json
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import os

# Import the main QuartzPublisher class
from quartz_publisher import QuartzPublisher


class QuartzPublisherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quartz Publisher - GUI")
        self.root.geometry("900x700")

        # Initialize publisher
        self.publisher = QuartzPublisher()

        # Queue for thread communication
        self.queue = queue.Queue()

        # Setup UI
        self.setup_ui()

        # Update status periodically
        self.update_status()
        self.root.after(1000, self.process_queue)

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
        config_scroll = ttk.Scrollbar(parent)
        config_scroll.pack(side='right', fill='y')

        config_canvas = tk.Canvas(parent, yscrollcommand=config_scroll.set)
        config_canvas.pack(side='left', fill='both', expand=True)
        config_scroll.config(command=config_canvas.yview)

        config_frame_inner = ttk.Frame(config_canvas)
        config_canvas.create_window((0, 0), window=config_frame_inner, anchor='nw')

        # Obsidian Vault Path
        obsidian_frame = ttk.LabelFrame(config_frame_inner, text="Obsidian Vault", padding=10)
        obsidian_frame.pack(fill='x', padx=10, pady=5)

        self.obsidian_var = tk.StringVar(value=self.publisher.config.get("obsidian_vault", ""))
        ttk.Entry(obsidian_frame, textvariable=self.obsidian_var, width=70).pack(side='left', padx=5)
        ttk.Button(obsidian_frame, text="Browse...", command=self.browse_obsidian).pack(side='left')

        # Quartz Directory Path
        quartz_frame = ttk.LabelFrame(config_frame_inner, text="Quartz Directory", padding=10)
        quartz_frame.pack(fill='x', padx=10, pady=5)

        self.quartz_var = tk.StringVar(value=str(self.publisher.quartz_dir))
        ttk.Entry(quartz_frame, textvariable=self.quartz_var, width=70).pack(side='left', padx=5)
        ttk.Button(quartz_frame, text="Browse...", command=self.browse_quartz).pack(side='left')

        # Build Settings
        build_frame = ttk.LabelFrame(config_frame_inner, text="Build Settings", padding=10)
        build_frame.pack(fill='x', padx=10, pady=5)

        self.build_cmd_var = tk.StringVar(value=self.publisher.config.get("build_command", "npx quartz build"))
        ttk.Label(build_frame, text="Build Command:").grid(row=0, column=0, sticky='w', pady=2)
        ttk.Entry(build_frame, textvariable=self.build_cmd_var, width=50).grid(row=0, column=1, padx=5)

        self.serve_cmd_var = tk.StringVar(value=self.publisher.config.get("serve_command", "npx quartz build --serve"))
        ttk.Label(build_frame, text="Serve Command:").grid(row=1, column=0, sticky='w', pady=2)
        ttk.Entry(build_frame, textvariable=self.serve_cmd_var, width=50).grid(row=1, column=1, padx=5)

        # File Patterns
        patterns_frame = ttk.LabelFrame(config_frame_inner, text="File Patterns", padding=10)
        patterns_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(patterns_frame, text="Include Patterns:").grid(row=0, column=0, sticky='nw', pady=2)
        self.include_patterns = tk.Text(patterns_frame, height=4, width=50)
        self.include_patterns.grid(row=0, column=1, padx=5)
        self.include_patterns.insert('1.0', '\n'.join(self.publisher.config.get("include_patterns", [])))

        ttk.Label(patterns_frame, text="Exclude Patterns:").grid(row=1, column=0, sticky='nw', pady=2)
        self.exclude_patterns = tk.Text(patterns_frame, height=4, width=50)
        self.exclude_patterns.grid(row=1, column=1, padx=5)
        self.exclude_patterns.insert('1.0', '\n'.join(self.publisher.config.get("exclude_patterns", [])))

        # Save button
        ttk.Button(config_frame_inner, text="Save Configuration", command=self.save_config).pack(pady=10)

        config_frame_inner.update_idletasks()
        config_canvas.config(scrollregion=config_canvas.bbox('all'))

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

    def clear_logs(self):
        """Clear the log display."""
        self.log_text.delete('1.0', 'end')

    def update_status(self):
        """Update the status display."""
        try:
            status = self.publisher.get_status()
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

    def save_config(self):
        """Save the configuration."""
        try:
            # Update publisher config
            self.publisher.config["obsidian_vault"] = self.obsidian_var.get()
            self.publisher.config["build_command"] = self.build_cmd_var.get()
            self.publisher.config["serve_command"] = self.serve_cmd_var.get()

            # Parse patterns
            include_text = self.include_patterns.get('1.0', 'end').strip()
            if include_text:
                self.publisher.config["include_patterns"] = [p.strip() for p in include_text.split('\n') if p.strip()]

            exclude_text = self.exclude_patterns.get('1.0', 'end').strip()
            if exclude_text:
                self.publisher.config["exclude_patterns"] = [p.strip() for p in exclude_text.split('\n') if p.strip()]

            # Save configuration
            self.publisher._save_config(self.publisher.config)

            # Also save to tool config if quartz dir changed
            if self.quartz_var.get() != str(self.publisher.quartz_dir):
                tool_config_file = Path(__file__).parent / "config.json"
                tool_config = {}
                if tool_config_file.exists():
                    with open(tool_config_file, 'r') as f:
                        tool_config = json.load(f)
                tool_config["quartz_dir"] = self.quartz_var.get()
                with open(tool_config_file, 'w') as f:
                    json.dump(tool_config, f, indent=2)

            messagebox.showinfo("Success", "Configuration saved successfully!")
            self.log_message("Configuration saved")

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
                    if hasattr(msg, '__iter__') and not isinstance(msg, str):
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

    def sync_obsidian(self):
        """Sync from Obsidian vault."""
        if not self.obsidian_var.get():
            messagebox.showwarning("Warning", "Please configure your Obsidian vault path first!")
            return

        self.log_message("Starting sync from Obsidian...")
        self.run_in_thread(self.publisher.sync_from_obsidian)

    def build_site(self):
        """Build the site."""
        self.log_message("Building site...")
        self.run_in_thread(self.publisher.build_site)

    def preview_site(self):
        """Preview the site."""
        def preview():
            server = self.publisher.preview_site()
            self.queue.put(("success", f"Preview server started at http://localhost:8080"))
            return server

        self.log_message("Starting preview server...")
        self.run_in_thread(preview)

    def deploy_site(self):
        """Deploy to GitHub Pages."""
        self.log_message("Deploying to GitHub Pages...")
        self.run_in_thread(self.publisher.deploy_to_github)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = QuartzPublisherGUI(root)

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