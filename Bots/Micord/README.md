# Micord
 Sync your Discord chat to your Minecraft server chat

- Send Minecraft Chat In Discord Channel
- Send Discord Messages In Minecraft Server
- Send Player Activity To Discord (Player Join Server, Player Death, Player Leave Server)

[Spigot Resource](https://www.spigotmc.org/resources/micord.85404/)

# Installation
## Creating Bot
1. Create Bot and Inviting it with [this tutorial](https://discordpy.readthedocs.io/en/latest/discord.html)
2. After that paste ths Token to Micord ```config.yml``` file
## Creating Webhook
First you need to create a webhook in a text channel. We're assuming you have both Manage Channel and Manage Webhooks permissions!

1. Go in a channel properties (Alternatively, Server Settings)
2. Click Integrations
3. Click View Webhooks
4. Click New Webhook
5. Type in a name (this is for local reference, it's overriden by the incoming hook data)
6. Copy the Webhook URL (you can use the Copy button)
7. Then paste the Webhook URL to your Micord ```config.yml``` file

![Webhook Images](/guide/webhook.png)

> Note: Do NOT give the Webhook URL out to the public. Anyone or service can post messages to this channel, without even needing to be in the server. Keep it safe!
## Getting Channel ID
### Enabling Developer Mode
First you need to enable Developer mode
> if you have Developer mode enabled skip this step
1. Go to your user Setting
2. Click Appearance
3. Scroll down
4. Enable Developer Mode

![Devmode](https://support.discord.com/hc/article_attachments/360058190591/Capture6.jpg)
### Getting Channel ID
1. Right click Channel you want to use
2. Click ``Copy ID`` Button
3. Then Paste the Channel ID to Micord ``config.yml`` file

![CopyIDImage](https://support.discord.com/hc/article_attachments/115002742811/mceclip1.png)
