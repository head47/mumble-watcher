# discord-watcher

Bot that watches a Discord voice channel and notifies a Telegram group when someone joins/leaves

## Prerequisites

* `pacman -S libolm`
* `pip -r requirements.txt`

## Configuring

* Run `login.py` once to generate credentials file
* Add `"discord_token": "YOUR_TOKEN_HERE"` to `credentials.json`
* Invite the bot account to the room (you have to accept the invite manually)
* Set room ID in `common.py`

## Running

* `main.py` -- run bot
* `discord-watcher.service` is a systemd unit that starts `main.py`
