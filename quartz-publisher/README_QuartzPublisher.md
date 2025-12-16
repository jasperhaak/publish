# Quartz Publisher

A Python tool to assist with publishing your Obsidian vault to GitHub Pages using Quartz. This tool simplifies the workflow of syncing content, building your site, and deploying to GitHub Pages.

## Features

- **Easy Sync**: Sync content from your Obsidian vault to Quartz content directory
- **Build Management**: Build your Quartz site with a single command
- **Local Preview**: Preview your site locally before deployment
- **GitHub Pages Integration**: Deploy to GitHub Pages with automatic commit and push
- **Configuration Management**: Persistent configuration for your setup
- **Status Monitoring**: Check the current state of your Quartz setup

## Installation

1. Ensure you have Python 3.7+ installed
2. Make sure you have Quartz already set up (you do!)
3. Download or copy `quartz_publisher.py` to your Quartz directory

## Quick Start

### 1. Configure your Obsidian vault

```bash
python quartz_publisher.py config --set-obsidian /path/to/your/obsidian/vault
```

### 2. Sync your content

```bash
# See what would be synced (dry run)
python quartz_publisher.py sync --dry-run

# Actually sync the files
python quartz_publisher.py sync
```

### 3. Build your site

```bash
# Build once
python quartz_publisher.py build

# Build and serve locally for development
python quartz_publisher.py build --serve
```

### 4. Preview your site

```bash
# Preview the built site on port 8080
python quartz_publisher.py preview --port 8080
```

### 5. Deploy to GitHub Pages

```bash
# Deploy with automatic commit message
python quartz_publisher.py deploy

# Deploy with custom commit message
python quartz_publisher.py deploy --message "Updated my digital garden"
```

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
python quartz_publisher.py config [--set-obsidian PATH] [--show]
```

Options:
- `--set-obsidian`: Set your Obsidian vault path
- `--show`: Display current configuration

## Configuration

The tool creates a `quartz-publisher.json` file in your Quartz directory with settings like:

```json
{
  "obsidian_vault": "/path/to/your/obsidian/vault",
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
  "auto_sync": false,
  "default_branch": "v4",
  "build_command": "npx quartz build",
  "serve_command": "npx quartz build --serve",
  "github_pages": {
    "enabled": true,
    "branch": "gh-pages",
    "auto_deploy": true
  }
}
```

## Typical Workflow

1. **Initial Setup**:
   ```bash
   python quartz_publisher.py config --set-obsidian ~/Documents/ObsidianVault
   ```

2. **Daily Usage**:
   ```bash
   # Sync new notes from Obsidian
   python quartz_publisher.py sync

   # Build and preview locally
   python quartz_publisher.py build
   python quartz_publisher.py preview

   # If happy with the result, deploy
   python quartz_publisher.py deploy
   ```

3. **Development**:
   ```bash
   # Continuous development with live reload
   python quartz_publisher.py build --serve
   ```

## Integration with Your Existing Setup

You already have:
- ✅ Quartz v4.5.2 installed
- ✅ GitHub Pages workflow configured (`.github/workflows/deploy.yml`)
- ✅ Git repository initialized
- ✅ Content directory structure

The Python publisher will work seamlessly with your existing setup, providing a more convenient interface for common tasks.

## Troubleshooting

### "Obsidian vault path not configured"
Run `python quartz_publisher.py config --set-obsidian /path/to/vault` first.

### "Site not built. Run build_site() first"
You need to build your site before previewing: `python quartz_publisher.py build`

### Git commands failing
Make sure you're in a git repository and have proper permissions to push to your GitHub repository.

## Tips

1. **Exclude patterns**: Edit `quartz-publisher.json` to exclude files you don't want in your site
2. **Custom commit messages**: Use descriptive messages when deploying for better history tracking
3. **Local preview**: Always preview locally before deploying to catch issues early
4. **Batch operations**: The sync command intelligently copies only new/changed files

## Example Automation Script

Here's a simple script to automate your publication workflow:

```bash
#!/bin/bash
# publish.sh - Simple publication script

echo "🔄 Syncing from Obsidian..."
python quartz_publisher.py sync

echo "🏗️  Building site..."
python quartz_publisher.py build

echo "👀 Previewing at http://localhost:8080..."
python quartz_publisher.py preview --port 8080 &

read -p "Press Enter to deploy to GitHub Pages..."

echo "🚀 Deploying to GitHub Pages..."
python quartz_publisher.py deploy

echo "✅ Done! Check your GitHub repository for deployment status."
```

Make it executable with `chmod +x publish.sh` and run it with `./publish.sh`.