# Redbot Bible Cog: Discord Setup Guide

This document records the setup steps used to get the Redbot Bible cog working in Discord.

## What was happening

Initially, the bot was not actually present in the Discord server, so commands like `.help` and `.repo list` appeared to do nothing. The missing pieces were:

- creating a Discord application + bot
- inviting the bot to the server
- running Redbot in Docker
- loading the `downloader` cog
- installing and loading the Bible cog
- setting a prefix

## Step-by-step setup

### 1. Create the Discord application

Open the Discord Developer Portal:

- https://discord.com/developers/applications

Then:

1. Click **New Application**.
2. Give it a name.
3. Click **Create**.

### 2. Open the bot settings

Inside the application:

1. Click **Bot** in the left sidebar.
2. If the bot already exists, you will see token and intent settings.
3. If needed, click **Reset Token** and copy the token.

### 3. Enable required intents

On the **Bot** page:

1. Turn on **Message Content Intent**.
2. Turn on **Server Members Intent** only if needed.

### 4. Invite the bot to the server

In the Developer Portal:

1. Click **OAuth2**.
2. Click **URL Generator**.
3. Under **Scopes**, check:
   - `bot`
   - `applications.commands` if you want slash commands
4. Under **Bot Permissions**, check at least:
   - View Channels
   - Send Messages
   - Read Message History
   - Embed Links
   - Attach Files
5. Copy the generated invite URL.
6. Open it in a browser.
7. Pick the target server.
8. Click **Authorize**.
9. Complete CAPTCHA if prompted.

### 5. Run Redbot in Docker

A minimal `docker-compose.yml` used for this setup:

```yaml
version: "3.2"

services:
  redbot:
    container_name: redbot
    image: phasecorex/red-discordbot:latest
    restart: unless-stopped
    environment:
      TOKEN: "${DISCORD_BOT_TOKEN}"
      PREFIX: "."
      TZ: "UTC"
    volumes:
      - ./redbot-data:/data
```

And a matching `.env` file:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
```

Start it with:

```bash
docker compose up -d
```

Watch logs with:

```bash
docker compose logs -f redbot
```

### 6. Confirm the bot is alive

The bot was confirmed working when:

- it appeared online in the server member list
- `.help` returned lots of output

That told us the bot was receiving commands correctly.

### 7. Load the downloader cog

The built-in repo/cog manager was not loaded at first.

Check loaded cogs with:

```text
.cogs
```

The output showed `downloader` was unloaded.

Load it with:

```text
.load downloader
```

This is what enables `.repo` and `.cog` commands.

### 8. Add the Bible cog repo

Once `downloader` was loaded:

```text
.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog
```

### 9. Install the Bible cog

Then install it from the repo:

```text
.cog install anvil bible
```

If Redbot says the package was not found, check the repo contents with:

```text
.cog list anvil
```

### 10. Load the Bible cog

After install:

```text
.load bible
```

### 11. Test the cog

A successful test command was:

```text
.bible lookup genesis 1:1
```

That confirmed the cog was installed and working.

### 12. Set the prefix

To change the prefix for just this server:

```text
.set serverprefix !
```

To change the global prefix for the bot everywhere:

```text
.set prefix !
```

After changing the prefix, commands become:

```text
!help
!bible lookup genesis 1:1
```

## Working command sequence

This is the final working flow that was established:

1. Start Redbot in Docker.
2. Invite the bot to the server.
3. Confirm `.help` works.
4. Check loaded cogs with `.cogs`.
5. Load downloader with `.load downloader`.
6. Add the repo with `.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog`.
7. Install the cog with `.cog install anvil bible`.
8. Load the cog with `.load bible`.
9. Test with `.bible lookup genesis 1:1`.
10. Set the prefix with `.set serverprefix !`.

## Notes

- The Bible cog commands include `lookup`, `search`, `isearch`, and note commands.
- The repo install step only works after `downloader` is loaded.
- If `.help` does nothing, the bot is likely not receiving commands or lacks the needed Discord settings/permissions.
- If `.repo list` gives no response but `.help` works, the package manager cog is probably unloaded.

## Reference commands

```text
.help
.cogs
.load downloader
.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog
.repo list
.cog list anvil
.cog install anvil bible
.load bible
.bible lookup genesis 1:1
.set serverprefix !
```
