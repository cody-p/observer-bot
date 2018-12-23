# observer-bot
Basic administration bot. ONLY has administration features, no other junk.
Still in beta, but usable.
The bot is currently intended to be a single server, self hosted bot. It is unknown if this will change in the future.

## Use
You must add the bot's token to a file named "token" in the execution directory in order for the bot to start.

## Features
Configurable. Will generate a default config (config.ini) if none is present. If the config is changed while the bot is running, the "reload" command must be used for it to take effect.

Reposts messages that are quickdeleted. Channel to repost is configurable; if invalid or left blank in config, will be reposted wherever the deletion happened. 

Has toss, untoss, timer, purge, and anonymous report commands.
Use the =help command for more commands.

## Planned features
* Make quickdelete have a channel blacklist
* Logging
* A say command
* Configurable prefixes
* Greet messages
* Word blacklist (slurs, etc)
* Message archiving
* Sniping (revealing recent edits)
