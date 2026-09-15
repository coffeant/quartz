---
title: "Obsidian CLI"
source: "https://obsidian.md/cli"
author:
published:
created: 2026-09-14
description: "Obsidian CLI is a programmatic playground for plain text. Anything you can do in Obsidian you can do from the command line."
tags:
  - "clippings"
---
## Command your vault.

Anything you can do in Obsidian you can do from the command line.

```
# Open today's daily note
obsidian daily

# Search your vault
obsidian search query="meeting notes"

# Add a task to your daily note
obsidian daily:append content="- [ ] Buy groceries"
```

Use cases

## Obsidian CLI is a programmatic playground for plain text.

Develop

Build plugins and themes faster. Edit code, reload, test, and debug without leaving the terminal.

Collaborate

Deploy documentation, sync shared vaults to servers, and integrate Obsidian into your team’s toolchain.

Automate

Orchestrate your workflow with cron jobs, shell scripts, and custom integrations. If you can script it, you can do it.

Tinker

Read, search, and write to your vault programmatically. Give agentic tools the ability to interact with your vault.

## Run your first command

Once installed, you’re ready to go. Note that the Obsidian app must be running.

Run a command

```
# Show help
obsidian help
```

Use TUI mode

```
# Open TUI (with autocomplete)
obsidian
```

Examples

## See it in action

Check out practical examples, from everyday note-taking to developer automation.

```
# Open today's daily note
obsidian daily

# Add a task to your daily note
obsidian daily:append content="- [ ] Buy groceries"

# Search your vault
obsidian search query="meeting notes"

# Read current file
obsidian read

# List all tasks from daily note
obsidian tasks daily

# Create a new note from template
obsidian create name="Trip to Paris" template=Travel

# View all tags with frequency
obsidian tags counts

# Compare two versions of a file
obsidian diff file=README from=1 to=3
```

```
# Open DevTools
obsidian devtools

# Reload plugin in development
obsidian plugin:reload my-plugin

# Capture app screenshot
obsidian dev:screenshot file=shot.png

# Execute JavaScript
obsidian eval "app.vault.getFiles().length"

# Review JS errors
obsidian dev:errors

# Inspect CSS properties
obsidian dev:css selector=".workspace"

# Query DOM elements
obsidian dev:dom selector=".nav"
```

```
#!/bin/bash
# Morning routine automation

# Open today's daily note
obsidian daily

# Add routine tasks
obsidian daily:append content="- [ ] Review inbox"
obsidian daily:append content="- [ ] Check calendar"

# Copy recent files to clipboard
obsidian files sort=modified limit=5 --copy

# Check for unresolved links
obsidian unresolved

# Search a specific vault and export as JSON
obsidian search query="status::active" vault="Notes" format=json
```

Sync

## Headless Sync

Run [Obsidian Sync](https://obsidian.md/sync) without a GUI. All the speed, privacy, and end-to-end encryption of Obsidian Sync, on any server or automated environment.

[Learn more](https://obsidian.md/help/sync/headless)

- Automate remote backups.
- Automate publishing a website.
- Give agentic tools access to a vault without access to your full computer.
- Sync a shared team vault to a server that feeds other tools.
- Run scheduled automations — aggregate daily notes into weekly summaries, auto-tag, and more.

## Get started

Learn how to install and use Obsidian CLI.