# Discord Setup Guide

## Pause Role Setup Guide

This guide explains how to create and configure the "Paused" role for the Grossmann bot's `/pause` command.

### What does the Paused role do?

The `/pause` command allows admins to temporarily restrict a user's activity on the server for a specified number of hours. The role is automatically removed after the time expires, and the state persists across bot restarts.

### Step 1: Create the Role in Discord

1. Open Discord and go to your server
2. Click the server name at the top left → **Server Settings**
3. Go to **Roles** in the left sidebar
4. Click the **Create Role** button
5. Configure the role:
   - **Name:** "Paused" (or your preferred name)
   - **Color:** Optional (e.g., gray to indicate inactive status)
   - **Display separately:** Optional

### Step 2: Configure Role Permissions

In the **Permissions** tab, **DENY** all permissions.

### Step 3: Get the Role ID

#### Option A: Use the bot's command
Run `/fetchrole` in Discord (requires admin permissions). This will list all roles with their IDs.

#### Option B: Use Discord Developer Mode
1. Go to **User Settings** → **App Settings** → **Advanced**
2. Enable **Developer Mode**
3. Go back to **Server Settings** → **Roles**
4. Right-click the Paused role
5. Click **Copy Role ID**

### Step 4: Configure the Bot

Edit `src/common/constants.py` and set the role IDs there.

### Step 5: Role Hierarchy (Important!)

**The bot's role must be ABOVE the Paused role in the role list.**

Discord only allows bots to manage roles that are lower than their own role in the hierarchy.

To fix this:
1. Go to **Server Settings** → **Roles**
2. Find the bot's role (usually named after the bot)
3. Drag it **above** the Paused role in the list
4. Save changes
