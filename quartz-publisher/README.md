# Quartz Publisher

A Python tool to assist with publishing your Obsidian vault to GitHub Pages using Quartz. This tool provides both command-line and graphical user interfaces for managing Quartz content, building your site, and deploying to GitHub Pages.

## Features

- **Easy Sync**: Sync content from your Obsidian vault to Quartz content directory
- **Build Management**: Build your Quartz site with a single command
- **Local Preview**: Preview your site locally before deployment
- **GitHub Pages Integration**: Deploy to GitHub Pages with automatic commit and push
- **Configuration Management**: Persistent configuration for your setup
- **Status Monitoring**: Check the current state of your Quartz setup
- **Graphical User Interface**: User-friendly GUI for all operations

## Installation

1. Ensure you have Python 3.7+ installed
2. Make sure you have Quartz already set up
3. Download or copy the files to your preferred location

## Quick Start

### Using the GUI (Recommended)

Simply double-click `Quartz Publisher GUI.bat` to launch the graphical interface:

![GUI Screenshot]

The GUI provides:
- **Dashboard**: View status and perform actions
- **Configuration**: Set up paths and preferences
- **Logs**: View operation history

### Using the Command Line

```bash
# Set your paths first
python quartz_publisher.py config --set-obsidian /path/to/your/obsidian/vault
python quartz_publisher.py config --set-quartz /path/to/your/quartz

# Sync your content
python quartz_publisher.py sync

# Build your site
python quartz_publisher.py build

# Preview locally
python quartz_publisher.py preview

# Deploy to GitHub Pages
python quartz_publisher.py deploy
```

## GUI Features

### Dashboard Tab
- **Status Display**: Shows current Quartz setup status
- **Quick Actions**: One-click buttons for sync, build, preview, deploy
- **Real-time Updates**: Status refreshes automatically every 5 seconds

### Configuration Tab
- **Path Configuration**: Browse and set Obsidian and Quartz directories
- **Build Settings**: Customize build and serve commands
- **File Patterns**: Configure which files to include/exclude
- **Save Settings**: Persist your configuration

### Logs Tab
- **Operation Logs**: View all operations and their results
- **Timestamps**: Each log entry is timestamped
- **Clear Logs**: Clean the log display when needed

## Command Reference

### `sync`
Sync files from your Obsidian vault to Quartz content directory.

```bash
python quartz_publisher.py sync [--dry-run]
```

Options:
- `--dry-run`: Show what would be copied without actually copying

### `build`
Build your Quartz site.

```bash
python quartz_publisher.py build [--serve]
```

Options:
- `--serve`: Build and start a development server with live reload

### `preview`
Start a local server to preview your built site.

```bash
python quartz_publisher.py preview [--port PORT]
```

Options:
- `--port`: Port to serve on (default: 8080)

### `deploy`
Commit and push changes to trigger GitHub Pages deployment.

```bash
python quartz_publisher.py deploy [--message MESSAGE]
```

Options:
- `--message`: Custom commit message

### `status`
Show current status of your Quartz setup.

```bash
python quartz_publisher.py status
```

### `config`
Manage configuration settings.

```bash
python quartz_publisher.py config [--set-obsidian PATH] [--set-quartz PATH] [--show]
```

Options:
- `--set-obsidian`: Set your Obsidian vault path
- `--set-quartz`: Set your Quartz directory path
- `--show`: Display current configuration

## Configuration

The tool creates configuration files:
- `config.json` - Main configuration in the tool directory
- `quartz-publisher.json` - Quartz-specific settings

Configuration includes:
- Obsidian vault path
- Quartz directory path
- File inclusion/exclusion patterns
- Build commands
- GitHub Pages settings

## Workflow Examples

### GUI Workflow
1. Launch the GUI (`Quartz Publisher GUI.bat`)
2. Go to Configuration tab to set your paths
3. Return to Dashboard and click "Sync from Obsidian"
4. Click "Build Site"
5. Click "Preview" to review
6. Click "Deploy" when ready

### CLI Workflow
```bash
# Initial setup
python quartz_publisher.py config --set-obsidian ~/Documents/ObsidianVault
python quartz_publisher.py config --set-quartz ~/Documents/quartz

# Daily usage
python quartz_publisher.py sync
python quartz_publisher.py build
python quartz_publisher.py deploy
```

## Troubleshooting

### GUI Issues
- **"Python not installed"**: Install Python 3.7+ and add to PATH
- **"Module not found"**: Run from the quartz-publisher directory
- **Window doesn't appear**: Check console for error messages

### Common Errors
- **"Obsidian vault path not configured"**: Set the path in Configuration tab
- **"Site not built"**: Run build before previewing
- **Git commands failing**: Check repository permissions and branch

## Tips

1. **First-time setup**: Configure paths in the GUI before using
2. **Preview before deploy**: Always check locally before pushing
3. **Check logs**: Use the Logs tab to troubleshoot issues
4. **Save config**: Remember to save configuration changes
5. **GitHub Pages**: Ensure your repository has GitHub Pages enabled

## File Structure

```
quartz-publisher/
├── quartz_publisher.py          # Main CLI tool
├── quartz_publisher_gui.py      # GUI application
├── Quartz Publisher GUI.bat     # GUI launcher (Windows)
├── quartz-publisher.bat         # CLI launcher (Windows)
├── config.json                 # Tool configuration
├── example_workflow.py          # Example script
└── README.md                   # This file
```

## Requirements

- Python 3.7 or higher
- Quartz installed and configured
- Git repository for GitHub Pages deployment
- Obsidian (optional, for content creation)

## License

This tool is provided as-is to help with Quartz publishing workflow. Feel free to modify and distribute as needed.