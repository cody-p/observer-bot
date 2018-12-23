# observer-bot
Basic administration bot. ONLY has administration features, no other junk.
Still in beta, not really ready to use yet.
The bot is currently intended to be a single server, self hosted bot. It is unknown if this will change in the future.

## Use
You must add the bot's token to a file named "token" in the execution directory in order for the bot to start.

## Features
Reposts messages that are quickdeleted. If there's a channel named #mod-chat, it will post the alerts there instead.
Toss, untoss, timer, and purge commands.
Use the =help command for more info.

## Planned features
* Toss should eventually remove roles. Untoss likewise restore them.
* Make channel and role names configurable
* Make quickdelete have a channel blacklist
* Give quickdelete a configurable, randomized time
* Logging
* A say command
* Configurable prefixes
* Anonymous report function
* Greet messages
* Word blacklist (slurs, etc)
* Message archiving
* Sniping (revealing recent edits)
