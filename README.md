# mumble-watcher

Bot that watches a Mumble voice channel and notifies a Telegram group when someone joins/leaves

## Prerequisites

* `pacman -S libolm`
* `slice2py /usr/share/mumble-server/MumbleServer.ice` to generate Python ZeroC Ice bindings
* `pip -r requirements.txt`

## Configuring

* Invite the bot account to the room (you have to accept the invite manually)
* Run `matrix_login.py` once to generate config file

## Running

* `main.py` -- run bot
* `discord-watcher.service` is a systemd unit that starts `main.py`
